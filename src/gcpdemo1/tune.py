import json
import time
import logging

from google.oauth2 import service_account
from googleapiclient import discovery


class MLPTuner:
    def __init__(self, project_name, credentials, job_id_prefix, master_type, job_dir_prefix, table_id):
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
        self.master_type = master_type
        self.job_dir_prefix = job_dir_prefix
        self.job_id = None
        self.table_id = table_id

    def tune(self, package_uri, parameters, output_path):
        """

        :param parameters:
        :param output_path:
        :return:
        """

        param_string = json.dumps(parameters).replace('\'', '\"')  # .replace('\"', '\\\"')

        self.job_id = f'{self.job_id_prefix}_{time.strftime("%Y%m%d_%H%M%S")}'

        # Create job via python client library
        project_id = 'projects/{}'.format(self.project_name)
        cloudml = discovery.build('ml', 'v1', credentials=self.credentials)
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

        logging.error('Could not execute a tuning job. Please see response object for specific error.\n{}'.format(response))

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
                return response

        logging.error('Could not execute get job status. Please see response object for specific error.\n{}'.format(response))


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

    sa_path = '../../credentials/ml-sandbox-1-191918-384dcea092ff.json'
    project_name = 'ml-sandbox-1-191918'
    bucket_name = 'gcp-cert-demo-1'
    local_trainer_package_path = '../../mlp_trainer'
    gcs_trainer_package_path = 'hp_tune_test/trainer-0.1.tar.gz'  # do not include bucket name
    output_path = 'gs://gcp-cert-demo-1/hp_tune_test/hp_tuning_results.csv'
    job_id_prefix = 'gcpdemo1_mlp_tuning'
    job_dir_prefix = 'gs://gcp-cert-demo-1/hp_tune_test'
    machine_type = 'large_model_v100'  # https://cloud.google.com/ml-engine/docs/machine-types
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

    hp_tuner = MLPTuner(project_name=project_name,
                        credentials=sa_path,
                        job_id_prefix=job_id_prefix,
                        master_type=machine_type,
                        job_dir_prefix=job_dir_prefix,
                        table_id=bq_table_id)

    package_uri = "gs://gcp-cert-demo-1/taxi_mlp_trainer/trainer-0.1.tar.gz"

    tuning_log_path = hp_tuner.tune(package_uri, params,
                                    output_path)

    logging.info('Tuning output located at {}.'.format(tuning_log_path))

    print(hp_tuner.tuning_status())
