# Demo 1 data pipeline

ETL is done by a Google Cloud Dataflow job in `./dataflow-etl`. The job will read data from the `bigquery-public-data:chicago_taxi_trips.taxi_trips` public dataset and prepare data for both training and predictions. The job will output data to Bigquery. 

## ETL prerequisites

You will need to create a Bigquery dataset in your project. If you use the default job options, create a datased named `chicagotaxi`. It can be named anything and customized in job options. If you do not specifiy a service account for the Dataflow job to use (`--serviceAccount`), it will use the project's default Compute Engine service account. Either the default GCE or the provided service account for the workers must be have read and write access to the dataset.

### Using the shuffle service

If you want to use the Dataflow shuffle service (`--experiments=shuffle_mode=service`), you will need to run your job in a GCP region that supports the service: https://cloud.google.com/dataflow/docs/guides/deploying-a-pipeline#cloud-dataflow-shuffle

### Instance types and worker counts

The job processes more than 250 GB of internal data. Using 6 n1-highmem-4 instances takes the job about an hour to finish.

## Dataflow options

In addition to the [Cloud Dataflow Runner options](https://beam.apache.org/documentation/runners/dataflow/#pipeline-options), these options can be customized:

- `--outputDataset`: Bigquery output dataset. Default: chicagotaxi
- `--outputTable`: Bigquery output table. Default: finaltaxi_encoded
- `--outputTableSpec`: Bigquery output tablespec. Default: chicagotaxi.finaltaxi_encoded
- `--inputTableSpec`: Bigquery input tablespec. Default: bigquery-public-data:chicago_taxi_trips.taxi_trips
- `--mlPartitionTrainWeight`: Weight to apply to random partitioning of training data. Example: 70 for 70 percent. Default: 70.0
- `--mlPartitionTestWeight`: Weight to apply to random partitioning of testing data. Example: 15 for 15 percent. Default: 15.0
- `--mlPartitionValidationWeight`: Weight to apply to random partitioning of validation data. Example: 15 for 15 percent. Default: 15.0
- `--mapCenterLat` Latitude in radians to center row latitude values on. Example: 41.8839. Default: 41.8839 (Chicago City Hall)
- `--mapCenterLong`: Longitude in radians to center row latitude values on. Example: -87.6319. Default: -87.6319 (Chicago City Hall)
- `--sampleSize`: Percent of data to sample. Example: 0-100. Default: 100

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