import time
import logging

from googleapiclient import discovery
from google.oauth2 import service_account


# Todo - possibly eliminate bucket param and just use job_dir as output location
class MLPTrainer:
    def __init__(self, credentials, project_name, bucket, job_id_prefix, job_dir_prefix, table_id, trainer_package_uri):
        """
        TODO
        :param credentials:
        :param project_name:
        :param bucket:
        :param table_id:
        """

        if isinstance(credentials, str):
            credentials = service_account.Credentials.from_service_account_file(
                credentials,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )

        # object attributes
        self.credentials = credentials
        self.project_name = project_name
        self.bucket = bucket
        self.job_id_prefix = job_id_prefix
        self.job_dir_prefix = job_dir_prefix
        self.job_id = None
        self.job_dir = None
        self.table_id = table_id
        self.trainer_package_uri = trainer_package_uri

    def train(self, params):
        """

        :param params:
        :return:
        """
        suffix = time.strftime("%Y%m%d_%H%M%S")

        self.job_id = f'{self.job_id_prefix}_{suffix}'
        self.job_dir = f'{self.job_dir_prefix}_{suffix}'

        # Create job via python client library
        project_id = 'projects/{}'.format(self.project_name)

        logging.info(f'Starting training job "{self.job_id}"')
        cloudml = discovery.build(
            'ml', 'v1',
            credentials=self.credentials,
            cache_discovery=False)
        training_inputs = {
            'scaleTier': 'CUSTOM',
            'masterType': 'standard_v100',
            'packageUris': [f'gs://{self.bucket}/{self.trainer_package_uri}'],
            'pythonModule': 'trainer.train',
            'region': 'us-central1',
            'jobDir': f'gs://{self.bucket}/{self.job_id}',
            'runtimeVersion': '1.14',
            'pythonVersion': '3.5',
            'args': [
                '--table-id', f'{self.table_id}',
                '--dense-neurons-1', f"{params['dense_neurons_1']}",
                '--dense-neurons-2', f"{params['dense_neurons_2']}",
                '--dense-neurons-3', f"{params['dense_neurons_3']}",
                '--activation', f"{params['activation']}",
                '--dropout-rate-1', f"{params['dropout_rate_1']}",
                '--dropout-rate-2', f"{params['dropout_rate_2']}",
                '--dropout-rate-3', f"{params['dropout_rate_3']}",
                '--optimizer', f"{params['optimizer']}",
                '--learning-rate', f"{params['learning_rate']}",
                '--chunk-size', f"{params['chunk_size']}",
                '--batch-size', f"{params['batch_size']}",
                '--epochs', f"{params['epochs']}",
                '--validation-freq', f"{params['validation_freq']}",
                '--kernel-initial-1', f"{params['kernel_initial_1']}",
                '--kernel-initial-2', f"{params['kernel_initial_2']}",
                '--kernel-initial-3', f"{params['kernel_initial_3']}"
            ]
        }
        job_spec = {
            'jobId': f'{self.job_id}',
            'trainingInput': training_inputs
        }
        request = cloudml.projects().jobs().create(body=job_spec,
                                                   parent=project_id)
        response = request.execute()

        # Check response object is valid
        if response:
            if response['state']:
                if response['state'] in 'QUEUED':
                    return self.job_dir

        logging.error('Could not execute a tuning job. Please see response object for specific error.\n{}'.format(response))

    # def training_status(self):
    #     """
    #     TODO
    #     :return:
    #     """
    #     logging.info(f'Fetching status of training job "{self.job_id}"')
    #     cloudml = discovery.build(
    #         'ml', 'v1',
    #         credentials=self.credentials,
    #         cache_discovery=False)
    #     request = cloudml.projects().jobs().get(name=f'projects/{self.project_name}/jobs/{self.job_id}')
    #     response = request.execute()
    #
    #     if response:
    #         if response['state']:
    #             return response['state']
    #
    #     logging.error('Could not execute get job status. Please see response object for specific error.\n{}'.format(response))

