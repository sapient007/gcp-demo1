import math
from typing import Tuple

import tensorflow as tf
# import tensorflow.keras.backend as K
# from tensorflow.python.client import device_lib

# from talos.model.normalizers import lr_normalizer

import trainer.data.bigquery as data
import trainer.data.bigquery_generator as generator


def base_model() -> tf.keras.Sequential:
    return tf.keras.Sequential([
        tf.keras.layers.Dense(
            global_params['dense_neurons_1'],
            input_shape=(26,),
            kernel_initializer=global_params['kernel_initial_1']
        ),
        tf.keras.layers.BatchNormalization(axis=1),
        tf.keras.layers.Activation(activation=global_params['activation']),
        tf.keras.layers.Dropout(float(global_params['dropout_rate_1'])),
        tf.keras.layers.Dense(
            global_params['dense_neurons_2'],
            kernel_initializer=global_params['kernel_initial_2'],
            activation=global_params['activation']
        ),
        tf.keras.layers.Dropout(float(global_params['dropout_rate_2'])),
        tf.keras.layers.Dense(
            global_params['dense_neurons_3'],
            kernel_initializer=global_params['kernel_initial_3'],
            activation=global_params['activation']
        ),
        tf.keras.layers.Dense(
            1,
            activation='sigmoid'
        )
    ])

# def create_mlp(params):
#     """
#     :param params:
#     :return:
#     """

#     # reset the tensorflow backend session.
#     # K.clear_session()

#     # define the model with variable hyperparameters.
#     mlp_model = base_model()

#     # num_gpus = len([x.name for x in device_lib.list_local_devices() if x.device_type == 'GPU'])
#     # if num_gpus > 1:
#     #     mlp_model = tf.keras.utils.multi_gpu_model(mlp_model, num_gpus)

#     # compile with tensorflow optimizer.
#     mlp_model.compile(
#         # optimizer=params['optimizer'](lr=lr_normalizer(params['learning_rate'], params['optimizer'])),
#         optimizer=tf.keras.optimizers.Adam(learning_rate=params['learning_rate']),
#         # loss='binary_crossentropy',
#         loss=tf.keras.losses.BinaryCrossentropy(),
#         metrics=['accuracy']
#     )

#     return mlp_model


def model_fn(features, labels, mode):
    model = base_model()
    # if mode == tf.estimator.ModeKeys.PREDICT:
    #     # predictions = {'logits': logits}
    #     return tf.estimator.EstimatorSpec(labels=labels, predictions=preds)

    training = (mode == tf.estimator.ModeKeys.TRAIN)
    preds = model(features, training=training)
    loss = tf.keras.losses.BinaryCrossentropy(
        reduction=tf.keras.losses.Reduction.NONE
    )(labels, preds)
    # print(loss)
    loss = tf.reduce_sum(loss) * (1. / global_params['batch_size'])

    # print(labels)
    # print(tf.reshape(labels, tf.TensorShape([None,1])))

    eval_ops = {}
    if mode == tf.estimator.ModeKeys.EVAL:
        acc = tf.keras.metrics.BinaryAccuracy()
        acc.update_state(labels, preds)
        eval_ops['accuracy'] = acc
        precision = tf.keras.metrics.Precision()
        precision.update_state(labels, preds)
        eval_ops['precision'] = precision
        recall = tf.keras.metrics.Recall()
        recall.update_state(labels, preds)
        eval_ops['recall'] = recall
        false_negs = tf.keras.metrics.FalseNegatives()
        false_negs.update_state(labels, preds)
        eval_ops['false_negatives'] = false_negs
        false_pos = tf.keras.metrics.FalsePositives()
        false_pos.update_state(labels, preds)
        eval_ops['false_positives'] = false_pos
        true_neg = tf.keras.metrics.TrueNegatives()
        true_neg.update_state(labels, preds)
        eval_ops['true_negatives'] = true_neg
        true_pos = tf.keras.metrics.TruePositives()
        true_pos.update_state(labels, preds)
        eval_ops['true_positives'] = true_pos

    train_op = None
    if training:
        optimizer = tf.optimizers.Adam(
            learning_rate=global_params['learning_rate']
        )
        optimizer = tf.train.experimental.enable_mixed_precision_graph_rewrite(
            optimizer
        )
        optimizer.iterations = tf.compat.v1.train.get_or_create_global_step()

        update_ops = model.get_updates_for(None) + model.get_updates_for(features)

        minimize_op = optimizer.get_updates(
            loss,
            model.trainable_variables)[0]
        train_op = tf.group(minimize_op, *update_ops)

    return tf.estimator.EstimatorSpec(
        mode=mode,
        predictions=preds,
        loss=loss,
        eval_metric_ops=eval_ops,
        export_outputs={
            "classifcation_output": tf.estimator.export.ClassificationOutput(scores=preds)
        },
        train_op=train_op
    )

