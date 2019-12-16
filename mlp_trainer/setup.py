from setuptools import find_packages
from setuptools import setup


REQUIRED_PACKAGES = [
    'google-cloud-bigquery-storage[pandas,fastavro]==0.7.0',
    'google-cloud-bigquery==1.22.0',
    'google-cloud-storage==1.23.0',
    'python-snappy==0.5.4',
    'kfp==0.1.35',
    'pytz>=2019.0,<2020'
    'tfa-nightly'
]

setup(
    name='mlp_trainer',
    version='0.1',
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    include_package_data=True,
    description='GCP Demo 1 Training Application'
)
