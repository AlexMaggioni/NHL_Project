import time
import comet_ml
import datetime
import hydra
import os
from pathlib import Path
from matplotlib import pyplot as plt
from omegaconf import DictConfig
import pandas as pd
from rich import print
from sklearn.metrics import (
            confusion_matrix,
            classification_report,
            )
from sklearn.metrics import (
            balanced_accuracy_score,
            accuracy_score,
            precision_score,
            recall_score,
            f1_score,
            )
from comet_ml import Artifact, Experiment
import ydata_profiling

from data_preprocessing import NHL_data_preprocessor
from feature_engineering import NHLFeatureEngineering
from utils.misc import init_logger, verify_dotenv_file

verify_dotenv_file(Path(__file__).parent.parent)


@hydra.main(
    version_base=None, config_path=os.getenv("YAML_CONF_DIR"), config_name="main_config"
)
def run_hp_optimization_search(cfg: DictConfig) -> None:
    global logger
    MODEL_CONFIG = cfg.model
    DATA_PIPELINE_CONFIG = cfg.data_pipeline
    print(dict(cfg))

    COMET_EXPERIMENT = Experiment(
        api_key=os.getenv("COMET_API_KEY"),
        project_name=f'{MODEL_CONFIG.model_type}',
        workspace='nhl-project',
    )

    COMET_EXPERIMENT.log_parameters(dict(cfg), prefix='HYDRA_')

    # =================================Prepare/Engineer Data==========================================================
    

    if cfg.load_engineered_data_from:
        logger.info(f" SKIPPING FEATURE ENGINEERING COMPUTATION : Loading feature-engineered data from {cfg.load_engineered_data_from}")
        df_processed = pd.read_csv(Path(os.getenv("DATA_FOLDER"))/ cfg.load_engineered_data_from)

    else:
        logger.info(f"Starting the data Feature-engineering")
        
        RAW_DATA_PATH = Path(os.getenv("DATA_FOLDER"))/ cfg.raw_train_data_path
        
        data_engineered = NHLFeatureEngineering(
            RAW_DATA_PATH = RAW_DATA_PATH ,
            distanceToGoal= DATA_PIPELINE_CONFIG.distanceToGoal,
            angleToGoal= DATA_PIPELINE_CONFIG.angleToGoal,
            isGoal= DATA_PIPELINE_CONFIG.isGoal,
            emptyNet= DATA_PIPELINE_CONFIG.emptyNet,
            verbose= DATA_PIPELINE_CONFIG.verbose,
            imputeRinkSide= DATA_PIPELINE_CONFIG.imputeRinkSide,
            periodTimeSeconds= DATA_PIPELINE_CONFIG.periodTimeSeconds,
            lastEvent= DATA_PIPELINE_CONFIG.lastEvent,
            lastCoordinates= DATA_PIPELINE_CONFIG.lastCoordinates,
            timeElapsed= DATA_PIPELINE_CONFIG.timeElapsed,
            distanceFromLastEvent= DATA_PIPELINE_CONFIG.distanceFromLastEvent,
            rebound= DATA_PIPELINE_CONFIG.rebound,
            changeAngle= DATA_PIPELINE_CONFIG.changeAngle,
            speed= DATA_PIPELINE_CONFIG.speed,
            computePowerPlayFeatures= DATA_PIPELINE_CONFIG.computePowerPlayFeatures,
            version= cfg.feature_engineering_version,
        )

        df_processed = data_engineered.dfUnify
        
        artifact = Artifact(
            name=f"FeatEng_df_{data_engineered.version}__{data_engineered.RAW_DATA_PATH.stem}__{data_engineered.uniq_id}", 
            artifact_type="FeatEng_df",
            version=str(data_engineered.version)+'.0.0',
            aliases=[f"FE_df_{data_engineered.version}__{data_engineered.RAW_DATA_PATH.stem}__{data_engineered.uniq_id}"],
            metadata={
                'local_path' : str(data_engineered.path_save_output),
                'source_raw_data_path' : str(data_engineered.RAW_DATA_PATH),
                'version' : data_engineered.version,
                'uniq_id' : data_engineered.uniq_id,
                'sqllite_file_path' : data_engineered.sqlite_file
            },
            version_tags=None
        )

        for p in data_engineered.path_save_output.glob("*.csv"):
            artifact.add(str(p))

        try:
            COMET_EXPERIMENT.log_artifact(artifact)
        except comet_ml.exceptions.APIError as e:
            logger.warning(f"Error while logging artifact {artifact} : {e}")


    # =================================Preprocess Data==========================================================
    mask_criteria = df_processed["season"] == 2020
    TRAIN_DF = df_processed[~mask_criteria].sample(frac=0.5, random_state=DATA_PIPELINE_CONFIG.seed)
    TEST_DF = df_processed[mask_criteria].sample(frac=0.5, random_state=DATA_PIPELINE_CONFIG.seed)
    
    data_preprocessor = NHL_data_preprocessor(
        df_train = TRAIN_DF,
        df_test = TEST_DF,
        cross_validation_k_fold = DATA_PIPELINE_CONFIG.K_Fold,
        shuffle_before_splitting = DATA_PIPELINE_CONFIG.shuffle_before_splitting,
        seed = DATA_PIPELINE_CONFIG.seed,
        label = DATA_PIPELINE_CONFIG.label,
    )
    
    CV_index_generator  = data_preprocessor._split_data()


if __name__ == "__main__":
    logger = init_logger("training_main.log")
    run_hp_optimization_search()