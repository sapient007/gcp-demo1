import argparse

import model


def train_and_evaluate(args):
    """
    TODO: description
    :param args:
    :return:
    """

    x_train, y_train, x_test, y_test, x_val, y_val = model.process_data(args.filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--filename',
        type=str,
        help='GCF filename of data',
        default='gs://gcp-cert-demo-1/test/results-20191007-193432.csv')
    args, _ = parser.parse_known_args()
    train_and_evaluate(args)
