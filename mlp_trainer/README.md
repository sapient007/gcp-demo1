```bash
gcloud ai-platform jobs submit training "chicagotaxi_train_dist_"$(date +"%Y%m%d_%H%M%S") \
    --job-dir gs://$BUCKET_NAME/model/output \
    --staging-bucket gs://$BUCKET_NAME \
    --package-path=mlp_trainer/trainer \
    --region=us-east1 \
    --config=./mlp_trainer/training_config.yaml
```