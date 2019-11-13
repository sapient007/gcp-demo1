import logging
import time
import json
from pprint import pprint

from google.cloud import storage
from googleapiclient import discovery


class MLPTrainer:
    def __init__(self, credentials, project_name, bucket, job_id, table_id, trainer_package_uri):
        """
        TODO
        :param credentials:
        :param project_name:
        :param bucket:
        :param table_id:
        """

        # object attributes
        self.credentials = credentials
        self.project_name = project_name
        self.project_id = f'projects/{self.project_name}'
        self.bucket = bucket
        self.job_id = f'{job_id}_{time.strftime("%Y%m%d_%H%M%S")}'
        self.table_id = table_id
        self.trainer_package_uri = trainer_package_uri

    def train(self, params):
        """

        :param params:
        :return:
        """

        # Todo - pass params all together.
        param_string = json.dumps(params).replace('\'', '\"')

        # Create job via python client library
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
                                                   parent=self.project_id)
        response = request.execute()

        # Check response object is valid
        if response:
            if response['state']:
                if response['state'] in 'QUEUED':
                    return self.job_id

        logging.error('Could not execute a tuning job. Please see response object for specific error.\n{}'.format(response))

    def training_status(self):
        """
        TODO
        :return:
        """
        logging.info(f'Fetching status of training job "{self.job_id}"')
        cloudml = discovery.build(
            'ml', 'v1',
            credentials=self.credentials,
            cache_discovery=False)
        request = cloudml.projects().jobs().get(name=f'projects/{self.project_name}/jobs/{self.job_id}')
        response = request.execute()

        if response:
            if response['state']:
                return response['state']

        logging.error('Could not execute get job status. Please see response object for specific error.\n{}'.format(response))

    def deploy(self, model_name, version_name=f'v_{time.strftime("%Y%m%d_%H%M%S")}'):
        """
        TODO
        :param model_name:
        :param version_name:
        :return:
        """

        # model_name = f'{model_name}_{round(time.time())}'

        # check if model training job is complete
        client = storage.Client(
            project=self.project_name,
            credentials=self.credentials
        )
        complete = storage.Blob(
            bucket=client.bucket(f'{self.bucket}'),
            name=f'{self.job_id}/saved_model.pb'
        ).exists(client)

        # do not deploy, training incomplete
        if not complete:
            logging.error('Unable to deploy model due to incomplete training job, '
                          'for training status use MLPTrainer.training_status()')
            return

        # start job via python client
        gcs_model_path = f'gs://{self.bucket}/{self.job_id}'
        logging.info(f'Deploying model "{model_name}" version "{version_name}" from "{gcs_model_path}"')
        cloudml = discovery.build(
            'ml', 'v1',
            credentials=self.credentials,
            cache_discovery=False)
        request = cloudml.projects().models().create(
            parent=self.project_id,
            body={'name': model_name}
        )
        response = request.execute()
        if response:
            if response['etag'] and response['name']:
                logging.info('Model created successfully.')
                request = cloudml.projects().models().versions().create(
                    parent=f'{self.project_id}/models/{model_name}',
                    body={'name': version_name,
                          'deploymentUri': gcs_model_path,
                          'runtimeVersion': '1.14',
                          'framework': 'TENSORFLOW',
                          'pythonVersion': '3.5'}
                )
                response = request.execute()
                if response:
                    if response['metadata'] and response['name']:
                        logging.info('Model version created successfully.')
                        return True

        logging.error(f'Could not deploy model. Please chck response object.\n{response}')
