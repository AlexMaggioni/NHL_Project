import pandas as pd
import json
from tqdm import tqdm
import datetime
import os

class JsonParser:

    def __init__(self, path=None, df=None):
        # You might either initialize with a path or with an existing DataFrame.
        self.path = path
        if df is not None:
            self.df = df
        elif path:
            self.df = self.parse_json_file()
        else:
            self.df = pd.DataFrame()

    def parse_json_file(self):
        with open(self.path, "r") as f:
            data = json.load(f)

        gameData = data["gameData"]
        liveData = data["liveData"]["plays"]["allPlays"]

        GAME_ID = gameData.get("game", {}).get("pk", None)
        SEASON = gameData.get("game", {}).get("season", None)
        GAME_TYPE = gameData.get("game", {}).get("type", None)
        GAME_DATE = datetime.datetime.strptime(gameData.get("datetime", {}).get("dateTime", ""), "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d") if gameData.get("datetime", {}).get("dateTime", None) else None
        HOME_TEAM = gameData.get("teams", {}).get("home", {}).get("abbreviation", None)
        AWAY_TEAM = gameData.get("teams", {}).get("away", {}).get("abbreviation", None)

        rows = []
        base_data = {
            "GAME_ID": GAME_ID,
            "SEASON": SEASON,
            "GAME_TYPE": GAME_TYPE,
            "GAME_DATE": GAME_DATE,
            "HOME_TEAM": HOME_TEAM,
            "AWAY_TEAM": AWAY_TEAM,
        }

        for play in liveData:
            row_data = base_data.copy()

            if play["result"]["eventTypeId"] in ["GOAL", "SHOT"]:
                PERIOD = play.get("about", {}).get("period", None)
                PERIOD_TIME = play.get("about", {}).get("periodTime", None)
                BY = play.get("team", {}).get("triCode", None)
                EVENT_TYPE = play.get("result", {}).get("eventTypeId", None)
                COORDINATES = (play.get("coordinates", {}).get("x", None), 
                               play.get("coordinates", {}).get("y", None))
                STRENGTH = play.get("result", {}).get("strength", {}).get("code", None)
                EMPTY_NET = play.get("result", {}).get("emptyNet", None)

                SHOOTER_NAME = None
                GOALIE_NAME = None  

                for player in play.get("players", []):
                    if player.get("playerType", "") in ["Scorer", "Shooter"]:
                        SHOOTER_NAME = player.get("player", {}).get("fullName", None)
                    elif player.get("playerType", "") == "Goalie":
                        GOALIE_NAME = player.get("player", {}).get("fullName", None)
            
                row_data.update({
                    "PERIOD": PERIOD,
                    "PERIOD_TIME": PERIOD_TIME,
                    "BY": BY,
                    "EVENT_TYPE": EVENT_TYPE,
                    "COORDINATES": COORDINATES,
                    "SHOOTER_NAME": SHOOTER_NAME,
                    "GOALIE_NAME": GOALIE_NAME,
                    "STRENGTH": STRENGTH,
                    "EMPTY_NET": EMPTY_NET,
                })

                rows.append(row_data)

        return pd.DataFrame(rows)

    def __add__(self, other):
        if not isinstance(other, JsonParser):
            raise ValueError("Can only add JsonParser objects.")
        combined_df = pd.concat([self.df, other.df], ignore_index=True)
        return JsonParser(df=combined_df)

    @staticmethod
    def load_all_seasons():
        if os.path.exists("clean_data.csv"):
            df = pd.read_csv("clean_data.csv")
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
