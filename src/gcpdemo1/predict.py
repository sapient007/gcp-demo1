import logging
import pandas as pd

import googleapiclient.discovery
from google.cloud import bigquery

import data


logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)-4.5s]  %(message)s',
        handlers=[logging.StreamHandler()])


class Predictor:
    def __init__(self, project, model, version=None):
        """Send json data to a deployed model for prediction.
    ​
        Args:
            project (str): project where the Cloud ML Engine Model is deployed.
            model (str): model name.
            instances ([Mapping[str: Any]]): Keys should be the names of Tensors
                your deployed model expects as inputs. Values should be datatypes
                convertible to Tensors, or (potentially nested) lists of datatypes
                convertible to tensors.
            version: str, version of the model to target.
        Returns:
            Mapping[str: any]: dictionary of prediction results defined by the
                model.
        """
        # Create the ML Engine service object.
        # To authenticate set the environment variable
        # GOOGLE_APPLICATION_CREDENTIALS=<path_to_service_account_file>
        service = googleapiclient.discovery.build('ml', 'v1', cache_discovery=False)
        name = 'projects/{}/models/{}'.format(project, model)

        if version is not None:
            name += '/versions/{}'.format(version)

        self.project = project
        self.model = model
        self.version = version
        self.name = name
        self.service = service

    def predict(self, instances):

        logging.info(f'Predicting using model "{self.model}" version "{self.version}"')
        response = self.service.projects().predict(name=self.name, body={'instances': instances}).execute()
        print(response)

        # if 'error' in response:
        #     raise RuntimeError(response['error'])

        return response['predictions']


if __name__ == "__main__":
    """
    For local testing.
    """

    project = 'ml-sandbox-1-191918'

    rows = data.get_reader_rows(
        'finaltaxi_encoded_sampled_small',
        partition_name='test'
    )
    df = pd.DataFrame(list(rows)[:10])
    df = df.drop(
        'cash',
        axis=1
    )
    vals = df.values
    instances = []
    for i, val in enumerate(vals):
        instances.append({
            'dense_input': list(val),
        })
    print(instances)

    predictor = Predictor(
        project,
        model='mlp_deployed_src_test_9',
        version='v_1573072064'
    )

    print(predictor.predict(instances))
