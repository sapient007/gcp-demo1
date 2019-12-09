import argparse
import logging
import os
import json

import trainer.model as model

# import trainer.model_tf as model_tf
# import trainer.save_model as save_model

def train_and_evaluate(args):
    """
    TODO: description
    :param args:
    :return:
    """


    # format parameters from input arguments
    params = {
        'hypertune': args.hypertune,
        'distribute': args.distribute,
        'data_source': args.data_source,
        'distribute_strategy': args.distribute_strategy,
        'cycle_length': args.cycle_length,
        'summary_write_steps': args.summary_write_steps,
        'checkpoint_write_steps': args.checkpoint_write_steps,
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

    """Parse TF_CONFIG to cluster_spec and call run() method.

    TF_CONFIG environment variable is available when running using
    gcloud either locally or on cloud. It has all the information required
    to create a ClusterSpec which is important for running distributed code.

    Args:
        args (args): Input arguments.
    """

    # for ML ENGINE:
    tf_config = os.environ.get('TF_CONFIG')
    job_name = None
    task_index = 0
    # tf.get_logger().info("NTC_DEBUG: Old TF_CONFIG: {}".format(tf_config))
    # If TF_CONFIG is not available run local.
    if tf_config:
        tf_config_json = json.loads(tf_config)
        cluster = tf_config_json.get('cluster')
        job_name = tf_config_json.get('task', {}).get('type')
        task_index = tf_config_json.get('task', {}).get('index')

        # tf_config_json["cluster"]["chief"] = cluster.get("master")
        # if cluster.get("master"):
        #     del tf_config_json["cluster"]["master"]
        #     cluster = tf_config_json.get('cluster')

        # # Map ML Engine master to chief for TF
        # if job_name == "master":
        #     tf_config_json["task"]["type"] = 'chief'
        #     job_name = 'chief'
        #     os.environ['TF_CONFIG'] = json.dumps(tf_config_json)
        # tf.get_logger().info("NTC_DEBUG: New TF_CONFIG: {}".format(tf_config_json))


        # if job_name is not None or task_index is not None:
        #     cluster_spec = tf.train.ClusterSpec(cluster)

        #     tf.get_logger().info("NTC_DEBUG: {}".format(cluster_spec))
        #     server = tf.distribute.Server(
        #         cluster_spec,
        #         job_name=job_name,
        #         task_index=task_index
        #     )
        #     if job_name == 'ps':
        #         server.join()
        #         return
        #     elif job_name in ['chief', 'worker']:
        #         tf.get_logger().info("NTC_DEBUG: job_name: {}; task_index: {}; server.target: {}".format(job_name, task_index, server.target))
        #         with tf.compat.v1.Session(server.target):
        #             return model.train_and_evaluate(
        #                 args.table_id, 
        #                 args.job_dir, 
        #                 params=params,
        #                 job_name=job_name,
        #                 task_index=task_index,
        #             )

    # os.environ["TF_CONFIG"] = json.dumps({
    #     "cluster": {
    #         "chief": ["localhost:2222"]
    #         # "worker": ["host1:port", "host2:port", "host3:port"],
    #         # "ps": ["host4:port", "host5:port"]
    #     },
    #     "task": {"type": args.tf_task, "index": 0}
    # })

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

    # model_tf.train_and_evaluate(args.table_id, params)
    # save_model.save_estimator_model(bucket_name=args.bucket, path=args.job_dir)

    # save model and history to job directory
    # save_model.save_model(
    #     mlp_model,
    #     bucket_name=args.bucket,
    #     path=args.job_dir
    # )


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
        help='Whether to run the job in distributed mode',
        default=False)
    parser.add_argument(
        '--distribute-strategy',
        type=str,
        help='Distribute strategy. Can be `parameter-server` or `multi-worker`',
        default='multi-worker')
    parser.add_argument(
        '--hypertune',
        type=bool,
        help='Whether training is running in a hypertuning session',
        default=False)
    parser.add_argument(
        '--num-workers',
        type=int,
        help='Number of workers in distribution strategy',
        default=1)
    parser.add_argument(
        '--log-step-count-steps',
        type=int,
        help='Frequency in steps (batches) to log loss summary during training',
        default=100)
    parser.add_argument(
        '--summary-write-steps',
        type=int,
        help='Steps (batches) to run before writing Tensorflow scalar summaries',
        default=100)
    parser.add_argument(
        '--checkpoint-write-steps',
        type=int,
        help='Steps (batches) to run before writing Tensorflow training checkpoints',
        default=500)
    parser.add_argument(
        '--table-id',
        type=str,
        help='BigQuery table containing dataset',
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
        help='train or tune',
        default='train')
    parser.add_argument(
        '--bucket',
        type=str,
        help='Bucket name to write history and export model',
        default='gcp-cert-demo-1')
    parser.add_argument(
        '--job-dir',
        type=str,
        help='Directory to create in bucket to write history, logs, and export model',
        default='model')
    parser.add_argument(
        '--cycle-length',
        type=int,
        help='The number of input elements that will be processed concurrently',
        default=8)
    parser.add_argument(
        '--dense-neurons-1',
        type=int,
        help='Number of neurons in first model layer, default=64',
        default=64)
    parser.add_argument(
        '--dense-neurons-2',
        type=int,
        help='Number of neurons in second model layer, default=32',
        default=32)
    parser.add_argument(
        '--dense-neurons-3',
        type=int,
        help='Number of neurons in third model layer, default=8',
        default=16)
    parser.add_argument(
        '--activation',
        type=str,
        help='Activation function, default=relu',
        default='relu')
    parser.add_argument(
        '--dropout-rate',
        type=float,
        help='Dropout rate for all model layers, default=0.1',
        default=0.1)
    # parser.add_argument(
    #     '--dropout-rate-1',
    #     type=float,
    #     help='Dropout rate for first model layer, default=0.1',
    #     default=0.1)
    # parser.add_argument(
    #     '--dropout-rate-2',
    #     type=float,
    #     help='Dropout rate for second model layer, default=0.1',
    #     default=0.1)
    # parser.add_argument(
    #     '--dropout-rate-3',
    #     type=float,
    #     help='Dropout rate for third model layer, default=0.1',
    #     default=0.1)
    parser.add_argument(
        '--optimizer',
        type=str,
        help='Optimizer function, default=adam',
        default='adam')
    parser.add_argument(
        '--learning-rate',
        type=float,
        help='Learning rate, default=0.01',
        default=0.1)
    parser.add_argument(
        '--batch-size',
        type=int,
        help='Batch size, default=64',
        default=64)
    parser.add_argument(
        '--batch-size-float',
        type=float,
        help='Batch size as float (for hypertuning only), default=64')
    parser.add_argument(
        '--chunk-size',
        type=int,
        help='Chunk size to load training data, default=200000',
        default=200000)
    parser.add_argument(
        '--epochs',
        type=int,
        help='Number of epochs to train, default=3',
        default=3)
    parser.add_argument(
        '--validation-freq',
        type=int,
        help='Validation frequency, default=1',
        default=1)
    parser.add_argument(
        '--kernel-initial-1',
        type=str,
        help='Kernel initializer for first model layer, default=normal',
        default='normal')
    parser.add_argument(
        '--kernel-initial-2',
        type=str,
        help='Kernel initializer for second model layer, default=normal',
        default='normal')
    parser.add_argument(
        '--kernel-initial-3',
        type=str,
        help='Kernel initializer for third model layer, default=normal',
        default='normal')
    args, _ = parser.parse_known_args()

    if args.task in 'train':
        train_and_evaluate(args)
    elif args.task in 'tune':
        tune(args)
    else:
        logging.error('--task must be \'train\' or \'tune\'')
