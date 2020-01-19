# Demo 1 data pipeline

ETL is done by a Google Cloud Dataflow job in `./dataflow-etl`. The job will read data from the `bigquery-public-data:chicago_taxi_trips.taxi_trips` public dataset and prepare data for both training and predictions. The job will output data to Bigquery. 

## Setup

### Environment Variables

Following are a list of environment variables necessary to run this portion of the demo

```
PROJECT_ID: <GCP Project ID associated with service key>
GCP_REGION: <GCP Region which where processing is run>
INSTANCE_TYPE: <Machine instance types>
MAX_WORKERS: < # of works to do ETL job >
LOCATION_OF_SA_JSON: < location of service account json key >
JOB_NAME: < name of the ETL job >
```

## ETL prerequisites

You will need to create a Bigquery dataset in your project. If you use the default job options, create a datased named `chicagotaxi`. It can be named anything and customized in job options. If you do not specifiy a service account for the Dataflow job to use (`--serviceAccount`), it will use the project's default Compute Engine service account. Either the default GCE or the provided service account for the workers must be have read and write access to the dataset.

### Using the shuffle service

If you want to use the Dataflow shuffle service (`--experiments=shuffle_mode=service`), you will need to run your job in a GCP region that supports the service: https://cloud.google.com/dataflow/docs/guides/deploying-a-pipeline#cloud-dataflow-shuffle

### Instance types and worker counts

The job processes more than 250 GB of internal data. Using 6 n1-highmem-4 instances takes the job about an hour to finish.

## Dataflow options

