import os
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import requests

import comet_ml

from ift6758.client.game_client import GameClient
from ift6758.client.serving_client import ServingClient
from ift6758.data.nhl_rest_api_fetcher_V2 import Game_endpoints_Fetcher_v2

# =====================================================================================

def backend_model_registry(
        workspace : str,
        model : str,
        version : str,
):
    
    ServingClient(
        ip=os.getenv('BACKEND_ADDRESS', '0.0.0.0'),
        port=os.getenv('BACKEND_PORT', '1234'),
        features=None,
    ).download_registry_model(
        workspace=workspace,
        model=model,
        version=version,
    )


def get_live_game_data(game_id):

    response_raw_data = Game_endpoints_Fetcher_v2(
                f"gamecenter/{game_id}/play-by-play"
            ).fetch(
                output_format="json",
            )
    
    return response_raw_data


def fetch_game_data_and_predict():

    PATH_CACHE = Path(os.getenv('DATA_FOLDER')) / f'cache_frontend/v2_nhl_api' / st.session_state.workspace_placeholder / st.session_state.model_placeholder / st.session_state.model_version_placeholder / 'cache.sqlite'

    samples_to_predict = GameClient(
        game_id=st.session_state['game_id_input'],
        nhl_api_version='v2',
        cache_sqllite_path_file=PATH_CACHE,
    ).get_game_data()

    if len(samples_to_predict) > 0:

        features_used = []
        if 'distance' in st.session_state.model_placeholder:
            features_used.append('distanceToGoal')
        if 'angle' in st.session_state.model_placeholder:
            features_used.append('angleToGoal')


        data_processed = None
        for team in samples_to_predict.byTeam.unique():

            samples_team = samples_to_predict[samples_to_predict.byTeam == team]

            preds = ServingClient(
                ip=os.getenv('BACKEND_ADDRESS', '0.0.0.0'),
                port=os.getenv('BACKEND_PORT', '1234'),
                features=features_used,
            ).predict(
                samples_team,
            )

            data_processed = pd.concat([data_processed, samples_team[[*features_used, 'byTeam']].assign(isGoal=preds['probabilities'].values)])
    
        update_cache(data_processed, st.session_state['game_id_input'], PATH_CACHE)

def update_cache(samples_to_predict : pd.DataFrame, game_id : str, PATH_CACHE : Path) -> None:
    """
    Updates cache for a given game ID.
    """

    from sqlite_utils import Database
    
    db = Database(PATH_CACHE)

    records_to_insert = samples_to_predict.reset_index().to_dict(orient='records')

    db[game_id].insert_all(
        records_to_insert,
        pk="index",
    )

def compute_xG_from_cache(team_abbrev : str):
    PATH_CACHE = Path(os.getenv('DATA_FOLDER')) / f'cache_frontend/v2_nhl_api' / st.session_state.workspace_placeholder / st.session_state.model_placeholder / st.session_state.model_version_placeholder / 'cache.sqlite'
    PATH_CACHE.parent.mkdir(parents=True, exist_ok=True)

    from sqlite_utils import Database

    db = Database(PATH_CACHE)

    table_already_computed_samples = list(db[st.session_state['game_id_input']].rows)
    
    if len(table_already_computed_samples) == 0:
        return None

    df = pd.DataFrame(table_already_computed_samples)

    df = df[df.byTeam == team_abbrev]

    return df[df.isGoal > 0.5].shape[0] / df.shape[0]


def retreive_used_data():
    PATH_CACHE = Path(os.getenv('DATA_FOLDER')) / f'cache_frontend/v2_nhl_api' / st.session_state.workspace_placeholder / st.session_state.model_placeholder / st.session_state.model_version_placeholder / 'cache.sqlite'

    from sqlite_utils import Database

    db = Database(PATH_CACHE)

    table_already_computed_samples = list(db[st.session_state['game_id_input']].rows)
    
    if len(table_already_computed_samples) == 0:
        return None

    df = pd.DataFrame(table_already_computed_samples)

    return df

