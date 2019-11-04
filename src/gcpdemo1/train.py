import logging
import os
import time
from googleapiclient import discovery
from googleapiclient import errors


class MLPTrainer:
    def __init__(self, project_name, table_id):

        # object attributes
        self.project_name = project_name
        self.table_id = table_id
        self.timestamp = None
        self.job_id = None
        self.job_dir = None

    def train(self, dense_neurons_1, dense_neurons_2, dense_neurons_3, activation, dropout_rate_1, dropout_rate_2,
              dropout_rate_3, optimizer, learning_rate, batch_size, validation_freq, kernel_initial_1, kernel_initial_2,
              kernel_initial_3):
        """

        :param dense_neurons_1:
        :param dense_neurons_2:
        :param dense_neurons_3:
        :param activation:
        :param dropout_rate_1:
        :param dropout_rate_2:
        :param dropout_rate_3:
        :param optimizer:
        :param learning_rate:
        :param batch_size:
        :param validation_freq:
        :param kernel_initial_1:
        :param kernel_initial_2:
        :param kernel_initial_3:
        :return:
        """

        # create job and model id
        self.timestamp = time.time()
        self.job_id = f'mlp_trainer_{self.timestamp}'
        self.job_dir = f'mlp_model_{self.timestamp}'

        # start job via gcloud
        os.system('gcloud config set project {}'.format(self.project_name))
        os.system(f'gcloud ai-platform jobs submit training "{self.job_id}" \
        --scale-tier CUSTOM \
        --master-machine-type "standard_v100" \
        --staging-bucket "gs://gcp-cert-demo-1" \
        --package-path "trainer" \
        --module-name "trainer.task" \
        --job-dir "gs://gcp-cert-demo-1/{self.job_dir}" \
        --region "us-central1" \
        --runtime-version 1.5 \
        --python-version 3.5')

        # # start job via python client library
        # project_id = 'projects/{}'.format(self.project_name)
        # cloudml = discovery.build('ml', 'v1')
        # training_inputs = {'region': 'us-central1',
        #                    'masterConfig': {'imageUri': 'gcr.io/cloud-ml-algos/linear_learner_cpu:latest'},
        #                    'scaleTier': 'CUSTOM',
        #                    'masterType': self.master_type,
        #                    'jobDir': self.job_dir,
        #                    'args': ['--preprocess', 'True',
        #                             '--model_type', 'classification',
        #                             '--batch_size', str(batch_size),
        #                             '--learning_rate', str(learning_rate),
        #                             '--max_steps', str(max_steps),
        #                             '--training_data_path', self.training_data_path]}
        # job_spec = {'jobId': self.job_id,
        #             'trainingInput': training_inputs}
        # request = cloudml.projects().jobs().create(body=job_spec,
        #                                            parent=project_id)
        # response = request.execute()
        # print(response)

    def deploy(self, model_prefix, version_prefix):
        model_name = "{}_{}".format(model_prefix, self.unique_id)
        version_name = "{}_{}".format(version_prefix, self.unique_id)
        framework = "TENSORFLOW"

        # deploy via gcloud
        os.system('gcloud config set project {}'.format(self.project_name))
        os.system('gcloud ml-engine models create {} --regions us-east1'.format(model_name))
        os.system('gcloud ai-platform versions create {} \
        --model={} \
        --origin={} \
        --runtime-version=1.14 \
        --framework {} \
        --python-version=3.5'.format(version_name,
                                     model_name,
                                     self.job_dir,
                                     framework))


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

    linear_learner = LinearLearner(project_name='ml-sandbox-1-191918',
                                   job_id_prefix='demo1_linear_learner',
                                   master_type='large_model_v100',
                                   job_dir_prefix='gs://gcp-cert-demo-1/linear_learner_',
                                   training_data_path='gs://gcp-cert-demo-1/data/csv/train-single.csv')

    linear_learner.train(batch_size=4,
                         learning_rate=0.001,
                         max_steps=1000)

    # linear_learner.deploy(model_prefix='demo1_linear_learner',
    #                       version_prefix='version')
