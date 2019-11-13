from setuptools import find_packages
from setuptools import setup


REQUIRED_PACKAGES = [
    'urllib3',
    'google-cloud-bigquery-storage[pandas,fastavro]==0.7.0',
    'gcsfs==0.3.1',
    'cloudml-hypertune==0.1.0.dev5'
]

setup(
    name='trainer',
    version='0.1',
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    include_package_data=True,
    description='GCP Demo 1 Training Application'
)
