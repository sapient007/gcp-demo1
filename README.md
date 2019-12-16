# Demo 1 - GCP ML Specialization Certification

This code package leverages Google Cloud Platform tools to create a model capable of predicting whether payment for a taxi trip in Chicago  will be made with cash. It is believed this would benefit drivers because cash tips tend to be greater than ones left on credit cards.

## Project components

### Data preprocessing pipeline

All data preprocessing occurs in a [Google Cloud Dataflow](https://cloud.google.com/dataflow/docs/) job using an [Apache Beam](https://beam.apache.org/) pipeline in the [`dataflow-etl/`](dataflow-etl/) directory. Instructions for running preprocessing are in that [directory](dataflow-etl/README.md).

### Tensorflow training application

The project's model is trained in a Tensorflow 2.0 application in [`mlp_trainer/`](mlp_trainer/). The application is packaged into a container for execution in Kubeflow. Instructions for creating the container are in the [training package's directory](mlp_trainer/README.md).

### Kubeflow training and hypertuning

Training and hypertuning can be run in Kubeflow. A [Kubeflow TFJob](https://www.kubeflow.org/docs/components/training/tftraining/) configuration for training and an [Experiment](https://www.kubeflow.org/docs/components/hyperparameter-tuning/hyperparameter/) configuration for hypertuning are provided in [`kubeflow/`](kubeflow/).
