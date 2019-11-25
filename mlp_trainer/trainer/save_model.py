from os import walk
from google.cloud import storage
from typing import List


def get_files(path: str) -> List[str]:
    files = []
    for (dirpath, dirnames, filenames) in walk(path):
        for file in filenames:
            files.append("%s/%s" % (dirpath, file))
    return files


def upload_blob(bucket_name: str, filename: str, path: str):
    """
    Uploads a file to the bucket
    :param bucket_name:
    :param filename:
    :param destination_blob_name:
    :return:
    """

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob("%s/%s" % (path, filename))
    blob.upload_from_filename(filename)


def save_keras_model(mlp_model, bucket_name, path):
    """

    :param mlp_model:
    :param job_dir:
    :return:
    """

    mlp_model.save('model', save_format='tf')
    # tf.keras.experimental.export_saved_model(
    #     mlp_model,
    #     'model')

    files = get_files('model')
    files.extend(get_files('logs'))
    for file in files:
        upload_blob(bucket_name, file, path)


def save_estimator_model(bucket_name, path):
    """

    :param job_dir:
    :return:
    """

    files = get_files('model')
    files.extend(get_files('logs'))
    for file in files:
        upload_blob(bucket_name, file, path)