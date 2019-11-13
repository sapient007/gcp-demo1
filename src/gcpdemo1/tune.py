import json
import time
import logging
from pprint import pprint
from google.oauth2 import service_account
from googleapiclient import discovery


# Todo - instantiate object like train

class MLPTuner:
    def __init__(self, project_name, credentials, job_id_prefix, master_type, job_dir_prefix, table_id, package_uri):
        """
        TODO: class description
        :param project_name:
        :param job_id_prefix:
        :param master_type:
        :param job_dir_prefix:
        :param training_data_path:
        """

        if isinstance(credentials, str):
            credentials = service_account.Credentials.from_service_account_file(
                credentials,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )

        # object attributes
        self.project_name = project_name
        self.credentials = credentials
        self.job_id_prefix = job_id_prefix
        self.job_dir_prefix = job_dir_prefix
        self.job_id = None
        self.job_dir = None
        self.master_type = master_type
        self.table_id = table_id
        self.package_uri = package_uri

    def tune(self, params):
        """

        :param params:
        :return:
        """

        suffix = time.strftime("%Y%m%d_%H%M%S")

        self.job_id = f'{self.job_id_prefix}_{suffix}'
        self.job_dir = f'{self.job_dir_prefix}_{suffix}'

        # Create job via python client library
        project_id = 'projects/{}'.format(self.project_name)
        cloudml = discovery.build('ml', 'v1', credentials=self.credentials)

        hyperparams = {
            'goal': 'MINIMIZE',
            'hyperparameterMetricTag': 'val_loss',
            'maxTrials': 2,
            'maxParallelTrials': 1,
            'enableTrialEarlyStopping': True,
            'params': []}

        for x in range(1, 4):
            hyperparams['params'].append({
                'parameterName': f'dense-neurons-{x}',
                'type': 'DISCRETE',
                'discreteValues': params[f'dense_neurons_{x}']})

        hyperparams['params'].append({
            'parameterName': 'activation',
            'type': 'CATEGORICAL',
            'categoricalValues': params['activation']})

        for x in range(1, 4):
            hyperparams['params'].append({
                'parameterName': f'dropout-rate-{x}',
                'type': 'DISCRETE',
                'discreteValues': params[f'dropout_rate_{x}']})

        hyperparams['params'].append({
            'parameterName': 'optimizer',
            'type': 'CATEGORICAL',
            'categoricalValues': params['optimizer']})

        hyperparams['params'].append({
            'parameterName': 'learning-rate',
            'type': 'DISCRETE',
            'discreteValues': params['learning_rate']})

        for x in range(1, 4):
            hyperparams['params'].append({
                'parameterName': f'kernel-initial-{x}',
                'type': 'CATEGORICAL',
                'categoricalValues': params[f'kernel_initial_{x}']})

        training_inputs = {'scaleTier': 'CUSTOM',
                           'masterType': self.master_type,
                           'packageUris': [self.package_uri],
                           'pythonModule': 'trainer.task',
                           'region': 'us-central1',
                           'jobDir': f'{self.job_dir_prefix}_{time.strftime("%Y%m%d_%H%M%S")}',
                           'runtimeVersion': '1.14',
                           'pythonVersion': '3.5',
                           'args': ['--table_id', self.table_id,
                                    '--output_path', output_path,
                                    '--task', 'tune',
                                    '--epochs', str(params['epochs']),
                                    '--validation_freq', str(params['validation_freq'])],
                           'hyperparameters': hyperparams}

        job_spec = {'jobId': self.job_id,
                    'trainingInput': training_inputs}
        request = cloudml.projects().jobs().create(body=job_spec,
                                                   parent=project_id)
        response = request.execute()

        # Check response object is valid
        if response:
            if response['state']:
                if response['state'] in 'QUEUED':
                    return output_path

        logging.error(f'Could not execute a tuning job. Please see response object for specific error.\n{response}')

    def tuning_status(self):
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

        logging.error(f'Could not execute get job status. Please see response object for specific error.\n{response}')


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
    #     "optimizer": ["Adam", "Nadam", "RMSprop", "SGD"],
    #     "learning_rate": [.0001, .0005, .001, .005, .01, .05, .1, .5, 1],
    #     "kernel_initial_1": ["normal", "glorot_normal", "he_normal", "lecun_normal"],
    #     "kernel_initial_2": ["normal", "glorot_normal", "he_normal", "lecun_normal"],
    #     "kernel_initial_3": ["normal", "glorot_normal", "he_normal", "lecun_normal"],
    #
    #     # Static params
    #     "batch_size": [128],
    #     "chunk_size": [500000],
    #     "epochs": [40],
    #     "validation_freq": [1],
    #     "patience": [20]
    # }

    sa_path = '../../credentials/ml-sandbox-1-191918-384dcea092ff.json'
    project_name = 'ml-sandbox-1-191918'
    bucket_name = 'gcp-cert-demo-1'
    package_uri = "gs://gcp-cert-demo-1/taxi_mlp_trainer/trainer-0.1.tar.gz"
    output_path = 'gs://gcp-cert-demo-1/gcpdemo1_mle_tuning/hp_tuning_results.csv'
    job_id_prefix = 'gcpdemo1_mle_tuning'
    job_dir_prefix = 'gs://gcp-cert-demo-1/gcpdemo1_mle_tuning'
    machine_type = 'large_model_v100'  # https://cloud.google.com/ml-engine/docs/machine-types
    bq_table_id = 'finaltaxi_encoded_sampled_small'

    params = {
        "dense_neurons_1": [9, 64],
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
        "epochs": 3,
        "validation_freq": 1,
        "patience": [5]
    }

    hp_tuner = MLPTuner(project_name=project_name,
                        credentials=sa_path,
                        job_id_prefix=job_id_prefix,
                        master_type=machine_type,
                        job_dir_prefix=job_dir_prefix,
                        table_id=bq_table_id,
                        package_uri=package_uri)

    tuning_log_path = hp_tuner.tune(params)

    logging.info('Tuning output located at {}.'.format(tuning_log_path))

    print(hp_tuner.tuning_status())
