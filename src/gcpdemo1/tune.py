import os
import json
import time
import glob
import logging
import subprocess

from google.oauth2 import service_account
from googleapiclient import discovery
from googleapiclient import errors

from google.cloud import storage


def download_blob(bucket_name, source_blob_name, destination_file_name, credentials):
    storage_client = storage.Client(credentials=credentials, project=credentials.project_id)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)


def upload_blob(bucket_name, source_file_name, destination_blob_name, credentials):
    """
    Uploads a file to the bucket
    :param bucket_name:
    :param source_file_name:
    :param destination_blob_name:
    :return:
    """

    storage_client = storage.Client(credentials=credentials, project=credentials.project_id)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)


def build_and_upload_trainer_package(bucket_name, destination_blob_name, local_trainer_package_path, credentials):

    os.system(f'python {local_trainer_package_path}/setup.py sdist --dist-dir {local_trainer_package_path}/dist')

    src_code_filepath = list(glob.glob(f'{local_trainer_package_path}/dist/*.tar.gz'))[0]

    upload_blob(bucket_name, src_code_filepath, destination_blob_name, credentials)

    return f'gs://{bucket_name}/{destination_blob_name}'


class HPTuner:
    def __init__(self, project_name, job_id_prefix, master_type, job_dir_prefix, table_id):
        """
        TODO: class description
        :param project_name:
        :param job_id_prefix:
        :param master_type:
        :param job_dir_prefix:
        :param training_data_path:
        """

        # object attributes
        self.project_name = project_name
        self.job_id_prefix = job_id_prefix
        self.master_type = master_type
        self.job_dir_prefix = job_dir_prefix
        self.table_id = table_id

    def tune(self, bucket_name, destination_blob_name, local_trainer_package_path, parameters, output_path, sa_path):
        """

        :param parameters:
        :param output_path:
        :return:
        """

        credentials = service_account.Credentials.from_service_account_file(
            sa_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        package_uri = build_and_upload_trainer_package(bucket_name, destination_blob_name, local_trainer_package_path, credentials)

        param_string = json.dumps(parameters).replace('\'', '\"')  # .replace('\"', '\\\"')

        # Run a local test
        # os.system(f'python ../../mlp_trainer/trainer/tune.py --table_id={self.table_id} \
        # --output_path={output_path} \
        # --parameters=\"{param_string}\"')

        # Create job via python client library
        project_id = 'projects/{}'.format(self.project_name)
        cloudml = discovery.build('ml', 'v1', credentials=credentials)
        training_inputs = {'scaleTier': 'CUSTOM',
                           'masterType': self.master_type,
                           'packageUris': [package_uri],
                           'pythonModule': 'trainer.tune',
                           'region': 'us-central1',
                           'jobDir': f'{self.job_dir_prefix}_{time.strftime("%Y%m%d_%H%M%S")}',
                           'runtimeVersion': '1.14',
                           'pythonVersion': '3.5',
                           'args': ['--table_id', self.table_id,
                                    '--output_path', output_path,
                                    '--parameters', param_string]}
        job_spec = {'jobId': f'{self.job_id_prefix}_{time.strftime("%Y%m%d_%H%M%S")}',
                    'trainingInput': training_inputs}
        request = cloudml.projects().jobs().create(body=job_spec,
                                                   parent=project_id)
        response = request.execute()
        # Todo - check response

        return output_path


if __name__ == "__main__":
    """
    For local testing.
    """

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)-4.5s]  %(message)s',
        handlers=[
            logging.FileHandler('train_testing.log'),
            logging.StreamHandler()
        ])

    project_name = 'ml-sandbox-1-191918'
    bucket_name = 'gcp-cert-demo-1'
    local_trainer_package_path = '../mlp_trainer'
    gcs_trainer_package_path = 'hp_tune_test/trainer-0.1.tar.gz'  # do not include bucket name
    output_path = 'gs://gcp-cert-demo-1/hp_tune_test/hp_tuning_results.csv'
    job_id_prefix = 'gcpdemo1_mlp_tuning'
    job_dir_prefix = 'gs://gcp-cert-demo-1/hp_tune_test'
    machine_type = 'complex_model_m_gpu'  # https://cloud.google.com/ml-engine/docs/machine-types
    bq_table_id = 'finaltaxi_encoded_sampled_small'

    # Optimizer parameters:
    #      "Adam"    for tf.keras.optimizers.Adam
    #      "Nadam"   for tf.keras.optimizers.Nadam
    #      "RMSprop" for tf.keras.optimizers.RMSprop
    #      "SGD"     for tf.keras.optimizers.SGD

    # params = {
    #     # Tunable params
    #     "dense_neurons_1": [64, 128, 9],
    #     "dense_neurons_2": [32, 64, 5],
    #     "dense_neurons_3": [8, 32, 7],
    #     "activation": ["relu", "elu"],
    #     "dropout_rate_1": [0, 0.5, 5],
    #     "dropout_rate_2": [0, 0.5, 5],
    #     "dropout_rate_3": [0, 0.5, 5],
    #     "optimizer": ["Adam"],
    #     "learning_rate": [.0001, .0005, .001, .005, .01, .05, .1, .5, 1],
    #     "kernel_initial_1": ["normal", "glorot_normal", "he_normal", "lecun_normal"],
    #     "kernel_initial_2": ["normal", "glorot_normal", "he_normal", "lecun_normal"],
    #     "kernel_initial_3": ["normal", "glorot_normal", "he_normal", "lecun_normal"],

    #     # Static params
    #     "batch_size": [1024],
    #     "chunk_size": [500000],
    #     "epochs": [40],
    #     "validation_freq": [5],
    #     "patience": [5]
    # }

    params = {
        "dense_neurons_1": [64, 9],
        "dense_neurons_2": [32],
        "dense_neurons_3": [8],
        "activation": ["relu"],
        "dropout_rate_1": [0.5],
        "dropout_rate_2": [0.5],
        "dropout_rate_3": [0.5],
        "optimizer": ["Adam"],
        "learning_rate": [.0001],
        "kernel_initial_1": ["normal"],
        "kernel_initial_2": ["normal"],
        "kernel_initial_3": ["normal"],

        "batch_size": [1024],
        "chunk_size": [500000],
        "epochs": [40],
        "validation_freq": [5],
        "patience": [5]
    }

    hp_tuner = HPTuner(project_name=project_name,
                       job_id_prefix=job_id_prefix,
                       master_type=machine_type,
                       job_dir_prefix=job_dir_prefix,
                       table_id=bq_table_id)

    tuning_log_path = hp_tuner.tune(bucket_name, gcs_trainer_package_path, local_trainer_package_path, params,
                                    output_path)

    logging.info('Tuning output located at {}.'.format(tuning_log_path))
