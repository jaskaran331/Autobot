import json
import os
import time
from pathlib import Path
from typing import Any

from playwright.sync_api import (
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)

try:
    from google import genai
except ImportError:
    genai = None


BASE_DIR = Path(__file__).resolve().parent
SESSION_FILE = BASE_DIR / "session.json"
CURRICULUM_FILE = BASE_DIR / "curriculum_data.json"
QUIZ_MAP_FILE = BASE_DIR / "quiz_answers.json"

# Set UPLOAD_IMAGE_PATH to a real, task-appropriate image if an activity requires one.
_upload_path = Path(os.environ.get("UPLOAD_IMAGE_PATH", "photo.jpg"))
PHOTO_PATH = _upload_path if _upload_path.is_absolute() else BASE_DIR / _upload_path

TRACK_URL = "https://businessclass.punjab.gov.in/student/track"
LOGIN_URL = "https://businessclass.punjab.gov.in/login"
ARTIFACT_DIR = BASE_DIR / "artifacts"
ARTIFACT_DIR.mkdir(exist_ok=True)

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY and genai else None


def screenshot(page, name: str) -> None:
    """Save a diagnostic screenshot without allowing screenshot failure to hide the real error."""
    try:
        page.screenshot(path=str(ARTIFACT_DIR / name), full_page=True)
    except Exception as exc:
        print(f"[WARN] Could not save screenshot {name}: {exc}")


def visible_text(page, limit: int = 4000) -> str:
    try:
        return page.locator("body").inner_text(timeout=5000)[:limit]
    except Exception:
        return ""


def debug_page(page, label: str) -> None:
    print(f"[DEBUG] {label} URL: {page.url}")
    try:
        print(f"[DEBUG] {label} title: {page.title()}")
    except Exception:
        pass
    body = visible_text(page, 1800)
    print(f"[DEBUG] {label} visible text:\n{body}")
    screenshot(page, f"{label.lower().replace(' ', '_')}.png")


def first_visible_locator(page, selectors: list[str]):
    for selector in selectors:
        locator = page.locator(selector)
        try:
            for i in range(min(locator.count(), 10)):
                item = locator.nth(i)
                if item.is_visible():
                    return item, selector
        except Exception:
            continue
    return None, None


