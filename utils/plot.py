from typing import List
from comet_ml import Experiment
import numpy as np
from pathlib import Path
import pandas as pd
from rich import print
from sklearn.calibration import calibration_curve
from sklearn.metrics import roc_curve, auc
import seaborn as sns
import matplotlib.pyplot as plt
import xgboost

def plotRocCurves(
    predictionsTest: dict,
    yTest: np.array, 
    outputPath: str = None
):
    """
    Plot ROC curves for the given predictions and ground truth values.
    :param predictions: Dictionary of model names and corresponding predictions
    :param yTest: Ground truth values
    :param outputPath: Path to save the plot to
    """
    
    # Check if outputPath is None and raise an error if it is
    if outputPath is None:
        raise ValueError("outputPath cannot be None. Please provide a valid file path.")

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 8))
    
    for modelName, modelPredictions in predictionsTest.items():
        goalProb = modelPredictions[:, 1]
        fpr, tpr, _ = roc_curve(yTest, goalProb)
        rocAuc = auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=2, label=f'{modelName} (AUC = {rocAuc:.2f})')

    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Classificateur Aléatoire (AUC = 0.50)')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Taux de Faux Positifs', fontsize=12)
    plt.ylabel('Taux de Vrais Positifs', fontsize=12)
    plt.title('Courbe ROC', fontsize=14)
    plt.legend(loc="lower right")

    # Save the plot
    plt.savefig(Path(outputPath), bbox_inches='tight')  # Save the figure to the specified path

def plotCombinedGoalRates(
    predictionsTest: dict, 
    yTest: np.array, 
    outputPath: str = None, 
    binWidth: int = 5
):
    """
    Plot combined goal rates for the given predictions and ground truth values.
    :param predictions: Dictionary of model names and corresponding predictions
    :param yTest: Ground truth values
    :param outputPath: Path to save the plot to
    :param binWidth: Width of each bin for calculating goal rates
    """
    
    # Check if outputPath is None and raise an error if it is
    if outputPath is None:
        raise ValueError("outputPath cannot be None. Please provide a valid file path.")

    plt.figure(figsize=(10, 6))

    for modelName, modelPredictions in predictionsTest.items():
        goalProb = modelPredictions[:, 1]

        modelPercentiles = []
        modelGoalRates = []

        for lowerBound in np.arange(0, 100, binWidth):
            upperBound = lowerBound + binWidth
            mask = (goalProb >= np.percentile(goalProb, lowerBound)) & (goalProb < np.percentile(goalProb, upperBound))

            totalShots = np.sum(mask)
            totalGoals = np.sum(yTest[mask])
            goalRate = (totalGoals / totalShots) * 100 if totalShots > 0 else 0

            modelPercentiles.append(lowerBound)
            modelGoalRates.append(goalRate)

        sns.lineplot(x=modelPercentiles, y=modelGoalRates, label=modelName, marker='o', markersize=8)

    plt.gca().invert_xaxis()
    plt.xticks(np.arange(0, 101, 10))
    plt.yticks(np.arange(0, 101, 10))
    plt.xlabel('Percentile de Probabilité du Modèle', fontsize=12)
    plt.ylabel('Taux de Buts (%)', fontsize=12)
    plt.title('Taux de Buts par Percentile de Probabilité', fontsize=14)
    plt.legend(title='Modèle')

    # Save the plot
    plt.savefig(Path(outputPath), bbox_inches='tight')  # Save the figure to the specified path

def plotCumulativeGoals(
    predictionsTest: dict, 
    yTest: np.array, 
    outputPath: str = None, 
    binWidth: int = 5
):
    """
    Plot cumulative goals for the given predictions and ground truth values.
    :param predictions: Dictionary of model names and corresponding predictions
    :param yTest: Ground truth values
    :param outputPath: Path to save the plot to
    :param binWidth: Width of each bin for calculating cumulative goals
    """
    
    # Check if outputPath is None and raise an error if it is
    if outputPath is None:
        raise ValueError("outputPath cannot be None. Please provide a valid file path.")

    plt.figure(figsize=(10, 6))

    for modelName, modelPredictions in predictionsTest.items():
        goalProb = modelPredictions[:, 1]  # Assuming the second column is the probability of a goal

        # Calculate percentiles
        percentiles = np.percentile(goalProb, np.arange(0, 100, binWidth))
        
        cumulativeGoals = []
        modelPercentiles = np.arange(0, 100, binWidth)
        totalGoals = np.sum(yTest)

        for percentile in percentiles:
            # Select data where goalProb is higher than the current percentile
            mask = goalProb >= percentile
            cumulativeGoals.append(np.sum(yTest[mask]) / totalGoals)

        # Plot
        plt.plot(modelPercentiles, cumulativeGoals, marker='o', label=modelName)

    plt.xticks(np.arange(0, 101, 10))
    plt.yticks(np.arange(0, 1.1, 0.1))
    plt.gca().invert_xaxis()
    plt.xlabel('Percentile de Probabilité du Modèle', fontsize=12)
    plt.ylabel('Proportion Cumulative de Buts', fontsize=12)
    plt.title('Proportion Cumulative de Buts par Percentile de Probabilité', fontsize=14)
    plt.legend()

    # Save the plot
    plt.savefig(Path(outputPath), bbox_inches='tight')  # Save the figure to the specified path

