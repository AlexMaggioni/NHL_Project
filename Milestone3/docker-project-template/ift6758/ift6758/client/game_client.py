
import logging
import os
from pathlib import Path
import tempfile
import omegaconf
from rich.logging import RichHandler


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(RichHandler())

class GameClient:
    '''
    Note about the cache design:
        it is a sqllite file (that will be created in the user's home directory if any path is provided)
            with a table per game_id (the name of the table is the game_id)
                and two columns 'id' (str type, id of samples already seen) and 'isGoal_prob_pred' (float type, the prediction of the model)

        The cache is updated at each request (if the sample is not already in the cache)
            and is used to avoid sending the same sample to the model multiple times
    
    '''

    def __init__(
            self,
            game_id: str,
            nhl_api_version: str = "v1",
            cache_sqllite_path_file : str = None,
        ) -> None:
        
        self.game_id = game_id
        self.nhl_api_version = nhl_api_version
        self.cache_sqllite_path_file = Path(cache_sqllite_path_file)
        self._init_cache()
        self.cache_sqllite_path_file.parent.mkdir(parents=True, exist_ok=True)

    def _init_cache(self) -> None:
        """
        Initialize cache for a given game ID.
        """

        logger.info(f"Initializing cache")
        if self.cache_sqllite_path_file is None:
            self.cache_sqllite_path_file = Path.home() / 'cache.sqlite3'
            logger("No cache file provided, using default cache file at {self.cache_sqllite_path_file}")


    def fetch_nhl_api(self, output_path_raw_data) -> Path:
        """
        Fetches data from NHL API for a given game ID.
        """

        logger.info(f"Fetching data for game {self.game_id} from NHL API {self.nhl_api_version}")

        if self.nhl_api_version == "v1":
            from ..data.nhl_rest_api_fetcher import Game_endpoints_Fetcher
            response_raw_data = Game_endpoints_Fetcher(f"game/{self.game_id}/feed/live").fetch(
                        output_format="json",
                        save_local=output_path_raw_data,
                    )
        elif self.nhl_api_version == "v2":
            from ..data.nhl_rest_api_fetcher_V2 import Game_endpoints_Fetcher_v2
            response_raw_data = Game_endpoints_Fetcher_v2(
                        f"gamecenter/{self.game_id}/play-by-play"
                    ).fetch(
                        output_format="json",
                        save_local=output_path_raw_data,
                    )
        
        return response_raw_data, output_path_raw_data
    
    def parse_raw_data(self, output_path_csv, raw_json_path) -> Path:
        """
        Parses raw data to create a dataframe.
        """

        logger.info(f"Parsing raw data for game {self.game_id} from raw json file {raw_json_path}")
        if self.nhl_api_version == "v1":
            from ..data.json_scrapper import JsonParser
            parser_obj = JsonParser.load_all_seasons(raw_json_path)

        elif self.nhl_api_version == "v2":
            from ..data.json_scrapper_v2 import JsonParser_v2
            parser_obj = JsonParser_v2.load_all_seasons(
                path_csv_output = output_path_csv,
                json_files_to_consider = [Path(raw_json_path)],
                shotGoalOnly=True,
            )
        
        return parser_obj


    def get_game_data(self) -> dict:
        """
        Fetches game data from NHL API for a given game ID.
        """

        # --------------------- Fetching data from NHL API
        json_output_path = Path(os.getenv('DATA_FOLDER')) / 'raw_data' / f'{self.game_id}.json'
        json_output_path.parent.mkdir(parents=True, exist_ok=True)
        raw_json_data, raw_json_path = self.fetch_nhl_api(json_output_path)

        # --------------------- Parsing raw data to create a dataframe
        csv_output_path = Path(os.getenv('DATA_FOLDER')) / 'scrapped_json' / f'{self.game_id}.csv'
        csv_output_path.parent.mkdir(parents=True, exist_ok=True)
        parser_obj = self.parse_raw_data(
            csv_output_path, 
            raw_json_path
        )
        
        # --------------------- Feature engineering data
        ROOT_PROJECT_PATH = Path(__file__).parent.parent

        from ..data.utils import create_engineered_data_object
        FEAT_ENG_CONF = omegaconf.OmegaConf.load( ROOT_PROJECT_PATH  / 'data/conf' / 'feature_engineering_inference.yaml')    

        feat_eng_data = create_engineered_data_object(
            RAW_DATA_PATH = parser_obj.output_path,
            DATA_PIPELINE_CONFIG = FEAT_ENG_CONF,
            version = FEAT_ENG_CONF.feature_engineering_version,
        )

        # --------------------- Preprocessing data
        from ..data.utils import create_preprocessor_data_object
        PREPROC_DATA_CONF = omegaconf.OmegaConf.load(ROOT_PROJECT_PATH / 'data/conf' / 'data_preprocessing_inference.yaml')

        data_preprocessor = create_preprocessor_data_object(
            TRAIN_DF = feat_eng_data.dfUnify,
            TEST_DF = feat_eng_data.dfUnify,
            DATA_PIPELINE_CONFIG = PREPROC_DATA_CONF,
        )

        logger.info('SUBSETTING data TO shot-on-goal | goal eventType')
        idx_train = data_preprocessor.X_train.query("eventType == 'shot-on-goal' | eventType == 'goal'").index

        logger.info(f"\t Before subsetting : {data_preprocessor.X_train.shape} rows in train set")
        data_preprocessor.X_train = data_preprocessor.X_train[data_preprocessor.X_train.index.isin(idx_train)]
        data_preprocessor.y_train = data_preprocessor.y_train[data_preprocessor.y_train.index.isin(idx_train)]
        logger.info(f"\t After subsetting : {data_preprocessor.X_train.shape} rows in train set")

        samples_to_predict = self.check_for_already_computed_data_in_cache(data_preprocessor.X_train)

        return samples_to_predict

        
    def check_for_already_computed_data_in_cache(self, samples_df) -> dict:
        """
        Checks if data has already been computed for a given game ID.
        """

        logger.info(f"Checking if data has already been computed for game {self.game_id}")

        from sqlite_utils import Database
        db = Database(self.cache_sqllite_path_file)

        table_already_computed_samples = list(db[self.game_id].rows)

        if len(table_already_computed_samples) > 0:
            already_computed_samples = list(map(lambda x: x['index'], table_already_computed_samples))
        else:
            already_computed_samples = []

        samples_to_predict = samples_df[~samples_df.index.isin(already_computed_samples)]

        return samples_to_predict