def login_if_needed(page, context) -> None:
    email = os.environ.get("BC_EMAIL", "").strip()
    password = os.environ.get("BC_PASSWORD", "")
    if not email or not password:
        raise RuntimeError("Missing BC_EMAIL or BC_PASSWORD GitHub Actions secrets.")

    page.goto(TRACK_URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(2000)

    # A successful page is determined by URL and visible login controls, not URL alone.
    email_box, _ = first_visible_locator(
        page,
        [
            'input[name="email"]',
            'input[type="email"]',
            'input[autocomplete="username"]',
            'input[placeholder*="email" i]',
            'input[name*="user" i]',
        ],
    )
    password_box, _ = first_visible_locator(
        page,
        [
            'input[name="password"]',
            'input[type="password"]',
            'input[autocomplete="current-password"]',
        ],
    )

    if not password_box and "/login" not in page.url.lower() and "/auth" not in page.url.lower():
        print("[OK] Track page opened without a visible login form; session appears active.")
        return

    if not email_box or not password_box:
        debug_page(page, "login_form_missing")
        raise RuntimeError(
            "Could not identify visible login fields on the portal. "
            "See artifacts/login_form_missing.png and the Actions logs."
        )

    email_box.fill(email)
    password_box.fill(password)

    submit, submit_selector = first_visible_locator(
        page,
        [
            'button[type="submit"]',
            'input[type="submit"]',
            'button:has-text("Log in")',
            'button:has-text("Login")',
            'button:has-text("Sign in")',
        ],
    )
    if not submit:
        debug_page(page, "login_submit_missing")
        raise RuntimeError("Login submit control not found; inspect artifacts/login_submit_missing.png.")

    print(f"[DEBUG] Login submit selector: {submit_selector}")
    submit.click()
    try:
        page.wait_for_load_state("domcontentloaded", timeout=15000)
    except PlaywrightTimeoutError:
        pass
    page.wait_for_timeout(2500)

    # Revisit the protected route to verify that authentication actually persisted.
    page.goto(TRACK_URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(2000)
    email_after, _ = first_visible_locator(
        page,
        ['input[type="email"]', 'input[name="email"]', 'input[type="password"]'],
    )
    if email_after or "/login" in page.url.lower() or "/auth" in page.url.lower():
        debug_page(page, "login_failed")
        raise RuntimeError(
            "Login could not be verified; the portal redirected to a login/auth page. "
            "Check credentials, CAPTCHA/OTP requirements, and artifacts/login_failed.png."
        )

    context.storage_state(path=str(SESSION_FILE))
    print("[OK] Login verified by reopening the protected track route.")


def normalize(value: Any) -> str:
    return " ".join(str(value).split()).casefold()


def load_quiz_answer_map() -> dict[str, str]:
    """Load explicit question -> answer pairs. Never click a global list of answer words."""
    if not QUIZ_MAP_FILE.is_file():
        raise RuntimeError(
            "A quiz was detected, but quiz_answers.json is missing. "
            "Create it with exact question text mapped to verified answer text; "
            "the agent will not guess or click unrelated options."
        )
    try:
        raw = json.loads(QUIZ_MAP_FILE.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Could not parse {QUIZ_MAP_FILE.name}: {exc}") from exc
    if not isinstance(raw, dict) or not raw:
        raise RuntimeError("quiz_answers.json must be a non-empty JSON object.")
    result = {
        normalize(question): str(answer).strip()
        for question, answer in raw.items()
        if str(question).strip() and str(answer).strip()
    }
    if not result:
        raise RuntimeError("quiz_answers.json contains no usable question/answer pairs.")
    return result


def answer_quiz_from_map(page, answer_map: dict[str, str]) -> int:
    """Answer only questions that can be unambiguously matched to an explicit mapping."""
    groups = page.locator("fieldset, [role='radiogroup'], [data-question]")
    matched = 0
    unmatched = []
    seen = set()

    for i in range(groups.count()):
        group = groups.nth(i)
        try:
            if not group.is_visible():
                continue
            group_text = normalize(group.inner_text())
            if not group_text:
                continue

            question_key = next(
                (q for q in answer_map if q in group_text),
                None,
            )
            if question_key is None:
                # It may be a wrapper/duplicate. Only count a group that appears to contain options.
                option_count = group.locator(
                    'input[type="radio"], [role="radio"], label'
                ).count()
                if option_count:
                    unmatched.append(group.inner_text()[:180])
                continue
            if question_key in seen:
                continue

            answer = answer_map[question_key]
            option = group.get_by_text(answer, exact=True)
            if option.count() != 1 or not option.first.is_visible():
                unmatched.append(group.inner_text()[:180])
                continue

            option.first.click()
            seen.add(question_key)
            matched += 1
        except Exception:
            unmatched.append(f"Question group {i}: unable to inspect")

    if matched == 0 or unmatched:
        screenshot(page, "quiz_match_failed.png")
        preview = "; ".join(x.replace("\n", " ") for x in unmatched[:4])
        raise RuntimeError(
            f"Quiz answer matching was incomplete ({matched} matched). "
            f"Unmatched groups: {preview or 'no mapped question matched'}. "
            "No quiz was submitted. Inspect artifacts/quiz_match_failed.png and update "
            "quiz_answers.json/selectors."
        )
    return matched


def generate_ai_response(page) -> dict[str, Any]:
    if client is None:
        raise RuntimeError(
            "GEMINI_API_KEY is missing or the google-genai package is unavailable. "
            "Activity was not submitted."
        )

    title = ""
    try:
        title = page.locator("h1, h2, h3, h4, h5").first.inner_text(timeout=2000)
    except Exception:
        pass
    context_text = visible_text(page, 5000)

    prompt = f"""
You are helping a student prepare a draft for an e-commerce business class activity.
Use only the activity details below. Do not claim that the student completed steps,
uploaded files, contacted suppliers, created accounts, or performed actions unless
the activity text explicitly confirms them. Do not invent URLs.
Return ONLY a valid JSON object with exactly these keys:
{{
  "response": "A relevant draft answer in 100-180 words",
  "needs_link": false,
  "needs_photo": false
}}
Set needs_link true only when the activity explicitly requires a URL/link/video.
Set needs_photo true only when the activity explicitly requires an image/photo/file.
Activity title: {title}
Visible page text:
{context_text}
"""
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        raw = (response.text or "").strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
            raw = raw.rsplit("```", 1)[0].strip()
        data = json.loads(raw)
        answer = str(data.get("response", "")).strip()
        if not answer:
            raise ValueError("Gemini returned an empty response field.")
        return {
            "text": answer,
            "needs_link": bool(data.get("needs_link", False)),
            "needs_photo": bool(data.get("needs_photo", False)),
        }
    except Exception as exc:
        raise RuntimeError(
            f"Could not generate/parse an activity draft ({type(exc).__name__}). "
            "The activity was not submitted."
        ) from exc


def validate_image(path: Path) -> str:
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(
            f"Activity requires an image, but a real non-empty file was not found at {path}."
        )
    try:
        from PIL import Image, UnidentifiedImageError
        with Image.open(path) as image:
            image.verify()
    except ImportError as exc:
        raise RuntimeError("Pillow is required to validate uploaded images; add pillow to requirements.txt.") from exc
    except Exception as exc:
        raise RuntimeError(f"Image is invalid or unreadable: {path}") from exc
    return str(path)


def find_button(page, names: list[str]):
    for name in names:
        locator = page.get_by_role("button", name=name, exact=True)
        try:
            for i in range(min(locator.count(), 10)):
                item = locator.nth(i)
                if item.is_visible() and item.is_enabled():
                    return item
        except Exception:
            continue
    return None


def main() -> None:
    headless = os.environ.get("HEADLESS", "true").strip().lower() in {"1", "true", "yes"}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=headless)
        context = (
            browser.new_context(storage_state=str(SESSION_FILE))
            if SESSION_FILE.is_file()
            else browser.new_context()
        )
        page = context.new_page()
        page.set_default_timeout(8000)

        try:
            login_if_needed(page, context)
            page.goto(TRACK_URL, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2000)

            idle_count = 0
            clicked_coords: set[tuple[int, int]] = set()

            while idle_count < 3:
                try:
                    page.wait_for_load_state("domcontentloaded", timeout=10000)
                except PlaywrightTimeoutError:
                    pass
                print(f"[DEBUG] Current URL: {page.url}")

                # If the portal redirects to login, stop with a useful diagnostic.
                if "/login" in page.url.lower() or "/auth" in page.url.lower():
                    debug_page(page, "unexpected_login_redirect")
                    raise RuntimeError(
                        "The portal redirected to login during navigation. "
                        "Authentication is not active; see artifacts/unexpected_login_redirect.png."
                    )

                action_taken = False

                retry = find_button(page, ["Try again"])
                if retry:
                    retry.click()
                    page.wait_for_timeout(1500)
                    action_taken = True
                    clicked_coords.clear()
                    continue

                quiz_submit = find_button(page, ["Submit Quiz"])
                if quiz_submit:
                    print("[INFO] Quiz detected; using explicit question-to-answer mappings.")
                    answer_map = load_quiz_answer_map()
                    answered = answer_quiz_from_map(page, answer_map)
                    quiz_submit.click()
                    print(f"[OK] Submitted quiz after matching {answered} question(s).")
                    page.wait_for_timeout(2500)
                    clicked_coords.clear()
                    continue

                textarea = page.locator("textarea").first
                if textarea.count() and textarea.is_visible():
                    print("[INFO] Text activity detected; generating a draft.")
                    ai_data = generate_ai_response(page)
                    textarea.fill(ai_data["text"])

                    if ai_data["needs_link"]:
                        link_box, _ = first_visible_locator(
                            page,
                            ['input[type="url"]', 'input[name*="url" i]', 'input[placeholder*="link" i]'],
                        )
                        if not link_box or not link_box.input_value().strip():
                            screenshot(page, "link_required.png")
                            raise RuntimeError(
                                "This activity requires a real link. Set the correct URL manually; "
                                "the agent will not insert a fake/example link. "
                                "See artifacts/link_required.png."
                            )

                    if ai_data["needs_photo"]:
                        file_input = page.locator('input[type="file"]').first
                        if not file_input.count():
                            screenshot(page, "image_upload_failed.png")
                            raise RuntimeError("Activity requires an image but no file input was found.")
                        file_input.set_input_files(validate_image(PHOTO_PATH))

                    submit = find_button(page, ["Submit Activity", "Submit"])
                    if not submit:
                        screenshot(page, "activity_submit_missing.png")
                        raise RuntimeError("Text activity has no visible Submit button.")
                    submit.click()
                    print("[OK] Submitted text activity draft.")
                    page.wait_for_timeout(2500)
                    clicked_coords.clear()
                    continue

                mark = find_button(page, ["Mark as Complete"])
                if mark:
                    mark.click()
                    print("[OK] Marked visible reading/video item complete.")
                    page.wait_for_timeout(2000)
                    clicked_coords.clear()
                    continue

                starts = []
                for name in ["Start Learning", "Continue Learning", "Attempt", "Start Activity"]:
                    locator = page.get_by_role("button", name=name, exact=True)
                    try:
                        for i in range(min(locator.count(), 20)):
                            item = locator.nth(i)
                            if item.is_visible() and item.is_enabled():
                                starts.append(item)
                    except Exception:
                        pass

                clicked = False
                for button in starts:
                    try:
                        label = button.inner_text().strip()
                        parent_text = button.evaluate(
                            """el => {
                                let p = el;
                                for (let i = 0; i < 5 && p; i++, p = p.parentElement) {
                                    const t = p.innerText || '';
                                    if (t.includes('Semester')) return t;
                                }
                                return '';
                            }"""
                        )
                        if "Semester 1" in parent_text:
                            continue
                        box = button.bounding_box()
                        if not box:
                            continue
                        coord = (round(box["x"]), round(box["y"]))
                        if coord in clicked_coords:
                            continue
                        print(f"[INFO] Clicking navigation button: {label}")
                        button.click()
                        clicked_coords.add(coord)
                        page.wait_for_timeout(2000)
                        clicked = action_taken = True
                        clicked_coords.clear()
                        break
                    except Exception as exc:
                        print(f"[WARN] Could not click candidate button: {exc}")

                if clicked:
                    continue

                if not action_taken:
                    idle_count += 1
                    print(f"[WARN] No actionable controls found. Idle check {idle_count}/3.")
                    debug_page(page, f"idle_check_{idle_count}")
                    page.wait_for_timeout(1500)
                else:
                    idle_count = 0

            screenshot(page, "agent_stopped_idle.png")
            raise RuntimeError(
                "Agent stopped after repeated idle checks. Completion has NOT been verified. "
                "Inspect artifacts/idle_check_*.png and the page text in the Actions logs."
            )
        finally:
            try:
                context.close()
            finally:
                browser.close()


if __name__ == "__main__":
    main()
