'''
general structure of a URL: 
    scheme://netloc/path;parameters?query#fragment. 
Each tuple item is a string, possibly empty. 
'''

import datetime
import json
import urllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Literal, Tuple, Union
import requests

import urllib3

from pregex.core.quantifiers import Optional
from pregex.core.groups import Capture
from pregex.core.operators import Either
from pregex.meta.essentials import Integer
from pregex.core.classes import AnyLetter, AnyDigit
from pregex.core.assertions import MatchAtEnd,MatchAtStart,EnclosedBy

from loguru import logger

logger.add(
    "log_file/data_acquisition.log", 
    compression="zip", 
    level='DEBUG',
    format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> <green>{elapsed}</green> | <level>{level: <8}</level> | <cyan>{file}</cyan>:<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>'
)

logger.remove(0)
 
@dataclass
class Base_Scrapper:

    path : str
    query : Dict[str,str]

    scheme: str = 'https'
    netloc: str = 'statsapi.web.nhl.com'
    root_path : Path = Path('/api/v1/')
    output_format : Tuple[str] = field(
        init=False,
        default=('json','binary','text','raw')
    )

    def fetch(
            self, 
            output_format  : str= 'json',
            save_local : str = None
        )->Union[dict,bytes,str,urllib3.response.HTTPResponse]:
        
        if output_format not in self.output_format:
            raise RuntimeError(f'''
                        OUTPUT SUPPORTED IN GET REQUESTS ARE : {self.output_format}
                        YOU SPECIFIED {output_format}
                               ''')
        
        if save_local is not None and Path(save_local).exists():
            logger.info(f'File already locally existing {save_local}. Skipping download {self.path}{self.query} ')
            return self._read_content_from_local(save_local,output_format)

        url_to_fetch = urllib.parse.urlunparse(
            (
                self.scheme,
                self.netloc,
                self.path,
                None, 
                self.query,
                None
            )
        )
    
        response = requests.get(url=url_to_fetch)

        logger.info(f'GET Request happened successfully at {response.url} , {response.status_code}')

        self.response = None

        if output_format=='json':
            self.response =  response.json()
        if output_format=='binary':
            self.response = response.content
        if output_format=='text':
            self.response = response.text
        if output_format=='raw':
            self.response = response.raw

        if save_local is not None:
            self._save_local(save_local)

        return self.response

    def _read_content_from_local(
            self,
            save_local : str,
            output_format : str):
        if output_format=='json':
            with open(save_local, 'r') as file:
                return json.load(file)

        if output_format=='binary':
            with open(save_local, 'rb') as file:
                return file.read(save_local)

        if output_format=='text':
            with open(save_local, 'r') as file:
                return file.read(save_local)

        if isinstance(self.response,urllib3.response.HTTPResponse):
            raise NotImplementedError('DONT KNOW HOT TO SERIALIZE A urllib3.response.HTTPResponse PYTHON OBJECT')

    def _save_local(self, path):
        if isinstance(self.response,dict):
            with open(path, 'w') as file:
                json.dump(self.response, file, indent=4)

        if isinstance(self.response,bytes):
            with open(path, 'wb') as file:
                file.write(self.response)

        if isinstance(self.response,bytes):
            with open(path, 'w') as file:
                file.write(self.response)

        if isinstance(self.response,urllib3.response.HTTPResponse):
            raise NotImplementedError('DONT KNOW HOT TO SERIALIZE A urllib3.response.HTTPResponse PYTHON OBJECT')

