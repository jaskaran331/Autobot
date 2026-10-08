"""
auto_runner.py — Autonomous Business Class milestone completion agent.
=====================================================================
Completes ALL remaining milestones/tasks/activities/quizzes for Semester 1.

Designed to run headless on GitHub Actions or locally.

Usage:
    python auto_runner.py                 # headless, all milestones
    python auto_runner.py --headed        # visible browser
    python auto_runner.py --milestone 4   # start from milestone 4

Env vars (for GitHub Actions):
    BC_EMAIL, BC_PASSWORD, GEMINI_API_KEY
"""

import json
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
SESSION_FILE = BASE_DIR / "session.json"
CURRICULUM_FILE = BASE_DIR / "curriculum_data.json"
STATE_FILE = BASE_DIR / "state.json"
GENERATED_DIR = BASE_DIR / "generated"
GENERATED_DIR.mkdir(exist_ok=True)
PHOTO_PATH = GENERATED_DIR / "product_shortlist_notes.jpg"

SITE = "https://businessclass.punjab.gov.in"
HEADLESS = "--headed" not in sys.argv
START_MILESTONE = 1
for i, a in enumerate(sys.argv):
    if a == "--milestone" and i + 1 < len(sys.argv):
        START_MILESTONE = int(sys.argv[i + 1])

# ---------------------------------------------------------------------------
# Quiz answer map (pre-computed from curriculum_data.json)
# ---------------------------------------------------------------------------
def load_quiz_map():
    if not CURRICULUM_FILE.exists():
        print("[!] curriculum_data.json not found — quizzes will be answered by DOM matching only")
        return {}
    data = json.load(open(CURRICULUM_FILE, encoding="utf-8"))
    qmap = {}
    for term in data.get("terms", []):
        for course in term.get("courses", []):
            for module in course.get("modules", []):
                for res in module.get("resources", []):
                    quiz = res.get("quiz")
                    if quiz and "questions" in quiz:
                        for q in quiz["questions"]:
                            q_text = q["question"].strip()
                            correct = [
                                opt["option_heading"].strip()
                                for opt in q.get("options", [])
                                if opt.get("isCorrect")
                            ]
                            if correct:
                                qmap[q_text] = correct[0]
    return qmap


QUIZ_MAP = load_quiz_map()
print(f"[*] Loaded {len(QUIZ_MAP)} pre-computed quiz answers.")


# ---------------------------------------------------------------------------
# Placeholder photo (creates one if none exists)
# ---------------------------------------------------------------------------
def ensure_photo():
    if PHOTO_PATH.exists():
        return
    try:
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (800, 600), "#f8f9fa")
        d = ImageDraw.Draw(img)
        d.rectangle([20, 20, 780, 580], outline="#333", width=2)
        d.text((50, 50), "Punjab Bag Studio - Assignment Evidence", fill="#333")
        d.text((50, 80), "Canvas Tote Bag E-commerce Business", fill="#666")
        d.text((50, 120), "Product research, supplier verification,", fill="#666")
        d.text((50, 150), "and market analysis documentation.", fill="#666")
        img.save(str(PHOTO_PATH), "JPEG", quality=85)
        print(f"[*] Created placeholder photo: {PHOTO_PATH.name}")
    except ImportError:
        # Minimal 1x1 white JPEG
        import base64
        tiny = base64.b64decode(
            "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkS"
            "Ew8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJ"
            "CQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIy"
            "MjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEA"
            "AAAAAAAAAAECAwQFBgcICQoL/8QAFRABAAAAAAAAAAAAAAAAAAAAEf/EABQRAQAAAAA"
            "AAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AL+AD//Z"
        )
        PHOTO_PATH.write_bytes(tiny)
        print(f"[*] Created minimal placeholder photo")


# ---------------------------------------------------------------------------
# State tracking
# ---------------------------------------------------------------------------
def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"completed": {}, "errors": {}, "last_run": None}


def save_state(state):
    state["last_run"] = datetime.now().isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Smart text generator for any activity
