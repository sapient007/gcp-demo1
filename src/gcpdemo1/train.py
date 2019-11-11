import logging
import time
from pprint import pprint

from google.cloud import storage

from googleapiclient import discovery


# begin logging
logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)-4.5s]  %(message)s',
        handlers=[logging.StreamHandler()])


class MLPTrainer:
    def __init__(self, credentials, project_name, bucket, table_id):
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
        self.table_id = table_id
        self.job_id = None
        self.model_dir = None

    def train(self, package_uri, dense_neurons_1, dense_neurons_2, dense_neurons_3, activation, dropout_rate_1,
              dropout_rate_2, dropout_rate_3, optimizer, learning_rate, chunk_size, batch_size, epochs,
              validation_freq, kernel_initial_1, kernel_initial_2, kernel_initial_3,
              job_id=f'mlp_trainer_{time.strftime("%Y%m%d_%H%M%S")}',
              job_dir=f'mlp_model_{time.strftime("%Y%m%d_%H%M%S")}'):
        """
        TODO
        :param package_uri:
        :param dense_neurons_1:
        :param dense_neurons_2:
        :param dense_neurons_3:
        :param activation:
        :param dropout_rate_1:
        :param dropout_rate_2:
        :param dropout_rate_3:
        :param optimizer:
        :param learning_rate:
        :param chunk_size:
        :param batch_size:
        :param epochs:
        :param validation_freq:
        :param kernel_initial_1:
        :param kernel_initial_2:
        :param kernel_initial_3:
        :param job_id:
        :param job_dir:
        :return:
        """

        # store job id and model directory path
        self.job_id = f'{job_id}_{round(time.time())}'
        self.model_dir = f'{job_dir}_{round(time.time())}'

        # Create job via python client library
        logging.info(f'Starting training job "{self.job_id}"')
        cloudml = discovery.build(
            'ml', 'v1',
            credentials=self.credentials,
            cache_discovery=False)
        training_inputs = {
            'scaleTier': 'CUSTOM',
            'masterType': 'standard_v100',
            'packageUris': [package_uri],
            'pythonModule': 'trainer.train',
            'region': 'us-central1',
            'jobDir': f'gs://{self.bucket}/{job_dir}',
            'runtimeVersion': '1.14',
            'pythonVersion': '3.5',
            'args': [
                '--table-id', f'{self.table_id}',
                '--dense-neurons-1', f'{dense_neurons_1}',
                '--dense-neurons-2', f'{dense_neurons_2}',
                '--dense-neurons-3', f'{dense_neurons_3}',
                '--activation', f'{activation}',
                '--dropout-rate-1', f'{dropout_rate_1}',
                '--dropout-rate-2', f'{dropout_rate_2}',
                '--dropout-rate-3', f'{dropout_rate_3}',
                '--optimizer', f'{optimizer}',
                '--learning-rate', f'{learning_rate}',
                '--chunk-size', f'{chunk_size}',
                '--batch-size', f'{batch_size}',
                '--epochs', f'{epochs}',
                '--validation-freq', f'{validation_freq}',
                '--kernel-initial-1', f'{kernel_initial_1}',
                '--kernel-initial-2', f'{kernel_initial_2}',
                '--kernel-initial-3', f'{kernel_initial_3}'
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
                    return

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
                return response

        return response

    def deploy(self, model_name, version_name=f'v_{round(time.time())}'):
        """
        TODO
        :param model_name:
        :param version_name:
        :return:
        """

        model_name = f'{model_name}_{round(time.time())}'

        # check if model training job is complete
        client = storage.Client(
            project=self.project_name,
            credentials=self.credentials
        )
        complete = storage.Blob(
            bucket=client.bucket(f'{self.bucket}'),
            name=f'{self.model_dir}/saved_model.pb'
        ).exists(client)

        # do not deploy, training incomplete
        if not complete:
            logging.warning('Unable to deploy model due to incomplete training job, '
                            'for training status use MLPTrainer.training_status()')

        # start job via gcloud
        else:
            gcs_model_path = f'gs://{self.bucket}/{self.model_dir}'
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
            # logging.info('Model creation response:')
            pprint(response)
            request = cloudml.projects().models().versions().create(
                parent=f'{self.project_id}/models/{model_name}',
                body={'name': version_name,
                      'deploymentUri': gcs_model_path,
                      'runtimeVersion': '1.14',
                      'framework': 'TENSORFLOW',
                      'pythonVersion': '3.5'}
            )
            response = request.execute()
            # logging.info('Version creation response:')
            pprint(response)