class Game_endpoints_Scrapper(Base_Scrapper):

    '''
     TODO: Retravailler le premier groupe de la regex qui controle lannee de la saison
     pour cette condition 1917 <= 4_premiers_digits <= current_year
    '''
    GAME_ID = MatchAtStart(Capture(4*AnyDigit())) + Capture('0' + Either('1','2','3','4')) + MatchAtEnd(Capture(4*AnyDigit()))

    '''
        TODO: Retravailler la regex GAME_ID ci-dessus car il ne peut pas y avoir MatchAtEnd ou MatchAtStart
    '''
    ALLOWED_ENDPOINT_PATH = Either(
        MatchAtStart('game/') + 4*AnyDigit() + '0' + Either('1','2','3','4')  + 4*AnyDigit() + MatchAtEnd(Capture(Either('/feed/live'+Optional('/diffPatch'),'/boxscore','/linescore','/content'))),
        MatchAtStart(MatchAtEnd('gameStatus')),
        MatchAtStart(MatchAtEnd('gameTypes')),
        MatchAtStart(MatchAtEnd('playTypes')),
    )

    def __init__(
            self, 
            path : str, 
            query_parameters : Dict[str,str] = None):
        '''
        To understand more on the verification done in this function 
        go here https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md?ref_type=heads#game-endpoints
        '''
        super().__init__(path,query_parameters)
        
        token_1, game_id, *_  = path.split('/')
        
        if token_1 == 'game':
            self._verify_game_id(game_id)

        self._verify_endpoint_path(path)
        
        if self.subpath_if_game_endpoint == '/feed/live/diffPatch' and query_parameters is None:

            raise RuntimeError(f'''
                            YOU USED QUERY PATH /feed/live/diffPatch
                               WITHOUT SPECIFTYING PARAMETERS
                            CAN NOT CONTINUE
                            see https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md?ref_type=heads#games
                               ''')

        if query_parameters is not None:
            self.query = urllib.parse.urlencode(query_parameters)

        self.path = str(self.root_path / path)

    def _verify_endpoint_path(self, endpoint_path : str) -> None:
        if self.ALLOWED_ENDPOINT_PATH.get_matches(endpoint_path) != []:
            logger.info(f'Endpoint path provided by user is correct : {self.root_path}/{endpoint_path} ')

            self.subpath_if_game_endpoint, *_ = self.ALLOWED_ENDPOINT_PATH.get_captures(endpoint_path)[0]
            

        else:
            raise RuntimeError(f'''
                                YOU PROVIDED A BAD ENDPOINT PATH {endpoint_path}
                                SEE MORE information on https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md?ref_type=heads#game-endpoints
                                CAN NOT CONTINUE THE GET REQUEST
                                ''')
        
    def _verify_game_id(self, game_id) -> None:
        if self.GAME_ID.get_matches(game_id) != []:
            logger.info(f'Game id provided by user {game_id} is correct')
            self.season_of_the_game, self.type_of_game, self.game_number = self.GAME_ID.get_captures(game_id)[0]
        else:
            raise RuntimeError(f'''
                                YOU PROVIDED A BAD GAME_ID {game_id}
                                SEE MORE information on https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md?ref_type=heads#game-ids
                                CAN NOT CONTINUE THE GET REQUEST
                                ''')


class Schedule_endpoints_Scrapper(Base_Scrapper):

    '''
     TODO: Ecrire une regex qui verifie https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md?ref_type=heads#schedule-modifiers
     dans les query ajoute par l'user
    '''

    '''
        TODO: Retravailler la Optional regex pour le cas 'seasons' pour preciser l'ecriture des annees 
    '''
    ALLOWED_ENDPOINT_PATH = Either(
        MatchAtEnd(MatchAtStart('schedule')),
        MatchAtStart('seasons') + MatchAtEnd(Optional('/'+Either(AnyDigit()*8,'/current')))
    )

    def __init__(
            self, 
            path : str, 
            query_parameters : Dict[str,str] = None):
        '''
        To understand more on the verification done in this function 
        go here https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md?ref_type=heads#game-endpoints
        '''
        super().__init__(path,query_parameters)

        self._verify_endpoint_path(path)

        if query_parameters is not None:
            self.query = urllib.parse.urlencode(query_parameters)

        self.path = str(self.root_path / path)

    def _verify_endpoint_path(self, endpoint_path : str) -> None:
        if self.ALLOWED_ENDPOINT_PATH.get_matches(endpoint_path) != []:
            logger.info(f'Endpoint path provided by user is correct : {self.root_path}/{endpoint_path} ')            

        else:
            raise RuntimeError(f'''
                                YOU PROVIDED A BAD ENDPOINT PATH {endpoint_path}
                                SEE MORE information on https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md?ref_type=heads#schedule-endpoints
                                CAN NOT CONTINUE THE GET REQUEST
                                ''')
        
    def _verify_game_id(self, game_id) -> None:
        if self.GAME_ID.get_matches(game_id) == []:
            logger.info(f'Game id provided by user {game_id} is correct')
            self.season_of_the_game, self.type_of_game, self.game_number = self.GAME_ID.get_captures(game_id)[0]
        else:
            raise RuntimeError(f'''
                                YOU PROVIDED A BAD GAME_ID {game_id}
                                SEE MORE information on https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md?ref_type=heads#game-ids
                                CAN NOT CONTINUE THE GET REQUEST
                                ''')

if __name__=='__main__':

    from tqdm import tqdm, trange
    
    for year in trange(2016,2021,desc=f'Iterating on year', unit=) :
        response = Schedule_endpoints_Scrapper(
            path='schedule',
            query_parameters={
                'season' : f'{year}{year+1}',
                'gameType' : 'R,P'
            }
        ).fetch()

        game_ids = []
        for date_data in response['dates']:
            for game in date_data['games']:
                game_ids.append(game['gamePk'])
        with tqdm(total=len(game_ids)) as pbar:
            for id in game_ids:
                path_save_local = Path('./data') / str(year) / f'{id}.json'
                path_save_local.parent.mkdir(parents=True,exist_ok=True)
                pbar.set_description(f'Fetching game/{id}/feed/live saved at {path_save_local}')
                pbar.update(1)
                Game_endpoints_Scrapper(f'game/{id}/feed/live').fetch(save_local=path_save_local)