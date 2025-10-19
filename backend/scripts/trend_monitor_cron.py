import asyncio
import schedule
import time
from agents.trend_monitor import trend_monitor
from datetime import datetime

async def run_monitoring():
    print(f"[{datetime.utcnow()}] Starting trend monitoring job...")
    try:
        await trend_monitor.run_daily_monitoring()
        print(f"[{datetime.utcnow()}] Trend monitoring completed successfully")
    except Exception as e:
        print(f"[{datetime.utcnow()}] Error in trend monitoring: {e}")

def job():
    asyncio.run(run_monitoring())

# Schedule daily at 9 AM IST (3:30 AM UTC)
schedule.every().day.at("03:30").do(job)

print("Trend monitoring cron started. Waiting for scheduled time...")

while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
Google Cloud Run Deployment
