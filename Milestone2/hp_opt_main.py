import time
import comet_ml
import datetime
import hydra
import os
from pathlib import Path
import loguru
from matplotlib import pyplot as plt
from omegaconf import DictConfig, OmegaConf
import pandas as pd
from rich import print
from comet_ml import Artifact, Experiment
from sklearn.metrics import roc_auc_score
from utils.comet_ml import log_data_splits_to_comet
from utils.metrics import assess_classifier_perf

from utils.misc import init_logger, verify_dotenv_file
from utils.model import train_classifier_model

verify_dotenv_file(Path(__file__).parent.parent)


def run_hp_optimization_search(cfg: DictConfig, logger) -> None:

    MODEL_CONFIG = cfg.model
    DATA_PIPELINE_CONFIG = cfg.data_pipeline

    print(dict(cfg))

    COMET_EXPERIMENT = Experiment(
        project_name=f'{MODEL_CONFIG.model_type}_hp_opt',
        workspace='nhl-project',
    )
    MODEL_TYPE = MODEL_CONFIG.model_type

    now_date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    OUTPUT_DIR = (
        Path(os.getenv("TRAINING_ARTIFACTS_PATH"))
        / f'hyp_opt_{MODEL_TYPE}'
        / now_date
    )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


    COMET_EXPERIMENT.log_parameters(dict(cfg), prefix='HYDRA_')

    # =================================Prepare Data==========================================================
    
    PATH_RAW_CSV = Path(os.getenv("DATA_FOLDER"))/ cfg.data_pipeline.raw_train_data_path
    FEATURE_ENG_VERSION = cfg.data_pipeline.feature_engineering_version
    TRAIN_TEST_SPLIT_CONDITION = cfg.data_pipeline.predicate_train_test_split
    LOAD_FROM_EXISTING_FEATURE_ENG_DATA = cfg.data_pipeline.load_engineered_data_from

    from utils.data import init_data_for_isgoal_classification_experiment

    DATA_PREPROCESSOR_OBJ, DATA_FEATURE_ENG_OBJ = init_data_for_isgoal_classification_experiment(
        RAW_DATA_PATH = PATH_RAW_CSV,
        DATA_PIPELINE_CONFIG = DATA_PIPELINE_CONFIG,
        version = FEATURE_ENG_VERSION,
        comet_experiment_object = COMET_EXPERIMENT,
        TRAIN_TEST_PREDICATE_SPLITTING = TRAIN_TEST_SPLIT_CONDITION,
        load_engineered_data_from = LOAD_FROM_EXISTING_FEATURE_ENG_DATA,
        logger = logger,
    )


    # =================================Task-Specific (Classification Prob goal) data pre-proc=================================
    # ================== eventType only SHOT | GOAL
    logger.info('SUBSETTING data TO SHOT | GOAL eventType')
    idx_train = DATA_PREPROCESSOR_OBJ.X_train.query("eventType == 'SHOT' | eventType == 'GOAL'").index
    idx_test = DATA_PREPROCESSOR_OBJ.X_test.query("eventType == 'SHOT' | eventType == 'GOAL'").index
    
    logger.info(f"\t Before subsetting : {DATA_PREPROCESSOR_OBJ.X_train.shape} rows in train set")
    DATA_PREPROCESSOR_OBJ.X_train = DATA_PREPROCESSOR_OBJ.X_train[DATA_PREPROCESSOR_OBJ.X_train.index.isin(idx_train)]
    DATA_PREPROCESSOR_OBJ.y_train = DATA_PREPROCESSOR_OBJ.y_train[DATA_PREPROCESSOR_OBJ.y_train.index.isin(idx_train)]
    logger.info(f"\t After subsetting : {DATA_PREPROCESSOR_OBJ.X_train.shape} rows in train set")
    
    logger.info(f"\t Before subsetting : {DATA_PREPROCESSOR_OBJ.X_test.shape} rows in test set")
    DATA_PREPROCESSOR_OBJ.X_test = DATA_PREPROCESSOR_OBJ.X_test[DATA_PREPROCESSOR_OBJ.X_test.index.isin(idx_test)]
    DATA_PREPROCESSOR_OBJ.y_test = DATA_PREPROCESSOR_OBJ.y_test[DATA_PREPROCESSOR_OBJ.y_test.index.isin(idx_test)]
    logger.info(f"\t After subsetting : {DATA_PREPROCESSOR_OBJ.X_test.shape} rows in test set")

    
    CV_index_generator  = DATA_PREPROCESSOR_OBJ._split_data()

    train_index, val_index = CV_index_generator.__next__()
    X_train = DATA_PREPROCESSOR_OBJ.X_train.iloc[train_index, :]
    y_train = DATA_PREPROCESSOR_OBJ.y_train.iloc[train_index]
    X_val = DATA_PREPROCESSOR_OBJ.X_train.iloc[val_index, :]
    y_val = DATA_PREPROCESSOR_OBJ.y_train.iloc[val_index]
    X_test = DATA_PREPROCESSOR_OBJ.X_test
    y_test = DATA_PREPROCESSOR_OBJ.y_test

    # =================================Optimizer Run==========================================================
    OPTIMIZER_CONF = cfg.hp_optimizer

    opt = comet_ml.Optimizer(
        OmegaConf.to_object(OPTIMIZER_CONF),
    )

    # we track the best model
    BEST_MODEL = {
        'path' : None,
        'score' : 0
    }
    
    for i, experiment in enumerate(opt.get_experiments()):
        
        experiment.set_name(f'{now_date}_{MODEL_CONFIG.model_type}__{i}')

        MERGED_DICT = OmegaConf.merge(
            OmegaConf.create(MODEL_CONFIG),
            OmegaConf.create(experiment.params),
        )

        TRAINED_CLASSIFIER, training_duration = train_classifier_model(
            X_train = X_train,
            y_train = y_train,
            X_val = X_val,
            y_val = y_val,
            DATA_PIPELINE_CONFIG = DATA_PIPELINE_CONFIG,
            MODEL_CONFIG = MERGED_DICT,
            logger = logger,
        )

        logger.info(f"Training duration : {training_duration}")

        VAL_METRICS = assess_classifier_perf(
            y=y_val,
            y_pred=TRAINED_CLASSIFIER.predict(X_val),
            title_model=f'{MODEL_CONFIG.model_type}',
        )

        SCORE = roc_auc_score(y_val, TRAINED_CLASSIFIER.predict_proba(X_val)[:, 1])
        if SCORE > BEST_MODEL['score']:
            logger.info(f"New best model found with score : {SCORE} saved at {OUTPUT_DIR / f'{now_date}_{MODEL_CONFIG.model_type}__{i}'}")
            BEST_MODEL['score'] = SCORE
            BEST_MODEL['path'] = OUTPUT_DIR / f'{now_date}_{MODEL_CONFIG.model_type}__{i}.pkl'

            #save model locally
            TRAINED_CLASSIFIER.save_model(BEST_MODEL['path'])

            experiment.log_model(
                model_name=f'{MODEL_CONFIG.model_type}',
                model=TRAINED_CLASSIFIER,
                overwrite=True,
            )

        experiment.log_metrics(VAL_METRICS, prefix='val_')
        experiment.log_metric('val_roc_auc_score', SCORE)
        
        # Optionally, end the experiment:
        experiment.end()

@hydra.main(
    version_base=None, config_path=os.getenv("YAML_CONF_DIR"), config_name="hp_opt_main_conf"
)
def main(cfg : DictConfig) -> None:
    logger = init_logger("run_hp_optimization_search.log")
    run_hp_optimization_search(cfg, logger)

if __name__ == "__main__":
    main()
