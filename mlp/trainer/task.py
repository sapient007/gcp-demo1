import argparse
import numpy
import pandas
import tensorflow as tf
import keras
from keras import backend as K
from tensorflow.keras.models import model_from_json
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
import pickle
from collections import Counter
from matplotlib import pyplot
import h5py
import os
import json
import talos as ta


def train_and_evaluate(args):
    """

    :param args:
    :return:
    """

    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--parameter',
        nargs='+',
        help='Help text',
        default=['Default value'])
    args, _ = parser.parse_known_args()
    train_and_evaluate(args)
