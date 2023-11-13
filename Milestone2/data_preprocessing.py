from pathlib import Path
from typing import List
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold

from rich.console import Console
from rich.table import Table

from utils.misc import unify_coordinates_referential, init_logger, verify_dotenv_file

verify_dotenv_file(Path(__file__).parent.parent)
logger = init_logger("feature_engineering.log")

class NHL_data_preprocessor:

    def __init__(
        self,
        df_train: pd.DataFrame,
        df_test: pd.DataFrame,
        cross_validation_k_fold : int, 
        shuffle_before_splitting : bool, 
        seed : int,
        label : List[str],
        dropNaCoordinates : bool = True,
        imputeNaSpeed : bool = True,
        encodeGameDate : bool = True,
        encodeGameType : bool = True,
        encodeShooterId : bool = True,
        encodeGoalieId : bool = True,
        encodeByTeam : bool = True,
        encodeShotType : bool = True,
        encodeStrength : bool = True,
        encodeLastEventType : bool = True,        
    ) -> None:

        self.df_train = df_train
        self.df_test = df_test
        self.cross_validation_k_fold = cross_validation_k_fold
        self.shuffle_before_splitting = shuffle_before_splitting
        self.seed = seed
        self.label = label

        self.dropNaCoordinates = dropNaCoordinates
        self.imputeNaSpeed = imputeNaSpeed
        self.encodeGameDate = encodeGameDate
        self.encodeGameType = encodeGameType
        self.encodeShooterId = encodeShooterId
        self.encodeGoalieId = encodeGoalieIdÀ
        self.encodeByTeam = encodeByTeam
        self.encodeShotType = encodeShotType
        self.encodeStrength = encodeStrength
        self.encodeLastEventType = encodeLastEventType

        if self.dropNaCoordinates:
            self.df_train = self.dropNaCoordinates(self.df_train)
            self.df_test = self.dropNaCoordinates(self.df_test)

        if self.imputeNaSpeed:
            self.df_train["speed"] = self.imputeNaSpeed(self.df_train)
            self.df_test["speed"] = self.imputeNaSpeed(self.df_test)

        if self.encodeGameDate:
            self.df_train["gameDate"] = self.encodeGameData(self.df_train)
            self.df_test["gameDate"] = self.encodeGameData(self.df_test)

        if self.encodeGameType:
            self.df_train["gameType"] = self.encodeGameType(self.df_train)
            self.df_test["gameType"] = self.encodeGameType(self.df_test)

        if self.encodeShooterId:
            self.df_train["shooterId"] = self.encodeShooterId(self.df_train)
            self.df_test["shooterId"] = self.encodeShooterId(self.df_test)

        if self.encodeGoalieId:
            self.df_train["goalieId"] = self.encodeGoalieId(self.df_train)
            self.df_test["goalieId"] = self.encodeGoalieId(self.df_test)

        if self.encodeShotType:
            self.df_train = self.encodeShotType(self.df_train)
            self.df_test = self.encodeShotType(self.df_test)

        if self.encodeStrength:
            self.df_train["strength"] = self.encodeStrength(self.df_train)
            self.df_test["strength"] = self.encodeStrength(self.df_test)

        if self.encodeLastEventType:
            self.df_train = self.encodeLastEventType(self.df_train)
            self.df_test = self.encodeLastEventType(self.df_test)

        if self.encodeByTeam:
            self.df_train["byTeam"] = self.encodeByTeam(self.df_train)
            self.df_test["byTeam"] = self.encodeByTeam(self.df_test)

        self.X_train = self.df_train.drop(columns=label)
        self.y_train = self.df_train[label]

        self.X_test = self.df_test.drop(columns=label)
        self.y_test = self.df_test[label]

    
    def dropNaCoordinates(self, data : pd.DataFrame) -> pd.DataFrame:
        '''
        Drop rows with NaN values in the following columns:
            - coordinateX
            - coordinateY
            - lastCoordinateX
            - lastCoordinateY
            - distanceToGoal
            - angleToGoal
            - distanceFromLastEvent
            - changeAngle
            - speed

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to drop rows from
        
        Returns
        -------
        pd.DataFrame
            The dataframe with rows dropped
        '''

        df = data.copy()
        df = df.dropna(subset=[
            "coordinateX", 
            "coordinateY", 
            "lastCoordinateX", 
            "lastCoordinateY", 
            "distanceToGoal", 
            "angleToGoal", 
            "distanceFromLastEvent", 
            "changeAngle", 
            "speed"
            ])

        return df

    def imputeNaSpeed(self, data : pd.DataFrame) -> pd.DataFrame:
        '''
        Impute NaN values in the speed column with the maximum speed value

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to impute NaN values from
        
        Returns
        -------
        pd.DataFrame
            The dataframe with NaN values imputed
        '''

        df = data.copy()
        df["speed"] = df["speed"].fillna(df["speed"].max())
        return df["speed"]


    def encodeGameDate(self, data : pd.DataFrame) -> pd.DataFrame:
        '''
        Encode the gameDate column by converting it to datetime and extracting the month. 
        The month is then transformed into an ordinal number where September is the first month.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to encode gameDate from
        
        Raises
        ------
        ValueError
            If the gameDate column is not found in the dataframe
        
        Returns
        -------
        pd.DataFrame
            The dataframe with gameDate encoded as ordinal month
        '''

        if "gameDate" not in data.columns:
            raise ValueError("gameDate column not found in dataframe") 

        df = data.copy()
        df["gameDate"] = pd.to_datetime(df["gameDate"])
        month = df["gameDate"].dt.month
        ordinal_month = month - 9
        ordinal_month[ordinal_month <= 0] += 12
        return ordinal_month

    def encodeGameType(self, data : pd.DataFrame) -> pd.DataFrame:
        '''
        Encode the gameType column by converting it to binary, where "P" is represented as 1 and any other value as 0.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to encode gameType from
        
        Raises
        ------
        ValueError
            If the gameType column is not found in the dataframe
        
        Returns
        -------
        pd.DataFrame
            The dataframe with gameType encoded as binary
        '''

        if "gameType" not in data.columns:
            raise ValueError("gameType column not found in dataframe") 

        df = data.copy()
        df["gameType"] = (data["gameType"] == "P").astype(int)
        return df["gameType"]

    def encodeShooterId(self, data: pd.DataFrame, confidence_threshold: int = 41) -> pd.DataFrame:
        '''
        Encode the shooterId column by calculating the mean goals per game for each player per season.
        A certainty threshold is used to determine in which proportion to use the player's 
        mean or the overall mean for the season.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to encode shooterId from
        
        Returns
        -------
        pd.DataFrame
            The dataframe with shooterId encoded
        '''

        df = data.copy()

        df['totalGoals'] = df.groupby(['season', 'shooterId'])['isGoal'].transform('sum')
        df['gamesPlayed'] = df.groupby(['season', 'shooterId'])['gameId'].transform('nunique')
        df['mean_goals_per_game'] = df['totalGoals'] / df['gamesPlayed']

        overall_mean_per_season = df.groupby('season')['mean_goals_per_game'].mean()
        df['season_mean'] = df['season'].map(overall_mean_per_season)

        weight = df['gamesPlayed'] / confidence_threshold
        weight = weight.where(weight <= 1, 1)  # Ensuring the ratio does not exceed 1
        df['weighted_mean_goals_per_game'] = weight * df['mean_goals_per_game'] + (1 - weight) * df['season_mean']

        return df['weighted_mean_goals_per_game']

    def encodeGoalieId(self, data : pd.DataFrame) -> pd.DataFrame:
        '''
        Encode the goalieId column by calculating the mean save ratio for each goalie per season.
        A certainty threshold is used to determine in which proportion to use the player's mean 
        or the overall mean for the season.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to encode goalieId from
        
        Returns
        -------
        pd.DataFrame
            The dataframe with goalieId encoded
        '''

        df = data.copy()

        df['shotsFaced'] = df.groupby(['season', 'goalieId'])['eventType'].transform(lambda x: (x == 'SHOT').sum() + (x == 'GOAL').sum())
        df['totalGoalsConceded'] = df.groupby(['season', 'goalieId'])['isGoal'].transform('sum')
        df['save_ratio'] = 1 - (df['totalGoalsConceded'] / df['shotsFaced'])

        overall_mean_per_season = df.groupby('season')['save_ratio'].mean()
        df['season_mean_save_ratio'] = df['season'].map(overall_mean_per_season)

        weight = df['shotsFaced'] / confidence_threshold
        weight = weight.where(weight <= 1, 1)  # Ensuring the ratio does not exceed 1
        df['weighted_save_ratio'] = weight * df['save_ratio'] + (1 - weight) * df['season_mean_save_ratio']

        return df['weighted_save_ratio']

    def encodeShotType(self, data : pd.DataFrame) -> pd.DataFrame:
        '''
        Encode the shotType column using one-hot encoding.
        Impute NA values with "Wrist Shot" because it is the most common shot type by a large margin.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to encode shotType from
        
        Returns
        -------
        pd.DataFrame
            The dataframe with shotType encoded
        '''

        if "shotType" not in data.columns:
            raise ValueError("shotType column not found in dataframe") 

        df = data.copy()

        df['shotType'] = df['shotType'].fillna('Wrist Shot')
        one_hot_encoded_df = pd.get_dummies(df, columns=['shotType'], prefix='', prefix_sep='shotType_')
        return one_hot_encoded_df

    def encodeStrength(self, data : pd.DataFrame) -> pd.DataFrame:
        '''
        Encode the strength column by calculating the difference between the number of skaters of the byTeam the other team skater.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to encode strength from
        
        Returns
        -------
        pd.DataFrame
            The dataframe with strength encoded
        '''

        if "homeSkaters" not in data.columns or "awaySkaters" not in data.columns or "byTeam" not in data.columns:
            raise ValueError("homeSkaters, awaySkaters or byTeam columns not found in dataframe")

        df = data.copy()

        isAwayTeam = (df["byTeam"] != df["homeTeam"])
        df["strength"] = df["homeSkaters"] - df["awaySkaters"]
        df.loc[isAwayTeam, "strength"] = -df.loc[isAwayTeam, "strength"]

        return df["strength"]

    def encodeLastEventType(self, data : pd.DataFrame) -> pd.DataFrame:
        '''
        Encode the lastEventType column by grouping certain event types into 'OTHER' and applying one-hot encoding.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to encode lastEventType from
        
        Returns
        -------
        pd.DataFrame
            The dataframe with lastEventType encoded
        '''

        df = data.copy()

        other_events = [
            'FACEOFF', 
            'STOP', 
            'PENALTY', 
            'PERIOD_START', 
            'PERIOD_READY', 
            'PERIOD_OFFICIAL', 
            'PERIOD_END', 
            'GAME_END', 
            'GAME_SCHEDULED', 
            'GAME_OFFICIAL', 
            'CHALLENGE', 
            'SHOOTOUT_COMPLETE', 
            'EARLY_INT_START', 
            'EARLY_INT_END', 
            'EMERGENCY_GOALTENDER'
        ]

        df.loc[df['lastEventType'].isin(other_events), 'lastEventType'] = 'OTHER'
        one_hot_encoded_df = pd.get_dummies(df, columns=['lastEventType'], prefix='', prefix_sep='lastEventType_')

        return one_hot_encoded_df

    def encodeByTeam(self, data : pd.DataFrame) -> pd.DataFrame:
        '''
        Encode the byTeam column by ranking the teams based on the number of wins per season.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to encode byTeam from
        
        Returns
        -------
        pd.DataFrame
            The dataframe with byTeam encoded
        '''
        
        if "byTeam" not in data.columns:
            raise ValueError("byTeam column not found in dataframe") 

        df = data.copy()

        unique_games_df = df.drop_duplicates(subset='gameId')
        team_wins = unique_games_df.groupby(['season', 'winTeam']).size()
        team_rank = team_wins.groupby(level=0, group_keys=False).rank(method='first', ascending=False)

        df = df.join(team_rank.rename('team_rank'), on=['season', 'winTeam'])
        return df['team_rank']