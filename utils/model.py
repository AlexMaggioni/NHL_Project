import time
from omegaconf import DictConfig
import pandas as pd

def create_model(
    MODEL_CONFIG : DictConfig, 
    DATA_PIPELINE_CONFIG : DictConfig,
    logger 
):
    if MODEL_CONFIG.model_type == "LogisticRegression":
        from sklearn.linear_model import LogisticRegression
        logger.info(f"Creating {MODEL_CONFIG.model_type}")
        classifier = LogisticRegression(
            penalty=MODEL_CONFIG.penalty,
            C=MODEL_CONFIG.C,
            solver=MODEL_CONFIG.solver,
            verbose=MODEL_CONFIG.verbose,
            class_weight=MODEL_CONFIG.class_weight,
        )

    if MODEL_CONFIG.model_type == "XGBoostClassifier":
        objective = "multi:softmax" # if len(DATA_PIPELINE_CONFIG.label) > 2 else "binary:logistic"
        logger.info(f"Creating {MODEL_CONFIG.model_type} with objective : {objective}")
        import xgboost as xgb
        classifier = xgb.XGBClassifier(
            n_estimators=MODEL_CONFIG.n_estimators,
            max_depth=MODEL_CONFIG.max_depth,
            max_leaves=MODEL_CONFIG.max_leaves,
            objective=objective,
            num_class=len(DATA_PIPELINE_CONFIG.label)+1,
            reg_lambda=MODEL_CONFIG.reg_lambda,
            learning_rate=MODEL_CONFIG.learning_rate,
            min_child_weight = MODEL_CONFIG.min_child_weight,
            subsample = MODEL_CONFIG.subsample,
            colsample_bytree = MODEL_CONFIG.colsample_bytree,
            eval_metric=['merror','mlogloss'],
            seed=DATA_PIPELINE_CONFIG.seed,
            importance_type=MODEL_CONFIG.importance_type,
        )
    
    return classifier

def train_classifier_model(
        X_train : pd.DataFrame,
        y_train : pd.Series,
        X_val : pd.DataFrame,
        y_val : pd.Series,
        DATA_PIPELINE_CONFIG : DictConfig,
        MODEL_CONFIG : DictConfig,
        logger,
):
    
    CLS_MODEL = create_model(
        MODEL_CONFIG = MODEL_CONFIG,
        DATA_PIPELINE_CONFIG = DATA_PIPELINE_CONFIG,
        logger = logger,
    )

    from sklearn.utils.class_weight import compute_sample_weight

    # balancing 'target' class weights
    sample_weights = compute_sample_weight(
        class_weight='balanced',
        y=y_train
    )

    

    kwargs_fit = {
        'X' : X_train,
        'y' : y_train,
        'sample_weight' : sample_weights,
    }

    if MODEL_CONFIG.model_type == "XGBoostClassifier":
        # TODO : MAKE SUPPORT OF ARGS FROM
        # https://xgboost.readthedocs.io/en/stable/python/python_api.html#xgboost.XGBClassifier.fit

        # time_callback = xgb.callback.TrainingSpeed()
        # early_stopping = xgb.callback.EarlyStopping(rounds=10, save_best=True, maximize=False, verbose=True)  
        # callbacks = [time_callback, early_stopping]
        # callbacks = [time_callback]
        kwargs_fit['verbose'] = 0
        kwargs_fit['eval_set'] = [(X_train, y_train), (X_val, y_val)]

    start_time = time.time()
    CLS_MODEL.fit(**kwargs_fit)
    elapsed_time = time.time() - start_time
    
    logger.info(f"\tTraining time : {elapsed_time} seconds")
    
    return CLS_MODEL, elapsed_time