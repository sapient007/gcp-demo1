import googleapiclient.discovery
import logging



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

        response = self.service.projects().predict(name=self.name, body={'instances': instances}).execute()

        # if 'error' in response:
        #     raise RuntimeError(response['error'])

        return response['predictions']


if __name__ == "__main__":
    """
    For local testing.
    """

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)-4.5s]  %(message)s',
        handlers=[
            logging.FileHandler('predictor.log'),
            logging.StreamHandler()
        ])

    project = 'ml-sandbox-1-191918'
    model = 'taxi_model_1565105801'

    instances = [{"csv_row": "6,0.927083333,0.9375,116,4,2013,0.1,0.606309877,0.671360099,0.653137315,0.663879711", "key": "dummy-key"}]

    predictor = Predictor(project, model)

    print(predictor.predict(instances))
