import os
from comet_ml import Experiment

def init_experiment(
        project_name : str, 
        workspace : str,
        display_summary_level : int,
    ) -> Experiment:
    
    return Experiment(
        api_key=os.getenv("COMET_API_KEY"),
        project_name=project_name,
        workspace=workspace,
    )
