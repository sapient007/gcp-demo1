import math
import datetime
from typing import Tuple

import tensorflow as tf
import tensorflow_addons as tfa

import trainer.base_model as base_model
import trainer.data.features as features
import trainer.data.bigquery as data
import trainer.data.bigquery_generator as bq_generator
import trainer.data.avro as avro_generator

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.DEBUG)


def model_fn(features, labels, mode, params={}):
    model = base_model.get(params)
    # if mode == tf.estimator.ModeKeys.PREDICT:
    #     # predictions = {'logits': logits}
    #     return tf.estimator.EstimatorSpec(labels=labels, predictions=preds)

    training = (mode == tf.estimator.ModeKeys.TRAIN)
    preds = model(features, training=training)

    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(
            mode=mode,
            predictions=preds,
        )

    loss = tf.keras.losses.BinaryCrossentropy(
        reduction=tf.keras.losses.Reduction.NONE
    )(labels, preds)
    # print(loss)
    loss = tf.reduce_sum(loss) * (1. / params['batch_size'])

    # print(labels)
    # print(tf.reshape(labels, tf.TensorShape([None,1])))

    eval_ops = {}
    if mode == tf.estimator.ModeKeys.EVAL:
        acc = tf.keras.metrics.BinaryAccuracy()
        acc.update_state(labels, preds)
        eval_ops['test_accuracy'] = acc
        f1 = tfa.metrics.FBetaScore(
            num_classes=1,
            average='micro',
            beta=1.0,
        )
        f1.update_state(labels, preds)
        eval_ops['test_f1'] = f1
        auc = tf.keras.metrics.AUC()
        auc.update_state(labels, preds)
        eval_ops['test_auc'] = auc
        precision = tf.keras.metrics.Precision()
        precision.update_state(labels, preds)
        eval_ops['test_precision'] = precision
        recall = tf.keras.metrics.Recall()
        recall.update_state(labels, preds)
        eval_ops['test_recall'] = recall
        false_negs = tf.keras.metrics.FalseNegatives()
        false_negs.update_state(labels, preds)
        eval_ops['test_false_negatives'] = false_negs
        false_pos = tf.keras.metrics.FalsePositives()
        false_pos.update_state(labels, preds)
        eval_ops['test_false_positives'] = false_pos
        true_neg = tf.keras.metrics.TrueNegatives()
        true_neg.update_state(labels, preds)
        eval_ops['test_true_negatives'] = true_neg
        true_pos = tf.keras.metrics.TruePositives()
        true_pos.update_state(labels, preds)
        eval_ops['test_true_positives'] = true_pos
        return tf.estimator.EstimatorSpec(
            mode=mode,
            loss=loss,
            eval_metric_ops=eval_ops,
        )

    train_op = None
    if training:
        if params['optimizer'] == 'adam':
            optimizer = tf.optimizers.Adam(
                learning_rate=params['learning_rate']
            )
        elif params['optimizer'] == 'rmsprop':
            optimizer = tf.optimizers.RMSprop(
                learning_rate=params['learning_rate']
            )
        elif params['optimizer'] == 'sgd':
            optimizer = tf.optimizers.SGD(
                learning_rate=params['learning_rate']
            )
        # optimizer = tf.train.experimental.enable_mixed_precision_graph_rewrite(
        #     optimizer
        # )
        optimizer.iterations = tf.compat.v1.train.get_or_create_global_step()

        update_ops = model.get_updates_for(None) + model.get_updates_for(features)

        minimize_op = optimizer.get_updates(
            loss,
            model.trainable_variables)[0]
        train_op = tf.group(minimize_op, *update_ops)

    return tf.estimator.EstimatorSpec(
        mode=mode,
        # predictions=preds,
        loss=loss,
        # export_outputs={
        #     "classifcation_output": tf.estimator.export.ClassificationOutput(scores=preds)
        # },
        train_op=train_op
    )


@tf.function
def input_fn_train_avro():
    dataset = avro_generator.get_data(
        BUCKET_NAME,
        PREFIX,
        'train',
        global_params['batch_size'],
        global_params['epochs'],
        global_params['chunk_size'],
        global_params['cycle_length'],
        NUM_WORKERS,
        TASK_INDEX,
    )
    return dataset


