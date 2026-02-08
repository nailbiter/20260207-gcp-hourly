# 20260207-gcp-hourly
Hourly dispatcher for GCP function triggering

## deployment
```sh
gcloud functions deploy logistics-manager-sync \
  --gen2 \
  --runtime=python311 \
  --region=us-east1 \
  --source=. \
  --entry-point=entrypoint \
  --trigger-topic=gcp-hourly \
  --set-secrets="MONGO_URI=mongo-url-gaq:latest" \
  --set-env-vars=GCLOUD_PROJECT=$GCLOUD_PROJECT \
  --timeout=300 --memory=512Mi
```
