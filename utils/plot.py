from itertools import cycle
from typing import List, Tuple
from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
import pandas as pd
from pathlib import Path

import pandas as pd

from rich import print
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.calibration import CalibrationDisplay
from sklearn.metrics import RocCurveDisplay

def plot_ROC_curve(
        y_true : np.ndarray, 
        y_proba : List[np.ndarray], 
        title_curve : List[str],
        title : str,
        output_path : Path,
    ):
    """Plot ROV curves handling several models predictions, so can output plot with several curves.

    Args:
        y_true (np.ndarray): ground-truth labels
        y_proba (List[np.ndarray]): probabilities of the positive class
        title_curve (List[str]): Name of each curves
        title (str): global plot title
        output_path (Path): path where plot will be saved
    """    
    
    from itertools import cycle

    fig, ax = plt.subplots(figsize=(6, 6))
    
    colors = cycle(["aqua", "darkorange", "cornflowerblue"])
    for i, (t, preds_proba, color) in enumerate(zip(title_curve, y_proba, colors)):
        
        kwargs_fn = {'plot_chance_level':False}
        if i == 0:
            kwargs_fn = {'plot_chance_level':True}
        
        RocCurveDisplay.from_predictions(
            y_true,
            preds_proba,
            name=t,
            color=color,
            ax=ax,
            **kwargs_fn,
        )

    plt.axis("square")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(title)
    plt.legend()
    plt.savefig(output_path)

def ratio_goal_wrt_percentile_fn(
    X : np.ndarray,
    q : np.ndarray,
) -> Tuple[np.ndarray,np.ndarray]:

    '''
    Soit X ∈ R^n le vecteur de probabilités pour la classe positive (GOAL) donnée par le modèle, n le nombre d'exemples.
    On définit la fonction f: [0,100] -> R telle que :

        f(q) = length(q_percentile_preds > 0.5) / length(q_percentile_preds)
            avec q_percentile_preds = conditional_subset(X, X_i < percentile(X, q))

        où :
            - conditional_subset(X, condition) est la fonction qui extrait 
                tous les éléments de X  qui respecte la condition.

            - percentile(X,q) est la fonction qui retourne le q-ème percentile de X.

            - length(X) est la fonction qui retourne la taille d'un vecteur X.

    Cette fonction calcule la quantité f(q) évoquée ci-dessus, d'une façon vectorisée
    
    Args:
        X (np.ndarray): vecteur de prédictions sous forme de probabilités pour la classe positive (GOAL) donné par un modèle
        q (np.ndarray): vecteur de percentile à calculer

    Returns:
        Tuple[np.ndarray,np.ndarray]: (
            vecteur de f(q) pour chaque q, même taille que q
            vecteur de nombre de buts (au lieu du ratio) pour chaque q, même taille que q
    '''

    # On calcule le percentile de X pour chaque q
    X_q = np.percentile(X, q=q, axis=0)

    ratio_goal = []
    for q in X_q:
        sub_X = X[X <= q]
        nb_goal = np.sum(sub_X > 0.5)
        ratio = nb_goal / len(sub_X)
        ratio_goal.append((ratio, nb_goal))

    # On calcule le ratio de buts pour chaque percentile
    return zip(*ratio_goal)

def plot_ratioORcumul_goal_percentile_curves(
    y_true : np.ndarray, 
    y_proba : List[np.ndarray], 
    title_curve : List[str],
    title : str,
    output_path : Path,
    ratio_goal : bool,
    random_model_line : bool,
):
    """
    étant donné, un vecteur de prédictions sous forme de probabilités pour la classe positive (GOAL)
    construit le taux de buts (#buts / (#non_buts + #buts)) en fonction du centile de
    la probabilité de but donnée par le modèle.

    Voir la fonction 

    Args:
        y_true (np.ndarray): ground-truth labels
        y_proba (List[np.ndarray]): probabilities of the positive class for different models trained on different set of features
        title_curve (List[str]): Name of each curves
        title (str): global plot title
        output_path (Path): path where plot will be saved
        ratio_goal (bool): if True, plot the ratio of goals, otherwise plot the cumulative number of goals
    """        
    from itertools import cycle

    fig, ax = plt.subplots(figsize=(6, 6))
    
    colors = cycle(["aqua", "darkorange", "cornflowerblue"])
    q_grid = np.linspace(0, 100, 6001)

    for t, preds_proba, color in zip(title_curve, y_proba, colors):
        
        y_values = list(ratio_goal_wrt_percentile_fn(preds_proba, q_grid))

        plt.plot(
            q_grid,
            y_values[0] if ratio_goal else y_values[1],
            label=t,
            color=color,
        )

    if random_model_line:

        preds_proba_base_model = np.random.uniform(0,1,y_proba[0].shape[0])

        y_values = list(ratio_goal_wrt_percentile_fn(preds_proba_base_model, q_grid))

        plt.plot(
            q_grid,
            y_values[0] if ratio_goal else y_values[1],
            label='Random model line',
            color='red',
        )

    plt.xlabel("GOAL probability model percentile")
    if ratio_goal:
        plt.ylabel("Goals ratio : #Goals / (#Goals + #No Goals)")
    else:
        plt.ylabel("Proportion of goals")
    plt.title(title)
    plt.legend()
    plt.savefig(output_path)

