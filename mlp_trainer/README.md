## Use gcloud to package and upload application

```
gcloud ai-platform jobs submit training "mlp_trainer_(date +"%Y%m%d_%H%M%S")" \
    --staging-bucket "gs://gcp-cert-demo-1/mlp_trainer" \
    --package-path "./" \
    --module-name "trainer.task" \
    --region "us-east1"
```