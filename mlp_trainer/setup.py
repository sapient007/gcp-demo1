from setuptools import find_packages
from setuptools import setup


REQUIRED_PACKAGES = [
    'talos==0.6.3',
    'tensorflow==2.0.0',
    'numpy==1.17.2',
    'pandas==0.19.2',
    'google-cloud-storage',
    'urllib3',
    'google-cloud-bigquery-storage[pandas,fastavro]==0.7.0'
]


setup(
    name='trainer',
    version='0.1',
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    include_package_data=True,
    description='GCP Demo 1 Training Application'
)
