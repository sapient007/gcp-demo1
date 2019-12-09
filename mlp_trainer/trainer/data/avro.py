import io
import math
from typing import Iterator, List, Tuple

from google.cloud import storage
from fastavro import reader
import tensorflow as tf

from trainer.data import features as features

client = storage.Client()


@tf.function
def list_blobs(bucket_name: str, prefix: str, partition: str) -> List[str]:

    obj_names = []

    for blob in client.list_blobs(
        bucket_name, 
        prefix="{}/{}".format(prefix, partition)
    ):
        obj_names.append(tf.constant(blob.name))
    return obj_names


def download_blob(client: storage.Client, obj_name: str, bucket_name: str) -> bytes:
    return storage.blob.Blob(obj_name, client.bucket(bucket_name)).download_as_string()


def fetch_gcs_avro(blob: bytes):
    avro_reader = reader(io.BytesIO(blob))
    for record in avro_reader:
        yield record


def generate_blob(bucket_name_bytes: bytes, obj_name_bytes: bytes):
    bucket_name = bucket_name_bytes.decode('utf-8')
    obj_name = obj_name_bytes.decode('utf-8')
    tf.get_logger().debug("Generating rows from GCS object gs://{}/{}".format(bucket_name, obj_name))
    blob_bytes = download_blob(
        client,
        obj_name,
        bucket_name,
    )
    for row in fetch_gcs_avro(blob_bytes):
        yield(
            tuple(features_from_row(row))
        )


def features_from_row(row: dict):
    feat_values = []
    for feat in features.defs():
        feat_values.append(row.get(feat.get('name')))
    feat_values.append(row.get('cash'))
    return feat_values


@tf.function
def get_data(bucket_name: str, prefix: str, partition: str, batch_size: int,
             epochs: int, chunk_size: int, cycle_length: int, num_workers: int,
             task_index: int, map_function='keras') -> tf.data.Dataset:
    if map_function == 'keras':
        map_fn = keras_map_fn
    elif map_function == 'estimator':
        map_fn = estimator_map_fn
    
    # blobs = list_blobs(bucket_name, prefix, partition)

    # tf.get_logger().info("Starting to read from {} GCS objects".format(len(blobs)))

    # dataset = tf.data.Dataset.from_tensor_slices(
    #     blobs
    # )

    dataset = tf.data.Dataset.list_files(
        "gs://{}/{}/{}/*.avro".format(bucket_name, prefix, partition)
    ).map(
        lambda file_path:
        tf.io.read_file(file_path)
    )


    
    # .shard(
    #         num_workers,
    #         task_index
    # ).interleave(
    #     lambda obj_name:
    #     print(obj_name),
    #     # tf.data.Dataset.from_generator(
    #     #     generate_blob,
    #     #     tuple(features.get_generator_output()),
    #     #     output_shapes=tuple(features.get_generator_output_shape()),
    #     #     args=(bucket_name, obj_name)
    #     # ).shard(
    #     #     num_workers,
    #     #     task_index
    #     # ).prefetch(
    #     #     buffer_size=batch_size*5
    #     # ).shuffle(
    #     #     buffer_size=batch_size*5
    #     # ),
    #     num_parallel_calls=tf.data.experimental.AUTOTUNE,
    #     cycle_length=cycle_length,
    #     # block_length=batch_size,
    # ).interleave(
    #     map_fn,
    #     num_parallel_calls=tf.data.experimental.AUTOTUNE,
    #     cycle_length=cycle_length
    # ).batch(
    #     batch_size
    # ).prefetch(
    #     math.ceil((batch_size*5) / batch_size)
    # ).repeat(epochs)

    return dataset


@tf.function
def estimator_map_fn(*args):
    feats = features.defs()
    feat_cols = {}
    i = 0
    # Loop over feat cols. Label is last and we'll manually add
    # This is ugly bc it depends on everything staying in order
    while i < len(args) - 1:
        feat_cols[feats[i].get('name')] = args[1]
        i += 1
    
    return tf.data.Dataset.from_tensors(
        ((feat_cols), args[len(args)-1], (None, 1))
    )


@tf.function
def keras_map_fn(*args):
    feat_cols = []
    i = 0
    # Loop over feat cols. Label is last and we'll manually add
    while i < len(args) - 1:
        feat_cols.append(args[i])
        i += 1
    
    return tf.data.Dataset.from_tensors(
        (
            tf.convert_to_tensor(tuple(feat_cols), dtype=tf.dtypes.float32), 
            tf.convert_to_tensor([args[len(args)-1]])
        )
    )