def get_backend_logs():

    return ServingClient(
        ip=os.getenv('BACKEND_ADDRESS', '0.0.0.0'),
        port=os.getenv('BACKEND_PORT', '1234'),
        features=None,
    ).logs()


# =====================================================================================


comet_api = comet_ml.api.API(api_key=os.getenv('COMET_API_KEY'))


st.title("NHL Analysis App - Team A07")

tab1, tab2= st.tabs(["App", "Backend Logs"])

with tab1:

    with st.sidebar:
        workspace_placeholder = st.selectbox(
            "CometML Workspace",
            ("nhl-project",),
            key='workspace_placeholder',
            placeholder='For now, only workspace providing usable models is nhl-project',
        )

        model_placeholder = st.selectbox(
            "Model Registry Name",
            comet_api.get_registry_model_names(workspace_placeholder),
            key='model_placeholder',
            placeholder=f'Select a model from the workspace {workspace_placeholder}'
        )

        model_version_placeholder = st.selectbox(
            "Model Version",
            comet_api.get_registry_model_versions(workspace_placeholder, model_placeholder),
            key='model_version_placeholder',
            placeholder='Select a model version'
        )

        download_model = st.button(
            "Download Model",
            on_click=backend_model_registry,
            kwargs={
                'workspace' : workspace_placeholder,
                'model' : model_placeholder,
                'version' : model_version_placeholder,
            },
        )

        model_info = Path(ServingClient(
            ip=os.getenv('BACKEND_ADDRESS', '0.0.0.0'),
            port=os.getenv('BACKEND_PORT', '1234'),
            features=None,).get_actual_model()['model_name']).parts[-4:-1]

        st.divider()

        st.subheader("Actually-Selected BACKEND Model: (DONT FORGET TO PUSH ABOVE BUTTON)") 
                
        st.text(f"""
        CometML Workspace - 
    {model_info[0]}

        Model Registry Name - 
    {model_info[1]}   

        Model Version - 
    {model_info[2]}""")

    with st.container():

        game_id_input = st.text_input(
            "Game ID",
            value='2021020329',
            key='game_id_input',
        )

        game_id_submit = st.button(
            "Fetch Game Data",
            key='game_id_submit',
            on_click=fetch_game_data_and_predict,
        )

    with st.container():

        data_nhl = get_live_game_data(game_id_input)

        team_info = {
            'away' : {
                'name' : data_nhl['awayTeam']['name']['default'],
                'abbrev' : data_nhl['awayTeam']['abbrev'],
            },
            'home' : {
                'name' : data_nhl['homeTeam']['name']['default'],
                'abbrev' : data_nhl['homeTeam']['abbrev'],
            },
        }

        st.header(
            f"Game {game_id_input}: (AWAY) {team_info['away']['name']} {team_info['away']['abbrev']} vs (HOME) {team_info['home']['name']} {team_info['home']['abbrev']}",
            divider='rainbow'
        )

        st.text(f"Period {data_nhl['period']} - {data_nhl['clock']['timeRemaining']} left")

        col1, col2 = st.columns(2)

        with col1:
            away_team_xG = compute_xG_from_cache(team_info['away']['abbrev'])

            score_away_team = data_nhl['awayTeam']['score']

            col1.metric(
                f"{team_info['away']['name']} xG (actual)", 
                None if away_team_xG is None else f"{away_team_xG} ({score_away_team})",
                None if away_team_xG is None else away_team_xG - score_away_team
            )

        with col2:

            home_team_xG = compute_xG_from_cache(team_info['home']['abbrev'])

            score_home_team = data_nhl['homeTeam']['score']

            col2.metric(
                f"{team_info['home']['name']} xG (actual)", 
                None if home_team_xG is None else f"{home_team_xG} ({score_home_team})",
                None if home_team_xG is None else home_team_xG - score_home_team
            )


        with st.container():
            st.header(
                f"Data used for predictions (and predicted probabilities of shot being a goal)",
            )

            st.dataframe(
                retreive_used_data(),
            )

with tab2:
    st.json(get_backend_logs())
