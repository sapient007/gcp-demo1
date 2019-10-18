import argparse

import tensorflow as tf

import trainer.model as model


def train_and_evaluate(args):
    """
    TODO: description
    :param args:
    :return:
    """

    # process data for training
    x_train, y_train, x_test, y_test, x_val, y_val = model.process_data(args.filename)

    # choose optimizer from input argument
    if args.optimizer.lower() == 'adam':
        optimizer = tf.keras.optimizers.Adam
    elif args.optimizer.lower() == 'nadam':
        optimizer = tf.keras.optimizers.Nadam
    elif args.optimizer.lower() == 'rmsprop':
        optimizer = tf.keras.optimizers.RMSprop
    elif args.optimizer.lower() == 'sgd':
        optimizer = tf.keras.optimizers.SGD
    else:
        optimizer = None

    # format parameters from input arguments
    params = {
        'dense_neurons_1': args.dense_neurons_1,
        'dense_neurons_2': args.dense_neurons_2,
        'dense_neurons_3': args.dense_neurons_3,
        'activation': args.activation,
        'dropout_rate_1': args.dropout_rate_1,
        'dropout_rate_2': args.dropout_rate_2,
        'dropout_rate_3': args.dropout_rate_3,
        'optimizer': optimizer,
        'learning_rate': args.learning_rate,
        'kernel_initial_1': args.kernel_initial_1,
        'kernel_initial_2': args.kernel_initial_2,
        'kernel_initial_3': args.kernel_initial_3
    }

    # train model and get history
    history, mlp_model = model.train_mlp(x_train, y_train, x_val, y_val, params)
    print(history.history)
    print(model)


if __name__ == '__main__':

    # TODO: update argument defaults with hp tuning results

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--filename',
        type=str,
        help='GCS filename of data',
        default='gs://gcp-cert-demo-1/test/test_results-20191007-193432.csv')
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
        default=8)
    parser.add_argument(
        '--activation',
        type=str,
        help='Activation function, default=relu',
        default='relu')
    parser.add_argument(
        '--dropout-rate-1',
        type=float,
        help='Dropout rate for first model layer, default=0.1',
        default=0.1)
    parser.add_argument(
        '--dropout-rate-2',
        type=float,
        help='Dropout rate for second model layer, default=0.1',
        default=0.1)
    parser.add_argument(
        '--dropout-rate-3',
        type=float,
        help='Dropout rate for third model layer, default=0.1',
        default=0.1)
    parser.add_argument(
        '--optimizer',
        type=str,
        help='Optimizer function, default=adam',
        default='adam')
    parser.add_argument(
        '--learning-rate',
        type=float,
        help='Learning rate, default=0.1',
        default=0.1)
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
    train_and_evaluate(args)
