from pathlib import Path
import sys
import pandas as pd
import json
from tqdm import tqdm
import datetime
import os

class JsonParser:
    """
    Class to Parse the json files from the NHL API to construct a DataFrame.
    
    For now, the sole useful use of this class is to instantiate it via the static method `load_all_seasons`.
    """    

    def __init__(
            self, 
            path : str = None, 
            df : pd.DataFrame =None) -> None:
        """Either initialize with a path or with an existing DataFrame.

        Args:
            path (str, optional): path_to_a_DataFrame. Defaults to None.
            df (pd.DataFrame, optional): pandas Dataframe. Defaults to None.
        """        
        self.path = path
        if df is not None:
            self.df = df
        elif path:
            self.df = self.parse_json_file(args.shotGoalOnly)
        else:
            self.df = pd.DataFrame()

    def parse_json_file(self, shotGoalOnly):
        with open(self.path, "r") as f:
            data = json.load(f)

        gameData = data["gameData"]
        liveData = data["liveData"]["plays"]["allPlays"]
        rinkSide = data["liveData"]["linescore"]["periods"]
        linescore = data["liveData"]["linescore"]

        winning_team = None
        if 'teams' in linescore:
                home_goals = linescore['teams']['home'].get('goals', 0)
                away_goals = linescore['teams']['away'].get('goals', 0)
                if home_goals > away_goals:
                    winning_team = linescore["teams"]["home"]["team"].get('triCode')
                elif away_goals > home_goals:
                    winning_team = linescore["teams"]["away"]["team"].get('triCode')
                else:
                    winning_team = np.nan

        # New logic for extracting rink side information
        rink_side_dict = {}
        for period_info in rinkSide:
            period_num = period_info.get('num', None)
            rink_side_dict[period_num] = {
                'home': period_info.get('home', {}).get('rinkSide', None),
                'away': period_info.get('away', {}).get('rinkSide', None)
            }

        game_info = self.extract_game_info(gameData)

        rows = []
        for play in liveData:
            if not shotGoalOnly or play["result"]["eventTypeId"] in ["GOAL", "SHOT"]:
                row_data = self.extract_play_data(play, game_info, rink_side_dict, winning_team)
                rows.append(row_data)

        df = pd.DataFrame(rows)
        return df

    def extract_game_info(self, gameData):

        game_info = {
            "gameId": int(gameData.get("game", {}).get("pk", None)),
            "season": int(gameData.get("game", {}).get("season", None)[:4]),
            "gameType": gameData.get("game", {}).get("type", None),
            "gameDate": self.parse_date(gameData.get("datetime", {}).get("dateTime", "")),
            "homeTeam": gameData.get("teams", {}).get("home", {}).get("abbreviation", None),
            "awayTeam": gameData.get("teams", {}).get("away", {}).get("abbreviation", None),
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

    def populate_event_specific_data(self, play, row_data):
        event_type = row_data["eventType"]
        event_populate_functions = {
            "GOAL": self.populate_goal_data,
            "SHOT": self.populate_shot_data,
            "PENALTY": self.populate_penalty_data,
            "BLOCKED_SHOT": self.populate_blocked_shot_data,
            "MISSED_SHOT": self.populate_missed_shot_data,
        }
        if event_type in event_populate_functions:
            event_populate_functions[event_type](play, row_data)

    def populate_goal_data(self, play, row_data):
        row_data["shotType"] = play.get("result", {}).get("secondaryType", None)
        row_data["strength"] = play.get("result", {}).get("strength", {}).get("code", None)
        row_data["emptyNet"] = play.get("result", {}).get("emptyNet", False)
        shooter_name, shooter_id = self.get_player_info(play, "Scorer")
        goalie_name, goalie_id = self.get_player_info(play, "Goalie")
        row_data["shooter"] = shooter_name
        row_data["goalie"] = goalie_name
        row_data["shooterId"] = int(shooter_id)
        row_data["goalieId"] = goalie_id

    def populate_shot_data(self, play, row_data):
        row_data["shotType"] = play.get("result", {}).get("secondaryType", None)
        shooter_name, shooter_id = self.get_player_info(play, "Shooter")
        goalie_name, goalie_id = self.get_player_info(play, "Goalie")
        row_data["shooter"] = shooter_name
        row_data["goalie"] = goalie_name
        row_data["shooterId"] = int(shooter_id)
        row_data["goalieId"] = goalie_id

    def populate_penalty_data(self, play, row_data):
        row_data["penaltySeverity"] = play.get("result", {}).get("penaltySeverity", None)
        row_data["penaltyMinutes"] = play.get("result", {}).get("penaltyMinutes", None)
        penalized_team = play.get("team", {}).get("triCode", None)
        row_data["penalizedTeam"] = penalized_team

    def populate_blocked_shot_data(self, play, row_data):
        shooter_name, shooter_id = self.get_player_info(play, "Shooter")
        row_data["shooter"] = shooter_name
        row_data["shooterId"] = int(shooter_id)

    def populate_missed_shot_data(self, play, row_data):
        shooter_name, shooter_id = self.get_player_info(play, "Shooter")
        row_data["shooter"] = shooter_name
        row_data["shooterId"] = int(shooter_id)

    def get_player_info(self, play, player_type):
        for player in play.get("players", []):
            if player.get("playerType", "") == player_type:
                player_name = player.get("player", {}).get("fullName", None)
                player_id = player.get("player", {}).get("id", None)
                return player_name, player_id
        return None, None

    def __add__(self, other):
        if not isinstance(other, JsonParser):
            raise ValueError("Can only add JsonParser objects.")
        combined_df = pd.concat([self.df, other.df], ignore_index=True)
        return JsonParser(df=combined_df)

    @staticmethod
    def load_all_seasons(
        path_csv_output : Path,
        seasons_to_consider : list[int],
        shotGoalOnly: bool):
        
        
        if os.path.exists(path_csv_output):
            df = pd.read_csv(path_csv_output, parse_dates=["gameDate"])
            logger.info(f"DataFrame loaded from {path_csv_output}")
            return df

        base_parser = JsonParser()

        ROOT_DATA = Path(os.getenv("DATA_FOLDER"))


        all_seasons = sorted(list(filter(
            lambda s : s in seasons_to_consider,
            os.listdir(ROOT_DATA)
        )))

        with tqdm(total=len(all_seasons)) as pbar1:
            for season in all_seasons:
                pbar1.set_description(f"Processing json files of season {season}")
                base_path = ROOT_DATA / season
                all_games = os.listdir(base_path)
                with tqdm(total=len(all_games)) as pbar2:
                    for game in all_games:
                        pbar2.set_description(f"Parsing json file {game}")
                        parser = JsonParser(str(base_path / game))
                        base_parser = base_parser + parser
                        pbar2.update(1)
                pbar1.update(1)

        OUTPUT_PATH = ROOT_DATA / path_csv_output
        base_parser.df.to_csv(OUTPUT_PATH, index=False)
        logger.info(f"DataFrame saved to {OUTPUT_PATH}")
        return base_parser.df

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

    JsonParser.load_all_seasons(
        args.path_to_csv,
        args.years,
        args.shotGoalOnly
    )