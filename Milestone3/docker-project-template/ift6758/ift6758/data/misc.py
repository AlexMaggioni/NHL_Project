from itertools import cycle
from typing import Dict, List, Tuple, Union
import numpy as np
import pandas as pd
from pathlib import Path
import pandas as pd

import pandas as pd

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


def safe_int_casting(x):
    return int(x) if x is not None else None

def is_not_nested_dict(d):
    return not isinstance(d, dict) or not any(isinstance(i, dict) for i in d.values())

def safe_getitem_nested_dict(dict, list_key, leaf_value_default=None):
    if is_not_nested_dict(dict) or len(list_key) == 1:
        return dict.get(list_key[0], leaf_value_default)
    else:
        if list_key[0] not in dict:
            return leaf_value_default
        return safe_getitem_nested_dict(dict[list_key[0]], list_key[1:], leaf_value_default)