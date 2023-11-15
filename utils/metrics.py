from copy import deepcopy
import numpy as np
from sklearn.metrics import (
            balanced_accuracy_score,
            accuracy_score,
            precision_score,
            recall_score,
            f1_score,
            )

from sklearn.metrics import (confusion_matrix,classification_report)

def assess_classifier_perf(
    y: np.ndarray,
    y_pred : np.ndarray,
    title_model : str,
    COMET_EXPERIMENT=None, 
) -> dict:
    
    print(f'Confusion Matrix | {title_model}')
    cf_matrix_array = confusion_matrix(y, y_pred)
    print(cf_matrix_array)

    print(f'\n--------------- Classification Report  | {title_model}  ---------------\n')
    print(classification_report(y, y_pred))

    y = y.to_numpy().ravel()

    res = {
        'accuracy' : {
            'accuracy' : accuracy_score(y, y_pred),
            'balanced_accuracy' : balanced_accuracy_score(y, y_pred),
        },
        'micro' : {
            'precision': precision_score(y, y_pred, average='micro'),
            'recall': recall_score(y, y_pred, average='micro'),
            'f1': f1_score(y, y_pred, average='micro'),
        },
        'macro' : {
            'precision': precision_score(y, y_pred, average='macro'),
            'recall': recall_score(y, y_pred, average='macro'),
            'f1': f1_score(y, y_pred, average='macro'),
        },
        'weighted' : {
            'precision': precision_score(y, y_pred, average='weighted'),
            'recall': recall_score(y, y_pred, average='weighted'),
            'f1': f1_score(y, y_pred, average='weighted'),
        },
        'conf_matrix' : cf_matrix_array
    }

    # import pdb; pdb.set_trace()

    if COMET_EXPERIMENT is not None:
        from utils.misc import collide_keys
        single_metric = deepcopy(res)
        single_metric.pop('conf_matrix')
        COMET_EXPERIMENT.log_metrics(
            collide_keys(single_metric),
            prefix=title_model,
        )

        COMET_EXPERIMENT.log_confusion_matrix(
            labels=['NO_GOAL','GOAL'],
            matrix=res['conf_matrix'],
            file_name=f"confusion_matrix_val_set_{title_model}.png",
        )

    return res