import argparse
import logging
import os
import json
from typing import Any, Dict, Tuple

import trainer.model as model


def get_params(args) -> Dict[str, Any]:
    # format parameters from input arguments
    params = {
        'hypertune': args.hypertune,
        'no_generated_job_path': args.no_generated_job_path,
        'distribute': args.distribute,
        'data_source': args.data_source,
        'distribute_strategy': args.distribute_strategy,
        'cycle_length': args.cycle_length,
        'summary_write_steps': args.summary_write_steps,
        # 'checkpoint_write_steps': args.checkpoint_write_steps,
        'log_step_count_steps': args.log_step_count_steps,
        'dense_neurons_1': args.dense_neurons_1,
        'dense_neurons_2': args.dense_neurons_2,
        'dense_neurons_3': args.dense_neurons_3,
        'activation': args.activation,
        'dropout_rate': float(args.dropout_rate),
        'optimizer': args.optimizer,
        'learning_rate': args.learning_rate,
        'chunk_size': args.chunk_size,
        'batch_size': args.batch_size,
        'epochs': args.epochs,
        'validation_freq': args.validation_freq,
        'kernel_initial_1': args.kernel_initial_1,
        'kernel_initial_2': args.kernel_initial_2,
        'kernel_initial_3': args.kernel_initial_3
    }

    if args.batch_size_float:
        params['batch_size'] = int(args.batch_size_float)
    
    return params


def get_tf_config() -> Tuple[Dict[str, Any], str, int]:
    # for ML ENGINE:
    tf_config = os.environ.get('TF_CONFIG')
    cluster = {}
    job_name = ''
    task_index = 0

    # If TF_CONFIG is not available run local.
    if tf_config:
        tf_config_json = json.loads(tf_config)
        cluster = tf_config_json.get('cluster')
        job_name = tf_config_json.get('task', {}).get('type')
        task_index = tf_config_json.get('task', {}).get('index')

        tf_config_json["cluster"]["chief"] = cluster.get("master")
        if cluster.get("master"):
            del tf_config_json["cluster"]["master"]
            cluster = tf_config_json.get('cluster')

        # Map ML Engine master to chief for TF
        if job_name == "master":
            tf_config_json["task"]["type"] = 'chief'
            job_name = 'chief'
            os.environ['TF_CONFIG'] = json.dumps(tf_config_json)
    
    return cluster, job_name, task_index



def train_and_evaluate(args):
    """
    TODO: description
    :param args:
    :return:
    """

    params = get_params(args)

    _, job_name, task_index = get_tf_config()

    if args.distribute is True:
        return model.train_and_evaluate_dist(
            args.table_id, 
            args.job_dir, 
            args.avro_bucket,
            args.avro_prefix,
            params=params,
            job_name=job_name,
            task_index=task_index,
            num_workers=args.num_workers,
            # hypertune=args.hypertune
        )
    else:
        return model.train_and_evaluate_local(
            args.table_id, 
            args.job_dir, 
            args.avro_bucket,
            args.avro_prefix,
            params=params,
            job_name=job_name,
            task_index=task_index,
            num_workers=args.num_workers,
            # hypertune=args.hypertune
        )


def save_model(args):
    params = get_params(args)
    params['no_generated_job_path'] = True

    model.save_model_local(
        args.table_id, 
        args.job_dir, 
        params=params,
    )


if __name__ == '__main__':

    # TODO: update argument defaults with hp tuning results

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--data-source',
        type=str,
        help='Get data from BigQuery Storiage API or avro files',
        default='bigquery')
    parser.add_argument(
        '--distribute',
        type=bool,
        help='Whether to run the job in distributed mode. Default: False',
        default=False)
    parser.add_argument(
        '--distribute-strategy',
        type=str,
        help='Distribute strategy. Can be `parameter-server` or `multi-worker`. Default: multi-worker',
        default='multi-worker')
    parser.add_argument(
        '--hypertune',
        type=bool,
        help='Whether training is running in a hypertuning session. Default: False',
        default=False)
    parser.add_argument(
        '--num-workers',
        type=int,
        help='Number of workers in distribution strategy',
        default=1)
    parser.add_argument(
        '--log-step-count-steps',
        type=int,
        help='Frequency in steps (batches) to log loss summary during training. Default: 100',
        default=100)
    parser.add_argument(
        '--summary-write-steps',
        type=int,
        help='Steps (batches) to run before writing Tensorflow scalar summaries. Default: 100',
        default=100)
    parser.add_argument(
        '--table-id',
        type=str,
        help='BigQuery table optionally containing dataset. Default: finaltaxi_encoded_sampled_small',
        default='finaltaxi_encoded_sampled_small')
    parser.add_argument(
        '--avro-bucket',
        type=str,
        help='Name of GCS bucket with avro data',
        default='gcp-cert-demo-1'
    )
    parser.add_argument(
        '--avro-prefix',
        type=str,
        help='Path prefix to avro data in GCS bucket',
        default='data/avro/1_pct'
    )
    parser.add_argument(
        '--task',
        type=str,
        help='train or save. Default: train',
        default='train')
    parser.add_argument(
        '--job-dir',
        type=str,
        help='Location to write history, logs, and export model. Can be a GCS (gs://..) URI. Default: model',
        default='model')
    parser.add_argument(
        '--no-generated-job-path',
        action='store_false',
        help='Do not add a path suffix to --job-dir with the date and time',
    )
    parser.add_argument(
        '--cycle-length',
        type=int,
        help='The number of input elements that will be processed concurrently. Should be set to the number of available CPUs. Default: 8',
        default=8)
    parser.add_argument(
        '--dense-neurons-1',
        type=int,
        help='Number of neurons in first model layer. Default: 64',
        default=64)
    parser.add_argument(
        '--dense-neurons-2',
        type=int,
        help='Number of neurons in second model layer. Default: 32',
        default=32)
    parser.add_argument(
        '--dense-neurons-3',
        type=int,
        help='Number of neurons in third model layer. Default: 16',
        default=16)
    parser.add_argument(
        '--activation',
        type=str,
        help='Activation function. Default: relu',
        default='relu')
    parser.add_argument(
        '--dropout-rate',
        type=float,
        help='Dropout rate for all model layers. Default: 0.1',
        default=0.1)
    parser.add_argument(
        '--optimizer',
        type=str,
        help='Optimizer function. Default: adam',
        default='adam')
    parser.add_argument(
        '--learning-rate',
        type=float,
        help='Learning rate. Default: 0.01',
        default=0.01)
    parser.add_argument(
        '--batch-size',
        type=int,
        help='Training batch size. Default: 102400',
        default=102400)
    parser.add_argument(
        '--batch-size-float',
        type=float,
        help='Batch size as float (for hypertuning only, do not use)')
    parser.add_argument(
        '--epochs',
        type=int,
        help='Number of epochs to train. Default: 3',
        default=3)
    parser.add_argument(
        '--validation-freq',
        type=int,
        help='Validation frequency. Default: 1',
        default=1)
    parser.add_argument(
        '--kernel-initial-1',
        type=str,
        help='Kernel initializer for first model layer. Default: normal',
        default='normal')
    parser.add_argument(
        '--kernel-initial-2',
        type=str,
        help='Kernel initializer for second model layer. Default: normal',
        default='normal')
    parser.add_argument(
        '--kernel-initial-3',
        type=str,
        help='Kernel initializer for third model layer. Default: normal',
        default='normal')
    args, _ = parser.parse_known_args()

    if args.task in ['train']:
        train_and_evaluate(args)
    elif args.task in 'save':
        save_model(args)
    else:
        logging.error('--task must be \'train\' or \'save\'')
