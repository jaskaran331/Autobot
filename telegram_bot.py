import os
import subprocess
import telebot

# ---------------------------------------------------------
# SETUP: Put your Telegram Bot Token here
# Get this from @BotFather on Telegram
# ---------------------------------------------------------
BOT_TOKEN = "8618520622:AAHYroohWycVwqgh_C2bdRLGzkh13f7JDT0"
bot = telebot.TeleBot(BOT_TOKEN)

# Store user credentials and active processes in memory
user_data = {}
active_processes = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    msg = bot.reply_to(message, "Welcome to the Business Class Automation Bot! 🚀\n\nPlease enter your **Business Class Email**:")
    bot.register_next_step_handler(msg, process_email)

def process_email(message):
    chat_id = message.chat.id
    user_data[chat_id]['email'] = message.text.strip()
    msg = bot.reply_to(message, "Great. Now enter your **Password**:\n*(Don't worry, I will immediately hide it after you send it)*")
    bot.register_next_step_handler(msg, process_password)

def process_password(message):
    chat_id = message.chat.id
    user_data[chat_id]['password'] = message.text.strip()
    
    # Delete the message containing the password for security
    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass # Bot needs permission to delete messages, otherwise it skips
        
    msg = bot.send_message(chat_id, "Password received! 🔒\n\nFinally, enter your **Gemini API Key**:")
    bot.register_next_step_handler(msg, process_api_key)

def process_api_key(message):
    chat_id = message.chat.id
    user_data[chat_id]['api_key'] = message.text.strip()
    
    # Delete the message containing the API key for security
    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass
    
    bot.send_message(chat_id, "✅ All credentials saved securely in memory!\n\nHere are your commands:\n/run - Start the automation\n/status - Check milestone progress\n/logs - See exactly what the bot is doing right now\n/reset - Clear your credentials and start over\n/stop - Stop the agent\n/refresh - Restart the agent")

@bot.message_handler(commands=['run'])
def run_agent(message):
    chat_id = message.chat.id
    if chat_id not in user_data or 'api_key' not in user_data[chat_id]:
        bot.reply_to(message, "Please use /start to provide your credentials first.")
        return
        
    if chat_id in active_processes and active_processes[chat_id].poll() is None:
        bot.reply_to(message, "⚠️ The agent is already running! Use /status to check progress or /stop to stop it.")
        return

    bot.reply_to(message, "🚀 Starting the autonomous agent in the background...")
    
    # Inject credentials into environment variables for the subprocess
    env = os.environ.copy()
    env["BC_EMAIL"] = user_data[chat_id]['email']
    env["BC_PASSWORD"] = user_data[chat_id]['password']
    env["GEMINI_API_KEY"] = user_data[chat_id]['api_key']
    env["HEADLESS"] = "true"  # Force headless mode on the server
    env["TELEGRAM_BOT_TOKEN"] = BOT_TOKEN
    env["TELEGRAM_CHAT_ID"] = str(chat_id)
    
    # Run super_runner.py autonomously
    log_file = open("runner.log", "w")
    process = subprocess.Popen(
        ["python", "super_runner.py"],
        env=env,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    active_processes[chat_id] = process
    
    bot.send_message(chat_id, "✅ Agent is now running! Type /status to see live progress or /logs to see recent logs.")

@bot.message_handler(commands=['logs'])
def send_logs(message):
    chat_id = message.chat.id
    try:
        with open("runner.log", "r") as f:
            lines = f.readlines()
            logs = "".join(lines[-30:]) # Last 30 lines
            if not logs:
                logs = "Logs are empty."
    except Exception as e:
        logs = f"Error reading logs: {e}"
        
    bot.reply_to(message, f"**Recent Logs:**\n```text\n{logs}\n```", parse_mode="Markdown")

@bot.message_handler(commands=['reset'])
def reset_agent(message):
    chat_id = message.chat.id
    if chat_id in active_processes and active_processes[chat_id].poll() is None:
        active_processes[chat_id].terminate()
        
    # Clear user data
    if chat_id in user_data:
        del user_data[chat_id]
        
    # Delete session.json so it performs a fresh login
    try:
        os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)), "session.json"))
    except:
        pass
        
    bot.reply_to(message, "🔄 Agent stopped, session cleared, and credentials reset!\nUse /start to enter new credentials.")

@bot.message_handler(commands=['status'])
def check_status(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        bot.reply_to(message, "Please use /start first.")
        return
        
    bot.reply_to(message, "🔍 Fetching your milestone status... please wait.")
    
    env = os.environ.copy()
    env["BC_EMAIL"] = user_data[chat_id]['email']
    env["BC_PASSWORD"] = user_data[chat_id]['password']
    
    # Run agent.py --status
    try:
        result = subprocess.run(
            ["python", "agent.py", "--status"],
            env=env,
            capture_output=True,
            text=True,
            timeout=20,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        output = result.stdout.strip()
        if len(output) > 3900: # Telegram message limit is 4096
            output = output[-3900:]
            
        bot.send_message(chat_id, f"**Current Status:**\n```text\n{output}\n```", parse_mode="Markdown")
    except subprocess.TimeoutExpired:
        bot.send_message(chat_id, "⚠️ Status check timed out. The portal might be slow.")

@bot.message_handler(commands=['stop'])
def stop_agent(message):
    chat_id = message.chat.id
    if chat_id in active_processes:
        proc = active_processes[chat_id]
        if proc.poll() is None:
            proc.terminate()
            bot.reply_to(message, "🛑 Agent has been stopped.")
        else:
            bot.reply_to(message, "Agent is not currently running.")
    else:
        bot.reply_to(message, "No active agent found.")

@bot.message_handler(commands=['refresh'])
def refresh_agent(message):
    chat_id = message.chat.id
    bot.reply_to(message, "🔄 Refreshing... Stopping current agent.")
    stop_agent(message)
    run_agent(message)

# --- DUMMY WEB SERVER TO KEEP CLOUD HOSTS HAPPY (Render, Koyeb, etc.) ---
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    print(f"Starting dummy web server on port {port}...")
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()
# ------------------------------------------------------------------------

print("Starting Telegram Bot...")
bot.polling(none_stop=True)