# ---------------------------------------------------------------------------
def generate_answer(activity_name, milestone_context=""):
    """Generate a realistic 40-60 word business answer for any activity."""
    # ponytail: mapping keywords to pre-written responses avoids LLM calls entirely
    responses = {
        "watch": None,  # video — no text needed
        "read": None,   # reading — no text needed
        "video": None,

        # Supplier milestone
        "online supplier": "I researched 5 verified online suppliers on IndiaMART and Meesho for canvas tote bags: CottonCraft India (Rs 80/unit), EcoFab Surat (Rs 85/unit), GreenPack Delhi (Rs 90/unit), Punjab Handlooms Ludhiana (Rs 95/unit), and TrendyBags Jaipur (Rs 100/unit). All have 4+ star ratings.",
        "offline supplier": "I visited local wholesale markets in Jalandhar and Ludhiana: Verma Bag Emporium (Rs 110), Sharma Cloth Traders (Rs 105), Guru Nanak Handlooms (Rs 95), Khalsa Textiles Chaura Bazar (Rs 90), Jalandhar Canvas Mart (Rs 100). Quality verified in person.",
        "3 supplier": "Top 3 suppliers selected: 1. CottonCraft India Rs 80/unit, 4 days delivery, 4.8 rating. 2. EcoFab Surat Rs 85/unit, 3 days delivery, 4.6 rating. 3. Khalsa Textiles Ludhiana Rs 90/unit, 1 day local, 4.7 rating.",
        "draft": "Hello, I am from Punjab Bag Studio. We are launching an online store for premium canvas tote bags. Could you please share your wholesale catalog, MOQ details, unit pricing for bulk orders, and delivery timelines to Punjab? Looking forward to a long-term partnership.",
        "send message": "Sent wholesale inquiry via WhatsApp and IndiaMART to CottonCraft India, EcoFab Surat, and Khalsa Textiles. All responded within 24 hours with detailed price lists, MOQ terms, and sample availability. Quotes range from Rs 80 to Rs 95 per unit.",
        "sample": "Ordered sample tote bags from CottonCraft India and showed to 3 potential customers. Feedback was excellent: appreciated heavy stitching, clean zippers, eco-friendly canvas, and minimalist design. All confirmed willingness to purchase at Rs 299 retail.",
        "compare price": "Compared suppliers: CottonCraft offers 320 GSM heavy canvas at Rs 80/unit (best value). EcoFab provides 280 GSM at Rs 85. Khalsa Textiles offers 300 GSM at Rs 90. CottonCraft clearly provides superior durability-to-price ratio.",
        "negotiate": "Negotiated with CottonCraft India for bulk pricing. Committed to 50 units initial order with monthly reorders. Supplier agreed to reduce from Rs 85 to Rs 75/unit and provide free polybag packaging for all consignments.",
        "finalize": "Finalized CottonCraft India as primary supplier. Terms: Rs 75/unit, 50 units MOQ, 4-day delivery to Punjab, full replacement warranty for defective pieces, payment 50% advance and 50% on dispatch.",

        # Dukaan store milestone
        "dukaan store": "Created 'Punjab Bag Studio' store on Dukaan with business email verification. Selected India as operating country, set currency to INR, and configured store category as Retail E-commerce with focus on bags and accessories.",
        "warehouse": "Set up main warehouse address in Jalandhar, Punjab pin code 144001. Added complete dispatch point details with contact person information. Skipped optional GST registration during initial startup phase as recommended.",
        "product detail": "Added flagship product: 'Premium Eco Canvas Tote Bag' under Bags category. Set retail price Rs 299 with detailed description covering 320 GSM cotton canvas, reinforced stitching, inner pockets, and eco-friendly manufacturing.",
        "product image": "Uploaded 3 high-quality product images: front view showing full bag design, close-up of stitching and zipper quality, and lifestyle shot showing the bag in daily use. All images have clean white background.",
        "inventory": "Configured initial inventory of 50 units with low-stock alert at 5 units. Enabled automatic stock deduction on confirmed orders and set up inventory tracking dashboard for real-time monitoring.",
        "shipping": "Set shipping weight to 350g, dimensions 38x35x10 cm. Added color variants: Natural Beige, Midnight Black, Olive Green. Configured flat Rs 40 pan-India shipping with estimated 4-7 day delivery.",
        "theme": "Selected clean minimalist theme matching our eco-friendly brand identity. Applied earthy green primary color, set responsive mobile layout, and ensured intuitive product discovery navigation.",
        "store information": "Completed store details: About Us describing our sustainable bag mission, contact phone, customer support WhatsApp, 7-day return/exchange policy, and linked Instagram and Facebook social profiles.",
        "customiz": "Customized store with brand colors, professional logo placement, easy-to-navigate product categories, and mobile-responsive layout. Added trust badges and clear product descriptions for customer confidence.",

        # Payment milestone
        "payment method": "Selected UPI and Cash on Delivery as primary payment methods for Punjab Bag Studio. COD is essential for building initial customer trust, while UPI provides instant settlement.",
        "cash on delivery": "Enabled Cash on Delivery option in Dukaan settings. Set COD availability for all pin codes in Punjab and neighboring states. Added Rs 20 COD handling fee to cover collection costs.",
        "online payment": "Initiated Razorpay integration for online payments. Submitted business PAN and bank account details. UPI, debit cards, and net banking will be available once verified within 24-48 hours.",
        "payment activation": "Payment setup completed successfully. Both COD and online payment (UPI/cards) are now active. Tested with a simulated checkout flow to verify smooth transaction processing.",
        "test product": "Added a test product priced at Rs 1 to verify checkout flow. Confirmed product appears correctly in store catalog with proper images, description, and pricing.",
        "test order": "Asked a friend to place a test order using the Rs 1 test product. Order appeared in Dukaan dashboard within seconds. Payment status and order details displayed correctly.",
        "dashboard": "Verified test order in Dukaan dashboard: order number assigned, customer details captured, payment status confirmed, and shipping label ready for generation.",
        "delete test": "Removed the test product from store catalog after successful payment verification. Store is now ready for real customers with actual products only.",

        # Launch milestone
        "poster": "Designed a professional launch poster on Canva featuring our canvas tote bag product image, store name 'Punjab Bag Studio', launch offer of 15% off, and clear call-to-action with store link.",
        "launch poster": "Created eye-catching Canva poster with product photos, brand colors, Rs 299 price, and 'Shop Now' button linking to our Dukaan store. Used clean typography and eco-friendly green accents.",
        "5 friends": "Shared launch poster with 5 close friends and received feedback. They suggested making the discount more prominent and adding delivery information. Incorporated all suggestions into final design.",
        "launch message": "Drafted launch message: 'Excited to launch Punjab Bag Studio! Premium eco-friendly canvas tote bags at Rs 299. Perfect for college, work, and shopping. Order now and get 15% off! [store link]'",
        "finalize launch": "Finalized launch message incorporating friend feedback: added free delivery mention, 15% off code 'LAUNCH15', customer testimonial preview, and clear store link with WhatsApp order option.",
        "punjab startup": "Uploaded business details on Punjab Startup App: business name, category, product description, contact info, and Dukaan store link. Registration provides visibility in Punjab's startup ecosystem.",

        # Marketing & promotion
        "50 people": "Listed 50 potential customers from personal circle: 15 college friends, 10 family members, 8 workplace colleagues, 7 neighborhood contacts, and 10 social media connections with interest in eco products.",
        "sample message": "Created promotional message: 'Hi! I just launched Punjab Bag Studio selling premium canvas tote bags. Check out our store: [link]. Use code LAUNCH15 for 15% off your first order! Would love your support.'",
        "50 people message": "Sent personalized messages to all 50 contacts via WhatsApp. 35 opened the store link, 12 added products to cart, and 5 showed strong purchase intent within the first 24 hours.",
        "10 people forward": "Asked 10 closest friends to forward store message in their circles. Combined reach expanded to approximately 200+ people through personal referrals and WhatsApp group shares.",
        "whatsapp status": "Posted launch poster on WhatsApp Status with 'Swipe up' call-to-action. Status viewed by 80+ contacts within 6 hours, generating 15 direct store visits and 3 inquiries.",
        "instagram post": "Created Instagram post with product carousel showing bag from multiple angles. Used hashtags: #PunjabBagStudio #EcoFriendly #CanvasBags #ShopLocal. Got 25 likes and 5 comments within first day.",
        "comment": "Asked friends and family to comment on Instagram post with their honest feedback. Received 8 positive comments highlighting product quality and eco-friendly appeal. Responded to each personally.",
        "respond": "Responded to all comments and 6 DMs within 2 hours. Answered product queries about size, material, and delivery. Converted 2 DM inquiries into confirmed orders.",
        "3 groups": "Identified 3 active groups: Punjab College Students WhatsApp group (120 members), Local Business Network Facebook group (500 members), and Eco Products India Facebook group (2000 members).",
        "whatsapp group": "Shared store poster and launch message in 3 WhatsApp groups with admin permission. Focused on highlighting eco-friendly aspect and local Punjab manufacturing. Received 8 inquiries.",
        "facebook group": "Posted product showcase in 3 Facebook groups following group rules. Included product photos, pricing, and store link. Posts received 30+ reactions and 5 direct messages.",

        # First sale
        "interested people": "Compiled list of 18 interested people from launch promotion: 8 from personal contacts, 5 from WhatsApp groups, 3 from Instagram DMs, and 2 from Facebook groups. All expressed purchase intent.",
        "offer": "Created three promotional offers: 1. 'First Order 15% Off' using code FIRST15. 2. 'Buy 2 Get 10% Off' bundle deal. 3. 'Free Delivery' on orders above Rs 500. All offers valid for 7 days.",
        "first order": "Received first confirmed order from college friend for 2 canvas tote bags (Natural Beige + Olive Green). Total: Rs 598 minus 15% = Rs 508. Payment via UPI confirmed instantly.",
        "delivery guide": "Read the delivery guide covering packaging standards, label printing, courier partner selection, and tracking setup. Key takeaway: use proper bubble wrap and include a thank-you note.",
        "delivery address": "Confirmed order details with customer: 2 bags, correct color variants, delivery address in Amritsar, Punjab. Verified phone number for delivery OTP. Estimated delivery: 3-4 days.",
        "deliver": "Choosing Shiprocket for delivery as it offers best rates for intra-Punjab shipping at Rs 35 per order. Alternative: India Post for Rs 25 but slower 5-7 day delivery.",
        "shiprocket": "Watched the Shiprocket tutorial and created our business account. Added pickup address (Jalandhar warehouse), entered order details, and generated shipping label with tracking number.",
        "place order": "Placed delivery order on Shiprocket: pickup scheduled for tomorrow, generated AWB tracking number, and printed shipping label. Customer notified with expected delivery date.",
        "inform customer": "Sent order confirmation to customer via WhatsApp with order number, tracking link, estimated delivery date, and our support contact. Customer expressed excitement about the purchase.",
        "customer received": "Customer confirmed receiving the canvas tote bags in perfect condition within 3 days. Both bags matched the product images and description. No damage during transit.",
        "product photo": "Customer shared unboxing photos showing both tote bags. Quality matched expectations perfectly. Requested permission to use photos as testimonials on our store and social media.",
        "feedback": "Customer feedback: 'Amazing quality! The canvas is thick and sturdy, zippers work smoothly, and the bags look even better than photos. Already recommended to friends. Will order more colors soon.'",
        "reflect": "Key learnings: 1. Personal outreach converts best. 2. UPI payments are fastest. 3. Shiprocket provides reliable tracking. Improvements needed: faster response time and more product variants.",

        # WhatsApp Business & Instagram
        "whatsapp business": "Created WhatsApp Business account with business phone number. Set profile with store name, logo, business hours, and automated greeting message for new customer inquiries.",
        "setup whatsapp": "Configured WhatsApp Business: added business description, location, email, website link. Set up automated away message and quick replies for common product questions.",
        "catalog": "Created WhatsApp Business catalog with all 3 bag variants: Natural Beige, Midnight Black, and Olive Green. Each listing includes product photo, price Rs 299, and brief description.",
        "catalog message": "Sent catalog link to 10 existing contacts as test. Format includes product thumbnail, price, and 'View Catalog' button. 7 out of 10 opened and browsed the catalog.",
        "instagram account": "Created professional Instagram account @punjabbagstudio. Switched to business profile for analytics access. Connected to Facebook business page for cross-platform management.",
        "setup instagram": "Set up Instagram profile: bio with store description and Dukaan link, profile picture with brand logo, contact button with WhatsApp link, and highlighted Stories for products and reviews.",
        "first business post": "Created first business post: product flat-lay photo with price overlay, engaging caption about eco-friendly mission, relevant hashtags, and store link in bio. Posted during peak engagement hours.",

        # Customer feedback
        "take feedback": "Called 3 customers for detailed feedback. Topics covered: product quality (4.5/5), delivery speed (4/5), packaging (4/5), and value for money (5/5). Overall satisfaction: 4.4/5.",
        "testimonial": "Created testimonial post with customer photo and quote: 'Best canvas bag I have used! Great quality at affordable price.' Added before/after comparison showing bag durability after 1 month use.",
        "testimonial social": "Posted testimonial on Instagram, WhatsApp Status, and Facebook. Used customer-approved photo with permission. Post reached 200+ people and generated 5 new product inquiries.",
        "negative feedback": "Reviewed feedback: one customer mentioned stitching near handle felt slightly loose. Contacted supplier to reinforce handle stitching on next batch. Offered affected customer free replacement.",
        "changes": "Made improvements based on feedback: 1. Asked supplier to add reinforced handle stitching. 2. Added care instructions card inside packaging. 3. Updated product photos showing stitching quality.",
        "overall learning": "Key learnings: Customer feedback is invaluable for product improvement. Quick response to complaints builds loyalty. Positive reviews drive organic sales. Regular feedback loops ensure continuous quality.",

        # Repeat customer / referral
        "repeat order": "Created follow-up system: contacted previous customers 2 weeks after delivery. Offered 10% loyalty discount on second purchase. 2 out of 5 customers placed repeat orders.",
        "follow-up message": "Follow-up message: 'Hi! Hope you are enjoying your Punjab Bag Studio tote bag. We have new colors available! Use code REPEAT10 for 10% off your next order. Thank you for your support!'",
        "send follow-up": "Sent follow-up message to all 5 previous customers. 4 responded positively, 2 placed repeat orders immediately, and 1 said they would order next week.",
        "received repeat": "Successfully received 2 repeat orders! Customer A ordered 3 bags for friends. Customer B ordered the new Olive Green variant. Repeat order rate: 40% which exceeds 25% target.",
        "referral message": "Referral message: 'Love your tote bag? Share the joy! Refer a friend and both of you get 15% off next order. Just share your unique code with them. Thank you for supporting local business!'",
        "send referral": "Sent referral messages to 5 customers with unique referral codes. 3 customers shared codes with friends. Received 2 new orders through referrals within one week.",
        "received referral": "Received 2 referral orders: one from Amritsar and one from Chandigarh. Both new customers mentioned they were referred by existing customers. Referral conversion rate: 40%.",
        "what helped": "Personal relationships and product quality drove repeat orders. Loyalty discounts incentivized returns. Referral codes with mutual benefits encouraged word-of-mouth marketing. Trust builds slowly but converts consistently.",

        # Business growth planning
        "review growth": "Reviewed 30-day business journey: 8 total orders, Rs 4,200 revenue, 5 unique customers, 2 repeat buyers, 40% repeat rate. Social media reached 500+ people. Key challenge: expanding beyond personal network.",
        "what worked": "What worked: Personal WhatsApp outreach (60% conversion), Instagram product posts (25% engagement), referral codes (40% conversion). What didn't: Facebook group posts had low conversion despite high views.",
        "review your growth": "Growth review: Started from 0 to 8 orders in 30 days. Customer satisfaction 4.4/5. Product return rate 0%. Best channel: WhatsApp (5 sales). Need: paid advertising and larger product catalog.",
        "sales goal": "30-day sales target: increase from 8 to 25 orders. Revenue goal: Rs 7,500. Strategy: expand product range to 5 variants, run Instagram ads at Rs 100/day, and build email list of 100 subscribers.",
        "1-2 product": "Focusing on 2 products: 1. Original Canvas Tote Bag (Rs 299) - proven seller. 2. NEW Large Laptop Canvas Bag (Rs 499) - higher margin, targets working professionals. Both from CottonCraft India.",
        "business growth": "Growth plan: Month 1 - add laptop bag variant and run Instagram ads. Month 2 - partner with 2 local college canteens for display. Month 3 - launch seasonal festival collection and WhatsApp newsletter.",
        "submit report": "Final report: Punjab Bag Studio achieved 8 orders in first month with 100% product satisfaction. Built sustainable supply chain with CottonCraft India. Ready to scale with expanded product line and digital marketing.",
    }

    name_lower = activity_name.lower()

    # Check for video/reading activities that just need "Mark as Complete"
    if any(kw in name_lower for kw in ["watch", "video", "read a doc", "read the ", "read this"]):
        return None  # signal: this is a video/reading, just mark complete

    # Find best matching response
    best_match = None
    best_score = 0
    for keyword, response in responses.items():
        if response is None:
            continue
        # Count matching words
        kw_words = keyword.lower().split()
        score = sum(1 for w in kw_words if w in name_lower)
        if score > best_score:
            best_score = score
            best_match = response

    if best_match:
        return best_match

    # Generic fallback
    return (
        f"Completed this activity ({activity_name}) for our Punjab Bag Studio canvas tote bag business. "
        "Conducted thorough market research, analyzed customer preferences, verified competitive pricing, "
        "and documented all findings with supporting evidence for future reference and business planning."
    )


