# Business Class Autonomous Agent

This is an automated agent designed to help complete tasks and milestones on the Business Class portal. It uses Playwright to navigate the site and Google's Gemini AI to generate answers and drafts.

## Prerequisites

1. **Python 3.9+** installed on your system.
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

*(Note: If you don't have a `requirements.txt`, install dependencies directly: `pip install playwright google-genai pillow`)*

## How to Run the Agent

You can run the agent in different ways depending on your needs:

### 1. The Main Agent (Interactive Review)
This runs the agent visibly in your browser and lets you review every AI-generated answer before it is submitted.
```bash
python agent.py
```
**Controls during review:**
- `A` = Approve and submit
- `S` = Skip and move to the next task
- `E` = Edit the answer yourself
- `Q` = Quit the agent

### 2. Super Runner (Fully Autonomous)
This runs completely autonomously in the background (headless). It will power through the milestones on its own.
```bash
python super_runner.py
```

### 3. Check Status
Want to just check your milestone progress without running the full agent?
```bash
python agent.py --status
```

## Authentication

The agent needs three things to work:
1. **Your Email** (for the portal)
2. **Your Password** (for the portal)
3. **Your Gemini API Key** (to generate AI answers)

**How to provide them:**
- **Interactive Prompt:** The easiest way! Just run the script (e.g., `python agent.py`). It will securely ask you to type in your email, password, and API key right in the terminal.
- **Environment Variables:** If you prefer, you can set them in your terminal before running the script so it won't ask you:
  - Windows (PowerShell):
    ```powershell
    $env:BC_EMAIL = "your_email@example.com"
    $env:BC_PASSWORD = "your_password"
    $env:GEMINI_API_KEY = "your_gemini_api_key"
    ```
  - Mac/Linux (Bash):
    ```bash
    export BC_EMAIL="your_email@example.com"
    export BC_PASSWORD="your_password"
    export GEMINI_API_KEY="your_gemini_api_key"
    ```

## Security & Privacy
- Your password is **never** saved to disk. When you type it in the terminal, it is hidden.
- The agent securely stores your login session cookies in a local `session.json` file so you don't have to log in repeatedly. You can delete this file at any time to log out.
- Your API key and credentials are never sent anywhere except directly to the portal and Google's Gemini service.
