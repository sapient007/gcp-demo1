import os
import math
import logging
import pickle
import codecs
import datetime
import pandas as pd
import numpy as np
from typing import Tuple, Iterator

import tensorflow as tf
import tensorflow.keras.backend as K
from tensorflow.python.client import device_lib

from talos.model.normalizers import lr_normalizer

from google.cloud import bigquery
from google.cloud import bigquery_storage_v1beta1

import trainer.data as data


def recall_metric(y_true, y_pred):
    """
    TODO: description
    :param y_true:
    :param y_pred:
    :return:
    """

    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())

    return recall


def precision_metric(y_true, y_pred):
    """
    TODO: description
    :param y_true:
    :param y_pred:
    :return:
    """

    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())

    return precision


def f1_metric(y_true, y_pred):
    """
    TODO: description
    :param y_true:
    :param y_pred:
    :return:
    """

    precision = precision_metric(y_true, y_pred)
    recall = recall_metric(y_true, y_pred)

    return 2 * ((precision * recall) / (precision + recall + K.epsilon()))


# TODO - move to data.py
def get_sample_count(table_id, partition):
    """

    :param table_id:
    :param partition:
    :return:
    """
    client = bigquery.Client()
    query_job = client.query('''
        SELECT COUNT(*) FROM `ml-sandbox-1-191918.chicagotaxi.{}` 
        WHERE ml_partition='{}';
        '''.format(table_id, partition))

    results = query_job.result()

    return list(results)[0][0]


def generator_input(table_id: bytes, chunk_size, batch_size: int, partition: bytes):
# -> Iterator[Tuple[np.array, np.array]]:
    """
    Produce features and labels needed by keras fit_generator
    :param table_id:
    :param chunk_size:
    :param batch_size:
    :param partition:
    :return:
    """
    # while True:
    session, readers = data.get_data_partition_sharded(table_id.decode("utf-8"), partition.decode("utf-8"))
    rows = readers[0].rows(session)
    for row in rows:
        # df = pd.DataFrame([row])
        yield (
            # df.drop(['cash', ], axis=1).values,
            # df['cash'].values 
            [
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
            ],
            row.get("cash")
        )

        #     if(i % batch_size == 0) and (i != 0):
        #         df = pd.DataFrame(df_rows)
        #         df_rows = [row]
        #         yield (
        #             df.drop(['cash', ], axis=1).values,
        #             df['cash'].values   
        #         )
        #     else:
        #         df_rows.append(row)
        # # Output remaining rows
        # if (len(df_rows) > 0):
        #     df = pd.DataFrame(df_rows)
        #     yield (
        #         df.drop(['cash', ], axis=1).values,
        #         df['cash'].values   
        #     )



def create_mlp(params):
    """
    :param params:
    :return:
    """

    # reset the tensorflow backend session.
    # K.clear_session()
    
    # define the model with variable hyperparameters.
    mlp_model = tf.keras.models.Sequential()
    mlp_model.add(tf.keras.layers.Dense(
        int(params['dense_neurons_1']),
        input_dim=26,
        kernel_initializer=params['kernel_initial_1']
    ))
    mlp_model.add(tf.keras.layers.BatchNormalization(axis=1))
    mlp_model.add(tf.keras.layers.Activation(activation=params['activation']))
    mlp_model.add(tf.keras.layers.Dropout(float(params['dropout_rate_1'])))
    mlp_model.add(tf.keras.layers.Dense(
        int(params['dense_neurons_2']),
        kernel_initializer=params['kernel_initial_2'],
        activation=params['activation']
    ))
    mlp_model.add(tf.keras.layers.Dropout(float(params['dropout_rate_2'])))
    mlp_model.add(tf.keras.layers.Dense(
        int(params['dense_neurons_3']),
        kernel_initializer=params['kernel_initial_3'],
        activation=params['activation']
    ))
    mlp_model.add(tf.keras.layers.Dense(
        1,
        activation='sigmoid'
    ))

    # num_gpus = len([x.name for x in device_lib.list_local_devices() if x.device_type == 'GPU'])
    # if num_gpus > 1:
    #     mlp_model = tf.keras.utils.multi_gpu_model(mlp_model, num_gpus)

    # compile with tensorflow optimizer.
    mlp_model.compile(
        optimizer=params['optimizer'](lr=lr_normalizer(params['learning_rate'], params['optimizer'])),
        loss='binary_crossentropy',
        metrics=['accuracy', f1_metric]
    )

    return mlp_model


client = bigquery_storage_v1beta1.BigQueryStorageClient()


def get_reader_for_stream(session_pickled: bytes, stream_name_bytes: bytes):
    session = pickle.loads(codecs.decode(session_pickled, "base64"))
    stream_name = stream_name_bytes.decode("utf-8")
    for stream in session.streams:
        if stream.name == stream_name:
            reader = data.get_reader(client, stream)
            rows = reader.rows(session)
            for row in rows:
                # df = pd.DataFrame([row])
                yield (
                    # df.drop(['cash', ], axis=1).values,
                    # df['cash'].values 
                    [
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
                    ],
                    row.get("cash")
                )
        client.finalize_stream(stream)
    


def bq_stream_generator(table_id: bytes, partition: bytes):
    session, _ = data.get_data_partition_sharded(table_id.decode("utf-8"), partition.decode("utf-8"), shards=100)
    encoded_session = codecs.encode(pickle.dumps(session), "base64")
    for stream in session.streams:
        tf.compat.v1.logging.info("Reading from BigQuery read session %s" % (stream.name))
        yield(encoded_session, stream.name)


