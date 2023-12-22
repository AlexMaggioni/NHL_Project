import json
import requests
import pandas as pd
import logging


logger = logging.getLogger(__name__)


class ServingClient:
    def __init__(
            self,
            ip: str = "0.0.0.0",
            port: int = 1234,
            features=None,
        ):
        
        self.base_url = f"http://{ip}:{port}"
        logger.info(f"Initializing client; base URL: {self.base_url}")

        if features is None:
            features = ["distanceToGoal", "angleToGoal"]
        self.features = features


    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Formats the inputs into an appropriate payload for a POST request, and queries the
        prediction service. Retrieves the response from the server, and processes it back into a
        dataframe that corresponds index-wise to the input dataframe.
        
        Args:
            X (Dataframe): Input dataframe to submit to the prediction service.
        """

        X_train = X[self.features]

        # standardize the data
        X_train = X_train.apply(lambda x: (x - x.mean()) / x.std(), axis=0)


        r_preds = requests.post(
            f"{self.base_url}/predict",
            json=json.loads(
                X_train.to_json()
            ),
        )
        # import pdb; pdb.set_trace()
        preds = pd.DataFrame(r_preds.json())

        return preds
        

    def logs(self) -> dict:
        """Get server logs"""

        r_logs = requests.get(f"{self.base_url}/logs")

        return r_logs.json()

    def download_registry_model(self, workspace: str, model: str, version: str) -> dict:
        """
        Triggers a "model swap" in the service; the workspace, model, and model version are
        specified and the service looks for this model in the model registry and tries to
        download it. 

        See more here:

            https://www.comet.ml/docs/python-sdk/API/#apidownload_registry_model
        
        Args:
            workspace (str): The Comet ML workspace
            model (str): The model in the Comet ML registry to download
            version (str): The model version to download
        """

        r_changed_model = requests.post(
            f"{self.base_url}/download_registry_model",
            json={
                'workspace' : workspace,
                'model' : model,
                'version' : version,
            },
        )

        return r_changed_model.json()
    
    def get_actual_model(self) -> dict:
        """Get the name of the model currently loaded in the service"""

        r_actual_model = requests.get(f"{self.base_url}/actual_model")

        return r_actual_model.json()