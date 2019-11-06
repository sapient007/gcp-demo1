import os
import json
import time
import logging

import tensorflow as tf

from googleapiclient import discovery
from googleapiclient import errors

# TODO - CHANGE IMAGE TO USE


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
        self.unique_id = None
        self.job_id = None
        self.job_dir = None

    def tune(self, parameters, output_path):
        """

        :param parameters:
        :param output_path:
        :return:
        """

        param_string = json.dumps(parameters) # .replace('\"', '\\\"')

        # Run a local test

        # os.system(f'python ../../mlp_trainer/trainer/tune.py --table_id={self.table_id} \
        # --output_path={output_path} \
        # --parameters=\"{param_string}\"')


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
        # -- \pip list goog
        # --dataset_name={self.training_data_path} \
        # --output_path={output_path} \
        # --parameters={json.dumps(parameters)}')

        # start job via python client library
        project_id = 'projects/{}'.format(self.project_name)
        cloudml = discovery.build('ml', 'v1')
        training_inputs = {'scaleTier': 'CUSTOM',
                           'masterType': self.master_type,
                           'packageUris': ['gs://gcp-cert-demo-1/hp_tune_test/trainer-0.1.tar.gz'],
                           'pythonModule': 'trainer.tune',
                           'region': 'us-central1',
                           'jobDir': self.job_dir,
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
        print(response)

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

    output_path = 'gs://gcp-cert-demo-1/hp_tune_test/hp_tuning_1.csv'

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

    # Todo - change these paths, test
    hp_tuner = HPTuner(project_name='ml-sandbox-1-191918',
                       job_id_prefix='demo1_hp_tuning_test_1',
                       master_type='complex_model_m_gpu',
                       job_dir_prefix='gs://gcp-cert-demo-1/mle_hp_tuning',
                       table_id='finaltaxi_encoded_sampled_small')

    tuning_log_path = hp_tuner.tune(params, output_path)

    logging.info('Tuning output located at {}.'.format(tuning_log_path))
