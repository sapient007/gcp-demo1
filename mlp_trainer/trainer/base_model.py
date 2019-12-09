
import tensorflow as tf


def get(params: dict) -> tf.keras.Sequential:
    return tf.keras.Sequential([
        tf.keras.layers.Dense(
            params['dense_neurons_1'],
            input_shape=(26,),
            kernel_initializer=params['kernel_initial_1']
        ),
        tf.keras.layers.BatchNormalization(axis=1),
        tf.keras.layers.Activation(activation=params['activation']),
        tf.keras.layers.Dropout(params['dropout_rate']),
        tf.keras.layers.Dense(
            params['dense_neurons_2'],
            kernel_initializer=params['kernel_initial_2'],
            activation=params['activation']
        ),
        tf.keras.layers.Dropout(params['dropout_rate']),
        tf.keras.layers.Dense(
            params['dense_neurons_3'],
            kernel_initializer=params['kernel_initial_3'],
            activation=params['activation']
        ),
        tf.keras.layers.Dropout(params['dropout_rate']),
        tf.keras.layers.Dense(
            1,
            activation='sigmoid'
        )
    ])