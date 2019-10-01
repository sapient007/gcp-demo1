from flask import Flask, jsonify, request
import googleapiclient.discovery
import logging
import json

PROJECT = 'ml-sandbox-1-191918'
MODEL = 'Cash_Or_Credit'

# with open('settings.json', 'r') as fp:
#     config = json.load(fp)

app = Flask(__name__)


def predict_json(project, model, instances, version=None):
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
    service = googleapiclient.discovery.build('ml', 'v1')
    name = 'projects/{}/models/{}'.format(project, model)

    if version is not None:
        name += '/versions/{}'.format(version)

    response = service.projects().predict(
        name=name,
        body={'instances': instances}
    ).execute()

    if 'error' in response:
        raise RuntimeError(response['error'])

    return response['predictions']


@app.route("/predict", methods=['POST'])
def get_predictions():
    """
    API endpoint to get a prediction from ML model.

    :param data: json string
    :return: json object containing predictions
    """

    instances = {}

    try:
        # data_dict = request.get_json(force=True)
        return jsonify(predict_json(PROJECT, MODEL, instances))

    except:
        return(jsonify("Error processing request."))


if __name__ == "__main__":
    """
    Program execution starts here.
    """

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)-4.5s]  %(message)s',
        handlers=[
            logging.FileHandler('scrape.log'),
            logging.StreamHandler()
        ])

    #get_predictions("iiii")
    app.run(host='0.0.0.0')