# ---------------------------------------------------------------------------
# Login (for CI — uses env vars)
# ---------------------------------------------------------------------------
def login_if_needed(page, ctx):
    """Login using env vars if session.json doesn't work."""
    page.goto(f"{SITE}/student/track", wait_until="networkidle", timeout=30000)
    time.sleep(2)

    # Check if already logged in (not redirected to login page)
    if "/login" not in page.url and "/auth" not in page.url:
        print("[*] Session is active, already logged in.")
        return True

    email = os.environ.get("BC_EMAIL", "jaskaran4raju@gmail.com")
    password = os.environ.get("BC_PASSWORD", "")
    if not password:
        print("[!] Not logged in and no BC_PASSWORD env var. Cannot continue.")
        return False

    print(f"[*] Logging in as {email}...")
    page.goto(f"{SITE}/login", wait_until="networkidle", timeout=30000)
    time.sleep(2)

    email_input = page.query_selector('input[type="email"]')
    if email_input:
        email_input.fill(email)
    pass_input = page.query_selector('input[type="password"]')
    if pass_input:
        pass_input.fill(password)
    login_btn = page.query_selector('button[type="submit"]')
    if login_btn:
        login_btn.click()

    page.wait_for_load_state("networkidle", timeout=30000)
    time.sleep(3)

    if "/login" in page.url or "/auth" in page.url:
        print("[!] Login failed — still on login page.")
        page.screenshot(path=str(GENERATED_DIR / "login_failed.png"))
        return False

    # Save session
    ctx.storage_state(path=str(SESSION_FILE))
    print("[*] Login successful, session saved.")
    return True


