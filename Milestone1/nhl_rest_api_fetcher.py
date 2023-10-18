"""
Inspired from the general structure of an URL:
    scheme://netloc/path;parameters?query#fragment.
In our case : 
    https://statsapi.web.nhl.com/api/v1/subpath?query.  

We choose an OOP approach to build the NHL REST API Fetcher objects, 
    with in mind a Base_Fetcher Class that will be inherited by other classes
    that corresponds to the different TYPES of endpoints of the NHL REST API.

For now, we have only leveraged two types of endpoints so we have two subclasses :
    - Game_endpoints_Fetcher
    - Schedule_endpoints_Fetcher

Mainly, the Base Class allows to factor out 
    the common attributes (such as part of urls that stays the same) 
    and methods (such as the one that actually make the GET request).

Especially, we delegate the verification of the endpoint path to the subclasses.
    Each subclass must a variable ALLOWED_ENDPOINT_PATH that is a regex that
    will be used to verify the endpoint path provided by the user.

This permits us to have a more flexible code that can be easily extended to other types of endpoints
if the following Milestones would require it.

For now, the script just needs an external config system (Hydra or CLI Interface) to be more flexible regarding Execution Parameters...
"""

import json
import os
import urllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Literal, Tuple, Union
import requests
import urllib3
from pregex.core.quantifiers import Optional
from pregex.core.groups import Capture
from pregex.core.operators import Either
from pregex.core.classes import AnyDigit
from pregex.core.assertions import MatchAtEnd, MatchAtStart
from dotenv import load_dotenv
from loguru import logger

@dataclass
class Base_Fetcher:
    '''
    Base class that will be inherited by the other classes.
    One important method is the `fetch()` method that will make the GET request
    '''

    # BASE attributes for common part of the url
    path: str
    query: Dict[str, str]
    scheme: str = "https"
    netloc: str = "statsapi.web.nhl.com"

    root_path: Path = Path("/api/v1/")
    output_format: Tuple[str] = field(
        init=False, default=("json", "binary", "text", "raw")
    )

    def fetch(
        self, 
        output_format: Literal["json", "binary", "text", "raw"] = "json",
        save_local: str = None,
    ) -> Union[dict, bytes, str, urllib3.response.HTTPResponse]:
        """Function that makes the GET request to an NHL REST API endpoint path
            and return the response in the format specified by the user (in our case will mainly be json).

            if save_local is not None, the response will be saved locally at the path specified by the user.
                and if save_local is not None and the file already exists, the GET request will be skipped.
        Args:
            output_format (str, optional): output format of the GET Request. Defaults to "json".
            save_local (str, optional): path to save json file, if already. Defaults to None.

        Raises:
            RuntimeError: if output_format is one of ["json", "binary", "text", "raw"]

        Returns:
            Union[dict, bytes, str, urllib3.response.HTTPResponse]: in our case will mainly be json --> so returning a dict
        """        ''''''
        
        if output_format not in self.output_format:
            raise RuntimeError(
                f"""
                        OUTPUT SUPPORTED IN GET REQUESTS ARE : {self.output_format}
                        YOU SPECIFIED {output_format}
                               """
            )

        if save_local is not None and Path(save_local).exists():
            logger.info(
                f'File already locally existing {save_local}. Skipping download {generate_url_path(self.path, use_posix=True)}{self.query if self.query else ""} '
            )
            return self._read_content_from_local(save_local, output_format)

        url_to_fetch = urllib.parse.urlunparse(
            (self.scheme, self.netloc, generate_url_path(self.path, use_posix=True), None, self.query, None)
        )

        response = requests.get(url=url_to_fetch)

        logger.info(
            f"GET Request happened successfully at {response.url} , {response.status_code}"
        )

        self.response = None

        if output_format == "json":
            self.response = response.json()
        if output_format == "binary":
            self.response = response.content
        if output_format == "text":
            self.response = response.text
        if output_format == "raw":
            self.response = response.raw

        if save_local is not None:
            self._save_local(save_local)

        return self.response

    def _read_content_from_local(self, save_local: str, output_format: str):

        """In case the json file already exists locally, function is called by `fectch()` to read the content of the file

        Raises:
            NotImplementedError: if the user provides an output_format that we don't to read from locally

        Returns:
            _type_: dict, bytes, str
        """        
        if output_format == "json":
            with open(save_local, "r") as file:
                return json.load(file)

        if output_format == "binary":
            with open(save_local, "rb") as file:
                return file.read(save_local)

        if output_format == "text":
            with open(save_local, "r") as file:
                return file.read(save_local)

        if isinstance(self.response, urllib3.response.HTTPResponse):
            raise NotImplementedError(
                "DONT KNOW HOT TO SERIALIZE A urllib3.response.HTTPResponse PYTHON OBJECT"
            )

    def _save_local(self, path : str):
        """Save locally the response of the GET request

        Args:
            path (str): path to save locally te file

        Raises:
            NotImplementedError: dont know how to serialize locally a urllib3.response.HTTPResponse object
        """        
        if isinstance(self.response, dict):
            with open(path, "w") as file:
                json.dump(self.response, file, indent=4)

        if isinstance(self.response, bytes):
            with open(path, "wb") as file:
                file.write(self.response)

        if isinstance(self.response, bytes):
            with open(path, "w") as file:
                file.write(self.response)

        if isinstance(self.response, urllib3.response.HTTPResponse):
            raise NotImplementedError(
                "DONT KNOW HOT TO SERIALIZE A urllib3.response.HTTPResponse PYTHON OBJECT"
            )


