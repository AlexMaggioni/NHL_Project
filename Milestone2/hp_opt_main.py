import sys
import os
from pathlib import Path

# Add the parent directory to sys.path to enable importing from there
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

import pickle
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
from utils.trainer import train_and_eval

verify_dotenv_file(Path(__file__).parent.parent)


def run_hp_optimization_search(cfg: DictConfig, logger) -> None:

    MODEL_CONFIG = cfg.model
    DATA_PIPELINE_CONFIG = cfg.data_pipeline

    print(dict(cfg))

    OPTIMIZER_CONF = cfg.hp_optimizer
        
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

    logger.info("DROPPING eventType column")
    DATA_PREPROCESSOR_OBJ.X_train = DATA_PREPROCESSOR_OBJ.X_train.drop(columns=['eventType'])
    DATA_PREPROCESSOR_OBJ.X_test = DATA_PREPROCESSOR_OBJ.X_test.drop(columns=['eventType'])

    # =================================COMET ML Optimizer Run==========================================================

    MODEL_TYPE = MODEL_CONFIG.model_type

    PROJECT_NAME = f'hp_opt_{MODEL_TYPE}' \
        + ('_CV' if cfg.USE_CROSS_VALIDATION else '') \
        
    now_date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    OUTPUT_DIR = (
        Path(os.getenv("TRAINING_ARTIFACTS_PATH"))
        / PROJECT_NAME
        / now_date
    )
    (OUTPUT_DIR / 'val').mkdir(parents=True, exist_ok=True)

    opt = comet_ml.Optimizer(
        OmegaConf.to_object(OPTIMIZER_CONF),
    )

    # we track the best model
    BEST_MODEL = {
        'path' : None,
        'score' : 0,
        'best_params' : None,
        'data': None,
    }
    CV_index_generator  = DATA_PREPROCESSOR_OBJ._split_data()
    # import pdb; pdb.set_trace()
    for i_hp, experiment in enumerate(opt.get_experiments(project_name=PROJECT_NAME)):
        experiment.log_parameters(dict(cfg), prefix='HYDRA_')
        experiment.set_name(f'{now_date}_{MODEL_CONFIG.model_type}__{i_hp}')

        MERGED_DICT_MODEL_PARAMS = OmegaConf.merge(
            OmegaConf.create(MODEL_CONFIG),
            OmegaConf.create(experiment.params),
        )

        if MODEL_CONFIG.model_type == "MLPClassifier":
        
            hidden_layer_sizes = [
                MERGED_DICT_MODEL_PARAMS.layer1_size,
                MERGED_DICT_MODEL_PARAMS.layer2_size,
                MERGED_DICT_MODEL_PARAMS.layer3_size,
                MERGED_DICT_MODEL_PARAMS.layer4_size,
            ]

            hidden_layer_sizes = hidden_layer_sizes[: MERGED_DICT_MODEL_PARAMS.n_layer]

            MERGED_DICT_MODEL_PARAMS.hidden_layer_sizes = hidden_layer_sizes

        if cfg.USE_CROSS_VALIDATION: 
            GENERATOR_IDX = CV_index_generator
        else:
            CV_index_generator  = DATA_PREPROCESSOR_OBJ._split_data()
            GENERATOR_IDX = [CV_index_generator.__next__()]
        for i_cv, (train_index, val_index) in enumerate(GENERATOR_IDX):
            print(f"Cross-Valisation Fold {i_cv}:")

            X_train = DATA_PREPROCESSOR_OBJ.X_train.iloc[train_index,:]
            y_train = DATA_PREPROCESSOR_OBJ.y_train.iloc[train_index,:]
            X_val = DATA_PREPROCESSOR_OBJ.X_train.iloc[val_index,:]
            y_val = DATA_PREPROCESSOR_OBJ.y_train.iloc[val_index,:]

            MODEL_KEY = f'{MODEL_CONFIG.model_type}__hp_{i_hp}_cv_{i_cv}'

            RES_EXP = train_and_eval(
                X_train = X_train,
                y_train = y_train,
                X_val = X_val,
                y_val = y_val,
                logger = logger,
                COMET_EXPERIMENT = experiment,
                title = MODEL_KEY,
                DATA_PIPELINE_CONFIG = DATA_PIPELINE_CONFIG,
                MODEL_CONFIG = MERGED_DICT_MODEL_PARAMS,
                OUTPUT_DIR = OUTPUT_DIR,
                X_test = None ,
                y_test = None ,
                USE_SAMPLE_WEIGHTS=cfg.USE_SAMPLE_WEIGHTS,
                log_data_splits  = False,
                log_model_to_comet  = False,
            )

            SCORE = roc_auc_score(y_val, RES_EXP[MODEL_KEY]['val']['proba_preds'][:,1])

            if SCORE > BEST_MODEL['score']:
                OUTPUT_PATH_BEST_MODEL = OUTPUT_DIR / f'{now_date}_{MODEL_CONFIG.model_type}__hp_{i_hp}_cv_{i_cv}_{SCORE}.pkl'
                logger.info(f"New best model found with score : {SCORE} saved at {OUTPUT_PATH_BEST_MODEL} and pushed to COMET")
                BEST_MODEL['score'] = SCORE
                BEST_MODEL['path'] = OUTPUT_PATH_BEST_MODEL
                BEST_MODEL['data'] = {'train':(X_train,y_train)}

                OUTPUT_DICT = BEST_MODEL.update(RES_EXP)

                with open(OUTPUT_PATH_BEST_MODEL, "wb") as f:
                    pickle.dump(OUTPUT_DICT, f)
                experiment.log_asset(str(OUTPUT_PATH_BEST_MODEL), OUTPUT_PATH_BEST_MODEL.name)

        experiment.log_metric('val_roc_auc_score', SCORE)

        # Optionally, end the experiment:
        experiment.end()

    #TODO: log best model to comet avec le nom de lexp comme BEST
    print('Best model found :')
    print(OUTPUT_DICT)

@hydra.main(
    version_base=None, config_path=os.getenv("YAML_CONF_DIR"), config_name="hp_opt_main_conf"
)
def main(cfg : DictConfig) -> None:
    logger = init_logger("run_hp_optimization_search.log")
    run_hp_optimization_search(cfg, logger)

if __name__ == "__main__":
    main()
