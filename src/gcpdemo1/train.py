import logging
import os
import time
from googleapiclient import discovery
from googleapiclient import errors


class LinearLearner:
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

    def train(self, batch_size, learning_rate, max_steps):
        """
        TODO: method description
        :param batch_size:
        :param learning_rate:
        :param max_steps:
        :return:
        """

        # create job and model id
        self.unique_id = time.time()
        self.job_id = "{}_{}".format(self.job_id_prefix, self.unique_id)
        self.job_dir = "{}_{}".format(self.job_dir_prefix, self.unique_id)

        # start job via gcloud
        os.system('gcloud config set project {}'.format(self.project_name))
        os.system('gcloud ai-platform jobs submit training {} \
        --region us-central1 \
        --master-image-uri=gcr.io/cloud-ml-algos/linear_learner_cpu:latest \
        --scale-tier=CUSTOM \
        --master-machine-type={} \
        --job-dir={} \
        -- \
        --preprocess \
        --model_type=classification \
        --batch_size={} \
        --learning_rate={} \
        --max_steps={} \
        --training_data_path={}'.format(self.job_id,
                                        self.master_type,
                                        self.job_dir,
                                        batch_size,
                                        learning_rate,
                                        max_steps,
                                        self.training_data_path))

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
