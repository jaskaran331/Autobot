## Authentication & Setup

You have two convenient ways to authenticate:

### Option A: One-Time Browser Login (Recommended)
Run the setup tool once. It opens the browser, types your email, and waits for you to enter your password and click Log In. It saves a persistent session to `session.json`, so you **never have to enter your credentials again**:
```powershell
cd C:\Users\Asus\.gemini\antigravity\scratch\businessclass-agent
python login_setup.py
```

### Option B: Automatic Credentials via Environment Variables
Set your password temporarily in your shell (never stored on disk):
```powershell
$env:BC_EMAIL = "jaskaran4raju@gmail.com"
$env:BC_PASSWORD = "your_actual_password_here"
$env:GEMINI_API_KEY = "your_gemini_api_key"
```

---

## Running the Agent

Once logged in (or with `$env:BC_PASSWORD` set):

```powershell
# 1. Calibrate selectors (discovers courses and assignment fields)
python calibrate.py

# 2. Run the main agent
python agent.py
```

You'll be prompted for your password (never stored). The agent will:

1. Log in and discover all modules
2. Skip already-completed modules
3. For each pending module:
   - Extract questions
   - Generate answers via Gemini
   - Generate images via Gemini Imagen (where required)
   - Show you each answer for review
   - Submit only after your explicit approval
4. Save progress to `state.json`
5. Print a summary of completed vs. errored modules

### Controls during review

| Key | Action |
|-----|--------|
| `A` | Approve — submit this answer |
| `S` | Skip — don't submit, move to next |
| `E` | Edit — type a replacement answer |
| `Q` | Quit — stop the agent |

## Files

| File | Purpose |
|------|---------|
| `agent.py` | Main automation agent |
| `calibrate.py` | Selector discovery/calibration tool |
| `state.json` | Progress tracker (auto-created) |
| `generated/` | AI-generated images and HTML dumps |

## Security

- Password is prompted at runtime via `getpass` — never written to disk
- `GEMINI_API_KEY` is read from environment variable
- `state.json` stores only module IDs and timestamps, no credentials
- Browser runs in visible (non-headless) mode so you can watch everything
