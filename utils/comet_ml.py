from comet_ml import Artifact, Experiment
import comet_ml
import pandas as pd
from Milestone2.feature_engineering import NHLFeatureEngineering


def log_feature_eng_obj(
        DATA_ENGINEERED_OBJ : NHLFeatureEngineering,
) -> int:
    COMET_EXPERIMENT = Experiment(
        project_name=f'feature-engineering-output',
        workspace='nhl-project',
    )

    artifact = Artifact(
        name=f"FeatEng_df_{DATA_ENGINEERED_OBJ.version}__{DATA_ENGINEERED_OBJ.RAW_DATA_PATH.stem}__{DATA_ENGINEERED_OBJ.uniq_id}", 
        artifact_type="FeatEng_df",
        version=str(DATA_ENGINEERED_OBJ.version)+'.0.0',
        aliases=[f"FE_df_{DATA_ENGINEERED_OBJ.version}__{DATA_ENGINEERED_OBJ.RAW_DATA_PATH.stem}__{DATA_ENGINEERED_OBJ.uniq_id}"],
        metadata={
            'local_path' : str(DATA_ENGINEERED_OBJ.path_save_output),
            'source_raw_data_path' : str(DATA_ENGINEERED_OBJ.RAW_DATA_PATH),
            'version' : DATA_ENGINEERED_OBJ.version,
            'uniq_id' : DATA_ENGINEERED_OBJ.uniq_id,
            'sqllite_file_path' : DATA_ENGINEERED_OBJ.sqlite_file
        },
        version_tags=None
    )

    for p in DATA_ENGINEERED_OBJ.path_save_output.glob("*.csv"):
        artifact.add(str(p))

    try:
        COMET_EXPERIMENT.log_artifact(artifact)
        DATA_ENGINEERED_OBJ.logged_to_comet = True
        return 0
    except Exception as e:
        print(f"Error while logging artifact {artifact} : {e}")
        return -1
    
def log_data_splits_to_comet(
        COMET_EXPERIMENT : Experiment,
        X_train : pd.DataFrame,
        y_train : pd.Series,
        X_val : pd.DataFrame,
        y_val : pd.Series,
        X_test : pd.DataFrame,
        y_test : pd.Series,
        title : str,
        logger,
) -> None:

    logger.info(f"Logging train splits to comet")
    COMET_EXPERIMENT.log_dataframe_profile(
        X_train, f"train_set_features__{title}", minimal=True)
    
    COMET_EXPERIMENT.log_dataframe_profile(
        y_train, f"train_set_label__{title}", minimal=True)
    
    logger.info(f"Logging val splits to comet")
    COMET_EXPERIMENT.log_dataframe_profile(
        X_val, f"val_set_features__{title}", minimal=True)
    
    COMET_EXPERIMENT.log_dataframe_profile(
        y_val, f"val_set_label__{title}", minimal=True)
    
    logger.info(f"Logging test splits to comet")
    COMET_EXPERIMENT.log_dataframe_profile(
        X_test, f"test_set_features__{title}", minimal=True)
    
    COMET_EXPERIMENT.log_dataframe_profile(
        y_test, f"test_set_label__{title}", minimal=True)