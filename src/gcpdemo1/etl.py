"""
conda install -c conda-forge google-cloud-bigquery
conda install pandas
"""

import logging
from google.cloud import bigquery


def run():
    return


if __name__ == "__main__":
    """
    For local testing.
    """

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)-4.5s]  %(message)s',
        handlers=[
            logging.FileHandler('etl_testing.log'),
            logging.StreamHandler()
        ])

    run()
