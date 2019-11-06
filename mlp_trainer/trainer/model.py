import os
import math
import logging
import pandas as pd

import tensorflow as tf
import tensorflow.keras.backend as K

from talos.model.normalizers import lr_normalizer

from google.cloud import bigquery
from google.cloud import storage

import trainer.data as data

# TODO: temp for testing GPU
from tensorflow.python.client import device_lib


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


def generator_input(table_id, chunk_size, batch_size, partition):
    """
    Produce features and labels needed by keras fit_generator
    :param table_id:
    :param chunk_size:
    :param batch_size:
    :param partition:
    :return:
    """

    while True:
        rows = data.get_reader_rows(table_id, partition)
        df_rows = []
        for idx, row in enumerate(rows):
            if (idx % chunk_size == 0) and (idx != 0):
                df = pd.DataFrame(df_rows)
                df_rows = [row]
                df_len = df.shape[0]
                for jdx in range(0, df_len, batch_size):
                    yield (
                        df.iloc[jdx:min(df_len, jdx + batch_size), 1:].values,
                        df.iloc[jdx:min(df_len, jdx + batch_size), 0].values
                    )
            else:
                df_rows.append(row)


def create_mlp(params):
    """

    :param params:
    :return:
    """

    # TODO: temp gpu testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)-4.5s]  %(message)s',
        handlers=[
            logging.FileHandler('gpu_testing.log'),
            logging.StreamHandler()
        ])

    # reset the tensorflow backend session.
    K.clear_session()

    # define the model with variable hyperparameters.
    mlp_model = tf.keras.models.Sequential()
    mlp_model.add(tf.keras.layers.Dense(
        int(params['dense_neurons_1']),
        input_dim=25,
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

    # compile with tensorflow optimizer.
    mlp_model.compile(
        optimizer=params['optimizer'](lr=lr_normalizer(params['learning_rate'], params['optimizer'])),
        loss='binary_crossentropy',
        metrics=['accuracy', f1_metric]
    )

    return mlp_model


def train_mlp(x_train, y_train, x_val, y_val, params):
    tf.keras.backend.clear_session()

    model = create_mlp(params)

    es = tf.keras.callbacks.EarlyStopping(monitor='val_loss', mode='min', verbose=0, patience=params['patience'])

    out = model.fit(
        x_train, y_train, epochs=params['epochs'], batch_size=params['batch_size'],
        verbose=0,
        validation_data=(x_val, y_val),
        callbacks=[es]
    )

    return out, model


def train_mlp_batches(table_id, params):
    """
    TODO: description
    :param table_id:
    :param params:
    :return:
    """

    # create model and define early stopping
    mlp_model = create_mlp(params)
    es = tf.keras.callbacks.EarlyStopping(
        monitor='val_loss',
        mode='min',
        verbose=0,
        patience=50
    )

    # train the model on TPU with fixed batch size.
    history = mlp_model.fit_generator(
        generator_input(
            table_id,
            chunk_size=params['chunk_size'],
            batch_size=params['batch_size'],
            partition='train'
        ),
        steps_per_epoch=math.ceil(get_sample_count(
            table_id,
            partition='train'
        ) / params['batch_size']),
        epochs=params['epochs'],
        verbose=2,
        callbacks=[es],
        validation_data=generator_input(
            table_id,
            chunk_size=params['chunk_size'],
            batch_size=params['batch_size'],
            partition='validation'
        ),
        validation_steps=math.ceil(get_sample_count(
            table_id,
            partition='validation'
        ) / params['batch_size']),
        validation_freq=params['validation_freq']
    )

    # Step 5: Return the history output and synced back cpu model.
    return history, mlp_model


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """
    Uploads a file to the bucket
    :param bucket_name:
    :param source_file_name:
    :param destination_blob_name:
    :return:
    """

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name.split(bucket_name + '/')[-1])
    blob.upload_from_filename(source_file_name)


def save_model(mlp_model, bucket, job_dir):
    """

    :param mlp_model:
    :param bucket:
    :param job_dir:
    :return:
    """

    tf.keras.experimental.export_saved_model(
        mlp_model,
        'model')
    os.system('gsutil -m cp -r model {}'.format(job_dir))

    # # export the model to a SavedModel
    # tf.keras.models.save_model(
    #     mlp_model,
    #     filepath=job_dir,
    #     overwrite=True,
    #     save_format='tf'
    # )
    # os.system('gsutil -m cp -r model {}'.format(job_dir))
    # shutil.rmtree('model')
