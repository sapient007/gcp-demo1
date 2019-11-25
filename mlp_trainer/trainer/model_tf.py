import datetime
import math
from typing import Iterator, Tuple, List, Any

import tensorflow as tf

import trainer.data.bigquery as data
import trainer.data.bigquery_generator as generator
import trainer.data.features as features


global_table_id = ""
global_params = {}

def create_mlp(params: dict, config: tf.estimator.RunConfig) -> tf.estimator.DNNClassifier:
    estimator = tf.estimator.DNNClassifier(
        hidden_units=[
            params['dense_neurons_1'],
            params['dense_neurons_2'],
            params['dense_neurons_3']
        ],
        optimizer=params['optimizer'],
        activation_fn=tf.nn.relu,
        feature_columns=features.get_estimator_cols(),
        dropout=params['dropout_rate_1'],
        batch_norm=True,
        config=config
    )
    return estimator

@tf.function
def input_fn_train():
    # return tf.data.Dataset.from_tensors(({"year_norm":[1.]}, [1.]))
    dataset = generator.get_data(
        global_table_id, 
        'train', 
        global_params['batch_size'],
        global_params['epochs'], 
        global_params['chunk_size'], 
        global_params['cycle_length'],
        map_function='estimator'
    )
    return dataset


@tf.function
def input_fn_eval():
    # return tf.data.Dataset.from_tensors(({"year_norm":[1.]}, [1.]))
    dataset = generator.get_data(
        global_table_id, 
        'validation', 
        global_params['batch_size'],
        global_params['epochs'], 
        global_params['chunk_size'], 
        global_params['cycle_length'],
        map_function='estimator'
    )
    return dataset

    # dataset = tf.data.Dataset.from_generator(
    #         generator.bg_generator,
    #         (tf.float64, tf.uint16),
    #         output_shapes=(tf.TensorShape([None]), tf.TensorShape([])),
    #         args=(global_table_id, 'train')
    #     )
    # # dataset.prefetch(buffer_size=global_params['chunk_size'])
    # dataset.batch(global_params['batch_size'])
    # # dataset.prefetch(
    # #     math.floor(global_params['chunk_size'] / global_params['batch_size'])
    # # )
    # dataset.repeat(global_params['epochs'])
    # return dataset

    # for value in dataset.take(1):
    #     print(value)


def train_and_evaluate(table_id: str, params: dict):
    global global_table_id
    global global_params
    global_table_id = table_id
    global_params = params
    
    strategy = tf.distribute.experimental.MultiWorkerMirroredStrategy()
    # strategy = tf.distribute.MirroredStrategy()

    config = tf.estimator.RunConfig(
        # model_dir='model',
        # train_distribute=strategy,
        eval_distribute=strategy
    )

    estimator = create_mlp(params, config)


    tf.estimator.train_and_evaluate(
        estimator,
        train_spec=tf.estimator.TrainSpec(input_fn=input_fn_train),
        eval_spec=tf.estimator.EvalSpec(input_fn=input_fn_eval),
    )

    # estimator.train(input_fn=input_fn_train)