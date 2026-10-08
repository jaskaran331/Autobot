FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run the agent in an infinite loop
CMD while true; do python super_runner.py; echo "[*] Sleeping for 60 seconds..."; sleep 60; done
