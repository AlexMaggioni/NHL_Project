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


 
@dataclass(frozen=True)
class Base_Scrapper:

    scheme: str = 'https'
    netloc: str = 'statsapi.web.nhl.com'
    root_path : Path = Path('/api/v1/')
    path : str
    query : Dict[str,str]

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
        
        url_to_fetch = urllib.parse.urlunparse(
            (
                self.scheme,
                self.netloc,
                self.path,
                None, 
                urllib.parse.urlencode(self.query),
                None
            )
        )
    
        response = requests.get(url=url_to_fetch)

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

    def _save_local(self, path):
        if isinstance(self.response,dict):
            with open(path, 'w') as file:
                json.dump(response.json(), file, indent=4)

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
        super().__init__()
        
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
        if self.ALLOWED_ENDPOINT_PATH.get_matches() == []:
            print(f'Endpoint path provided by user {endpoint_path} is correct')

            self.subpath_if_game_endpoint, *_ = self.ALLOWED_ENDPOINT_PATH.get_captures(endpoint_path)[0]
            

        else:
            raise RuntimeError(f'''
                                YOU PROVIDED A BAD ENDPOINT PATH {endpoint_path}
                                SEE MORE information on https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md?ref_type=heads#game-endpoints
                                CAN NOT CONTINUE THE GET REQUEST
                                ''')
        
    def _verify_game_id(self, game_id) -> None:
        if self.GAME_ID.get_matches(game_id) == []:
            print(f'Game id provided by user {game_id} is correct')
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
        super().__init__()

        self._verify_endpoint_path(path)

        if query_parameters is not None:
            self.query = urllib.parse.urlencode(query_parameters)

        self.path = str(self.root_path / path)

    def _verify_endpoint_path(self, endpoint_path : str) -> None:
        if self.ALLOWED_ENDPOINT_PATH.get_matches() == []:
            print(f'Endpoint path provided by user {endpoint_path} is correct')            

        else:
            raise RuntimeError(f'''
                                YOU PROVIDED A BAD ENDPOINT PATH {endpoint_path}
                                SEE MORE information on https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md?ref_type=heads#schedule-endpoints
                                CAN NOT CONTINUE THE GET REQUEST
                                ''')
        
    def _verify_game_id(self, game_id) -> None:
        if self.GAME_ID.get_matches(game_id) == []:
            print(f'Game id provided by user {game_id} is correct')
            self.season_of_the_game, self.type_of_game, self.game_number = self.GAME_ID.get_captures(game_id)[0]
        else:
            raise RuntimeError(f'''
                                YOU PROVIDED A BAD GAME_ID {game_id}
                                SEE MORE information on https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md?ref_type=heads#game-ids
                                CAN NOT CONTINUE THE GET REQUEST
                                ''')

if __name__=='__main__':

    for year in range(2016,2021):
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

        for id in game_ids:
            path_save_local = Path('./data') / year / f'{id}.json'
            Game_endpoints_Scrapper(f'game/{id}/feed/live/').fetch(save_local=path_save_local)