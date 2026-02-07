# GEMINI.md

## Project Overview

**Name:** Logistics Hourly Manager

**Role:** A "Manager" Cloud Run Function (2nd Gen) that acts as a custom task scheduler.

**Stack:** Python 3.11, MongoDB (PyMongo), GCP Pub/Sub, GCP Cloud Scheduler.

## System Architecture

1. **Trigger:** `Cloud Scheduler` fires a heartbeat every hour (`0 * * * *`).
2. **Transport:** Scheduler pushes a message to the Pub/Sub topic `gcp-hourly`.
3. **Execution:** The Cloud Run Function `logistics-manager-sync` is triggered by the topic.
4. **Logic:** - Connects to MongoDB using a secret-managed URI.
* Normalizes current time to `HH:00:00`.
* Scans the `logistics.20260207-hourly-execution` collection.
* Matches `cronline` patterns against the normalized time using `croniter`.
* Dispatches a `POST` request to any matching `url`.



## Data Schema (MongoDB)

**Database:** `logistics`

**Collection:** `20260207-hourly-execution`

| Field | Type | Description |
| --- | --- | --- |
| `url` | String | The full HTTPS endpoint of the target Cloud Run service. |
| `cronline` | String | Standard crontab string (e.g., `0 * * * *` or `0 9-17 * * 1-5`). |

## Key Technical Specs

* **Timezone:** All scheduling is calculated in **UTC** to avoid Daylight Savings issues.
* **Dependencies:** `pymongo`, `croniter`, `requests`, `functions-framework`.
* **Secret Management:** The MongoDB connection string is stored in GCP Secret Manager as `mongo-url-gaq`.
* **Execution Mode:** Synchronous (Blocking) `requests.post` calls.

## Deployment Context

* **Region:** `us-east1` (Primary).
* **Runtime:** `python311`.
* **Memory:** `256Mi` (Default).
* **Entry Point:** `entrypoint` in `main.py`.

## Constraints & Assumptions

* The function assumes it is triggered exactly at the top of the hour.
* It truncates `now` to minutes/seconds = 0 to ensure high-precision matching with `croniter`.
* Target URLs must be reachable from the function (check VPC settings or Service Account permissions).

---

Would you like me to add a **"Known Issues/Future Work"** section to this file so Gemini knows what you're planning to optimize next (like adding OIDC auth or async support)?
