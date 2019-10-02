# gcp-demo1

### Install Anaconda

### Setup Environment

### Building Source Code
```
python setup.py bdist_wheel sdist
cd dist
pip install -U <filename.whl>
```

### Authenticating to GCP
Set GOOGLE_APPLICATION_CREDENTIALS environment variable to the path to the SA credentials provided.  

Windows -
```
set GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

Linux -
```
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```