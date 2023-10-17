import pandas as pd
import json
from tqdm import tqdm
import datetime
import os

class JsonParser:
    """
    Class to Parse the json files from the NHL API to construct a DataFrame.
    
    For now, the solel useful use of this class is to instantiate it via the static method `load_all_seasons`.
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
            self.df = self.parse_json_file()
        else:
            self.df = pd.DataFrame()

    # TODO :    def safe_getitem_dict(
    #         self, 
    #         dict, 
    #         list_key, 
    #         leaf_value_default
    #     ):


    def parse_json_file(self):
        '''
        The most important function of the class.
        Parse the json file and return a DataFrame containing the plays.
        '''
        with open(self.path, "r") as f:
            data = json.load(f)

        gameData = data["gameData"]
        liveData = data["liveData"]["plays"]["allPlays"]
        rinkSide = data["liveData"]["linescore"]["periods"]

        gameId = int(gameData.get("game", {}).get("pk", None))
        season = int(gameData.get("game", {}).get("season", None)[0:4])
        gameType = gameData.get("game", {}).get("type", None)
        gameDate = datetime.datetime.strptime(gameData.get("datetime", {}).get("dateTime", ""), "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d") if gameData.get("datetime", {}).get("dateTime", None) else None
        homeTeam = gameData.get("teams", {}).get("home", {}).get("abbreviation", None)
        awayTeam = gameData.get("teams", {}).get("away", {}).get("abbreviation", None)

        rink_side_dict = {}
        for period_info in rinkSide:
            period_num = period_info.get('num', None)
            rink_side_dict[period_num] = {
                'home': period_info.get('home', {}).get('rinkSide', None),
                'away': period_info.get('away', {}).get('rinkSide', None)
            }

        rows = []
        base_data = {
            "gameId": gameId,
            "season": season,
            "gameType": gameType,
            "gameDate": gameDate,
            "homeTeam": homeTeam,
            "awayTeam": awayTeam,
        }

        for play in liveData:
            row_data = base_data.copy()

            if play["result"]["eventTypeId"] in ["GOAL", "SHOT"]:

                period = int(play.get("about", {}).get("period", None))
                periodTime = play.get("about", {}).get("periodTime", None)
                byTeam = play.get("team", {}).get("triCode", None)
                eventType = play.get("result", {}).get("eventTypeId", None)
                shotType = play.get("result", {}).get("secondaryType", None)
                coordinateX = play.get("coordinates", {}).get("x", None)
                coordinateY = play.get("coordinates", {}).get("y", None)
 
                # jq request to see `.liveData.plays.allPlays.[] | select(.result.eventTypeId=="GOAL") | .result.strength | keys`
                strength = play.get("result", {}).get("strength", None) .get("code", None)  if play["result"]["eventTypeId"]=='GOAL' else None
                
                emptyNet = play.get("result", {}).get("emptyNet", False)

                shooterName = None
                goalieName = None  

                for player in play.get("players", []):
                    if player.get("playerType", "") in ["Scorer", "Shooter"]:
                        shooterName = player.get("player", {}).get("fullName", None)
                    elif player.get("playerType", "") == "Goalie":
                        goalieName = player.get("player", {}).get("fullName", None)

                if period == 5:
                    row_data['rinkSide'] = 'Shootout'
                else:
                    row_data['rinkSide'] = rink_side_dict.get(period, {}).get('home' if byTeam == homeTeam else 'away', None)

                row_data.update({
                    "period": period,
                    "periodTime": periodTime,
                    "byTeam": byTeam,
                    "eventType": eventType,
                    "shotType": shotType,
                    "coordinateX": coordinateX,
                    "coordinateY": coordinateY,
                    "shooterName": shooterName,
                    "goalieName": goalieName,
                    "strength": strength,
                    "emptyNet": emptyNet,
                })

                rows.append(row_data)

        df = pd.DataFrame(rows)
        
        return df

    def __add__(self, other):
        if not isinstance(other, JsonParser):
            raise ValueError("Can only add JsonParser objects.")
        combined_df = pd.concat([self.df, other.df], ignore_index=True)
        return JsonParser(df=combined_df)

    @staticmethod
    def load_all_seasons():
        '''
        This the main function through which any object should be instantiated.

        It will parse every json file in the `./data/` folder and
            leveraing the `__add__` method, it will return a big DataFrame containing all the plays.
        '''
        if os.path.exists("clean_data.csv"):
            df = pd.read_csv("clean_data.csv", parse_dates=["gameDate"])
            print("DataFrame loaded from 'clean_data.csv'")
            return df

        base_parser = JsonParser()

        all_seasons = os.listdir("./data/")
        for season in tqdm(all_seasons, desc="Processing seasons"):
            base_path = f"./data/{season}"
            all_games = os.listdir(base_path)
            for game in tqdm(all_games, desc=f"Processing games in {season}", leave=False):
                parser = JsonParser(base_path + f"/{game}")
                base_parser = base_parser + parser

        base_parser.df.to_csv("clean_data.csv", index=False)
        print("DataFrame saved to 'clean_data.csv'")
        return base_parser.df

if __name__ == "__main__":
    df = JsonParser.load_all_seasons()