@tf.function
def input_fn_eval_avro():
    dataset = avro_generator.get_data(
        BUCKET_NAME,
        PREFIX,
        'validation',
        global_params['batch_size'],
        global_params['epochs'],
        global_params['chunk_size'],
        global_params['cycle_length'],
        NUM_WORKERS,
        TASK_INDEX,
    )
    return dataset


@tf.function
def input_fn_train_bq():
    dataset = bq_generator.get_data(
        global_table_id,
        'train',
        global_params['batch_size'],
        global_params['epochs'],
        global_params['chunk_size'],
        global_params['cycle_length'],
        NUM_WORKERS,
        TASK_INDEX,
    )
    return dataset


@tf.function
def input_fn_eval_bq():
    dataset = bq_generator.get_data(
        global_table_id,
        'validation',
        global_params['batch_size'],
        global_params['epochs'],
        global_params['chunk_size'],
        global_params['cycle_length'],
        NUM_WORKERS,
        TASK_INDEX,
    )
    return dataset

def get_session_config(job_name: str, task_index: int):
    if job_name == 'chief':
        return tf.compat.v1.ConfigProto(device_filters=['/job:ps', '/job:chief'])
    if job_name == 'ps':
        return tf.compat.v1.ConfigProto(device_filters=['/job:ps', '/job:chief', '/job:worker'])
    elif job_name == 'worker':
        return tf.compat.v1.ConfigProto(device_filters=[
            '/job:worker/task:%d' % task_index
        ])
    return None


def make_job_output(job_dir: str, add_suffix: bool):
    if add_suffix is True:
        return "{}/{}".format(
            job_dir,
            datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        )
    else:
        return job_dir


global_table_id = ""
global_params = {}
JOB_NAME = None
TASK_INDEX = -1
NUM_WORKERS = 1
BUCKET_NAME = ''
PREFIX = ''

def train_and_evaluate_dist(
    table_id: str,
    job_dir: str,
    bucket_name: str,
    prefix: str,
    params: dict,
    job_name=None,
    task_index=-1,
    num_workers=1,
):
    """
    TODO: description
    :param table_id:
    :param params:
    :return:
    """

    global global_table_id
    global global_params
    global TASK_INDEX
    global NUM_WORKERS
    global JOB_NAME
    global BUCKET_NAME
    global PREFIX
    global_table_id = table_id
    # params['batch_size'] = params['batch_size'] * NUM_WORKERS
    global_params = params
    JOB_NAME = job_name
    TASK_INDEX = task_index
    NUM_WORKERS = num_workers
    BUCKET_NAME = bucket_name
    PREFIX = prefix

    # strategy = tf.distribute.MirroredStrategy()

    # strategy = tf.distribute.experimental.MultiWorkerMirroredStrategy()
    strategy = tf.distribute.experimental.ParameterServerStrategy()

    tf.get_logger().info("NTC_DEBUG: Number of devices in strategy: {}".format(strategy.num_replicas_in_sync))

    tf.summary.trace_on(
        graph=False,
        profiler=False
    )

    train_steps_per_epoch = math.ceil(
                data.get_sample_count(
                    table_id,
                    partition='train'
                ) / params['batch_size']
            )
    
    config = tf.estimator.RunConfig(
        log_step_count_steps=global_params['log_step_count_steps'],
        save_summary_steps=global_params['summary_write_steps'],
        # Evaluate every quarter through the epoch
        save_checkpoints_steps=math.floor(
            train_steps_per_epoch*.25
        ),
        # session_config=get_session_config(job_name, task_index),
        train_distribute=strategy,
        eval_distribute=strategy
    )

    classifier = tf.estimator.Estimator(
        model_fn=model_fn, 
        model_dir=make_job_output(job_dir, global_params['no_generated_job_path']), 
        config=config
    )

    if global_params['data_source'] == 'bigquery':
        input_fn_train = input_fn_train_bq
        input_fn_eval = input_fn_eval_bq
    elif global_params['data_source'] == 'avro':
        input_fn_train = input_fn_train_avro
        input_fn_eval = input_fn_eval_avro

    tf.estimator.train_and_evaluate(
        classifier,
        train_spec=tf.estimator.TrainSpec(
            input_fn=input_fn_train,
            max_steps=train_steps_per_epoch * params['epochs']
        ),
        eval_spec=tf.estimator.EvalSpec(
            input_fn=input_fn_eval,
            steps=math.ceil(
                data.get_sample_count(
                    table_id,
                    partition='validation'
                ) / params['batch_size']
            ),
            # throttle_secs=60,
        )
    )


