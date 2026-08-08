# backend/keep_alive.py  — run this locally or as a cron
import httpx, time
while True:
    httpx.get("https://save-the-world-api.onrender.com/health")
    time.sleep(840)  # ping every 14 minutes