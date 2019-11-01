import logging
import argparse
import talos as ta
import pandas as pd
import tensorflow as tf

# Custom code
import model


def download_data_from_gcs(path):
    df = pd.DataFrame()

    return df


def tune(args):
    para = {
        'dense_neurons_1': [64, 9],
        'dense_neurons_2': [32],
        'dense_neurons_3': [8],
        'activation': ['relu'],
        'dropout_rate_1': [0.5],
        'dropout_rate_2': [0.5],
        'dropout_rate_3': [0.5],
        'optimizer': [tf.keras.optimizers.Adam],
        'learning_rate': [.0001],
        'kernel_initial_1': ['normal'],
        'kernel_initial_2': ['normal'],
        'kernel_initial_3': ['normal']
    }

    logging.info("Preprocessing Data")
    print(args.filename)
    X_train, y_train, X_test, y_test, X_val, y_val = model.process_data(args.filename)

    logging.info
    # Run the tuning
    scan_results = ta.Scan(x=X_train, y=y_train, x_val=X_val, y_val=y_val, params=para, model=model.train_mlp,
                           experiment_name='test_1')

    logging.info('Scanning complete.')

    # Use Scan object as input
    analyze_object = ta.Analyze(scan_results)

    # Access the DataFrame with the results
    output_filename = 'hp_tuning.csv'
    analyze_object.data.to_csv(output_filename)


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'filename',
        type=str,
        help='Dataset file local or GCS')
    # parser.add_argument(
    #     '--test-split',
    #     type=float,
    #     default=0.2,
    #     help='Split between training and test, default=0.2')
    # parser.add_argument(
    #     '--num-epochs',
    #     type=float,
    #     default=500,
    #     help='number of times to go through the data, default=500')
    # parser.add_argument(
    #     '--batch-size',
    #     type=int,
    #     default=128,
    #     help='number of records to read during each training step, default=128')
    # parser.add_argument(
    #     '--learning-rate',
    #     type=float,
    #     default=.001,
    #     help='learning rate for gradient descent, default=.001')
    # parser.add_argument(
    #     '--verbosity',
    #     choices=['DEBUG', 'ERROR', 'FATAL', 'INFO', 'WARN'],
    #     default='INFO')

    args, _ = parser.parse_known_args()
    return args


if __name__ == '__main__':
    args = get_args()
    tune(args)

