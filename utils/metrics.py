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
) -> dict:
    
    print(f'Confusion Matrix | {title_model}')
    cf_matrix_array = confusion_matrix(y, y_pred)
    print(cf_matrix_array)

    print(f'\n--------------- Classification Report  | {title_model}  ---------------\n')
    print(classification_report(y, y_pred))

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

    return res