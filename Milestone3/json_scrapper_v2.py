from pathlib import Path
import sys
import numpy as np
import pandas as pd
import json
from tqdm import tqdm
import datetime
import os

from utils.misc import init_logger, verify_dotenv_file, safe_getitem_nested_dict

class JsonParser_v2:
    """
    Class to Parse the json files from the NHL API to construct a DataFrame.
    
    For now, the sole useful use of this class is to instantiate it via the static method `load_all_seasons`.
    """    

    def __init__(
            self, 
            path : str = None, 
            df : pd.DataFrame =None,
            shotGoalOnly : bool = True) -> None:
        """Either initialize with a path or with an existing DataFrame.

        Args:
            path (str, optional): path_to_a_DataFrame. Defaults to None.
            df (pd.DataFrame, optional): pandas Dataframe. Defaults to None.
        """        
        self.path = path
        self.shotGoalOnly = shotGoalOnly
        if df is not None:
            self.df = df
        elif path:
            self.df = self.parse_json_file(self.shotGoalOnly)
        else:
            self.df = pd.DataFrame()

    def parse_json_file(self, shotGoalOnly):
        with open(self.path, "r") as f:
            data = json.load(f)

        liveData = data["plays"]

        winning_team = None
        # if 'teams' in linescore:
        home_goals = safe_getitem_nested_dict(data, ['homeTeam', 'score'], -1)
        away_goals = safe_getitem_nested_dict(data, ['awayTeam', 'score'], -1)
        if home_goals > away_goals:
            winning_team = safe_getitem_nested_dict(data, ['homeTeam', 'abbrev'], np.nan)
        elif away_goals > home_goals:
            winning_team = safe_getitem_nested_dict(data, ['awayTeam', 'abbrev'], np.nan)
        else:
            winning_team = np.nan

        rink_side_dict = self.create_rink_side_info(data)

        game_info = self.extract_game_info(data)

        rows = []
        for play in data["plays"]:
            if shotGoalOnly:
                if play["typeDescKey"] in ["goal", "shot-on-goal", "missed-shot", "blocked-shot"]:
                    row_data = self.extract_play_data(play, game_info, rink_side_dict, winning_team)
            else : 
                row_data = self.extract_play_data(play, game_info, rink_side_dict, winning_team)

            rows.append(row_data)

        df = pd.DataFrame(rows)
        return df
    
    def create_rink_side_info(self, data):

        # New logic for extracting rink side information
        homeTeamDefendingSide_first_period = data["plays"][0].get('homeTeamDefendingSide', None)
        
        if homeTeamDefendingSide_first_period is None:
            """
            HERE WHEN THE FIRST PLAY DEOS NOT HAVE A homeTeamDefendingSide KEY
            WE GOT TO SEARCH FOR THE FIRST PLAY WITH A zoneCode KEY
            AND DEDUCE FROM THE SIGN OF THE x COORDINATE THE rink_side_dict 
            """
            i=0
            actual_play = data["plays"][i]
            while safe_getitem_nested_dict(actual_play, ['details', 'zoneCode'], None) is None:
                actual_play = data["plays"][i]
                i+=1
            
            eventOwnerTeamId_actual_play = actual_play['details']['eventOwnerTeamId']
            eventOwnerTeamId_is_home_team = eventOwnerTeamId_actual_play == data['homeTeam']['id']
        
            if 

            home_team_attacking_side = 'left' if eventOwnerTeamId_is_home_team else 'right'

        rink_side_dict = {
            1 : {
                'home': 'right' if homeTeamDefendingSide_first_period == 'left' else 'right',
                'away': homeTeamDefendingSide_first_period,
            }
        }
        nb_period = data['period']
        for num_period in range(2, nb_period+1):
            home_team_attacking_side = rink_side_dict[num_period-1]['home']
            rink_side_dict[num_period] = {
                'home': home_team_attacking_side,
                'away': 'left' if home_team_attacking_side == 'right' else 'right',
            }

        return rink_side_dict


    def extract_game_info(self, gameData):

        game_info = {
            "gameId": int(safe_getitem_nested_dict(gameData, ["id"])),
            "season": int(safe_getitem_nested_dict(gameData, ["season"])),
            "gameType": int(safe_getitem_nested_dict(gameData, ["gameType"])),
            "gameDate": int(safe_getitem_nested_dict(gameData, ["gameDate"])),
            "homeTeam": safe_getitem_nested_dict(gameData, ["homeTeam", "abbrev"]),
            "awayTeam": safe_getitem_nested_dict(gameData, ["awayTeam", "abbrev"]),
        }
        return game_info

    def parse_date(self, date_str):
        return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d") if date_str else None

    def extract_play_data(self, play, game_info, rink_side_dict, win_team):
        period = int(play.get("about", {}).get("period", None))
        byTeam = play.get("team", {}).get("triCode", None)
        homeTeam = game_info["homeTeam"]

        row_data = game_info.copy()
        row_data.update({
            "period": period,
            "periodTime": play.get("about", {}).get("periodTime", None),
            "byTeam": byTeam,
            "eventType": play.get("result", {}).get("eventTypeId", None),
        })
        
        coordinates = play.get("coordinates", {})
        coordinateX = coordinates.get("x", None)
        coordinateY = coordinates.get("y", None)

        row_data["coordinateX"] = coordinateX
        row_data["coordinateY"] = coordinateY
        row_data['winTeam'] = win_team

        self.populate_event_specific_data(play, row_data)

        # Add rink side information
        if period == 5:
            row_data['rinkSide'] = 'Shootout'
        else:
            row_data['rinkSide'] = rink_side_dict.get(period, {}).get('home' if byTeam == homeTeam else 'away', None)

        return row_data


    def __add__(self, other):
        if not isinstance(other, JsonParser_v2):
            raise ValueError("Can only add JsonParser_v2 objects.")
        combined_df = pd.concat([self.df, other.df], ignore_index=True)
        return JsonParser_v2(df=combined_df)

    @staticmethod
    def load_all_seasons(
        path_csv_output : Path,
        json_files_to_consider : list[Path],
        shotGoalOnly: bool):


        ROOT_DATA = Path(os.getenv("DATA_FOLDER"))
        OUTPUT_PATH = ROOT_DATA / path_csv_output
        
        if os.path.exists(OUTPUT_PATH):
            df = pd.read_csv(OUTPUT_PATH, parse_dates=["gameDate"])
            logger.info(f"SKIPPING SCRAPPING >>> DataFrame loaded from {OUTPUT_PATH}")
            return JsonParser_v2(df=df, path=OUTPUT_PATH)


        base_parser = JsonParser_v2()
        with tqdm(total=len(json_files_to_consider)) as pbar1:
            for json_file in json_files_to_consider:
                pbar1.set_description(f"Processing json file - {json_file} ")
                parser = JsonParser_v2(json_file)
                base_parser = base_parser + parser
                pbar1.update(1)

        base_parser.df.to_csv(OUTPUT_PATH, index=False)
        logger.info(f"DataFrame saved to {OUTPUT_PATH}")
        base_parser.path = OUTPUT_PATH
        return base_parser


