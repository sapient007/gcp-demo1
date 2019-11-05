import json
import logging
import argparse
import talos as ta
import tensorflow as tf

# Custom code
import model


def tune(dataset_name, output_path, params):

    logging.info("Preprocessing dataset {}.".format(dataset_name))
    X_train, y_train, X_test, y_test, X_val, y_val = model.process_data(dataset_name)

    # Run the tuning
    logging.info('Running scan on hyper-parameters')
    scan_results = ta.Scan(x=X_train, y=y_train, x_val=X_val, y_val=y_val, params=params, model=model.train_mlp,
                           experiment_name='test_1')

    logging.info('Scanning complete.')

    # Analyze the scan object
    analyze_object = ta.Analyze(scan_results)

    # Save the DataFrame with the results
    logging.info("Writing output to {}.".format(output_path))
    analyze_object.data.to_csv(output_path)


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'dataset_name',
        type=str,
        help='Dataset file local or GCS')

    parser.add_argument(
        'output_path',
        type=str,
        help='Output file to be saved to GCS')

    parser.add_argument(
        '--parameters',
        type=float,
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
            'optimizer': [tf.keras.optimizers.Adam],
            'learning_rate': [.0001],
            'kernel_initial_1': ['normal'],
            'kernel_initial_2': ['normal'],
            'kernel_initial_3': ['normal']
        }
    else:
        params = json.loads(args.parameters)

        optimizers = []
        if 'Adam' in params['optimizer']:
            optimizers.append(tf.keras.optimizers.Adam)

        if len(optimizers) == 0:
            optimizers = [tf.keras.optimizers.Adam]

        params['optimizer'] = optimizers

    # TODO - check both GCS location is valid
    # logging.info(args.dataset_name[5:])
    # if tf.io.gfile.exists(args.dataset_name[5:]):

    tune(args.dataset_name, args.outputh_path, params)