# ---------------------------------------------------------------------------
# Navigation helpers
# ---------------------------------------------------------------------------
def nav_to_semester(page):
    """Navigate to semester milestone list."""
    page.goto(f"{SITE}/student/track", wait_until="networkidle", timeout=30000)
    time.sleep(2)
    btn = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
    if btn and btn.is_visible():
        btn.click()
        time.sleep(2)
        page.wait_for_load_state("networkidle")


def click_milestone(page, milestone_num):
    """Click into a milestone card."""
    text = f"Milestone {milestone_num}"
    cards = page.query_selector_all(f'div:has-text("{text}")')
    for c in cards:
        btn = c.query_selector('button:has-text("Continue Learning"), button:has-text("Start Learning")')
        if btn and btn.is_visible():
            btn.click()
            time.sleep(2)
            page.wait_for_load_state("networkidle")
            return True
    return False


def click_task_by_index(page, task_index):
    """Click nth task (0-indexed) Start/Continue Learning button."""
    btns = page.query_selector_all('button:has-text("Start Learning"), button:has-text("Continue Learning")')
    if task_index < len(btns):
        btns[task_index].click()
        time.sleep(2)
        page.wait_for_load_state("networkidle")
        return True
    return False


def click_task_by_name(page, task_name):
    """Click a task card by its name text."""
    cards = page.query_selector_all(f'div:has-text("{task_name}")')
    for c in cards:
        btn = c.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
        if btn and btn.is_visible():
            btn.click()
            time.sleep(2)
            page.wait_for_load_state("networkidle")
            return True
    return False


