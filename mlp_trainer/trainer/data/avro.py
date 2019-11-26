import io
from typing import Iterator

from google.cloud import storage
from fastavro import reader

client = storage.Client()


def list_blobs(bucket_name: bytes, prefix: bytes) -> Iterator[storage.blob.Blob]: 
    for blob in client.list_blobs(bucket_name.decode('utf-8'), prefix=prefix.decode('utf-8')):
        yield (blob.name, blob.bucket.name)


def download_blob(client: storage.Client, obj_name: str, bucket_name: str) -> bytes:
    return storage.blob.Blob(obj_name, client.bucket(bucket_name)).download_as_string()


def fetch_gcs_avro(blob: bytes):
    avro_reader = reader(io.BytesIO(blob))
    for record in avro_reader:
        yield record


def generate_blob(bucket_name: bytes, prefix: bytes):
    blob_bytes = download_blob(client, bucket_name.decode('utf-8'), prefix.decode('utf-8'))
    for row in fetch_gcs_avro(blob_bytes):
        yield(
            features_from_row(row),
            row.get("cash")
        )


def features_from_row(row: dict):
    return [
        row.get("year"),
        row.get("start_time_norm_midnight"),
        row.get("start_time_norm_noon"),
        row.get("pickup_lat_std"),
        row.get("pickup_long_std"),
        row.get("pickup_lat_centered"),
        row.get("pickup_long_centered"),
        row.get("day_of_week_MONDAY"),
        row.get("day_of_week_TUESDAY"),
        row.get("day_of_week_WEDNESDAY"),
        row.get("day_of_week_THURSDAY"),
        row.get("day_of_week_FRIDAY"),
        row.get("day_of_week_SATURDAY"),
        row.get("day_of_week_SUNDAY"),
        row.get("month_JANUARY"),
        row.get("month_FEBRUARY"),
        row.get("month_MARCH"),
        row.get("month_APRIL"),
        row.get("month_MAY"),
        row.get("month_JUNE"),
        row.get("month_JULY"),
        row.get("month_AUGUST"),
        row.get("month_SEPTEMBER"),
        row.get("month_OCTOBER"),
        row.get("month_NOVEMBER"),
        row.get("month_DECEMBER"),
    ]

        # train_data = tf.data.Dataset.from_generator(
        #     avro_data.list_blobs,
        #     (tf.string, tf.string),
        #     # output_shapes=(tf.TensorShape([]), tf.TensorShape([])),
        #     args=(avro_bucket, "%strain/" % avro_path)
        # ).interleave(lambda obj_name, bucket_name: 
        #     tf.data.Dataset.from_generator(
        #         avro_data.generate_blob,
        #         (tf.float64, tf.uint16),
        #         output_shapes=(tf.TensorShape([None]), tf.TensorShape([])),
        #         args=(obj_name, bucket_name)
        #     ).prefetch(buffer_size=params['chunk_size']),
        #     num_parallel_calls=tf.data.experimental.AUTOTUNE,
        #     cycle_length=params['cycle_length']
        # ).batch(params['batch_size']).prefetch(20).repeat(params['epochs'])

        # validation_data = tf.data.Dataset.from_generator(
        #     avro_data.list_blobs,
        #     (tf.string, tf.string),
        #     # output_shapes=(tf.TensorShape([]), tf.TensorShape([])),
        #     args=(avro_bucket, "%svalidation/" % avro_path)
        # ).interleave(lambda obj_name, bucket_name: 
        #     tf.data.Dataset.from_generator(
        #         avro_data.generate_blob,
        #         (tf.float64, tf.uint16),
        #         output_shapes=(tf.TensorShape([None]), tf.TensorShape([])),
        #         args=(obj_name, bucket_name)
        #     ).prefetch(buffer_size=params['chunk_size']),
        #     num_parallel_calls=tf.data.experimental.AUTOTUNE,
        #     cycle_length=params['cycle_length']
        # ).batch(params['batch_size']).prefetch(20).repeat(params['epochs'])