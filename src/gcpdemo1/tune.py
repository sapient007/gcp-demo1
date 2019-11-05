import os
import json
import time
import logging

import tensorflow as tf

from googleapiclient import discovery
from googleapiclient import errors

# TODO - CHANGE IMAGE TO USE


class HPTuner:
    def __init__(self, project_name, job_id_prefix, master_type, job_dir_prefix, training_data_path):
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
        self.training_data_path = training_data_path
        self.unique_id = None
        self.job_id = None
        self.job_dir = None

    def tune(self, parameters, output_path):
        """

        :param parameters:
        :param output_path:
        :return:
        """

        # Run a local test
        os.system(f'python tune.py --dataset_name={self.training_data_path} \
        --output_path={output_path} \
        --parameters={json.dumps(parameters)}')


        # create job and model id
        # self.unique_id = time.time()
        # self.job_id = "{}_{}".format(self.job_id_prefix, self.unique_id)
        # self.job_dir = "{}_{}".format(self.job_dir_prefix, self.unique_id)

        # start job via gcloud
        # os.system('gcloud config set project {}'.format(self.project_name))
        # os.system(f'gcloud ai-platform jobs submit training {self.job_id} \
        # --region us-central1 \
        # --master-image-uri=gcr.io/cloud-ml-algos/linear_learner_cpu:latest \
        # --scale-tier=CUSTOM \
        # --master-machine-type={self.master_type} \
        # --job-dir={self.job_dir} \
        # -- \
        # --dataset_name={self.training_data_path} \
        # --output_path={output_path} \
        # --parameters={json.dumps(parameters)}')

        # start job via python client library
        # project_id = 'projects/{}'.format(self.project_name)
        # cloudml = discovery.build('ml', 'v1')
        # training_inputs = {'region': 'us-central1',
        #                    'masterConfig': {'imageUri': 'gcr.io/cloud-ml-algos/linear_learner_cpu:latest'},
        #                    'scaleTier': 'CUSTOM',
        #                    'masterType': self.master_type,
        #                    'jobDir': self.job_dir,
        #                    'args': ['--dataset_name', self.training_data_path,
        #                             '--output_path', output_path,
        #                             '--parameters', json.dumps(parameters)]}
        # job_spec = {'jobId': self.job_id,
        #             'trainingInput': training_inputs}
        # request = cloudml.projects().jobs().create(body=job_spec,
        #                                            parent=project_id)
        # response = request.execute()
        # print(response)

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

    output_path = 'gs://gcp-cert-demo-1/hp_tune_test/hp_tuning.csv'

    parameters = {
        'dense_neurons_1': [64, 9],
        'dense_neurons_2': [32],
        'dense_neurons_3': [8],
        'activation': ['relu'],
        'dropout_rate_1': [0.5],
        'dropout_rate_2': [0.5],
        'dropout_rate_3': [0.5],
        'optimizer': [tf.keras.optimizers.Adam],
        'learning_rate': [.0001],
        'kernel_initial_1': ['normal'],
        'kernel_initial_2': ['normal'],
        'kernel_initial_3': ['normal']
    }

    # Todo - change these paths, test
    hp_tuner = HPTuner(project_name='ml-sandbox-1-191918',
                       job_id_prefix='demo1_linear_learner',
                       master_type='large_model_v100',
                       job_dir_prefix='gs://gcp-cert-demo-1/linear_learner_',
                       training_data_path='gs://gcp-cert-demo-1/data/csv/train-single.csv')

    tuning_log_path = hp_tuner.tune(parameters, output_path)

    logging.info('Tuning output located at {}.'.format(tuning_log_path))