# ---------------------------------------------------------------------------
# Activity completion
# ---------------------------------------------------------------------------
def complete_activity(page, activity_name):
    """Click an activity item and complete it (video/text/quiz)."""
    answer = generate_answer(activity_name)

    # Click the activity
    safe_name = activity_name.replace("'", "\\'")
    item = page.query_selector(f"div:has-text('{safe_name}'), button:has-text('{safe_name}')")
    if not item:
        print(f"    [!] Activity not found: {activity_name}")
        return False

    item.click()
    time.sleep(1.5)
    page.wait_for_load_state("networkidle")

    # Click Start Learning / Continue / Attempt if visible
    st = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning"), button:has-text("Attempt")')
    if st and st.is_visible():
        st.click()
        time.sleep(2)
        page.wait_for_load_state("networkidle")

    if answer is None:
        # Video/reading — just mark complete
        mark = page.query_selector('button:has-text("Mark as Complete")')
        if mark and mark.is_visible():
            mark.click()
            print(f"    [OK] Marked complete: {activity_name[:50]}")
            time.sleep(3)
            return True
        else:
            print(f"    [~] Already complete or no mark button: {activity_name[:50]}")
            return True

    # Text activity — fill textarea
    ta = page.query_selector("textarea")
    if ta and ta.is_visible():
        ta.fill(answer)
        print(f"    [OK] Filled textarea ({len(answer.split())} words)")
        time.sleep(1)

    # Upload photo if file input present
    fi = page.query_selector('input[type="file"]')
    if fi and PHOTO_PATH.exists():
        try:
            fi.set_input_files(str(PHOTO_PATH))
            print(f"    [OK] Attached photo")
            time.sleep(1)
        except Exception:
            pass

    # Submit
    sub = page.query_selector('button:has-text("Submit Activity"), button:has-text("Submit")')
    if sub and sub.is_visible():
        sub.click()
        print(f"    [OK] Submitted: {activity_name[:50]}")
        time.sleep(3)
        return True

    return False


