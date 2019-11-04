import logging
import os
import time


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
