from typing import List, Tuple

import tensorflow as tf

def defs():
    return [
    { "name": "year_norm", "dtype": tf.dtypes.float32},
    { "name": "start_time_norm_midnight", "dtype": tf.dtypes.float32},
    { "name": "start_time_norm_noon", "dtype": tf.dtypes.float32},
    { "name": "pickup_lat_std", "dtype": tf.dtypes.float32},
    { "name": "pickup_long_std", "dtype": tf.dtypes.float32},
    { "name": "pickup_lat_centered", "dtype": tf.dtypes.float32},
    { "name": "pickup_long_centered", "dtype": tf.dtypes.float32},
    { "name": "day_of_week_MONDAY", "dtype": tf.dtypes.float32},
    { "name": "day_of_week_TUESDAY", "dtype": tf.dtypes.float32},
    { "name": "day_of_week_WEDNESDAY", "dtype": tf.dtypes.float32},
    { "name": "day_of_week_THURSDAY", "dtype": tf.dtypes.float32},
    { "name": "day_of_week_FRIDAY", "dtype": tf.dtypes.float32},
    { "name": "day_of_week_SATURDAY", "dtype": tf.dtypes.float32},
    { "name": "day_of_week_SUNDAY", "dtype": tf.dtypes.float32},
    { "name": "month_JANUARY", "dtype": tf.dtypes.float32},
    { "name": "month_FEBRUARY", "dtype": tf.dtypes.float32},
    { "name": "month_MARCH", "dtype": tf.dtypes.float32},
    { "name": "month_APRIL", "dtype": tf.dtypes.float32},
    { "name": "month_MAY", "dtype": tf.dtypes.float32},
    { "name": "month_JUNE", "dtype": tf.dtypes.float32},
    { "name": "month_JULY", "dtype": tf.dtypes.float32},
    { "name": "month_AUGUST", "dtype": tf.dtypes.float32},
    { "name": "month_SEPTEMBER", "dtype": tf.dtypes.float32},
    { "name": "month_OCTOBER", "dtype": tf.dtypes.float32},
    { "name": "month_NOVEMBER", "dtype": tf.dtypes.float32},
    { "name": "month_DECEMBER", "dtype": tf.dtypes.float32},
]

def get_generator_output(label_output=tf.dtypes.float32) -> List[tf.DType]:
    outputs = []
    for feature in defs():
        outputs.append(feature.get('dtype'))
    outputs.append(label_output)
    return outputs


def get_generator_output_shape(label_shape=tf.TensorShape([])) -> List[tf.TensorShape]:
    shapes = []
    for feature in defs():
        shapes.append(tf.TensorShape([]))
    shapes.append(label_shape)
    return shapes


def get_estimator_cols():
    feats = []

    for feature in defs():
        feats.append(
            tf.feature_column.numeric_column(
                key=feature.get('name'),
                dtype=feature.get('dtype')
            )
        )

    return feats

