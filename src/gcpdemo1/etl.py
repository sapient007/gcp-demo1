import logging
from google.cloud import bigquery


def run(project):
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

    project = 'ml-sandbox-1-191918'

    run(project=project)