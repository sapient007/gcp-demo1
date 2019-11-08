import os
import glob

from google.oauth2 import service_account

from google.cloud import storage


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

    src_code_filepath = list(glob.glob('dist/*.tar.gz'))[0]  # {local_trainer_package_path}/

    upload_blob(bucket_name, src_code_filepath, destination_blob_name, credentials)

    return f'gs://{bucket_name}/{destination_blob_name}'
