## Use gcloud to package and upload application

```
gcloud ai-platform jobs submit training "mlp_trainer" \
    --staging-bucket "gs://gcp-cert-demo-1" \
    --package-path "./" \
    --module-name "trainer.task" \
    --region "us-east1"
```