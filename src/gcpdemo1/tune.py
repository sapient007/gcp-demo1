import time
import logging

from googleapiclient import discovery
from google.oauth2 import service_account


# Custom code
from gcpdemo1 import gcp


class MLPTuner:
    def __init__(self, project_name, credentials, job_id_prefix, master_type, master_gpu_type: str, job_dir_prefix, table_id, trainer_package_uri):
        """
        TODO
        :param project_name:
        :param credentials:
        :param job_id_prefix:
        :param master_type:
        :param job_dir_prefix:
        :param table_id:
        :param trainer_package_uri:
        """

        if isinstance(credentials, str):
            credentials = service_account.Credentials.from_service_account_file(
                credentials,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )

        # object attributes
        self.credentials = credentials
        self.project_name = project_name
        self.job_id_prefix = job_id_prefix
        self.job_dir_prefix = job_dir_prefix
        self.job_id = None
        self.job_dir = None
        self.master_type = master_type
        self.master_gpu_type = master_gpu_type
        self.table_id = table_id
        self.trainer_package_uri = trainer_package_uri

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
            'hyperparameterMetricTag': 'loss',
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

        # Todo - pass rest of params - pateince, batch_size, chunk_size
        training_inputs = {'scaleTier': 'CUSTOM',
                           'masterType': self.master_type,
                           'masterConfig': {
                               "acceleratorConfig": {
                                    "count": 2,
                                    "type": self.master_gpu_type
                               }
                           },
                           'packageUris': [self.trainer_package_uri],
                           'pythonModule': 'trainer.task',
                           'region': 'us-east1',
                           'jobDir': f'{self.job_dir_prefix}_{time.strftime("%Y%m%d_%H%M%S")}',
                           'runtimeVersion': '1.14',
                           'pythonVersion': '3.5',
                           'args': ['--table_id', self.table_id,
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
                    return self.job_dir

        logging.error(f'Could not execute a tuning job. Please see response object for specific error.\n{response}')


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

    sa_path = '/mnt/c/Users/erik.lincoln/Downloads/ml-sandbox-1-191918-4361247d7c4d.json'
    project_name = 'ml-sandbox-1-191918'
    trainer_package_uri = "gs://gcp-cert-demo-1/taxi_mlp_trainer/trainer-0.1.tar.gz"
    job_id_prefix = 'gcpdemo1_mle_tuning'
    job_dir_prefix = 'gs://gcp-cert-demo-1/gcpdemo1_mle_tuning'
    machine_type = 'n1-highmem-16'  # https://cloud.google.com/ml-engine/docs/machine-types
    gpu_type = 'NVIDIA_TESLA_K80'
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

    mlp_tuner = MLPTuner(project_name=project_name,
                        credentials=sa_path,
                        job_id_prefix=job_id_prefix,
                        master_type=machine_type,
                        master_gpu_type=gpu_type,
                        job_dir_prefix=job_dir_prefix,
                        table_id=bq_table_id,
                        trainer_package_uri=trainer_package_uri)

    tuning_log_path = mlp_tuner.tune(params)

    logging.info('Tuning output located at {}.'.format(tuning_log_path))

    print(gcp.check_mle_job_status(mlp_tuner))
