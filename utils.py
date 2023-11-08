import pandas as pd
from pathlib import Path

def unify_coordinates_referential(
        df_with_coordinates: pd.DataFrame,
) -> pd.DataFrame:
    
    """
    Les coordonnees des plays dans le dataframe sont raletif a un sens de jeu (selon si le but est a gauche ou a droite ?).
    Cette fonction permet d'unifier les coordonnees des plays relativement a un meme sens de jeu.

    Pour chaque ligne de df_with_coordinates (une row = un play),
      Les coordonnes doivent etre disponible via "coordinateX" amd "coordinateY"
      et une colonne 'rinkSide' doit etre disponible (soit 'left', soit 'right').

    
    Parameters
    ----------
    df_with_coordinates : pd.DataFrame
        A dataframe containing the plays with their coordinates and a relative sense.

    Returns
    -------
    pd.DataFrame
        A dataframe containing the shots with their coordinates unified.
    """

    if not set(df_with_coordinates.columns).issuperset({"coordinateX", "coordinateY", "rinkSide"}):
        raise RuntimeError("The dataframe must contain the columns 'coordinateX', 'coordinateY' and 'rinkSide'.")
    
    df_with_coordinates = df_with_coordinates.copy()
    right_rink_side = df_with_coordinates['rinkSide'] == 'right'
    df_with_coordinates.loc[right_rink_side, 'coordinateX'] = -df_with_coordinates.loc[right_rink_side, 'coordinateX']
    df_with_coordinates.loc[right_rink_side, 'coordinateY'] = -df_with_coordinates.loc[right_rink_side, 'coordinateY']
    df_with_coordinates.loc[right_rink_side, 'rinkSide'] = 'left'

    # Handling of plays with rinkSide == 'Shootout'
    # We gonna assume that if coordinateX is negative, then the goal was on the left side
    # Thus, we can only inverse those kinnds of shootout plays
    shootout_plays = (df_with_coordinates['rinkSide'] == 'Shootout') & (df_with_coordinates['coordinateX'] <= 0)
    df_with_coordinates.loc[shootout_plays, 'coordinateX'] = -df_with_coordinates.loc[shootout_plays, 'coordinateX']
    df_with_coordinates.loc[shootout_plays, 'coordinateY'] = -df_with_coordinates.loc[shootout_plays, 'coordinateY']
    df_with_coordinates.loc[shootout_plays, 'rinkSide'] = 'left'

    return df_with_coordinates

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
        compression="zip",
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
    print(f"Loading {file_dot_env_to_load} file from {position_of_execution}")
    if load_dotenv(position_of_execution / file_dot_env_to_load, verbose=True):
        return True
    else:
        raise RuntimeError(f"COULD NOT LOAD THE {file_dot_env_to_load} FILE FROM {position_of_execution}")

# vous pouvez approximer le filet en un seul point (c'est-à-dire que vous n'avez pas
# besoin de tenir compte de la largeur du filet lors du calcul de la distance ou de l'angle).
# x, y 
GOAL_POSITION = [89,0]

if __name__ == '__main__':

    data = pd.read_csv("clean_data.csv")
    data = data[(data['gameId']==2016020001) & (data['period']==1)][['rinkSide', 'coordinateX', 'coordinateY', 'periodTime']]
    import pdb; pdb.set_trace()
    transformed_coords = unify_coordinates_referential(data)
    plot_referential_differences(data,transformed_coords)

    