import os
import numpy as np
import pandas as pd

import tensorflow as tf

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler


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


def process_data(file_path):
    """
    TODO: description
    :param file_path:
    :return:
    """

    # read in the data
    df = pd.read_csv(file_path)

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
    test_array = df_array[df['ml_partition'] == 'test']
    train_array = df_array[df['ml_partition'] == 'train']
    val_array = df_array[df['ml_partition'] == 'validation']

    # shuffle
    np.random.shuffle(test_array)
    np.random.shuffle(train_array)
    np.random.shuffle(val_array)

    # seperate predictors and targets
    x_train = train_array[:, 1:22]
    y_train = train_array[:, 0]
    x_test = test_array[:, 1:22]
    y_test = test_array[:, 0]
    x_val = val_array[:, 1:22]
    y_val = val_array[:, 0]

    return x_train, y_train, x_test, y_test, x_val, y_val


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
    tf.keras.backend.clear_session()

    # Step 2: Define the model with variable hyperparameters.
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Dense(
        int(params['dense_neurons_1']),
        input_dim=x_train.shape[1:],
        kernel_initializer=params['kernel_initial_1']
    ))
    model.add(tf.keras.layers.BatchNormalization('dense_neurons_1'))
    model.add(tf.keras.layers.Activation(activation=params['activation_1']))
    model.add(tf.keras.layers.Dropout(float(params['dropout_rate_1'])))
    model.add(tf.keras.layers.Dense(int(
        params['dense_neurons_2']),
        kernel_initializer=params['kernel_initial_2'],
        activation=params['activation_2']
    ))
    model.add(tf.keras.layers.Dropout(float(params['dropout_rate_2'])))
    model.add(tf.keras.layers.Dense(
        int(params['dense_neurons_3']),
        kernel_initializer=params['kernel_initial_3'],
        activation='activation_3'
    ))
    model.add(tf.keras.layers.Dense(
        1,
        activation='sigmoid'
    ))

    # Step 3: conver the model to tpu model and compile with tensorflow optimizer.
    tpu_model = tf.contrib.tpu.keras_to_tpu_model(
        model,
        strategy=tf.contrib.tpu.TPUDistributionStrategy(
            tf.contrib.cluster_resolver.TPUClusterResolver(tpu='grpc://' + os.environ['COLAB_TPU_ADDR'])
        )
    )
    tpu_model.compile(
        optimizer=params['optimizer'](lr=lr_normalizer(params['lr'], params['optimizer'])),
        loss='binary_crossentropy',
        metrics=['accuracy', 'fmeasure']
    )
    es = tf.keras.callbacks.EarlyStopping(monitor='val_loss', mode='min', verbose=0, patience=50)

    # Step 4: Train the model on TPU with fixed batch size.
    out = tpu_model.fit(
        x_train,
        y_train,
        epochs=1000,
        batch_size=1024,
        verbose=0,
        validation_data=(x_val, y_val),
        callbacks=[es]
    )

    # Step 5: Return the history output and synced back cpu model.
    return out, tpu_model.sync_to_cpu()
