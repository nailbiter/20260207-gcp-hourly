import os
import datetime
import requests
import functions_framework
from pymongo import MongoClient
from croniter import croniter

# Config pulled from Environment Variables (mapped to Secrets)
MONGO_URI = os.environ.get("MONGO_URI")
DB_NAME = "logistics"
COLLECTION_NAME = "20260207-hourly-execution"

@functions_framework.cloud_event
def entrypoint(cloud_event):
    """
    Triggered by a Pub/Sub message via Cloud Scheduler.
    """
    client = MongoClient(MONGO_URI)
    try:
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # 1. Normalize "now" to the start of the hour (UTC)
        # e.g., 2026-02-07 13:48:00 -> 2026-02-07 13:00:00
        now = datetime.datetime.now(datetime.timezone.utc).replace(
            minute=0, second=0, microsecond=0
        )
        
        print(f"Checking schedules for reference time: {now}")

        # 2. Iterate through your MongoDB documents
        cursor = collection.find({})
        triggered_count = 0

        for doc in cursor:
            url = doc.get("url")
            cron = doc.get("cronline")

            if not url or not cron:
                continue

            # 3. Match cronline against our truncated hour
            if croniter.match(cron, now):
                print(f"Match! Cron '{cron}' triggers URL: {url}")
                try:
                    # Sync POST request to the Cloud Run service
                    response = requests.post(url, timeout=30)
                    response.raise_for_status()
                    triggered_count += 1
                except Exception as req_err:
                    print(f"Failed to trigger {url}: {req_err}")

        print(f"Execution finished. Total triggered: {triggered_count}")

    except Exception as e:
        print(f"Critical error during execution: {e}")
    finally:
        client.close()
