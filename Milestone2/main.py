import comet_ml
import datetime
import hydra
import os
from pathlib import Path
from matplotlib import pyplot as plt
from omegaconf import DictConfig
import pandas as pd
from rich import print
from sklearn.metrics import accuracy_score
from comet_ml import Artifact, Experiment

from data_preprocessing import NHL_data_preprocessor
from feature_engineering import NHLFeatureEngineering
from utils.comet_ml import init_experiment
from utils.misc import init_logger, verify_dotenv_file

verify_dotenv_file(Path(__file__).parent.parent)


@hydra.main(
    version_base=None, config_path=os.getenv("YAML_CONF_DIR"), config_name="main_config"
)
def run_experiment(cfg: DictConfig) -> None:
    global logger
    MODEL_CONFIG = cfg.model
    DATA_PIPELINE_CONFIG = cfg.data_pipeline
    print(dict(cfg))

    COMET_EXPERIMENT = init_experiment(
        project_name=cfg.comet_ml.project_name,
        workspace=cfg.comet_ml.workspace,
        display_summary_level=cfg.comet_ml.display_summary_level,
    )

    # =================================Prepare/Engineer Data==========================================================
    

    if cfg.load_engineered_data_from:
        logger.info(f" SKIPPING FEATURE ENGINEERING COMPUTATION : Loading feature-engineered data from {cfg.load_engineered_data_from}")
        df_processed = pd.read_csv(Path(os.getenv("DATA_FOLDER"))/ cfg.raw_train_data_path)

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

        # for p in data_engineered.path_save_output.glob("*.csv"):
        #     artifact.add(str(p))

        # try:
        #     COMET_EXPERIMENT.log_artifact(artifact)
        # except comet_ml.exceptions.APIError as e:
        #     logger.warning(f"Error while logging artifact {artifact} : {e}")


    # =================================Preprocess Data==========================================================
    mask_criteria = df_processed["season"] == 2020
    TRAIN_DF = df_processed[~mask_criteria]
    TEST_DF = df_processed[mask_criteria]
    
    data_preprocessor = NHL_data_preprocessor(
        df_train = TRAIN_DF,
        df_test = TEST_DF,
        cross_validation_k_fold = DATA_PIPELINE_CONFIG.K_Fold,
        shuffle_before_splitting = DATA_PIPELINE_CONFIG.shuffle_before_splitting,
        seed = DATA_PIPELINE_CONFIG.seed,
        label = DATA_PIPELINE_CONFIG.label,
    )
    
    CV_index_generator  = data_preprocessor._split_data()

    # =================================Train Model==========================================================

    MODEL_TYPE = MODEL_CONFIG.model_type

    now_date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    OUTPUT_DIR = (
        Path(os.getenv("TRAINING_ARTIFACTS_PATH"))
        / MODEL_TYPE 
        / now_date
    )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    stats = {}

    train_index, val_index = CV_index_generator.__next__()
    for features_to_include in [["distanceToGoal"], ["angleToGoal"], ["distanceToGoal", "angleToGoal"]]:
        logger.info(f"Training model {MODEL_CONFIG.model_type} with features : {features_to_include}")

        if MODEL_CONFIG.model_type == "logistic_regression":
            from sklearn.linear_model import LogisticRegression
            classifier = LogisticRegression(
                penalty=MODEL_CONFIG.penalty,
                C=MODEL_CONFIG.C,
                solver=MODEL_CONFIG.solver,
            )
        if MODEL_CONFIG.model_type == "xgboost":
            pass
        
        # for i, (train_index, test_index) in enumerate(CV_index_generator):
        #     print(f"Fold {i}:")
        X_train = data_preprocessor.X_train.iloc[train_index, :][features_to_include]
        y_train = data_preprocessor.y_train.iloc[train_index]
        X_val = data_preprocessor.X_train.iloc[val_index, :][features_to_include]
        y_val = data_preprocessor.y_train.iloc[val_index]
        X_test = data_preprocessor.X_test[features_to_include]
        y_test = data_preprocessor.y_test

        print(X_train.describe())
        import pdb; pdb.set_trace()
        classifier.fit(X_train, y_train)
        # evaluate accuracy on val set
        y_val_pred = classifier.predict(X_val)
        val_accuracy = accuracy_score(y_val, y_val_pred)
        logger.info(f"Accuracy on val set : {val_accuracy}")

        val_proba_preds = classifier.predict_proba(X_val)

        # DONT ;ODIFY NAME OF THE KEYS IN THIS DICT ---> hard-coded IN OTHER FILES
        stats['+'.join(features_to_include)] = {
            'model': classifier,
            'val':{
                'data' : X_val,
                'accuracy' : val_accuracy,
                'proba_preds' : val_proba_preds,
                'preds' : y_val_pred 
            },
            'test':{
                'accuracy' : accuracy_score(y_test, classifier.predict(X_test)),
                'proba_preds' : classifier.predict_proba(X_test),
                'preds' : classifier.predict(X_test),
            }
        }
    # _______________________ Training and evaluation finished

    import pickle
    pickle.dump(stats, open(OUTPUT_DIR / "stats_training.pkl", "wb"))

    # _______________________ PLOTTING GRAPHS : ROC, RATIO-GOAL, CUMUL-GOAL, CALIBRATION CURVES

    OUTPUT_DIR = OUTPUT_DIR / 'val'
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    from utils.plot import plot_perf_model
    plot_perf_model(
        ROC_curve = True,
        ratio_goal_percentile_curve = True,
        proportion_goal_percentile_curve = True,
        calibration_curve = True,
        stats = stats,
        split = 'val',
        y_true = y_val,
        OUTPUT_DIR = OUTPUT_DIR,
        model_type = MODEL_CONFIG.model_type,
    )


if __name__ == "__main__":
    logger = init_logger("milestone2_main.log")
    run_experiment()
