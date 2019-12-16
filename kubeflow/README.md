# Training and hypertuning in Kubeflow

Once data has been preprocessed and the training application container is created and pushed to Cloud Container Registry, training and hypertuning sessions can be run with Kubeflow. Kubeflow is a Kubernetes-based machine learning platform. Instructions on [deploying Kubeflow](https://www.kubeflow.org/docs/gke/) into a Google Cloud Kubernetes Engine cluster can be found on Kubeflow's website.

## Starting a training job

To start a training job on the full data, run:

```bash
kubectl apply -f job.yaml
```

The training job options can be customized by editing `job.yaml`. By default, it will train for 12 epochs and requires a 14 CPU and 100 Gb of memory (a single n1-highmem-16 worker node will work). Reducing the `--batch-size` will allow the job to run in a container with less computing resources at the sacrifice of accuracy.

Once the job is completed, pods will be delete. To delete pods from failed jobs run:

```bash
kubectl delete tfjob {JOB_NAME}
```

## Starting a hypertuning experiment

Hypertuning can be run in Katib, which is part of Kubeflow. A pre-configured Experiment is in `hypertune.yaml`. It is suggested to run hypertuning with only a 1 percent sample of the data (it will still take a bit more than 2 days to complete). Sampled data sets can be generated using the `--sampleSize` option in the [Dataflow job](../dataflow-etl).

