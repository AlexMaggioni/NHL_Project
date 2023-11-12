from typing import Generator, Tuple
import os
from pathlib import Path
from omegaconf import DictConfig
import pandas as pd
from rich import print

from comet_ml import Artifact, Experiment

from Milestone2.data_preprocessing import NHL_data_preprocessor
from Milestone2.feature_engineering import NHLFeatureEngineering
from utils.comet_ml import log_feature_eng_obj

def create_engineered_data_object(
        RAW_DATA_PATH : Path,
        DATA_PIPELINE_CONFIG : DictConfig,
        version : str,
) -> NHLFeatureEngineering:
    
    GOAL_POSITION = [DATA_PIPELINE_CONFIG.GOAL_POSITION.x, DATA_PIPELINE_CONFIG.GOAL_POSITION.y]
    
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
                version= version,
                GOAL_POSITION=GOAL_POSITION
            )
    return data_engineered

def create_preprocessor_data_object(
        TRAIN_DF : pd.DataFrame,
        TEST_DF : pd.DataFrame,
        DATA_PIPELINE_CONFIG : DictConfig,
    ) -> NHL_data_preprocessor:

    data_preprocessor = NHL_data_preprocessor(
        df_train = TRAIN_DF,
        df_test = TEST_DF,
        cross_validation_k_fold = DATA_PIPELINE_CONFIG.K_Fold,
        shuffle_before_splitting = DATA_PIPELINE_CONFIG.shuffle_before_splitting,
        seed = DATA_PIPELINE_CONFIG.seed,
        label = DATA_PIPELINE_CONFIG.label,
    )
    
    return data_preprocessor

def init_data_for_experiment(
        RAW_DATA_PATH : Path,
        DATA_PIPELINE_CONFIG : DictConfig,
        version : str,
        comet_experiment_object : Experiment,
        TRAIN_TEST_PREDICATE_SPLITTING : str,
        load_engineered_data_from : str,
        logger,
) -> Tuple[NHL_data_preprocessor, NHLFeatureEngineering]:
    

    if load_engineered_data_from:
        PATH_RESUME_DATA_ENGINEERED = Path(os.getenv("DATA_FOLDER"))/ load_engineered_data_from
        logger.info(f" SKIPPING FEATURE ENGINEERING COMPUTATION : Loading feature-engineered data from {PATH_RESUME_DATA_ENGINEERED}")
        df_processed = pd.read_csv(PATH_RESUME_DATA_ENGINEERED)
        DATA_ENGINEERED_OBJ = PATH_RESUME_DATA_ENGINEERED
    
    else : 
        DATA_ENGINEERED_OBJ = create_engineered_data_object(
            RAW_DATA_PATH = RAW_DATA_PATH,
            DATA_PIPELINE_CONFIG = DATA_PIPELINE_CONFIG,
            version = version,
            comet_experiment_object = comet_experiment_object,
        )
        
        log_feature_eng_obj(
            COMET_EXPERIMENT = comet_experiment_object,
            DATA_ENGINEERED_OBJ = DATA_ENGINEERED_OBJ,
        )

        df_processed = DATA_ENGINEERED_OBJ.dfUnify

    TEST_DF, TRAIN_DF = train_test_splitting(TRAIN_TEST_PREDICATE_SPLITTING, df_processed)

    logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!! TAKE OUT THOSE TWO LINES JUST TO MAKE TEST RUN FASTER !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    TEST_DF = TEST_DF.sample(frac=0.5, random_state=DATA_PIPELINE_CONFIG.seed)
    TRAIN_DF = TRAIN_DF.sample(frac=0.5, random_state=DATA_PIPELINE_CONFIG.seed)

    DATA_PREPROCESSOR_OBJ = create_preprocessor_data_object(
        TRAIN_DF = TRAIN_DF,
        TEST_DF = TEST_DF,
        DATA_PIPELINE_CONFIG = DATA_PIPELINE_CONFIG,
    )

    return DATA_PREPROCESSOR_OBJ, DATA_ENGINEERED_OBJ

def train_test_splitting(TRAIN_TEST_PREDICATE_SPLITTING, df_processed):
    idx_test_set = df_processed.query(TRAIN_TEST_PREDICATE_SPLITTING).index
    idx_train_set = df_processed.index.difference(idx_test_set)
    TEST_DF = df_processed.iloc[idx_test_set]
    TRAIN_DF = df_processed.iloc[idx_train_set]
    return TEST_DF,TRAIN_DF