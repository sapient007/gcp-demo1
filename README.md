# Demo 1 - GCP ML Specialization Certification

This code package leverages GCP tools to create a model capable of
predicting whether a taxi trip in Chicago, USA will be a cash or
credit card payment. It is believed this would benefit drivers because
cash tips tend to be greater than ones left on credit cards.

## Setup

### Requirements
Python 3.7.4  
Package Manager - Anaconda3
### Install Anaconda
[Anaconda Distribution](https://docs.anaconda.com/anaconda/install/)

### Setup Environment
```
conda create -n gcp-demo1 -y python=3.7.4
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
### Python Package Installation
TODO - Package Installation
### Building Source Code
```
python setup.py bdist_wheel sdist
cd dist
pip install -U <filename.whl>
```
### Installing Google SDK
Please use this link to install the [GCloud SDK](https://cloud.google.com/sdk/docs/quickstarts).  
Authentication will be made with the provided service account. 
```
gcloud auth activate-service-account --key-file=/path/to/credentials.json
```

### Python Authentication to GCP
Set GOOGLE_APPLICATION_CREDENTIALS environment variable to the path to the SA credentials provided.  

Windows -
```
set GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```
Linux -
```
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

You may run the workflow from the provided Jupyter Notebook or feel free to use the source code
methods as you see fit.