global_table_id = ""
global_params = {}

@tf.function
def input_fn_train():
    # return tf.data.Dataset.from_tensors(({"year_norm":[1.]}, [1.]))
    dataset = generator.get_data(
        global_table_id,
        'train',
        global_params['batch_size'],
        global_params['epochs'],
        global_params['chunk_size'],
        global_params['cycle_length']
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
        global_params['cycle_length']
    )
    return dataset


def get_session_config(job_name: str, task_index: int):
    if job_name == 'chief':
        return tf.compat.v1.ConfigProto(device_filters=['/job:ps', '/job:chief'])
    elif job_name == 'worker':
        return tf.compat.v1.ConfigProto(device_filters=[
            '/job:ps',
            '/job:worker/task:%d' % task_index
        ])
    return None


def train_and_evaluate(table_id: str, job_dir: str, params: dict, job_name='', task_index=-1):
    """
    TODO: description
    :param table_id:
    :param params:
    :return:
    """

    global global_table_id
    global global_params
    global_table_id = table_id
    global_params = params

    # strategy = tf.distribute.MirroredStrategy()
    strategy = tf.distribute.experimental.MultiWorkerMirroredStrategy()
    tf.get_logger().info("NTC_DEBUG: Number of devices in strategy: {}".format(strategy.num_replicas_in_sync))

    # tf.summary.trace_on(
    #     graph=True,
    #     profiler=True
    # )
    
    config = tf.estimator.RunConfig(
        log_step_count_steps=5,
        # save_summary_steps=100,
        # save_checkpoints_steps=5,
        session_config=get_session_config(job_name, task_index),
        train_distribute=strategy,
        # eval_distribute=strategy
    )

    classifier = tf.estimator.Estimator(
        model_fn=model_fn, model_dir=job_dir, config=config)
    return tf.estimator.train_and_evaluate(
        classifier,
        train_spec=tf.estimator.TrainSpec(
            input_fn=input_fn_train, 
            max_steps=math.ceil(
                data.get_sample_count(
                    table_id,
                    partition='train'
                ) / params['batch_size']
            ) * params['epochs']
        ),
        eval_spec=tf.estimator.EvalSpec(
            input_fn=input_fn_eval, 
            steps=math.ceil(
                data.get_sample_count(
                    table_id,
                    partition='validation'
                ) / params['batch_size']
            )
        )
    )

    # estimator = tf.keras.estimator.model_to_estimator(
    #     keras_model=mlp_model,
    #     config=config
    # )

    # # best = tf.estimator.BestExporter()

    # results = tf.estimator.train_and_evaluate(
    #     estimator,
    #     train_spec=tf.estimator.TrainSpec(input_fn=input_fn_train),
    #     eval_spec=tf.estimator.EvalSpec(
    #         input_fn=input_fn_eval,
    #         # exporters=[best]
    #     )
    # )

    # print(results)


# global_epochs = 1
# global_batch_size = 1024
# global_chunk_size = 5000000
# global_cycle_length = 4
# global_table_id = ""

