import pandas as pd

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
    df_with_coordinates.loc[df_with_coordinates['rinkSide'] == 'right', 'coordinateX'] = -df_with_coordinates['coordinateX']
    df_with_coordinates.loc[df_with_coordinates['rinkSide'] == 'right', 'coordinateY'] = -df_with_coordinates['coordinateY']
    df_with_coordinates.loc[df_with_coordinates['rinkSide'] == 'right', 'rinkSide'] = 'left'

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

if __name__ == '__main__':

    data = pd.read_csv("clean_data.csv")
    data = data[(data['gameId']==2016020001) & (data['period']==1)][['rinkSide', 'coordinateX', 'coordinateY', 'periodTime']]
    import pdb; pdb.set_trace()
    transformed_coords = unify_coordinates_referential(data)
    plot_referential_differences(data,transformed_coords)

    