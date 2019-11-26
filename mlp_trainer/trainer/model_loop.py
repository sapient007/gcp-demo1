import time
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

global_table_id = ""
global_params = {}

# @tf.function
def input_fn_train(dist=False, strategy=None):
    # return tf.data.Dataset.from_tensors(({"year_norm":[1.]}, [1.]))
    dataset = generator.get_data(
        global_table_id,
        'train',
        global_params['batch_size'],
        global_params['epochs'],
        global_params['chunk_size'],
        global_params['cycle_length']
    )
    if dist is True:
        dataset = strategy.experimental_distribute_dataset(dataset)
    return dataset


# @tf.function
def input_fn_eval(dist=False, strategy=None):
    # return tf.data.Dataset.from_tensors(({"year_norm":[1.]}, [1.]))
    dataset = generator.get_data(
        global_table_id,
        'validation',
        global_params['batch_size'],
        global_params['epochs'],
        global_params['chunk_size'],
        global_params['cycle_length']
    )
    if dist is True:
        dataset = strategy.experimental_distribute_dataset(dataset)
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

    #https://www.tensorflow.org/tutorials/distribute/custom_training
    with strategy.scope():
        loss_object = tf.keras.losses.BinaryCrossentropy(
            reduction=tf.keras.losses.Reduction.NONE
        )

        def compute_loss(labels, predictions):
            # equivalent of:
            # loss = tf.reduce_sum(loss_object(labels, predictions)) * (1. / global_params['batch_size'])
            per_example_loss = loss_object(labels, predictions)
            return per_example_loss, tf.nn.compute_average_loss(per_example_loss, global_batch_size=global_params['batch_size'])

        train_eval_ops = [
            tf.keras.metrics.BinaryAccuracy(),
            tf.keras.metrics.Precision(),
            tf.keras.metrics.Recall(),
        ]

        test_loss = tf.keras.metrics.Mean(name='test_loss')
        test_eval_ops = [
            tf.keras.metrics.BinaryAccuracy(),
            tf.keras.metrics.Precision(),
            tf.keras.metrics.Recall(),
            tf.keras.metrics.FalseNegatives(),
            tf.keras.metrics.FalsePositives(),
            tf.keras.metrics.TrueNegatives(),
            tf.keras.metrics.TruePositives()
        ]

        model = base_model()

        # optimizer = tf.train.experimental.enable_mixed_precision_graph_rewrite(
        #     tf.optimizers.Adam(
        #         learning_rate=global_params['learning_rate']
        #     )
        # )

        optimizer = tf.optimizers.Adam(
            learning_rate=global_params['learning_rate']
        )

        checkpoint = tf.train.Checkpoint(optimizer=optimizer, model=model)
        checkpoint_mgr = tf.train.CheckpointManager(
            checkpoint,
            directory=job_dir,
            max_to_keep=5
        )

        def train_step(inputs):
            features, labels = inputs

            with tf.GradientTape() as tape:
                predictions = model(features, training=True)
                batch_losses, loss = compute_loss(labels, predictions)

            gradients = tape.gradient(loss, model.trainable_variables)
            optimizer.apply_gradients(zip(gradients, model.trainable_variables))

            # op = optimizer.get_updates(
            #     loss,
            #     model.trainable_variables)

            # strategy.experimental_run_v2(op)

            # tf.distribute.get_replica_context.merge_call(strategy.experimental_run_v2(op))

            for op in train_eval_ops:
                op.update_state(labels, predictions)
            return loss


        def test_step(inputs):
            features, labels = inputs

            predictions = model(features, training=False)
            t_loss = loss_object(labels, predictions)

            test_loss.update_state(t_loss)

            for op in test_eval_ops:
                op.update_state(labels, predictions)
            

        @tf.function
        def distributed_train_step(dataset_inputs):
            per_replica_losses = strategy.experimental_run_v2(train_step,
                                                            args=(dataset_inputs,))
            return strategy.reduce(tf.distribute.ReduceOp.SUM, per_replica_losses,
                                axis=None)


        @tf.function
        def distributed_test_step(dataset_inputs):
            return strategy.experimental_run_v2(test_step, args=(dataset_inputs,))

        for epoch in range(global_params['epochs']):
            tf.get_logger().info("Epoch {}: Starting training".format(epoch+1))
            # TRAIN LOOP
            total_loss = 0.0
            num_batches = 0
            train_dist_dataset = input_fn_train(dist=True, strategy=strategy)
            start = time.process_time()
            for x in train_dist_dataset:
                total_loss += distributed_train_step(x)
                num_batches += 1
                if num_batches % 100 == 0:
                    end = time.process_time()
                    tf.get_logger().info("Epoch {}: Step {} training complete. Loss: {}; Time elapsed: {} ({} steps/sec)".format(
                        epoch+1, 
                        num_batches, 
                        total_loss / num_batches,
                        round(end - start, 2),
                        round(100 / (end - start), 2)
                        )
                    )
                    start = time.process_time()
            train_loss = total_loss / num_batches
            tf.get_logger().info("Epoch {}: Training complete. Steps: {}; Loss: {}".format(epoch+1, num_batches, train_loss))

            # TEST LOOP
            tf.get_logger().info("Epoch {}: Starting testing".format(epoch+1))
            test_dist_dataset = input_fn_eval(dist=True, strategy=strategy)
            num_test_batches = 0
            start = time.process_time()
            for x in test_dist_dataset:
                distributed_test_step(x)
                num_test_batches += 1
                if num_test_batches % 100 == 0:
                    end = time.process_time()
                    tf.get_logger().info("Epoch {}: Test step {} complete. Time elapsed: {} ({} steps/sec)".format(
                        epoch+1, 
                        num_test_batches,
                        round(end - start, 2),
                        round(100 / (end - start), 2)
                    ))
                    start = time.process_time()
            
            tf.get_logger().info("Epoch {}: Testing finished in {} steps".format(epoch+1, num_test_batches))

            tf.get_logger().info("Epoch {}: Saving checkpoint".format(epoch+1))
            checkpoint_mgr.save(epoch+1)
            tf.get_logger().info("Epoch {}: Checkpoint saved".format(epoch+1))

            outputs = {
                'epoch': epoch+1,
                'batches': num_batches+1,
                'train_loss': train_loss,
                'test_loss': test_loss.result()
            }

            test_loss.reset_states()
            
            for op in train_eval_ops:
                outputs["train_{}".format(op.name)] = op.result()
                op.reset_states()

            for op in test_eval_ops:
                outputs["test_{}".format(op.name)] = op.result()
                op.reset_states()

            tf.get_logger().info("Epoch {} results: {}".format(epoch, outputs))
        # return