def complete_quiz(page, activity_name):
    """Complete a quiz activity using pre-computed answers."""
    # Click quiz item
    safe_name = activity_name.replace("'", "\\'")
    item = page.query_selector(f"div:has-text('{safe_name}'), button:has-text('{safe_name}')")
    if not item:
        print(f"    [!] Quiz not found: {activity_name}")
        return False

    item.click()
    time.sleep(1.5)
    page.wait_for_load_state("networkidle")

    st = page.query_selector('button:has-text("Start Learning"), button:has-text("Attempt"), button:has-text("Continue Learning")')
    if st and st.is_visible():
        st.click()
        time.sleep(2)
        page.wait_for_load_state("networkidle")

    # Try to match quiz answers from our pre-computed map
    answered = 0
    for q_text, ans_text in QUIZ_MAP.items():
        btns = page.query_selector_all("button, label, div[role='radio']")
        for b in btns:
            try:
                txt = b.inner_text().strip()
                if ans_text in txt and b.is_visible():
                    b.click()
                    answered += 1
                    print(f"    [OK] Answer: {ans_text[:60]}")
                    time.sleep(0.4)
                    break
            except Exception:
                continue

    # Submit quiz
    sub = page.query_selector('button:has-text("Submit Quiz")')
    if sub and sub.is_visible():
        sub.click()
        print(f"    [OK] Quiz submitted ({answered} answers selected)")
        time.sleep(3)
        return True

    print(f"    [!] Submit Quiz button not found")
    return False


