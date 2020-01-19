# Demo 1 - GCP ML Specialization Certification

This code package leverages Google Cloud Platform tools to create a model capable of predicting whether payment for a taxi trip in Chicago  will be made with cash. It is believed this would benefit drivers because cash tips tend to be greater than ones left on credit cards.

## Setup

### Authenticating your Google Cloud project
Google Cloud SDK needs to be enabled to control resources hosted on Google Cloud Platform (GCP). Please follow instructions on how to install [SDK client](https://cloud.google.com/sdk/docs/)

Container Registry is a private container image registry that runs on Google Cloud. This function is used in the ETL process of the demo and needs to be enabled. Please follow instuctions on how to use the [Container Registry](https://cloud.google.com/container-registry/docs/quickstart). 


## Project components

### Data preprocessing pipeline

All data preprocessing occurs in a [Google Cloud Dataflow](https://cloud.google.com/dataflow/docs/) job using an [Apache Beam](https://beam.apache.org/) pipeline in the [`dataflow-etl/`](dataflow-etl/) directory. Instructions for running preprocessing are in that [directory](dataflow-etl/README.md).

### Tensorflow training application

The project's model is trained in a Tensorflow 2.0 application in [`mlp_trainer/`](mlp_trainer/). The application is packaged into a container for execution in Kubeflow. Instructions for creating the container are in the [training package's directory](mlp_trainer/README.md).

### Kubeflow training and hypertuning

Training and hypertuning can be run in Kubeflow. A [Kubeflow TFJob](https://www.kubeflow.org/docs/components/training/tftraining/) configuration for training and an [Experiment](https://www.kubeflow.org/docs/components/hyperparameter-tuning/hyperparameter/) configuration for hypertuning are provided in [`kubeflow/`](kubeflow/).
Instructions for training and hybertuning are in the [Kubeflow's directory](kubeflow/README.md).