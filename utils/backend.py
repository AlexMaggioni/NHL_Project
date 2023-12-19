import comet_ml
from comet_ml.exceptions import CometRestApiValueError

class CometMLClient:
    def __init__(self, workspace, project_name = None):
        self.workspace = workspace
        self.project_name = project_name
        self.comet_api = comet_ml.api.API()

    def get_model_versions(self, model_name):
        """
        Returns a list of all the versions of a given model
        """
        project = self.comet_api.get(self.workspace + "/" + self.project_name)
        model = project.get_model(model_name)
        return model.get_versions()
    
    def get_model_list(self):
        """
        Returns a list of all the models in a given project
        """
        return self.comet_api.get_registry_model_names(self.workspace)

    def download_model(self, model_name, version, destination_path):
        """
        Downloads a given model version to a given destination path
        """
        try:
            self.comet_api.download_registry_model(
                self.workspace,
                model_name,
                version,
                output_path=destination_path,
            )

            model_fn = self.comet_api.get_registry_model_details(self.workspace, model_name, version)['assets'][0]['fileName']

            return True, (destination_path / model_fn)
        except CometRestApiValueError as e:
            print(e)
            return False, None