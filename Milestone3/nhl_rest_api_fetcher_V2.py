from dataclasses import field
from pathlib import Path
from typing import Dict, Tuple
import os
import urllib
from Milestone1.nhl_rest_api_fetcher import Base_Fetcher

from pregex.core.quantifiers import Optional
from pregex.core.groups import Capture
from pregex.core.operators import Either
from pregex.core.classes import AnyDigit
from pregex.core.assertions import MatchAtEnd, MatchAtStart

from loguru import logger


class Game_endpoints_Fetcher_v2(Base_Fetcher):
    """SubClass of Base_Fetcher that will be used to fetch GAME-RELATED endpoints from the NHL REST API

    Args:
        Base_Fetcher (_type_): Base class implementing fetch() method and other useful attributes

    Raises:
        RuntimeError: if the user provides a bad endpoint path that does not match the regex self.ALLOWED_ENDPOINT_PATH
        RuntimeError: if the user provides a bad game_id that does not match the regex self.GAME_ID
        RuntimeError: if the user specified the endpoint /feed/live/diffPatch without specifying query parameters
    """    

    """
    To understand more on the verification done in the below REGEX
    go here https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md?ref_type=heads#game-endpoints
    """

    
    # TODO: Retravailler le premier groupe de la regex qui controle lannee de la saison
    # pour respect cette condition : 1917 <= 4_premiers_digits <= current_year
    
    GAME_ID = (
        MatchAtStart(Capture(4 * AnyDigit()))
        + Capture("0" + Either("1", "2", "3", "4"))
        + MatchAtEnd(Capture(4 * AnyDigit()))
    )

    
    # TODO: Retravailler la regex GAME_ID ci-dessus car il ne peut pas y avoir MatchAtEnd ou MatchAtStart
    # et l'utiliser dans la regex en dessous
    
    ALLOWED_ENDPOINT_PATH = Either(
        MatchAtStart("gamecenter/")
            + 4 * AnyDigit()
            + "0"
            + Either("1", "2", "3", "4")
            + 4 * AnyDigit()
            + MatchAtEnd(
                Capture(
                    Either(
                        "/play-by-play",
                    )
                )
        ),
    )

    def __init__(self, path: str, query_parameters: Dict[str, str] = None):
        """
        https://api-web.nhle.com/v1/gamecenter/{GAME_ID}/play-by-play

        Par exemple, le match 2022030411, peut être trouvé ici :
            https://api-web.nhle.com/v1/gamecenter/2022030411/play-by-play

        Args:
            path (str): ENDPOINT PATH to fetch of the NHL REST API
            query_parameters (Dict[str, str], optional): Parameter for the GET Request. Defaults to None.

        """
        super().__init__(path, query_parameters)

        self.netloc = "api-web.nhle.com"
        self.root_path = Path("/v1/")

        token_1, game_id, *_ = path.split("/")

        if token_1 == "gamecenter":
            self._verify_game_id(game_id)

        self._verify_endpoint_path(path)

        if (
            self.subpath_if_game_endpoint == "/feed/live/diffPatch"
            and query_parameters is None
        ):
            raise RuntimeError(
                f"""
                            YOU USED QUERY PATH /feed/live/diffPatch
                               WITHOUT SPECIFTYING PARAMETERS
                            CAN NOT CONTINUE
                            see https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md?ref_type=heads#games
                               """
            )

        if query_parameters is not None:
            self.query = urllib.parse.urlencode(query_parameters)

        self.path = generate_url_path(self.root_path, path, use_posix=True)

    def _verify_endpoint_path(self, endpoint_path: str) -> None:
        """Verify if self.ALLOWED_ENDPOINT_PATH matches the endpoint path provided by the user
        
        if match happened successfully we add a class attribute which is 
            the subpath of the game endpoint in `self.subpath_if_game_endpoint`
            i.e. in '/game/{gameid}/feed/live' the subpath is '/feed/live'

        Args:
            endpoint_path (str): endpoint path provided by the user

        Raises:
            RuntimeError: if the user provides a bad endpoint path that does not match the regex self.ALLOWED_ENDPOINT_PATH
        """        
        if self.ALLOWED_ENDPOINT_PATH.get_matches(endpoint_path) != []:
            logger.info(
                f"Endpoint path provided by user is correct : {self.root_path}/{endpoint_path} "
            )

            self.subpath_if_game_endpoint, *_ = self.ALLOWED_ENDPOINT_PATH.get_captures(
                endpoint_path
            )[0]

        else:
            raise RuntimeError(
                f"""
                YOU PROVIDED A BAD ENDPOINT PATH {endpoint_path}
                SEE MORE information on https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md?ref_type=heads#game-endpoints
                CAN NOT CONTINUE THE GET REQUEST
                """
            )

    def _verify_game_id(self, game_id : str) -> None:
        """Verify if the game_id provided by the user is correct
        Called only if the user specified an endpoint path as followed '/game/{game_id}'

        if match happened successfully we add a class attribute which is 
            the 3 components of gameId in respectively self.season_of_the_game, self.type_of_game, self.game_number
            i.e. in '2016020001' the 3 components are ('2016', '02', '0001')
        
        Args:
            game_id (str): game id provided by the user

        Raises:
            RuntimeError: if the user provides a bad game_id that does not match the regex self.GAME_ID
        """            
        if self.GAME_ID.get_matches(game_id) != []:
            logger.info(f"Game id provided by user {game_id} is correct")
            (
                self.season_of_the_game,
                self.type_of_game,
                self.game_number,
            ) = self.GAME_ID.get_captures(game_id)[0]
        else:
            raise RuntimeError(
                f"""
                YOU PROVIDED A BAD GAME_ID {game_id}
                SEE MORE information on https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md?ref_type=heads#game-ids
                CAN NOT CONTINUE THE GET REQUEST
                """
            )
        
def generate_url_path(*parts, use_posix=False):
    '''
    Emerges from the problem of running this script on Windows and Linux.
    Needed an OS-agnostic way to generate an url path (mainly used in the GET request endpoint path)
    '''
    path = Path(*parts)
    return path.as_posix() if use_posix else str(path)

def init_logger():
    '''
    Initialize the logger that will log into some files and not on stdout
    We use the loguru library so it takes care of the rotation/renaming of the logs file 
        and offer less boilerplate code than the standard logging library...
    '''
    logger.add(
        Path(os.getenv('LOGGING_FILE')) / "data_acquisition.log",
        compression="zip",
        level="DEBUG",
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> <green>{elapsed}</green> | <level>{level: <8}</level> | <cyan>{file}</cyan>:<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )

    # Remove print on stdout (otherwise hide the progress bars)
    logger.remove(0)

if __name__ == "__main__":

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    from utils.misc import init_logger, verify_dotenv_file

    verify_dotenv_file(Path(__file__).parent.parent)
    logger = init_logger("nhl_rest_api_fetcher_v2.log")

    game_id = "2022030411"

    path_save_local = Path(os.getenv('DATA_FOLDER')) / "v2_api" / f"{game_id}.json"
    path_save_local.parent.mkdir(parents=True, exist_ok=True)

    # Test the class Game_endpoints_Fetcher_v2
    output = Game_endpoints_Fetcher_v2(
        f"gamecenter/{game_id}/play-by-play"
    ).fetch(save_local=path_save_local)