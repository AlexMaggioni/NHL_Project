"""
If you are in the same directory as this file (app.py), you can run run the app using gunicorn:
    
    $ gunicorn --bind 0.0.0.0:<PORT> app:app

gunicorn can be installed via:

    $ pip install gunicorn

"""
from datetime import timedelta
import os
from pathlib import Path
import logging
import comet_ml
from flask import Flask, jsonify, request
import sklearn
import pandas as pd
import joblib, random
import numpy as np

from utils.backend import CometMLClient

LOG_FILE = os.environ.get("FLASK_LOG", Path(__name__).parent / "backend_logs")
ROOT_LOCAL_MODEL_PATH = os.environ.get("LOCAL_MODEL_PATH", Path(__name__).parent / "downloaded_models")
ACTUAL_MODEL_PATH = None

app = Flask(__name__)


def init_logger():
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

def download_default_model():
    DEFAULT_MODEL = Path('nhl-project/baseline_logisticregression_angletogoal/1.0.0')

    downloading_succeeded, filename_model = CometMLClient(workspace=DEFAULT_MODEL.parts[0]).download_model(
        DEFAULT_MODEL.parts[1], 
        DEFAULT_MODEL.parts[2], 
        ROOT_LOCAL_MODEL_PATH / DEFAULT_MODEL
    )

    global ACTUAL_MODEL_PATH
    ACTUAL_MODEL_PATH = str(filename_model)
    app.logger.info(f"Initializing app with default model {ACTUAL_MODEL_PATH}, downloading_succeeded={downloading_succeeded}")

@app.before_request
def before_first_request():
    """
    Hook to handle any initialization before the first request (e.g. load model,
    setup logging handler, etc.)
    """
    global ACTUAL_MODEL_PATH
    if ACTUAL_MODEL_PATH is None:
        # logging to multiple destinations ; file and stdout
        init_logger()

        app.logger.info("New Session detected")
        app.logger.info("Downloading default model")
        
        download_default_model()

    else:
        app.logger.info("Model name already in session")
        if not os.path.exists(LOG_FILE):
            init_logger()
            app.logger.info("Existing session detected")
            app.logger.info(ACTUAL_MODEL_PATH)
        else:
            app.logger.info("LOG FILE already exists")


@app.route("/logs", methods=["GET"])
def logs():
    """Reads data from the log file and returns them as the response"""
    
    with open(LOG_FILE, "r") as f:
        logs = f.readlines()
    response = logs
    return jsonify(response)  # response must be json serializable!


@app.route("/download_registry_model", methods=["POST"])
def download_registry_model():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/download_registry_model

    The comet API key should be retrieved from the ${COMET_API_KEY} environment variable.

    Recommend (but not required) json with the schema:

        {
            workspace: (required),
            model: (required),
            version: (required),
            ... (other fields if needed) ...
        }
    
    """
    global ACTUAL_MODEL_PATH
    # Get POST json data
    json = request.get_json()

    response = {
        "model_name": ACTUAL_MODEL_PATH,
    }

    local_model_path = Path(ROOT_LOCAL_MODEL_PATH) / json['workspace'] / json['model'] / json['version']
    model_name = " - ".join(local_model_path.parts[-3:])

    # TODO: check to see if the model you are querying for is already downloaded
    already_downloaded = local_model_path.exists()
    response['already_downloaded'] = already_downloaded

    # TODO: if yes, load that model and write to the log about the model change.  
    if already_downloaded:
        app.logger.info(f'Model : {model_name} already downloaded.')
        if ACTUAL_MODEL_PATH != str(local_model_path):
            app.logger.info(f'Loading model : {model_name}.')
            ACTUAL_MODEL_PATH = str(list(local_model_path.glob('*'))[0])
            response['changed_model'] = True
        else:
            app.logger.info(f'Model : {model_name} already loaded DOING NOTHING.')
            response['changed_model'] = False

    # TODO: if no, try downloading the model: if it succeeds, load that model and write to the log
    # about the model change. If it fails, write to the log about the failure and keep the 
    # currently loaded model
    else:
        app.logger.info(f'Model : {model_name} not downloaded. Downloading it.')

        downloading_succeeded, filename_model = CometMLClient(
            workspace=json['workspace']
        ).download_model(
            json['model'], json['version'], local_model_path
        )

        response['downloading_succeeded'] = downloading_succeeded

        if downloading_succeeded:
            app.logger.info(f'Model : {model_name} downloaded. Loading it.')
            ACTUAL_MODEL_PATH = str(filename_model)
            response['changed_model'] = True
        else:
            app.logger.info(f'Failed to download model : {model_name}. Keeping current model.')
            response['changed_model'] = False

    response['model_name'] = ACTUAL_MODEL_PATH

    app.logger.info(f'in /download_registry_model {response =}')
    return jsonify(response)  # response must be json serializable!


@app.route("/predict", methods=["POST"])
def predict():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/predict

    Returns predictions
    """
    global ACTUAL_MODEL_PATH
    # Get POST json data
    json_data = request.get_json()
    app.logger.info(json_data)
    
    model = joblib.load(ACTUAL_MODEL_PATH)
    data = pd.DataFrame(json_data)

    app.logger.info(f'Predicting on {len(data)} samples, with {data.columns} features')

    prob_preds = model.predict_proba(data)
    preds = model.predict(data)

    response = {
        "predictions": preds.tolist(),
        "probabilities": prob_preds.tolist(),
    }

    app.logger.info(response)
    return jsonify(response)  # response must be json serializable!
