```bash
gcloud ai-platform jobs submit training "chicagotaxi_train_dist_"$(date +"%Y%m%d_%H%M%S") \
    --job-dir gs://$BUCKET_NAME/model/output \
    --staging-bucket gs://$BUCKET_NAME \
    --package-path=mlp_trainer/trainer \
    --runtime-version=1.14 \
    --python-version=3.5 \
    --region=us-east1 \
    --config=./mlp_trainer/training_config.yaml


NOW=$(date +"%Y%m%d_%H%M%S") && gcloud ai-platform jobs submit training "chicagotaxi_train_dist_"$NOW \
    --job-dir gs://$BUCKET_NAME/model/output/$NOW \
    --master-image-uri=gcr.io/ml-sandbox-1-191918/gcp-demo1:training \
    --region=us-east1 \
    --config=./mlp_trainer/training_config.yaml


rm -r mlp_trainer/model && gcloud ai-platform local train --module-name=trainer.task --job-dir=model --package-path=mlp_trainer/trainer -- --batch-size=1024 --epochs=1 --chunk-size=250000
```


```powershell
(docker build --pull -f .\Dockerfile -t gcr.io/$env:PROJECT_ID/gcp-demo1:training .\) -and (doc
ker push gcr.io/$env:PROJECT_ID/gcp-demo1:training)
```