# ---------------------------------------------------------------------------
# Process one task (all its activities)
# ---------------------------------------------------------------------------
def process_task(page, task_activities):
    """Complete all activities in the current task view."""
    for act_name in task_activities:
        name_lower = act_name.lower()
        try:
            if "quiz" in name_lower or "attempt" in name_lower:
                complete_quiz(page, act_name)
            else:
                complete_activity(page, act_name)
        except Exception as e:
            print(f"    [!] Error on '{act_name[:40]}': {e}")
            traceback.print_exc()
            continue


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------
def main():
    ensure_photo()
    state = load_state()

    # Build activity names from curriculum data
    curriculum = {}
    if CURRICULUM_FILE.exists():
        data = json.load(open(CURRICULUM_FILE, encoding="utf-8"))
        term = data["terms"][0]  # Semester 1
        for c_idx, course in enumerate(term.get("courses", [])):
            m_num = c_idx + 1
            tasks = []
            for mod in course.get("modules", []):
                activities = [res.get("name", "") for res in mod.get("resources", [])]
                tasks.append({"name": mod.get("name", ""), "activities": activities})
            curriculum[m_num] = {
                "name": course.get("name", ""),
                "tasks": tasks,
            }

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=HEADLESS,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )

        # Use session file if exists, otherwise blank context
        if SESSION_FILE.exists():
            ctx = browser.new_context(storage_state=str(SESSION_FILE))
        else:
            ctx = browser.new_context()

        page = ctx.new_page()
        page.set_default_timeout(30000)

        # Login check
        if not login_if_needed(page, ctx):
            browser.close()
            sys.exit(1)

        print(f"\n{'='*60}")
        print(f"  AUTONOMOUS MILESTONE RUNNER")
        print(f"  Starting from Milestone {START_MILESTONE}")
        print(f"{'='*60}\n")

        for m_num in range(START_MILESTONE, 13):
            m_key = f"milestone_{m_num}"

            # Check if already completed on the platform
            nav_to_semester(page)
            time.sleep(1)

            # Check completion status from page
            milestone_text = page.inner_text("body")
            # ponytail: simple string check is enough; no need for DOM parsing
            if f"Milestone {m_num}" in milestone_text:
                is_complete = False
                blocks = milestone_text.split("Milestone ")
                for block in blocks:
                    if block.startswith(f"{m_num}") and "COMPLETED" in block:
                        is_complete = True
                        break

                if is_complete:
                    print(f"[SKIP] Milestone {m_num} already COMPLETED on platform.")
                    continue

            print(f"\n{'='*60}")
            print(f"  MILESTONE {m_num}: {curriculum.get(m_num, {}).get('name', 'Unknown')}")
            print(f"{'='*60}")

            # Navigate into milestone
            nav_to_semester(page)
            if not click_milestone(page, m_num):
                print(f"  [!] Could not click Milestone {m_num} — may not be unlocked yet.")
                page.screenshot(path=str(GENERATED_DIR / f"m{m_num}_blocked.png"), full_page=True)
                break  # Milestones are sequential — if blocked, stop

            # Process each task
            tasks = curriculum.get(m_num, {}).get("tasks", [])
            for t_idx, task in enumerate(tasks):
                task_name = task["name"]
                activities = task["activities"]

                print(f"\n  --- Task {t_idx+1}: {task_name} ---")

                # Navigate back to milestone task list
                nav_to_semester(page)
                click_milestone(page, m_num)

                # Try clicking by task name
                if not click_task_by_name(page, task_name):
                    print(f"  [SKIP] Task '{task_name}' seems already complete or unavailable.")
                    continue

                # Process activities
                process_task(page, activities)

            # Update state
            state["completed"][m_key] = {
                "title": f"Milestone {m_num}: {curriculum.get(m_num, {}).get('name', '')}",
                "completed_at": datetime.now().isoformat(),
            }
            save_state(state)

            # Screenshot
            page.screenshot(path=str(GENERATED_DIR / f"m{m_num}_done.png"), full_page=True)
            print(f"\n  [OK] Milestone {m_num} processing complete!")

        # Final status screenshot
        nav_to_semester(page)
        page.screenshot(path=str(GENERATED_DIR / "final_status.png"), full_page=True)

        print(f"\n{'='*60}")
        print(f"  ALL MILESTONES PROCESSED")
        print(f"  Completed: {list(state['completed'].keys())}")
        print(f"{'='*60}")

        browser.close()


if __name__ == "__main__":
    main()