def train_mlp_batches(table_id, params):
    """
    TODO: description
    :param table_id:
    :param params:
    :return:
    """

    # create model and define early stopping
    # https://www.tensorflow.org/guide/distributed_training#multiworkermirroredstrategy
    # strategy = tf.distribute.experimental.ParameterServerStrategy(
    #     tf.distribute.experimental.CollectiveCommunication.AUTO)
    strategy = tf.distribute.MirroredStrategy()
    # strategy = tf.distribute.experimental.MultiWorkerMirroredStrategy()
    with strategy.scope():
        mlp_model = create_mlp(params)

    # https://www.tensorflow.org/api_docs/python/tf/data/Dataset#from_generator
    # train_data = tf.data.Dataset.from_generator(
    #     generator_input,
    #     (tf.float64, tf.uint16),
    #     output_shapes=(tf.TensorShape([None]), tf.TensorShape([])),
    #     # output_shapes=(tf.TensorShape([None])),
    #     args=[
    #         table_id,
    #         params['chunk_size'],
    #         params['batch_size'],
    #         'train']
    # ).batch(params['batch_size']).repeat(params['epochs']).prefetch(buffer_size=tf.data.experimental.AUTOTUNE).cache(filename="/tmp/train")

    # validation_data = tf.data.Dataset.from_generator(
    #     generator_input,
    #     (tf.float64, tf.uint16),
    #     output_shapes=(tf.TensorShape([None]), tf.TensorShape([])),
    #     # output_shapes=(tf.TensorShape([None])),
    #     args=[
    #         table_id,
    #         params['chunk_size'],
    #         params['batch_size'],
    #         'validation']
    # ).batch(params['batch_size']).repeat(params['epochs']).prefetch(buffer_size=tf.data.experimental.AUTOTUNE)

    train_data = tf.data.Dataset.from_generator(
        bq_stream_generator,
        (tf.string, tf.string),
        # output_shapes=(tf.TensorShape([]), tf.TensorShape([])),
        args=(table_id, 'train')
    ).interleave(
        lambda session, stream:
        tf.data.Dataset.from_generator(
            get_reader_for_stream,
            (tf.float64, tf.uint16),
            output_shapes=(tf.TensorShape([None]), tf.TensorShape([])),
            args=(session, stream)
        ).prefetch(buffer_size=tf.data.experimental.AUTOTUNE),
        num_parallel_calls=8,
        cycle_length=10
    ).prefetch(buffer_size=tf.data.experimental.AUTOTUNE).batch(params['batch_size']).repeat(params['epochs'])

    validation_data = tf.data.Dataset.from_generator(
        bq_stream_generator,
        (tf.string, tf.string),
        # output_shapes=(tf.TensorShape([]), tf.TensorShape([])),
        args=(table_id, 'validation')
    ).interleave(
        lambda session, stream:
        tf.data.Dataset.from_generator(
            get_reader_for_stream,
            (tf.float64, tf.uint16),
            output_shapes=(tf.TensorShape([None]), tf.TensorShape([])),
            args=(session, stream)
        ).prefetch(buffer_size=tf.data.experimental.AUTOTUNE),
        # num_parallel_calls=tf.data.experimental.AUTOTUNE,
        num_parallel_calls=8,
        cycle_length=10
    ).prefetch(buffer_size=tf.data.experimental.AUTOTUNE).batch(params['batch_size']).repeat(params['epochs'])

    es = tf.keras.callbacks.EarlyStopping(
        monitor='val_loss',
        mode='min',
        verbose=0,
        patience=50
    )

    log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

    history = mlp_model.fit(train_data,
                            epochs=params['epochs'],
                            verbose=2,
                            callbacks=[es, tensorboard_callback],
                            steps_per_epoch=math.floor(get_sample_count(
                                table_id,
                                partition='train'
                            ) / params['batch_size']),
                            validation_data=validation_data,
                            validation_steps=math.ceil(
                                get_sample_count(
                                    table_id,
                                    partition='validation'
                                ) / params['batch_size']),
                            validation_freq=params['validation_freq'],
                            )

    # train the model on TPU with fixed batch size.
    # history = mlp_model.fit_generator(
    #     generator_input(
    #         table_id,
    #         chunk_size=params['chunk_size'],
    #         batch_size=params['batch_size'],
    #         partition='train'
    #     ),
    #     steps_per_epoch=math.ceil(get_sample_count(
    #         table_id,
    #         partition='train'
    #     ) / params['batch_size']),
    #     epochs=params['epochs'],
    #     verbose=2,
    #     callbacks=[es, tensorboard_callback],
    #     validation_data=generator_input(
    #         table_id,
    #         chunk_size=params['chunk_size'],
    #         batch_size=params['batch_size'],
    #         partition='validation'
    #     ),
        # validation_steps=math.ceil(get_sample_count(
        #     table_id,
        #     partition='validation'
        # ) / params['batch_size']),
    #     validation_freq=params['validation_freq']
    # )

    # Step 5: Return the history output and synced back cpu model.
    return history, mlp_model


def save_model(mlp_model, job_dir):
    """

    :param mlp_model:
    :param job_dir:
    :return:
    """

    tf.keras.experimental.export_saved_model(
        mlp_model,
        'model')
    os.system('gsutil -m cp -r model {}'.format(job_dir))
    os.system('gsutil -m cp -r logs {}'.format(job_dir))
