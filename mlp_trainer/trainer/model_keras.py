import math
import datetime
from typing import Tuple

import tensorflow as tf

import trainer.data.bigquery as data
import trainer.data.bigquery_generator as generator
import trainer.base_model as base_model


def make_job_output(job_dir):
    return "{}/{}".format(
        job_dir,
        datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    )


def train_and_evaluate( 
    table_id: str,
    job_dir: str,
    params: dict,
    job_name=None,
    task_index=-1,
    num_workers=1,
):

    strategy = tf.distribute.MirroredStrategy()

    with strategy.scope():
        model = base_model.get(params)
        model.compile(
            loss=tf.keras.losses.binary_crossentropy,
            optimizer=tf.keras.optimizers.Adam(
                learning_rate=params['learning_rate']
            ),
            metrics=[
                tf.keras.metrics.BinaryAccuracy()
            ],
        )

        tensorboard_callback = tf.keras.callbacks.TensorBoard(
            log_dir=make_job_output(job_dir), 
            histogram_freq=1
        )

        model.fit(
            x=generator.get_data(
                table_id,
                'train',
                params['batch_size'],
                params['epochs'],
                params['chunk_size'],
                params['cycle_length'],
                num_workers,
                task_index,
            ),
            validation_data=generator.get_data(
                table_id,
                'test',
                params['batch_size'],
                params['epochs'],
                params['chunk_size'],
                params['cycle_length'],
                num_workers,
                task_index,
            ),
            verbose=2,
            shuffle=False,
            callbacks=[
                tensorboard_callback
            ],
            epochs=params['epochs'],
            steps_per_epoch=math.ceil(
                data.get_sample_count(
                    table_id,
                    partition='train'
                ) / params['batch_size']
            ),
            validation_steps=round(
                data.get_sample_count(
                    table_id,
                    partition='test'
                ) / params['batch_size'],
                0
            ),
            # validation_freq=params['validation_freq'],
        )