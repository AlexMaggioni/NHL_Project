from itertools import cycle
from typing import List, Tuple
from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
import pandas as pd
from pathlib import Path
import pandas as pd

import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.calibration import CalibrationDisplay
from sklearn.metrics import RocCurveDisplay

def unify_coordinates_referential(
    df_with_coordinates: pd.DataFrame,
    impute_rinkSide_by_mean: bool = False
) -> pd.DataFrame:
    """
    Normalizes the coordinates of plays in a hockey game DataFrame, ensuring all coordinates are relative to the same direction.
    Optionally imputes missing 'rinkSide' values based on the mean of 'coordinateX' for specific event types.
 
    Parameters
    ----------
    df_with_coordinates : pd.DataFrame
        DataFrame containing plays with coordinates and rink side ('left', 'right', 'Shootout', or NaN).
    impute_rinkSide_by_mean : bool, optional
        If True, imputes missing 'rinkSide' values based on the mean of 'coordinateX' for specific event types.
 
    Returns
    -------
    pd.DataFrame
        DataFrame with unified coordinates.
    """
 
    # Check for necessary columns
    required_columns = {'coordinateX', 'coordinateY', 'rinkSide', 'gameId', 'byTeam', 'period', 'eventType'}
    if not required_columns.issubset(df_with_coordinates.columns):
        raise ValueError(f"The DataFrame must contain the columns: {required_columns}")
 
    df = df_with_coordinates.copy()
 
    # Impute missing rinkSide values
    if impute_rinkSide_by_mean:
        # Filter for specific event types and compute mean coordinateX
        mean_coordinateX_df = df[df['eventType'].isin(['SHOT', 'GOAL', 'MISSED_SHOT', 'BLOCKED_SHOT'])]\
                               .groupby(['gameId', 'byTeam', 'period'])['coordinateX']\
                               .mean().reset_index()\
                               .rename(columns={'coordinateX': 'mean_coordinateX'})
 
        # Merge the original DataFrame with the mean coordinateX DataFrame
        merged_df = df.merge(mean_coordinateX_df, on=['gameId', 'byTeam', 'period'], how='left')
 
        # Use vectorized operation to update 'rinkSide'
        merged_df['rinkSide'] = np.where(merged_df['rinkSide'].isna(),
                                         np.where(merged_df['period'] == 5, 'Shootout',
                                                  np.where(merged_df['mean_coordinateX'] < 0, 'right', 'left')),
                                         merged_df['rinkSide'])
 
        # Drop the supplementary column
        df = merged_df.drop(columns=['mean_coordinateX'])
 
    # Flipping coordinates for 'right' rinkSide
    df.loc[df["rinkSide"] == "right", ["coordinateX", "coordinateY"]] *= -1
    df.loc[df["period"] == 5, "rinkSide"] = "Shootout"
    df.loc[df["rinkSide"] == "right", "rinkSide"] = "left"
 
    # Flip coordinates for 'Shootout' rinkSide when coordinateX is negative
    shootout_condition = (df["rinkSide"] == "Shootout") & (df["coordinateX"] < 0)
    df.loc[shootout_condition, ["coordinateX", "coordinateY"]] *= -1
 
    return df

def plot_referential_differences(
        initial_coordinates_df: pd.DataFrame,
        unified_coordinates_df: pd.DataFrame,
):

    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    import plotly.express as px

    fig = make_subplots(rows=1, cols=2)

    initial_coordinates_figure = go.Scatter(
        x=initial_coordinates_df['coordinateX'],
        y=initial_coordinates_df['coordinateY'],
        mode='markers',
        marker=dict(
            color=['red' if side == 'left' else 'green' for side in initial_coordinates_df['rinkSide']],
            size=5,
        ),
        name='initial coordinates'
    )

    fig.add_trace(
        initial_coordinates_figure,
        row=1, col=1
    )


    unified_coordinates_df['rinkSide'] = initial_coordinates_df['rinkSide']
    
    fig.add_trace(
        go.Scatter(
            x=unified_coordinates_df['coordinateX'],
            y=unified_coordinates_df['coordinateY'],
            mode='markers',
            marker=dict(
                color='purple',
                size=5,
            ),
            name='transformed coordinates right ---> left'
        ),
        row=1, col=2
    )

    fig.add_trace(
        initial_coordinates_figure,
        row=1, col=2
    )

    for x0,y0,x1,y1 in zip(initial_coordinates_df['coordinateX'], initial_coordinates_df['coordinateY'], unified_coordinates_df['coordinateX'], unified_coordinates_df['coordinateY']):
        fig.add_shape(
            type="line",
            x0=x0, y0=y0, x1=x1, y1=y1,
            line=dict(
                color="MediumPurple",
                width=1,
                dash="dot",
            ),
            row=1, col=2
        )

    fig.update_layout(height=600, width=800, title_text="Side By Side Subplots")
    fig.show()


def is_not_nested_dict(d):
    return not isinstance(d, dict) or not any(isinstance(i, dict) for i in d.values())

def safe_getitem_nested_dict(dict, list_key, leaf_value_default=None):
    print(dict.keys(), list_key, len(list_key), leaf_value_default)
    if is_not_nested_dict(dict) or len(list_key) == 1:
        print('not nested dict')
        print(dict, list_key, leaf_value_default)
        print('toto  ', dict.get(list_key[0], leaf_value_default))
        return dict.get(list_key[0], leaf_value_default)
    else:
        return safe_getitem_nested_dict(dict[list_key[0]], list_key[1:], leaf_value_default)

def generate_url_path(*parts, use_posix=False):
    '''
    Emerges from the problem of running this script on Windows and Linux.
    Needed an OS-agnostic way to generate an url path (mainly used in the GET request endpoint path)
    '''
    path = Path(*parts)
    return path.as_posix() if use_posix else str(path)


def init_logger(log_file_path : str):
    '''
    Initialize the logger that will log into some files and not on stdout
    We use the loguru library so it takes care of the rotation/renaming of the logs file 
        and offer less boilerplate code than the standard logging library...
    '''
    from loguru import logger
    import os
    logger.add(
        Path(os.getenv('LOGGING_FILE')) / log_file_path,
        level="DEBUG",
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> <green>{elapsed}</green> | <level>{level: <8}</level> | <cyan>{file}</cyan>:<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )

    if log_file_path == "nhl_rest_api_fetcher.log":
        # Remove print on stdout (otherwise hide the progress bars) when executing "nhl_rest_api_fetcher.py"
        logger.remove(0)

    return logger

import os
from dotenv import load_dotenv

def get_dotenv_file_to_load():
    '''
    Just to support the case if runnning inside a docker of the image nvcr.io/nvidia/pytorch:23.10-py3
    '''
    return '.env_docker' if os.getenv("RUNNING_IN_DOCKER") else '.env'

def verify_dotenv_file(position_of_execution : Path):
    file_dot_env_to_load = get_dotenv_file_to_load()
    from rich import print
    # print(f"Loading {file_dot_env_to_load} file from {position_of_execution}")
    if load_dotenv(position_of_execution / file_dot_env_to_load, verbose=True):
        return True
    else:
        raise RuntimeError(f"COULD NOT LOAD THE {file_dot_env_to_load} FILE FROM {position_of_execution}")



if __name__ == '__main__':

    data = pd.read_csv("clean_data.csv")
    data = data[(data['gameId']==2016020001) & (data['period']==1)][['rinkSide', 'coordinateX', 'coordinateY', 'periodTime']]
    transformed_coords = unify_coordinates_referential(data)
    plot_referential_differences(data,transformed_coords)

    