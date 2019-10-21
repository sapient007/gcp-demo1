import numpy as np
import pandas as pd

import tensorflow as tf
import tensorflow.keras.backend as K

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler

from talos.model.normalizers import lr_normalizer


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


def process_data(filename):
    """
    TODO: description
    :param filename:
    :return:
    """

    # read in the data
    df = pd.read_csv(tf.gfile.Open(filename))

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

    # separate predictors and targets
    x_train = train_array[:, 1:]
    y_train = train_array[:, 0]
    x_test = test_array[:, 1:]
    y_test = test_array[:, 0]
    x_val = val_array[:, 1:]
    y_val = val_array[:, 0]

    return x_train, y_train, x_test, y_test, x_val, y_val


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
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Dense(
        int(params['dense_neurons_1']),
        input_dim=x_train.shape[1],
        kernel_initializer=params['kernel_initial_1']
    ))
    model.add(tf.keras.layers.BatchNormalization(axis=1))
    model.add(tf.keras.layers.Activation(activation=params['activation']))
    model.add(tf.keras.layers.Dropout(float(params['dropout_rate_1'])))
    model.add(tf.keras.layers.Dense(
        int(params['dense_neurons_2']),
        kernel_initializer=params['kernel_initial_2'],
        activation=params['activation']
    ))
    model.add(tf.keras.layers.Dropout(float(params['dropout_rate_2'])))
    model.add(tf.keras.layers.Dense(
        int(params['dense_neurons_3']),
        kernel_initializer=params['kernel_initial_3'],
        activation=params['activation']
    ))
    model.add(tf.keras.layers.Dense(
        1,
        activation='sigmoid'
    ))

    # Step 3: =compile with tensorflow optimizer.
    model.compile(
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
    history = model.fit(
        x_train,
        y_train,
        epochs=1000,
        batch_size=16,
        verbose=0,
        validation_data=(x_val, y_val),
        callbacks=[es]
    )

    # Step 5: Return the history output and synced back cpu model.
    return history, model


def save_model(model, history, job_dir):

    # export the model to a SavedModel
    model.save(
        'model.h5',
        save_format='tf'
    )

    # create history dataframe and write to csv
    pd.DataFrame(history.history).to_csv(
        'history.csv',
        index=False
    )
