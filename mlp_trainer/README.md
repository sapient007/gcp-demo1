# Demo 1 training package

This package creates a pipeline for training a multilayer perceptron model with this project's data in TensorFlow 2.0. This documentation will walk you through packaging this application into a container for training in a Kubeflow cluster.

## Setup

### Environment Variables

Following are a list of environment variables necessary to run this portion of the demo

```
PROJECT_ID: <GCP Project ID associated with service key>
```

### Linux/macOS

```bash
docker build --pull -f ./Dockerfile -t gcr.io/$PROJECT_ID/gcp-demo1:training ./ && docker push gcr.io/$PROJECT_ID/gcp-demo1:training
```

### Windows

```powershell
docker build --pull -f .\Dockerfile -t gcr.io/$env:PROJECT_ID/gcp-demo1:training .\; docker push gcr.io/$env:PROJECT_ID/gcp-demo1:training
```

## Application options

```
  -h, --help            show this help message and exit
  --hypertune HYPERTUNE
                        Whether training is running in a hypertuning session.
                        Default: False
  --log-step-count-steps LOG_STEP_COUNT_STEPS
                        Frequency in steps (batches) to log loss summary
                        during training. Default: 100
  --summary-write-steps SUMMARY_WRITE_STEPS
                        Steps (batches) to run before writing Tensorflow
                        scalar summaries. Default: 100
  --table-id TABLE_ID   BigQuery table optionally containing dataset. Default:
                        finaltaxi_encoded_sampled_small
  --task TASK           train or save. Default: train
  --job-dir JOB_DIR     Location to write history, logs, and export model. Can
                        be a GCS (gs://..) URI. Default: model
  --no-generated-job-path
                        Do not add a path suffix to --job-dir with the date
                        and time
  --cycle-length CYCLE_LENGTH
                        The number of input elements that will be processed
                        concurrently. Should be set to the number of available
                        CPUs. Default: 8
  --dense-neurons-1 DENSE_NEURONS_1
                        Number of neurons in first model layer. Default: 64
  --dense-neurons-2 DENSE_NEURONS_2
                        Number of neurons in second model layer. Default: 32
  --dense-neurons-3 DENSE_NEURONS_3
                        Number of neurons in third model layer. Default: 16
  --activation ACTIVATION
                        Activation function. Default: relu
  --dropout-rate DROPOUT_RATE
                        Dropout rate for all model layers. Default: 0.1
  --optimizer OPTIMIZER
                        Optimizer function. Default: adam
  --learning-rate LEARNING_RATE
                        Learning rate. Default: 0.01
  --batch-size BATCH_SIZE
                        Training batch size. Default: 102400
  --batch-size-float BATCH_SIZE_FLOAT
                        Batch size as float (for hypertuning only, do not use)
  --epochs EPOCHS       Number of epochs to train. Default: 3
  --validation-freq VALIDATION_FREQ
                        Validation frequency. Default: 1
  --kernel-initial-1 KERNEL_INITIAL_1
                        Kernel initializer for first model layer. Default:
                        normal
  --kernel-initial-2 KERNEL_INITIAL_2
                        Kernel initializer for second model layer. Default:
                        normal
  --kernel-initial-3 KERNEL_INITIAL_3
                        Kernel initializer for third model layer. Default:
                        normal
```

## Working with the code

## Setup

### Requirements
Python 3.7
Package Manager - Anaconda3
### Install Anaconda
[Anaconda Distribution](https://docs.anaconda.com/anaconda/install/)

### Setup Environment

```
conda create --name <env> python=3.7.0
```

Activate the virtual environment

```
source activate gcp-demo1
```

or in some shells

```
conda activate gcp-demo1
```

You can deactivate with

```
source deactivate
```

or in some shells

```
conda deactivate
```