In addition to the [Cloud Dataflow Runner options](https://beam.apache.org/documentation/runners/dataflow/#pipeline-options), these options can be customized:

```
  --avroOutputPath=<ValueProvider>
    Default: 
    GCS output path for Avro. Example: gs://bucket/path/to/avro/
  --csvHeaderOutputPath=<ValueProvider>
    GCS output path for CSV header. Example: gs://bucket/path/to/csv/header
  --csvOutputPath=<ValueProvider>
    GCS output path for CSV. Example: gs://bucket/path/to/csv/
  --csvShards=<ValueProvider>
    Default: 30
    Number of CSV shards to create. Example: 30 for 30 files. Default: 30
  --dropTable=<ValueProvider>
    Default: true
    Drop output table when job starts
  --hotEncodeCompany=<ValueProvider>
    Default: false
    One-hot-encode company field
  --inputTableSpec=<ValueProvider>
    Default: bigquery-public-data:chicago_taxi_trips.taxi_trips
    Bigquery input tablespec. Example:
    bigquery-public-data:chicago_taxi_trips.taxi_trips
  --mapCenterLat=<ValueProvider>
    Default: 41.8839
    Latitude in radians to center row latitude values on. Example: 41.8839.
    Default: 41.8839 (Chicago City Hall)
  --mapCenterLong=<ValueProvider>
    Default: -87.6319
    Longitude in radians to center row latitude values on. Example: -87.6319.
    Default: -87.6319 (Chicago City Hall)
  --mlPartitionTestWeight=<ValueProvider>
    Default: 15.0
    Weight to apply to random partitioning of testing data. Example: 15 for 15
    percent. Default: 15.0
  --mlPartitionTrainWeight=<ValueProvider>
    Default: 70.0
    Weight to apply to random partitioning of training data. Example: 70 for 70
    percent. Default: 70.0
  --mlPartitionValidationWeight=<ValueProvider>
    Default: 15.0
    Weight to apply to random partitioning of validation data. Example: 15 for
    15 percent. Default: 15.0
  --outputDataset=<ValueProvider>
    Default: chicagotaxi
    Bigquery output dataset
  --outputTable=<ValueProvider>
    Default: finaltaxi_encoded
    Bigquery output table
  --outputTableSpec=<ValueProvider>
    Default: chicagotaxi.finaltaxi_encoded
    Bigquery output tablespec. Example: project_id:dataset.table
  --sampleSize=<ValueProvider>
    Default: 100
    Percent of data to sample. Example: 0-100. Default: 100
```

## Start a job in an existing JDK 8 environment

If you already have a JDK 8 development environment setup, Dataflow jobs can be started by running (from inside `./dataflow-etl`):

```bash
./gradlew run -Pargs="--project=$PROJECT_ID --runner=DataflowRunner --region=$GCP_REGION --workerMachineType=$INSTANCE_TYPE --maxNumWorkers=$MAX_WORKERS --experiments=shuffle_mode=service"
```

## Creating a container via Docker and start job in container (recommended)

### Step 1: Create the container

Make sure the GCP Container Registry API is enabled first: https://cloud.google.com/container-registry/docs/quickstart

#### Using application default credentials

##### Windows

```powershell
docker run --rm -v "$env:UserProfile\AppData\Roaming\gcloud:/root/.config/gcloud"  -v './dataflow-etl:/opt/etl' -w /opt/etl openjdk:8 ./gradlew jib --image gcr.io/$env:PROJECT_ID/$env:REPO_NAME"
```

##### macOS and Linux

```bash
docker run --rm -v "~/.config/gcloud:/root/.config/gcloud"  -v './dataflow-etl:/opt/etl' -w /opt/etl openjdk:8 ./gradlew jib --image gcr.io/$PROJECT_ID/$REPO_NAME"
```

#### Using a service account

```bash
docker run --rm -v "$LOCATION_OF_SA_JSON:/opt/sa/key.json"  -v './dataflow-etl:/opt/etl' -e GOOGLE_APPLICATION_CREDENTIALS=/opt/sa/key.json -w /opt/etl openjdk:8 ./gradlew jib --image gcr.io/$PROJECT_ID/$REPO_NAME"
```

### Step 2: Start the job from the container

#### Using application default credentials

##### Windows

```powershell
docker run --rm -v "$Env:UserProfile\AppData\Roaming\gcloud:/root/.config/gcloud" gcr.io/$PROJECT_ID/$REPO_NAME --project=$PROJECT_ID --runner=DataflowRunner --region=$GCP_REGION --workerMachineType=$INSTANCE_TYPE --maxNumWorkers=$MAX_WORKERS --experiments=shuffle_mode=service --jobName=$JOB_NAME
```

##### macOS and Linux

```bash
docker run --rm -v "~/.config/gcloud:/root/.config/gcloud" gcr.io/$PROJECT_ID/$REPO_NAME --project=$PROJECT_ID --runner=DataflowRunner --region=$GCP_REGION --workerMachineType=$INSTANCE_TYPE --maxNumWorkers=$MAX_WORKERS --experiments=shuffle_mode=service --jobName=$JOB_NAME
```

#### Using a service account

```bash
docker run --rm -v "$LOCATION_OF_SA_JSON:/opt/sa/key.json" -e GOOGLE_APPLICATION_CREDENTIALS=/opt/sa/key.json gcr.io/$PROJECT_ID/$REPO_NAME --project=$PROJECT_ID --runner=DataflowRunner --region=$GCP_REGION --workerMachineType=$INSTANCE_TYPE --maxNumWorkers=$MAX_WORKERS --experiments=shuffle_mode=service --jobName=$JOB_NAME
```

## Start a job via Docker

### Using application default credentials

#### Windows

```powershell
docker run --rm -v "$Env:UserProfile\AppData\Roaming\gcloud:/root/.config/gcloud"  -v '.\dataflow-etl\:/opt/etl' -w /opt/etl openjdk:8 ./gradlew run -Pargs="--project=$PROJECT_ID --runner=DataflowRunner --region=$GCP_REGION --workerMachineType=$INSTANCE_TYPE --maxNumWorkers=$MAX_WORKERS --experiments=shuffle_mode=service  --jobName=$JOB_NAME"
```

#### macOS and Linux

```bash
docker run --rm -v "~/.config/gcloud:/root/.config/gcloud"  -v './dataflow-etl\:/opt/etl' -w /opt/etl openjdk:8 ./gradlew run -Pargs="--project=$PROJECT_ID --runner=DataflowRunner --region=$GCP_REGION --workerMachineType=$INSTANCE_TYPE --maxNumWorkers=$MAX_WORKERS --experiments=shuffle_mode=service  --jobName=$JOB_NAME"
```

### Using a service account

```bash
docker run --rm -v "$LOCATION_OF_SA_JSON:/opt/sa/key.json"  -v './dataflow-etl\:/opt/etl' -e GOOGLE_APPLICATION_CREDENTIALS=/opt/sa/key.json -w /opt/etl openjdk:8 ./gradlew run -Pargs="--project=$PROJECT_ID --runner=DataflowRunner --region=$GCP_REGION --workerMachineType=$INSTANCE_TYPE --maxNumWorkers=$MAX_WORKERS --experiments=shuffle_mode=service  --jobName=$JOB_NAME"
```