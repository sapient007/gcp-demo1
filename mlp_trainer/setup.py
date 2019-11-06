from setuptools import find_packages
from setuptools import setup


REQUIRED_PACKAGES = [
    'talos==0.6.3',
    'google-api-core==1.14.3',
    'google-api-python-client==1.7.11',
    'google-auth==1.6.3',
    'google-auth-httplib2==0.0.3',
    'google-auth-oauthlib==0.4.1',
    'google-cloud==0.34.0',
    'google-cloud-bigquery==1.21.0',
    'google-cloud-bigquery-storage==0.7.0',
    'google-cloud-core==1.0.3',
    'google-pasta==0.1.7',
    'google-resumable-media==0.4.1',
    'googleapis-common-protos==1.6.0',
    'urllib3',
    'google-cloud-bigquery-storage[pandas,fastavro]==0.7.0'
]


# 'tensorflow-gpu==2.0.0',
# 'numpy==1.17.2',
# 'pandas==0.19.2',

setup(
    name='trainer',
    version='0.1',
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    include_package_data=True,
    description='GCP Demo 1 Training Application'
)
