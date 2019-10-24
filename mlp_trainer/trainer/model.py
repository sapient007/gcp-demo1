import os
import numpy as np
import pandas as pd

import tensorflow as tf
import tensorflow.keras.backend as K

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler

from talos.model.normalizers import lr_normalizer

from google.cloud import storage


CSV_COLUMNS = [
    'cash', 'year' , 'start_time', 'trip_miles', 'company', 'ml_partition', 'pickup_latitude',
    'pickup_longitude', 'pickup_lat_norm', 'pickup_long_norm', 'pickup_lat_std', 'pickup_long_std',
    'day_of_week_MONDAY', 'day_of_week_TUESDAY', 'day_of_week_THURSDAY', 'day_of_week_SUNDAY',
    'day_of_week_SATURDAY', 'day_of_week_FRIDAY', 'day_of_week_WEDNESDAY', 'month_JANUARY', 'month_SEPTEMBER',
    'month_JULY', 'month_JUNE', 'month_MAY', 'month_MARCH', 'month_OCTOBER', 'month_FEBRUARY', 'month_NOVEMBER',
    'month_AUGUST', 'month_DECEMBER', 'month_APRIL'
]

def scale_data(data, col_index, scaler):
    """
    TODO: description
    :param data:
    :param col_index:
    :param scaler:
    :return:
    """

    if scaler is not None:
        col = data[:, col_index].reshape(data.shape[0], 1)
        scaler.fit(col)
        scaled = scaler.transform(col)
        data[:, col_index] = scaled[:, 0]

    return data, scaler


def process_data(df, partition):
    """
    TODO: description
    :param df:
    :return:
    """

    # drop unusused columns
    df_ready = df.drop(
        ['start_time', 'trip_miles', 'company', 'pickup_lat_norm', 'pickup_long_norm',
         'pickup_lat_std', 'pickup_long_std', 'ml_partition'],
        axis=1
    )

    # convert to numpy
    df_array = df_ready.values

    # remove rows with NaN
    df_array = df_array[~np.isnan(df_array).any(axis=1)]

    # scale
    df_array, year_scaler = scale_data(df_array, 1, MinMaxScaler())
    df_array, lat_scaler = scale_data(df_array, 2, StandardScaler())
    df_array, long_scaler = scale_data(df_array, 3, StandardScaler())

    # partition
    df_array = df_array[df['ml_partition'] == partition]

    # shuffle
    np.random.shuffle(df_array)

    # separate predictors and targets
    x = df_array[:, 1:]
    y = df_array[:, 0]

    return x, y


def generator_input(filename, chunk_size, batch_size, partition):
    """
    Produce features and labels needed by keras fit_generator
    :param filename:
    :param chunk_size:
    :param batch_size:
    :param partition:
    :return:
    """

    feature_cols = None
    while True:
        input_reader = pd.read_csv(
            tf.io.gfile.GFile(filename),
            names=CSV_COLUMNS,
            chunksize=chunk_size,
        )

        for input_data in input_reader:

            # Retains schema for next chunk processing.
            if feature_cols is None:
                feature_cols = input_data.columns

            x, y = process_data(
                input_data,
                partition=partition
            )

            idx_len = input_data.shape[0]
            for index in range(0, idx_len, batch_size):
                print((x[index:min(idx_len, index + batch_size)].shape, y[index:min(idx_len, index + batch_size)].shape))
                # yield (x[index:min(idx_len, index + batch_size)],
                #    y[index:min(idx_len, index + batch_size)])


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


def train_mlp(x_train, y_train, x_val, y_val, params):
    """
    TODO: description
    :param x_train:
    :param y_train:
    :param x_val:
    :param y_val:
    :param params:
    :return:
    """

    # Step 1: reset the tensorflow backend session.
    K.clear_session()

    # Step 2: Define the model with variable hyperparameters.
    mlp_model = tf.keras.models.Sequential()
    mlp_model.add(tf.keras.layers.Dense(
        int(params['dense_neurons_1']),
        input_dim=x_train.shape[1],
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

    # Step 3: =compile with tensorflow optimizer.
    mlp_model.compile(
        optimizer=params['optimizer'](lr=lr_normalizer(params['learning_rate'], params['optimizer'])),
        loss='binary_crossentropy',
        metrics=['accuracy', f1_metric]
    )
    es = tf.keras.callbacks.EarlyStopping(
        monitor='val_loss',
        mode='min',
        verbose=0,
        patience=50
    )

    # Step 4: Train the model on TPU with fixed batch size.
    history = mlp_model.fit(
        x_train,
        y_train,
        epochs=1000,
        batch_size=16,
        verbose=0,
        validation_data=(x_val, y_val),
        callbacks=[es]
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


def save_model(mlp_model, history, bucket, job_dir):
    """
    TODO: description
    :param mlp_model:
    :param history:
    :param bucket:
    :param job_dir:
    :return:
    """

    # export the model to a SavedModel
    mlp_model.save('model.h5',
                   overwrite=True)
    upload_blob(
        bucket,
        source_file_name='model.h5',
        destination_blob_name=os.path.join(job_dir, 'model.h5')
    )
    os.remove('model.h5')

    # create history dataframe and write to csv
    pd.DataFrame(history.history).to_csv(
        'history.csv',
        index=False
    )
    upload_blob(
        bucket,
        source_file_name='history.csv',
        destination_blob_name=os.path.join(job_dir, 'history.csv')
    )
    os.remove('history.csv')
