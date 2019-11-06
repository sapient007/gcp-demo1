import json
import logging
import argparse
import talos as ta
import pandas as pd
import tensorflow as tf

# Custom code
import trainer.model as model
import trainer.data as data


def process_data(table_id, partitions=['train', 'validation', 'test']):

    datasets = {}
    for partition in partitions:
        datasets[partition] = {}
        rows = data.get_reader_rows(table_id, partition)
        print(type(rows))

        df = pd.DataFrame(rows)

        datasets[partition]['y'] = df['cash'].values
        datasets[partition]['x'] = df.drop('cash', axis=1).values

    return datasets['train']['x'], datasets['train']['y'], \
           datasets['test']['x'], datasets['test']['y'], \
           datasets['validation']['x'], datasets['validation']['y']


def tune(table_id, output_path, params):

    # logging.info("Preprocessing dataset {}.".format(table_id))
    X_train, y_train, X_test, y_test, x_val, y_val = process_data(table_id)

    # Run the tuning
    logging.info('Running scan on hyper-parameters')
    scan_results = ta.Scan(x=X_train, y=y_train, x_val=x_val, y_val=y_val,
                           params=params, model=model.train_mlp, experiment_name='HP_Tuning',
                           disable_progress_bar=True)

    logging.info('Scanning complete.')

    # Analyze the scan object
    analyze_object = ta.Analyze(scan_results)

    # Save the DataFrame with the results
    logging.info("Writing output to {}.".format(output_path))
    analyze_object.data.to_csv(output_path)


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--table_id',
        type=str,
        help='Dataset file local or GCS')

    parser.add_argument(
        '--output_path',
        type=str,
        help='Output file to be saved to GCS')

    parser.add_argument(
        '--parameters',
        type=str,
        default=None,
        help='Dictionary containing parameters. See README for acceptable & default values.')

    args, _ = parser.parse_known_args()
    return args


if __name__ == '__main__':

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)-4.5s]  %(message)s',
        handlers=[
            logging.FileHandler('predictor.log'),
            logging.StreamHandler()
        ])

    args = get_args()

    if args.parameters is None:
        params = {
            'dense_neurons_1': [64, 9],
            'dense_neurons_2': [32],
            'dense_neurons_3': [8],
            'activation': ['relu'],
            'dropout_rate_1': [0.5],
            'dropout_rate_2': [0.5],
            'dropout_rate_3': [0.5],
            'optimizer': ['Adam'],
            'learning_rate': [.0001],
            'kernel_initial_1': ['normal'],
            'kernel_initial_2': ['normal'],
            'kernel_initial_3': ['normal'],

            'batch_size': [1024],
            'chunk_size': [500000],
            'epochs': [40],
            'validation_freq': [5],
            'patience': [5]
        }
    else:
        print(args.parameters)
        params = json.loads(args.parameters)

    # Create optimizers
    optimizers = []
    if 'Adam' in params['optimizer']:
        optimizers.append(tf.keras.optimizers.Adam)
    if 'Nadam' in params['optimizer']:
        optimizers.append(tf.keras.optimizers.Nadam)
    if 'RMSprop' in params['optimizer']:
        optimizers.append(tf.keras.optimizers.RMSprop)
    if 'SGD' in params['optimizer']:
        optimizers.append(tf.keras.optimizers.SGD)

    if len(optimizers) == 0:
        optimizers = [tf.keras.optimizers.Adam]

    params['optimizer'] = optimizers

    tune(args.table_id, args.output_path, params)
