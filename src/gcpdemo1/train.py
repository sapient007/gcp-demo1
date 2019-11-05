import logging
import os
import time


class MLPTrainer:
    def __init__(self, project_name, table_id):

        # object attributes
        self.project_name = project_name
        self.table_id = table_id

    def train(self, table_id, dense_neurons_1, dense_neurons_2, dense_neurons_3, activation, dropout_rate_1,
              dropout_rate_2, dropout_rate_3, optimizer, learning_rate, chunk_size, batch_size, epochs, validation_freq,
              kernel_initial_1, kernel_initial_2, kernel_initial_3, job_id=f'mlp_trainer_{time.time()}',
              job_dir=f'mlp_model_{time.time()}'):

        # start job via gcloud
        os.system('gcloud config set project {}'.format(self.project_name))
        os.system(f'gcloud ai-platform jobs submit training "{job_id}" \
        --scale-tier CUSTOM \
        --master-machine-type "standard_v100" \
        --staging-bucket "gs://gcp-cert-demo-1" \
        --package-path "trainer" \
        --module-name "trainer.task" \
        --job-dir "gs://gcp-cert-demo-1/{job_dir}" \
        --region "us-central1" \
        --runtime-version 1.5 \
        --python-version 3.5 \
        -- \
        --table-id="{table_id}" \
        --dense-neurons-1={dense_neurons_1} \
        --dense-neurons-2={dense_neurons_2} \
        --dense-neurons-3={dense_neurons_3} \
        --activation={activation} \
        --dropout-rate-1={dropout_rate_1} \
        --dropout-rate-2={dropout_rate_2} \
        --dropout-rate-3={dropout_rate_3} \
        --optimizer={optimizer} \
        --learning-rate={learning_rate} \
        --chunk-size={chunk_size} \
        --batch-size={batch_size} \
        --epochs={epochs} \
        --validation-freq={validation_freq} \
        --kernel-initial_1={kernel_initial_1} \
        --kernel-initial_2={kernel_initial_2} \
        --kernel-initial_3={kernel_initial_3}')


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

    mlp_trainer = MLPTrainer(
        project_name='ml-sandbox-1-191918',
        table_id='finaltaxi_encoded_sampled_small')

    mlp_trainer.train(
        table_id, dense_neurons_1, dense_neurons_2, dense_neurons_3, activation, dropout_rate_1,
              dropout_rate_2, dropout_rate_3, optimizer, learning_rate, chunk_size, batch_size, epochs, validation_freq,
              kernel_initial_1, kernel_initial_2, kernel_initial_3, job_id=f'mlp_trainer_{time.time()}',
              job_dir=f'mlp_model_{time.time()}')

    # linear_learner.deploy(model_prefix='demo1_linear_learner',
    #                       version_prefix='version')
