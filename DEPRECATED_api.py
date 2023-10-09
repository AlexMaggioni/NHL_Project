import datetime
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

class NHL_API:

    def __init__(self, season: str):
        
        season = str(season)
        
        # Valider la saison
        current_year = datetime.datetime.now().year
        if not (1917 <= int(season) <= current_year):
            raise ValueError(f"Saison invalide. Les saisons existantes vont de 1917 à {current_year} inclusivement.")

        self.season = season

    def load_season(self):
        
        season_data_path = os.getenv("DATA_FOLDER") + self.season + '/'
        
        if os.path.exists(season_data_path):
            
            print(f'Les donnée pour la saison {self.season} sont déjà téléchargées')
            return

        else:
            
            # Créer un dossier pour les données
            os.mkdir(season_data_path)

            # Avoir la liste de tous les ID des parties de la saison
            id_path = os.getenv("BASE_URL") + 'schedule?season=' + self.season + str(int(self.season) + 1) + '&gameType=R,P'
            all_games = requests.get(id_path).json()
            game_ids = []
            for date_data in all_games['dates']:
                for game in date_data['games']:
                    game_ids.append(game['gamePk'])

            for id in game_ids:
                response = requests.get(os.getenv("BASE_URL") + 'game/' + str(id) + '/feed/live/')
                with open(season_data_path + str(id) + '.json', 'w') as file:
                    json.dump(response.json(), file, indent=4)

if __name__ == "__main__":

    for season in range(2016, 2021):
        nhl_api_instance = NHL_API(season)
        nhl_api_instance.load_season()