def get_train_steps(table_id: str, params: dict) -> Tuple[int, int]:
    train_steps_per_epoch = math.ceil(
            data.get_sample_count(
                table_id,
                partition='train'
            ) / params['batch_size']
        )

    checkpoint_steps = math.floor(
            train_steps_per_epoch*.5
    )

    if checkpoint_steps < 1:
        checkpoint_steps = train_steps_per_epoch

    if params['hypertune'] is True:
        checkpoint_steps = train_steps_per_epoch
    
    return train_steps_per_epoch, checkpoint_steps


def create_mlp(job_dir: str, checkpoint_steps: int, params: dict):

    config = tf.estimator.RunConfig(
        log_step_count_steps=params['log_step_count_steps'],
        save_summary_steps=params['summary_write_steps'],
        # Evaluate halfway through the epoch
        save_checkpoints_steps=checkpoint_steps,
    )

    mlp = tf.estimator.Estimator(
        model_fn=model_fn, 
        model_dir=job_dir, 
        config=config,
        params=params,
    )

    return mlp

def train_and_evaluate_local(
    table_id: str,
    job_dir: str,
    bucket_name: str,
    prefix: str,
    params: dict,
    job_name=None,
    task_index=-1,
    num_workers=1,
):
    """
    TODO: description
    :param table_id:
    :param params:
    :return:
    """

    global global_table_id
    global global_params
    global TASK_INDEX
    global NUM_WORKERS
    global JOB_NAME
    global BUCKET_NAME
    global PREFIX
    global_table_id = table_id
    # params['batch_size'] = params['batch_size'] * NUM_WORKERS
    global_params = params
    JOB_NAME = job_name
    TASK_INDEX = task_index
    NUM_WORKERS = num_workers
    BUCKET_NAME = bucket_name
    PREFIX = prefix

    tf.summary.trace_on(
        graph=False,
        profiler=False
    )

    train_steps_per_epoch, checkpoint_steps = get_train_steps(table_id, params)
    classifier = create_mlp(
        make_job_output(job_dir, global_params['no_generated_job_path']), 
        checkpoint_steps,
        params
    )

    if global_params['data_source'] == 'bigquery':
        input_fn_train = input_fn_train_bq
        input_fn_eval = input_fn_eval_bq
    elif global_params['data_source'] == 'avro':
        input_fn_train = input_fn_train_avro
        input_fn_eval = input_fn_eval_avro

    # serving_input_receiver_fn = tf.estimator.export.build_parsing_serving_input_receiver_fn(
    #         features.input_serving_feature_spec()
    # )

    # exporters = [
    #     tf.estimator.BestExporter(
    #         serving_input_receiver_fn=serving_input_receiver_fn
    #     )
    # ]

    tf.estimator.train_and_evaluate(
        classifier,
        train_spec=tf.estimator.TrainSpec(
            input_fn=input_fn_train,
            max_steps=train_steps_per_epoch * params['epochs']
        ),
        eval_spec=tf.estimator.EvalSpec(
            input_fn=input_fn_eval,
            steps=math.ceil(
                data.get_sample_count(
                    table_id,
                    partition='validation'
                ) / params['batch_size']
            ),
            # throttle_secs=60,
            # exporters=exporters,
        ),
    )


def save_model_local(
    table_id: str,
    job_dir: str,
    params: dict,
):
    tf.compat.v1.disable_eager_execution()

    _, checkpoint_steps = get_train_steps(table_id, params)
    mlp = create_mlp(job_dir, checkpoint_steps, params)

    mlp.export_saved_model(
        "{}/saved_model".format(job_dir),
        features.serving_input_receiver_fn
    )