class Game_endpoints_Fetcher(Base_Fetcher):
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
        MatchAtStart("game/")
            + 4 * AnyDigit()
            + "0"
            + Either("1", "2", "3", "4")
            + 4 * AnyDigit()
            + MatchAtEnd(
                Capture(
                    Either(
                        "/feed/live" + Optional("/diffPatch"),
                        "/boxscore",
                        "/linescore",
                        "/content",
                    )
                )
        ),
        MatchAtStart(MatchAtEnd("gameStatus")),
        MatchAtStart(MatchAtEnd("gameTypes")),
        MatchAtStart(MatchAtEnd("playTypes")),
    )

    def __init__(self, path: str, query_parameters: Dict[str, str] = None):
        """
        To understand more on the verification done here
        go here https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md?ref_type=heads#game-endpoints

        Args:
            path (str): ENDPOINT PATH to fetch of the NHL REST API
            query_parameters (Dict[str, str], optional): Parameter for the GET Request. Defaults to None.

        Raises:
            RuntimeError: if `path` == '/feed/live/diffPatch' and `query_parameters` == None
        """
        super().__init__(path, query_parameters)

        token_1, game_id, *_ = path.split("/")

        if token_1 == "game":
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


class Schedule_endpoints_Fetcher(Base_Fetcher):
    """SubClass of Base_Fetcher that will be used to fetch SCHEDULE-RELATED endpoints from the NHL REST AP

    Args:
        Base_Fetcher (_type_): Base class implementing fetch() method and other useful attributes

    Raises:
        RuntimeError: if the user provides a bad endpoint path that does not match the regex self.ALLOWED_ENDPOINT_PATH
    """    


    # TODO: Ecrire une regex qui verifie https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md?ref_type=heads#schedule-modifiers
    # dans les query ajoute par l'user
    # TODO: Retravailler la Optional regex pour le cas 'seasons' pour imposer une ecriture des annees 
    
    ALLOWED_ENDPOINT_PATH = Either(
        MatchAtEnd(MatchAtStart("schedule")),
        MatchAtStart("seasons")
        + MatchAtEnd(Optional("/" + Either(AnyDigit() * 8, "/current"))),
    )

    def __init__(self, path: str, query_parameters: Dict[str, str] = None):
        """Schedule_endpoints_Fetcher constructor
        To understand more on the verification done in this function
        go here https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md?ref_type=heads#game-endpoints

        Args:
            path (str): ENDPOINT PATH to fetch of the NHL REST API
            query_parameters (Dict[str, str], optional): Parameter for the GET Request . Defaults to None.
        """        
        super().__init__(path, query_parameters)

        self._verify_endpoint_path(path)

        if query_parameters is not None:
            self.query = urllib.parse.urlencode(query_parameters)

        self.path = generate_url_path(self.root_path, path, use_posix=True)

    def _verify_endpoint_path(self, endpoint_path: str) -> None:
        if self.ALLOWED_ENDPOINT_PATH.get_matches(endpoint_path) != []:
            logger.info(
                f"Endpoint path provided by user is correct : {self.root_path}/{endpoint_path} "
            )

        else:
            raise RuntimeError(
                f"""
                YOU PROVIDED A BAD ENDPOINT PATH {endpoint_path}
                SEE MORE information on https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md?ref_type=heads#schedule-endpoints
                CAN NOT CONTINUE THE GET REQUEST
                """
            )


def regular_playoff_p_by_p_data_per_season():
    '''
    For now, Main Entrypoint of the script.
    Will instantiate the Schedule_endpoints_Fetcher and Game_endpoints_Fetcher classes
    in order to fetch the data from the NHL REST API and save them locally.


    '''
    from tqdm import tqdm, trange

    #TODO : Refactor list of years using a config file. 
    #       Generally make this file more flexible by using external config files
    # such as with Hydra library OR with a CLI Interface
    for year in trange(2016, 2021, desc=f"Iterating on year"):
        
        response = Schedule_endpoints_Fetcher(
            path="schedule",
            query_parameters={"season": f"{year}{year+1}", "gameType": "R,P"},
        ).fetch()

        game_ids = []
        for date_data in response["dates"]:
            for game in date_data["games"]:
                game_ids.append(game["gamePk"])

        with tqdm(total=len(game_ids)) as pbar:
            for id in game_ids:
                path_save_local = Path(os.getenv('DATA_FOLDER')) / str(year) / f"{id}.json"
                path_save_local.parent.mkdir(parents=True, exist_ok=True)
                pbar.set_description(
                    f"Fetching game/{id}/feed/live saved at {path_save_local}"
                )
                pbar.update(1)
                Game_endpoints_Fetcher(f"game/{id}/feed/live").fetch(
                    save_local=path_save_local
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
    if load_dotenv(Path(__file__).parent.parent / '.env',verbose=True):
        init_logger()
        regular_playoff_p_by_p_data_per_season()
    else:
        raise RuntimeError("COULD NOT LOAD THE .env FILE")