def plotCalibrationCurves(
    predictionsTest: dict, 
    yTest: np.array, 
    outputPath: str = None, 
    nBins: int = 10
):
    """
    Plot calibration curves for the given predictions and test values.
    :param predictionsDict: Dictionary of model names and corresponding predictions
    :param yTest: Test labels
    :param outputPath: Path to save the plot to
    :param nBins: Number of bins to use for calibration
    """
    
    # Check if outputPath is None and raise an error if it is
    if outputPath is None:
        raise ValueError("outputPath cannot be None. Please provide a valid file path.")

    sns.set(style='whitegrid')
    fig, ax = plt.subplots(figsize=(10, 8))

    for modelName, yProb in predictionsTest.items():
        goalProb = yProb[:, 1]  # Assuming the second column is the probability of a goal
        probTrue, probPred = calibration_curve(yTest, goalProb, n_bins=nBins)
        ax.plot(probPred, probTrue, marker='o', label=modelName)

    ax.plot([0, 1], [0, 1], 'k--', label='Parfaitement Calibré')
    ax.set_xlabel('Probabilité Prédite Moyenne (Classe Positive : 1)', fontsize=12)
    ax.set_ylabel('Fraction de Positifs', fontsize=12)
    ax.set_title('Graphique de Calibration', fontsize=14)
    ax.legend(loc='best')

    # Save the plot
    plt.savefig(Path(outputPath), bbox_inches='tight')  # Save the figure to the specified path

def plotPerfModel(
    predictionsTest: dict,
    yTest: np.ndarray,
    outputDir: Path,
    rocCurve: bool,
    ratioGoalPercentileCurve: bool,
    proportionGoalPercentileCurve: bool,
    calibrationCurve: bool,
) -> List[Path]:
    outputDir.mkdir(parents=True, exist_ok=True)

    res_output = []

    if rocCurve:
        outputFile = outputDir / "ROC_curves.png"
        plotRocCurves(
            predictionsTest=predictionsTest,
            yTest=yTest,
            outputPath=outputFile
        )
        print(f'ROC curves saved at {outputFile}')
        res_output.append(outputFile)

    if ratioGoalPercentileCurve:
        outputFile = outputDir / "ratio_goal_percentile_curves.png"
        plotCombinedGoalRates(
            predictionsTest=predictionsTest,
            yTest=yTest,
            outputPath=outputFile
        )
        print(f'Goal Ratio wrt percentile plot saved at {outputFile}')
        res_output.append(outputFile)

    if proportionGoalPercentileCurve:
        outputFile = outputDir / "proportion_goal_percentile_curves.png"
        plotCumulativeGoals(
            predictionsTest=predictionsTest,
            yTest=yTest,
            outputPath=outputFile
        )
        print(f'Cumulative Number of Goals wrt percentile plot saved at {outputFile}')
        res_output.append(outputFile)
    
    if calibrationCurve:
        outputFile = outputDir / "calibration_curves.png"
        plotCalibrationCurves(
            predictionsTest=predictionsTest,
            yTest=yTest,
            outputPath=outputFile
        )
        print(f'Calibration curves saved at {outputFile}')
        res_output.append(outputFile)
    
    return res_output

def plot_XGBOOST_losses(results, OUTPUT_DIR, title) -> List[Path]:

    res = []

    epochs = len(results['validation_0'][list(results['validation_0'].keys())[0]])
    x_axis = range(0, epochs)

    for split, metric in results.items():

        fig, ax = plt.subplots(figsize=(9,5))
        for loss_name, value_loss in metric.items():
            ax.plot(x_axis, value_loss, label=loss_name)
        ax.legend()
        plt.ylabel('Losses/Error')
        plt.title(f'{title} {split} losses/error')
        plt.savefig(OUTPUT_DIR / f'{title}_{split}_losses.png')
        res.append(OUTPUT_DIR / f'{title}_{split}_losses.png')

    return res

def plot_XGBOOST_feat_importance(
        OUTPUT_DIR : Path,
        COMET_EXPERIMENT : Experiment,
        logger,
        classifier : xgboost.XGBClassifier,
        X_train_samples : pd.DataFrame,
):
    PATH_GRAPHS = []

    key = '+'.join(X_train_samples.columns)

    #feature importance plot
    importances = classifier._Booster.get_score(importance_type=classifier.importance_type)
    print(importances)
    for key in importances:
        COMET_EXPERIMENT.log_other(key, importances[key])
        
    COMET_EXPERIMENT.log_asset_data(importances)

    logger.info(f"Plotting XGBoost feature importance at {OUTPUT_DIR}")
    ax = xgboost.plot_importance(classifier)
    output_feat_imp = OUTPUT_DIR / f'{key}_feature_importance.png'
    ax.figure.savefig(str(output_feat_imp))
    PATH_GRAPHS.append(output_feat_imp)

    COMET_EXPERIMENT.log_image(str(output_feat_imp))

    import shap
        
    logger.info(f"Plotting XGBoost SHAP values at {OUTPUT_DIR}")

    # model_bytearray = classifier._Booster.save_raw('json')#[4:]
    # def myfunc(self=None):
    #     return model_bytearray
    # classifier.save_raw = myfunc

    explainer = shap.TreeExplainer(classifier)

    shap_values = explainer.shap_values(X_train_samples)
    shap.initjs()

    # log decision plot
    # FIXME : on the following line features_name should be
    # shap.multioutput_decision_plot(explainer.expected_value, shap_values, X_train_samples.index, show=False)
    # plt.savefig(str(OUTPUT_DIR / 'decision_plot.png'))
    # COMET_EXPERIMENT.log_image(str(OUTPUT_DIR / 'decision_plot.png'))
    # plt.clf()


    feature_names = X_train_samples.columns
    # log Summary plot
    shap.summary_plot(shap_values, feature_names, show=False)
    new_var = OUTPUT_DIR / f'{key}_summary_plot.png'
    plt.savefig(str( new_var))
    PATH_GRAPHS.append(new_var)
    COMET_EXPERIMENT.log_image(str(new_var))

    return PATH_GRAPHS