def cli_args():
    '''
    CLI Interface, to specify for now:
        - path of the csv file (value specified by the value returned as pathlib.Path)
        - shotGoalOnly argument
    '''
    import argparse
    parser = argparse.ArgumentParser(
        description="""
        Script to scrap json files from the NHL API and construct a Dataframe (and a .csv file). 
        if the csv file already exists do nothing, otherwise parse json files to create it
        """,
        epilog='''
        Example : 
        export PYTHONPATH="$pwd"
        # télécharge chaque play de chaque match, que ce soit des playoffs ou de la saison régulière, pour chaque saison de 2016 à 2020
        python Milestone1/json_scrapper.py -p_csv very_big_file.csv --years $(seq -s ' ' 2016 2020)
        '''
    )
    parser.add_argument('-p_csv', '--path_to_csv', type=str, required=True, help='Path to the csv file. WILL BE CONCATENATED WITH the .env\'s DATA_FOLDER var. PUT THE COMMIT ID IN THE NAME !!!!!!!!!!!!!!!!!!!!')
    parser.add_argument('-y','--years', required=True, nargs='+', type=str, help='years of seasons to iterate on')
    parser.add_argument('--shotGoalOnly', action='store_true', help='Filter only "GOAL" and "SHOT" events')
    parser.add_argument('--comet_dl',default=True, action='store_true', help='Comet : at exp. "json-scrapper-output" push as an artifact the csv file ')
    args = parser.parse_args()
    return args

if __name__ == "__main__":

    # Add the parent directory to sys.path
    parent_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(parent_dir))

    from utils.misc  import init_logger, verify_dotenv_file

    verify_dotenv_file(parent_dir)
    logger = init_logger("json_scrapper.log")
    args = cli_args()

    parser_obj = JsonParser_v2.load_all_seasons(
        args.path_to_csv,
        args.years,
        args.shotGoalOnly
    )

    if args.comet_dl:
        parser_obj.log_csv_as_artifact()