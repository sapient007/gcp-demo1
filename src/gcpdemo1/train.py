import logging
import os
import time

from google.cloud import storage


# begin logging
logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)-4.5s]  %(message)s',
        handlers=[logging.StreamHandler()])


class MLPTrainer:
    def __init__(self, project_name, table_id):
        """

        :param project_name:
        :param table_id:
        """

        # object attributes
        self.project_name = project_name
        self.table_id = table_id
        self.job_id = None
        self.model_dir = None

    def train(self, dense_neurons_1, dense_neurons_2, dense_neurons_3, activation, dropout_rate_1, dropout_rate_2,
              dropout_rate_3, optimizer, learning_rate, chunk_size, batch_size, epochs, validation_freq,
              kernel_initial_1, kernel_initial_2, kernel_initial_3, job_id=f'mlp_trainer_{time.time()}',
              job_dir=f'mlp_model_{time.time()}'):
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
        self.job_id = job_id
        self.model_dir = job_dir

        # start training job via gcloud
        os.system(f'gcloud config set project {self.project_name}')
        os.system(f'gcloud ai-platform jobs submit training "{job_id}" \
        --scale-tier CUSTOM \
        --master-machine-type "standard_v100" \
        --staging-bucket "gs://gcp-cert-demo-1" \
        --package-path "../../mlp_trainer/trainer" \
        --module-name "trainer.task" \
        --job-dir "gs://gcp-cert-demo-1/{job_dir}" \
        --region "us-central1" \
        --runtime-version 1.5 \
        --python-version 3.5 \
        -- \
        --table-id="{self.table_id}" \
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
        --kernel-initial-1={kernel_initial_1} \
        --kernel-initial-2={kernel_initial_2} \
        --kernel-initial-3={kernel_initial_3}')

    def training_status(self):
        """

        :return:
        """
        os.system(f'gcloud ai-platform jobs describe {self.job_id}')

    def deploy(self, model_name):

        # check if model training job is complete
        os.system(f'gcloud config set project {self.project_name}')
        client = storage.Client()
        complete = storage.Blob(
            bucket=client.bucket('gcp-cert-demo-1'),
            name=f'{self.model_dir}/model.h5'
        ).exists(client)

        # do not deploy, training incomplete
        if not complete:
            logging.warning('Unable to deploy model due to incomplete training job, '
                            'for training status use MLPTrainer.training_status()')

        # start job via gcloud
        else:
            os.system(f'gcloud ai-platform models create {model_name}')
            # os.system(f'gcloud ai-platform versions create $VERSION_NAME \
            # --model={model_name} \
            # --staging-bucket="gcp=cert-demo-1--origin={self.model_dir} \
            # --runtime-version=1.5 \
            # --framework "TENSORFLOW" \
            # --python-version=3.5')


if __name__ == "__main__":
    """
    For local testing.
    """

    # # mlp train testing
    # mlp_trainer = MLPTrainer(
    #     project_name='ml-sandbox-1-191918',
    #     table_id='finaltaxi_encoded_sampled_small'
    # )
    # mlp_trainer.train(
    #     dense_neurons_1=64,
    #     dense_neurons_2=32,
    #     dense_neurons_3=8,
    #     activation='relu',
    #     dropout_rate_1=0.1,
    #     dropout_rate_2=0.1,
    #     dropout_rate_3=0.1,
    #     optimizer='adam',
    #     learning_rate=0.1,
    #     chunk_size=500000,
    #     batch_size=1024,
    #     epochs=3,
    #     validation_freq=5,
    #     kernel_initial_1='normal',
    #     kernel_initial_2='normal',
    #     kernel_initial_3='normal',
    #     job_id=f'mlp_trainer_src_test',
    #     job_dir=f'mlp_model_src_test'
    # )

    # # status testing
    # mlp_trainer = MLPTrainer(
    #     project_name='ml-sandbox-1-191918',
    #     table_id='finaltaxi_encoded_sampled_small'
    # )
    # mlp_trainer.job_id = 'mlp_trainer_src_test'
    # mlp_trainer.training_status()

    # describe and deploy testing
    mlp_trainer = MLPTrainer(
        project_name='ml-sandbox-1-191918',
        table_id='finaltaxi_encoded_sampled_small'
    )
    mlp_trainer.model_dir = 'mlp_model_src_test'
    mlp_trainer.deploy(model_name='mlp_deployed_src_test')