# This is for distributed datasets
# @tf.function
# def train_data]_fn(input_context):
#     batch_size = input_context.get_per_replica_batch_size(global_batch_size)
#     train_data = tf.data.Dataset.from_generator(
#         bq_stream_generator,
#         (tf.string, tf.string),
#         # output_shapes=(tf.TensorShape([]), tf.TensorShape([])),
#         args=(global_table_id, 'train')
#     ).interleave(
#         lambda session, stream:
#         tf.data.Dataset.from_generator(
#             get_reader_for_stream,
#             (tf.float64, tf.uint16),
#             output_shapes=(tf.TensorShape([None]), tf.TensorShape([])),
#             args=(session, stream)
#         ).prefetch(buffer_size=global_chunk_size),
#         num_parallel_calls=tf.data.experimental.AUTOTUNE,
#         cycle_length=global_cycle_length
#     ).batch(global_batch_size).prefetch(
#         math.floor(global_chunk_size / global_batch_size)
#     ).repeat(global_epochs)
#     return train_data.shard(input_context.num_input_pipelines, input_context.input_pipeline_id)
# @tf.function
# def train_step(batch):
#     return global_mlp_model.train_on_batch(batch)

# def train_mlp_batches(table_id: str, avro_bucket: str, avro_path: str, params: dict):
#     """
#     TODO: description
#     :param table_id:
#     :param params:
#     :return:
#     """

#     global global_table_id
#     global global_mlp_model
#     global_table_id = table_id

#     # create model and define early stopping
#     # https://www.tensorflow.org/guide/distributed_training#multiworkermirroredstrategy
#     # strategy = tf.distribute.experimental.ParameterServerStrategy(
#     #     tf.distribute.experimental.CollectiveCommunication.AUTO)
#     # strategy = tf.distribute.MirroredStrategy()
#     strategy = tf.distribute.experimental.MultiWorkerMirroredStrategy()
#     # inputs = strategy.experimental_distribute_datasets_from_function(train_data_fn)
#     #  for batch in inputs:
#     #     # print(batch)
#     #     # replica_results = strategy.experimental_run_v2(train_step, args=(batch))
#     #     replica_results = strategy.experimental_run_v2(global_mlp_model.train_on_batch, args=(batch))
#     #     # print(replica_results)
#         # replica_results = strategy.experimental_run_v2(mlp_model.fit,
#         #     args=(
#         #         batch,
#         #         epochs=params['epochs'],
#         #         verbose=2,
#         #         # callbacks=[es, tensorboard_callback],
#         #         steps_per_epoch=math.ceil(
#         #             get_sample_count(
#         #                 table_id,
#         #                 partition='train'
#         #             ) / params['batch_size']
#         #         )
#         #     )
#         # )

#     with strategy.scope():
#         global_mlp_model = create_mlp(params)

#     train_data = generator.get_data(table_id,
#                                     'train',
#                                     params['batch_size'],
#                                     params['epochs'],
#                                     params['chunk_size'],
#                                     params['cycle_length'])

#     validation_data = generator.get_data(table_id,
#                                          'validation',
#                                          params['batch_size'],
#                                          params['epochs'],
#                                          params['chunk_size'],
#                                          params['cycle_length'])


#     es = tf.keras.callbacks.EarlyStopping(
#         monitor='val_loss',
#         mode='min',
#         verbose=1,
#         patience=10,
#         restore_best_weights=True
#     )

#     log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
#     tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, profile_batch=100, write_images=True, write_graph=True, update_freq='epoch', histogram_freq=1)

#     # # Step 5: Return the history output and synced back cpu model.
#     history = global_mlp_model.fit(train_data,
#                             epochs=params['epochs'],
#                             verbose=1,
#                             # callbacks=[es, tensorboard_callback],
#                             # steps_per_epoch=1,
#                             steps_per_epoch=math.ceil(
#                                 data.get_sample_count(
#                                     table_id,
#                                     partition='train'
#                                 ) / params['batch_size']),
#                             validation_data=validation_data,
#                             validation_steps=math.ceil(
#                                 data.get_sample_count(
#                                     table_id,
#                                     partition='validation'
#                                 ) / params['batch_size']),
#                             validation_freq=params['validation_freq'],
#                             )
#     return history, global_mlp_model