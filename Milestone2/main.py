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

    COMET_EXPERIMENT = Experiment(
        api_key=os.getenv("COMET_API_KEY"),
        project_name=f'{MODEL_CONFIG.model_type}',
        workspace='nhl-project',
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

        for p in data_engineered.path_save_output.glob("*.csv"):
            artifact.add(str(p))

        try:
            COMET_EXPERIMENT.log_artifact(artifact)
        except comet_ml.exceptions.APIError as e:
            logger.warning(f"Error while logging artifact {artifact} : {e}")


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

        # for i, (train_index, test_index) in enumerate(CV_index_generator):
        #     print(f"Fold {i}:")
        X_train = data_preprocessor.X_train.iloc[train_index, :][features_to_include]
        y_train = data_preprocessor.y_train.iloc[train_index]
        X_val = data_preprocessor.X_train.iloc[val_index, :][features_to_include]
        y_val = data_preprocessor.y_train.iloc[val_index]
        X_test = data_preprocessor.X_test[features_to_include]
        y_test = data_preprocessor.y_test

        print(X_train.describe())

        # Log TRAIN/VAL/TEST dataframes to comet_ml
        COMET_EXPERIMENT.log_dataframe_profile(
            X_train, "train_set_features", minimal=False)
        
        COMET_EXPERIMENT.log_dataframe_profile(
            y_train, "train_set_label", minimal=False)

        COMET_EXPERIMENT.log_dataframe_profile(
            X_val, "val_set_features", minimal=False)
        
        COMET_EXPERIMENT.log_dataframe_profile(
            y_val, "val_set_label", minimal=False)
        
        COMET_EXPERIMENT.log_dataframe_profile(
            X_test, "test_set_features", minimal=False)
        
        COMET_EXPERIMENT.log_dataframe_profile(
            y_test, "test_set_label", minimal=False)

        from sklearn.utils.class_weight import compute_sample_weight

        # balancing 'target' class weights
        sample_weights = compute_sample_weight(
            class_weight='balanced',
            y=y_train)

        if MODEL_CONFIG.model_type == "LogisticRegression":
            from sklearn.linear_model import LogisticRegression
            classifier = LogisticRegression(
                penalty=MODEL_CONFIG.penalty,
                C=MODEL_CONFIG.C,
                solver=MODEL_CONFIG.solver,
                verbose=MODEL_CONFIG.verbose,
                class_weight=MODEL_CONFIG.class_weight,
            )

            classifier.fit(X_train, y_train, sample_weights)

        if MODEL_CONFIG.model_type == "XGBoostClassifier":

            import xgboost as xgb
            classifier = xgb.XGBClassifier(
                n_estimators=MODEL_CONFIG.n_estimators,
                max_depth=MODEL_CONFIG.max_depth,
                max_leaves=MODEL_CONFIG.max_leaves,
                objective="multi:softmax",
                num_class=len(DATA_PIPELINE_CONFIG.label),
                reg_lambda=MODEL_CONFIG.reg_lambda,
                learning_rate=MODEL_CONFIG.learning_rate,
                min_child_weight = MODEL_CONFIG.min_child_weight,
                subsample = MODEL_CONFIG.subsample,
                colsample_bytree = MODEL_CONFIG.colsample_bytree,
                eval_metric=['merror','mlogloss'],
                seed=DATA_PIPELINE_CONFIG.seed,
            )

            classifier.fit(
                X_train, 
                y_train,
                verbose=0, # set to 1 to see xgb training round intermediate results
                sample_weight=sample_weights,
                eval_set=[(X_train, y_train), (X_val, y_val)],
            )

            # preparing evaluation metric plots
            results = classifier.evals_result()
        
        import pdb; pdb.set_trace()
        
        # evaluate accuracy on val set
        y_val_pred = classifier.predict(X_val)

        val_proba_preds = classifier.predict_proba(X_val)

        print('\n------------------ Confusion Matrix -----------------\n')
        cf_matrix_array = confusion_matrix(y_val, y_val_pred)
        print(f'Confusion Matrix | {MODEL_TYPE} on {"+".join(features_to_include)}')
        print(cf_matrix_array)

        print(f'\n--------------- Classification Report  | {MODEL_TYPE} on {"+".join(features_to_include)}  ---------------\n')
        print(classification_report(y_val, y_val_pred))

        from utils.misc import assess_classifier_perf

        # DONT MODIFY NAME OF THE KEYS IN THIS DICT ---> hard-coded IN OTHER FILES
        stats['+'.join(features_to_include)] = {
            'model': classifier,
            'val':{
                'data' : (X_val, y_val),
                'proba_preds' : val_proba_preds,
                'preds' : y_val_pred,
                'performance' : assess_classifier_perf(y_val, y_val_pred)
            },
            'test':{
                'data' : (X_test, y_test),
                'proba_preds' : classifier.predict_proba(X_test),
                'preds' : classifier.predict(X_test),
                'performance' : assess_classifier_perf(y_test, classifier.predict(X_test))
            }
        }
        if MODEL_CONFIG.model_type == "XGBoostClassifier":
            stats['+'.join(features_to_include)]['val']['results'] = results

    # _______________________ Training and Validation finished

    # Saving stats to disk and logging to comet_ml
    import pickle
    pickle.dump(stats, open(OUTPUT_DIR / "stats_training.pkl", "wb"))
    COMET_EXPERIMENT.log_asset(str(OUTPUT_DIR / "stats_training.pkl"), "stats_training_with_model.pkl")

    # PLOTTING GRAPHS : LOSSES, ROC, RATIO-GOAL, CUMUL-GOAL, CALIBRATION CURVES

    OUTPUT_DIR = OUTPUT_DIR / 'val'
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    PATH_GRAPHS = []

    if MODEL_CONFIG.model_type == "XGBoostClassifier":
        from utils.plot import plot_xgboost_losses
        for k, results in stats.items():
            PATH_GRAPHS.append(plot_xgboost_losses(results['val']['results'], OUTPUT_DIR, k))
    
    from utils.plot import plotPerfModel
    PATH_GRAPHS = plotPerfModel(
        predictionsTest = {
            f'{MODEL_TYPE} trained on {k}' : d['val']['proba_preds'] for k,d in stats.items()
        },
        yTest = y_val,
        outputDir = OUTPUT_DIR,
        rocCurve = True,
        ratioGoalPercentileCurve = True,
        proportionGoalPercentileCurve = True,
        calibrationCurve = True,
    )

    for p in PATH_GRAPHS:
        try:
            COMET_EXPERIMENT.log_asset(str(p), p.stem)
        except comet_ml.exceptions.APIError as e:
            logger.warning(f"Error while logging artifact {p} : {e}")

if __name__ == "__main__":
    logger = init_logger("milestone2_main.log")
    run_experiment()
