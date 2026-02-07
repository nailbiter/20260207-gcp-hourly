import os
import datetime
import requests
import functions_framework
from pymongo import MongoClient
from croniter import croniter

from alex_leontiev_toolbox_python.utils.logging_helpers import get_configured_logger

from common.call_cloud_run import call_cloud_run

# Config pulled from Environment Variables (mapped to Secrets)
MONGO_URI = os.environ.get("MONGO_URI")
DB_NAME = "logistics"
COLLECTION_NAME = "20260207-hourly-execution"

logger = get_configured_logger(
    "main",
    log_format="%(asctime)s - %(name)s - %(levelname)s - Line:%(lineno)d - %(message)s",
)


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

        logger.info(f"Checking schedules for reference time: {now}")

        # 2. Iterate through your MongoDB documents
        cursor = collection.find({})
        triggered_count = 0

        for doc in cursor:
            url = doc.get("url")
            cron = doc.get("cronline")
            is_active = doc.get("is_active", True)
            text = doc.get("text")

            logger.debug(dict(url=url, cros=cron, is_active=is_active, text=text))

            if (not url) or (not cron) or (not is_active):
                continue

            # 3. Match cronline against our truncated hour
            if croniter.match(cron, now):
                logger.info(f"Match! Cron '{cron}' triggers URL: {url}")
                try:
                    # Sync POST request to the Cloud Run service
                    # response = requests.post(url, timeout=30)
                    # response.raise_for_status()
                    call_cloud_run(url, text=text)
                    triggered_count += 1
                except Exception as req_err:
                    logger.info(f"Failed to trigger {url}: {req_err}")

        logger.info(f"Execution finished. Total triggered: {triggered_count}")

    except Exception as e:
        logger.error(f"Critical error during execution: {e}")
    finally:
        client.close()
