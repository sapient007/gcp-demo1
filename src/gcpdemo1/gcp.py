import os
import glob
import time
import logging

from google.cloud import storage
from googleapiclient import discovery
from google.oauth2 import service_account


def get_credentials(sa_path):
    """
    TODO
    :param sa_path:
    :return:
    """

    credentials = service_account.Credentials.from_service_account_file(
        sa_path,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    return credentials


def upload_blob(bucket_name, source_file_name, destination_blob_name, credentials):
    """
    TODO
    :param bucket_name:
    :param source_file_name:
    :param destination_blob_name:
    :param credentials:
    :return:
    """

    if isinstance(credentials, str):
        credentials = service_account.Credentials.from_service_account_file(
            credentials,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

    storage_client = storage.Client(credentials=credentials, project=credentials.project_id)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)


def build_and_upload_trainer_package(bucket_name, destination_blob_name, local_trainer_package_path, credentials):
    """
    TODO
    :param bucket_name:
    :param destination_blob_name:
    :param local_trainer_package_path:
    :param credentials:
    :return:
    """

    os.system(f'bash {local_trainer_package_path}/build.sh')  # --dist-dir {local_trainer_package_path}/dist

    src_code_filepath = list(glob.glob(os.path.join(local_trainer_package_path, 'dist/*.tar.gz')))[0]  # {local_trainer_package_path}/

    upload_blob(bucket_name, src_code_filepath, destination_blob_name, credentials)

    return f'gs://{bucket_name}/{destination_blob_name}'


def check_mle_job_status(mle_job):
    """
    TODO
    :return:
    """

    if mle_job.job_id is None:
        logging.error('Job object must have attribute \'job_id\'.')
        return 'Error'
    if mle_job.project_name is None:
        logging.error('Job object must have attribute \'project_name\'.')
        return 'Error'
    if mle_job.credentials is None:
        logging.error('Job object must have attribute \'credentials\'.')
        return 'Error'

    logging.info(f'Fetching status of training job "{mle_job.job_id}"')
    cloudml = discovery.build(
        'ml', 'v1',
        credentials=mle_job.credentials,
        cache_discovery=False)
    request = cloudml.projects().jobs().get(name=f'projects/{mle_job.project_name}/jobs/{mle_job.job_id}')

    response = request.execute()

    if response:
        if response['state']:
            return response['state']

    logging.error(f'Could not execute get job status. Please see response object for specific error.\n{response}')


def deploy_model_to_mle(trainer, model_name, version_name=f'v_{time.strftime("%Y%m%d_%H%M%S")}'):
    """
    TODO
    :param trainer:
    :param model_name:
    :param version_name:
    :return:
    """

    # model_name = f'{model_name}_{round(time.time())}'

    # check if model training job is complete
    client = storage.Client(
        project=trainer.project_name,
        credentials=trainer.credentials
    )
    complete = storage.Blob(
        bucket=client.bucket(f'{trainer.bucket}'),
        name=f'{trainer.job_id}/saved_model.pb'
    ).exists(client)

    # do not deploy, training incomplete
    if not complete:
        logging.error('Unable to deploy model due to incomplete training job, '
                      'for training status use MLPTrainer.training_status()')
        return

    # start job via python client
    gcs_model_path = f'gs://{trainer.bucket}/{trainer.job_id}'
    logging.info(f'Deploying model "{model_name}" version "{version_name}" from "{gcs_model_path}"')
    cloudml = discovery.build(
        'ml', 'v1',
        credentials=trainer.credentials,
        cache_discovery=False)
    request = cloudml.projects().models().create(
        parent=trainer.project_id,
        body={'name': model_name}
    )
    response = request.execute()
    if response:
        if response['etag'] and response['name']:
            logging.info('Model created successfully.')
            request = cloudml.projects().models().versions().create(
                parent=f'{trainer.project_id}/models/{model_name}',
                body={'name': version_name,
                      'deploymentUri': gcs_model_path,
                      'runtimeVersion': '1.14',
                      'framework': 'TENSORFLOW',
                      'pythonVersion': '3.5'}
            )
            response = request.execute()
            if response:
                if response['metadata'] and response['name']:
                    logging.info('Model version created successfully.')
                    return True

    logging.error(f'Could not deploy model. Please chck response object.\n{response}')