def plot_calibration_curve(
    y_true : np.ndarray, 
    y_proba : List[np.ndarray], 
    title_curve : List[str],
    title : str,
    output_path : Path,
):
    fig = plt.figure(figsize=(10, 10))
    gs = GridSpec(len(y_proba)+1, 2)
    colors = plt.get_cmap("Dark2")

    ax_calibration_curve = fig.add_subplot(gs[:2, :2])
    calibration_displays = {}
    markers = cycle(["^", "v", "s", "o"])
    for i, (t, preds_proba, marker) in enumerate(zip(title_curve, y_proba, markers)):

        kwargs_fn = {'ref_line':False}
        if i == 0:
            kwargs_fn = {'ref_line':True}

        display = CalibrationDisplay.from_predictions(
            y_true,
            preds_proba,
            name=t,
            ax=ax_calibration_curve,
            **kwargs_fn,
            n_bins=10,
            strategy='uniform',
            color=colors(i),
            marker=marker,
        )
        calibration_displays[t] = display

    ax_calibration_curve.grid()
    ax_calibration_curve.set_title(title)

    # Add histogram
    grid_positions = [(2, 0), (2, 1), (3, 0), (3, 1)]
    for i, name in enumerate(title_curve):
        row, col = grid_positions[i]
        ax = fig.add_subplot(gs[row, col])

        ax.hist(
            calibration_displays[name].y_prob,
            range=(0, 1),
            bins=10,
            label=name,
            color=colors(i),
        )
        ax.set(title=name, xlabel="Mean predicted probability", ylabel="Count")

    plt.savefig(output_path)

def plot_perf_model(
    ROC_curve : bool,
    ratio_goal_percentile_curve : bool,
    proportion_goal_percentile_curve : bool,
    calibration_curve : bool,
    stats : dict,
    split : str,
    y_true : np.ndarray,
    OUTPUT_DIR : Path,
    model_type : str,
):
    if split not in ['train', 'val', 'test']:
        raise ValueError(f'split must be in ["train", "val", "test"], got {split}')
    
    OUTPUT_DIR = OUTPUT_DIR / split
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    y_proba = [ d_with_preds[split]['proba_preds'][:,1] for _, d_with_preds in stats.items()]
    title_curve = [ feature_set for feature_set, _ in stats.items()]
    
    if ROC_curve:
        output_file = OUTPUT_DIR / "val_ROC_curves.png"
        plot_ROC_curve(
            y_true = y_true,
            y_proba = y_proba,
            title_curve = title_curve,
            title = 'ROC curves: \n {model_type} trained on different set of features',
            output_path = output_file,
        )
        print(f'ROC curves for val set saved at {output_file}')

    if ratio_goal_percentile_curve:
        output_file = OUTPUT_DIR / "val_ratio_goal_percentile_curves.png"
        plot_ratioORcumul_goal_percentile_curves(
            y_true,
            y_proba,
            title_curve,
            'Goal Rate: \n {model_type} trained on different set of features',
            output_file,
            ratio_goal = True,
            random_model_line=True,
        )
        print(f'Goal Ratio wrt percentile plot for val set saved at {output_file}')

    if proportion_goal_percentile_curve:
        output_file = OUTPUT_DIR / "val_proportion_goal_percentile_curves.png"
        plot_ratioORcumul_goal_percentile_curves(
            y_true,
            y_proba,
            title_curve,
            'Cumulative \% of goals: \n {model_type} trained on different set of features',
            output_file,
            ratio_goal = False,
            random_model_line=True,
        )
        print(f'Cumulative Number of Goal wrt percentile plot for val set saved at {output_file}')
    
    if calibration_curve:
        output_file = OUTPUT_DIR / "val_calibration_curves.png"
        plot_calibration_curve(
            y_true,
            y_proba,
            title_curve,
            'Calibration curves: \n {model_type} trained on different set of features',
            output_file,
        )
        print(f'Calibration curves for val set saved at {output_file}')