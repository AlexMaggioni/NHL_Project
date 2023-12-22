from pathlib import Path
from typing import List
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold

from rich.console import Console
from rich.table import Table

class NHL_data_preprocessor:

    def __init__(
        self,
        df_train: pd.DataFrame,
        df_test: pd.DataFrame,
        cross_validation_k_fold : int, 
        shuffle_before_splitting : bool, 
        seed : int,
        label : List[str],
        columns_to_drop : List[str],
        dropNaCoordinates : bool,
        imputeNaSpeed : bool,
        encodeGameDate : bool,
        encodeGameType : bool,
        encodeShooterId : bool,
        encodeGoalieId : bool,
        encodeByTeam : bool,
        encodeShotType : bool,
        encodeStrength : bool,
        encodeLastEventType : bool,        
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
        self.encodeGoalieId = encodeGoalieId
        self.encodeByTeam = encodeByTeam
        self.encodeShotType = encodeShotType
        self.encodeStrength = encodeStrength
        self.encodeLastEventType = encodeLastEventType

        if self.imputeNaSpeed:
            logger.info("IMPUTE NA IN speed COLUMN - Imputing NaN values in the speed column with the maximum speed value (cause by TimeElapsed = 0)")
            self.df_train["speed"] = self._imputeNaSpeed(self.df_train)
            self.df_test["speed"] = self._imputeNaSpeed(self.df_test)

        if self.dropNaCoordinates:
            logger.info("DROP NA IN COORDINATES - Dropping rows with NaN values in coordinate columns")
            self.df_train = self._dropNaCoordinates(self.df_train)
            self.df_test = self._dropNaCoordinates(self.df_test)

        if self.encodeGameDate:
            logger.info("ENCODE GAME DATE - Encoding gameDate column by converting it to datetime and extracting the month")
            self.df_train["gameDate"] = self._encodeGameDate(self.df_train)
            self.df_test["gameDate"] = self._encodeGameDate(self.df_test)

        if self.encodeGameType:
            logger.info("ENCODE GAME TYPE - Encoding gameType column by converting it to binary")
            self.df_train["gameType"] = self._encodeGameType(self.df_train)
            self.df_test["gameType"] = self._encodeGameType(self.df_test)

        if self.encodeShooterId:
            logger.info("ENCODE SHOOTER ID - Encoding shooterId column by calculating the mean goals per game for each player per season")
            self.df_train["shooterId"] = self._encodeShooterId(self.df_train)
            self.df_test["shooterId"] = self._encodeShooterId(self.df_test)

        if self.encodeGoalieId:
            logger.info("ENCODE GOALIE ID - Encoding goalieId column by calculating the mean save ratio for each goalie per season and impute NA by median")
            self.df_train["goalieId"] = self._encodeGoalieId(self.df_train)
            self.df_test["goalieId"] = self._encodeGoalieId(self.df_test)

        if self.encodeShotType:
            logger.info("ENCODE SHOT TYPE - Encoding shotType column using one-hot encoding")
            self.df_train = self._encodeShotType(self.df_train)
            self.df_test = self._encodeShotType(self.df_test)

        if self.encodeStrength:
            logger.info("ENCODE STRENGTH - Encoding strength column by calculating the difference between the number of skaters of the byTeam the other team skater")
            self.df_train["strength"] = self._encodeStrength(self.df_train)
            self.df_test["strength"] = self._encodeStrength(self.df_test)

        if self.encodeLastEventType:
            logger.info("ENCODE LAST EVENT TYPE - Encoding lastEventType column by grouping certain event types into 'OTHER' and applying one-hot encoding")
            self.df_train = self._encodeLastEventType(self.df_train)
            self.df_test = self._encodeLastEventType(self.df_test)

        if self.encodeByTeam:
            logger.info("ENCODE BY TEAM - Encoding byTeam column by ranking the teams based on the number of wins per season")
            self.df_train["byTeam"] = self._encodeByTeam(self.df_train)
            self.df_test["byTeam"] = self._encodeByTeam(self.df_test)

        

        self.columns_to_drop = columns_to_drop

        self.df_train = self.df_train.drop(columns=self.columns_to_drop)
        self.df_test = self.df_test.drop(columns=self.columns_to_drop)

        self.X_train = self.df_train.drop(columns=label)
        self.y_train = self.df_train[label]

        self.X_test = self.df_test.drop(columns=label)
        self.y_test = self.df_test[label]

    
    def _dropNaCoordinates(self, data : pd.DataFrame) -> pd.DataFrame:
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
        logger.info(f"\t Number of rows before: {df.shape}")
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
        logger.info(f"\t Number of rows after: {df.shape}")

        return df

    def _imputeNaSpeed(self, data : pd.DataFrame) -> pd.DataFrame:
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


    def _encodeGameDate(self, data : pd.DataFrame) -> pd.DataFrame:
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
        ordinal_month = month - 9 # October is considered as the first month : Beginning of the season
        ordinal_month[ordinal_month <= 0] += 12
        return ordinal_month.astype(pd.CategoricalDtype(categories=ordinal_month.unique(), ordered=True))

    def _encodeGameType(self, data : pd.DataFrame) -> pd.DataFrame:
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

    def _encodeShooterId(self, data: pd.DataFrame, confidence_threshold: int = 41) -> pd.DataFrame:
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

    def _encodeGoalieId(self, data : pd.DataFrame, confidence_threshold: int = 41) -> pd.DataFrame:
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

        df['gamesPlayed'] = df.groupby(['season', 'goalieId'])['gameId'].transform('nunique')
        weight = df['gamesPlayed'] / confidence_threshold
        weight = weight.where(weight <= 1, 1)  # Ensuring the ratio does not exceed 1
        df['weighted_save_ratio'] = weight * df['save_ratio'] + (1 - weight) * df['season_mean_save_ratio']

        logger.info(f" IMPUTING GoalieID with median of {df['weighted_save_ratio'].median()}")
        # Impute NaN values in weighted_save_ratio with the median
        df['weighted_save_ratio'] = df['weighted_save_ratio'].fillna(df['weighted_save_ratio'].median())

        return df['weighted_save_ratio']

    def _encodeShotType(self, data : pd.DataFrame) -> pd.DataFrame:
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

        logger.info("IMPUTE NA IN shotType COLUMN BY 'Wrist Shot'")
        df['shotType'] = df['shotType'].fillna('Wrist Shot')
        one_hot_encoded_df = pd.get_dummies(df, columns=['shotType'], prefix='', prefix_sep='shotType_')
        logger.info('ONE-HOT ENCODING shotType COLUMN : {}'.format(df['shotType'].nunique()))
        return one_hot_encoded_df

    def _encodeStrength(self, data : pd.DataFrame) -> pd.DataFrame:
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

    def _encodeLastEventType(self, data : pd.DataFrame) -> pd.DataFrame:
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
        logger.info('ONE-HOT ENCODING lastEventType COLUMN : {}'.format(df['lastEventType'].nunique()))
        return one_hot_encoded_df

    def _encodeByTeam(self, data : pd.DataFrame) -> pd.DataFrame:
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

        return df['team_rank'].astype(pd.CategoricalDtype(categories=sorted(df['team_rank'].unique(),reverse=True), ordered=True))
    

    def _split_data(self):

        skf = StratifiedKFold(
            n_splits=self.cross_validation_k_fold, 
            shuffle=self.shuffle_before_splitting, 
            random_state=self.seed
        )

        logger.info(f"Splitting the data for Cross-Validation keeping class balance with K : {self.cross_validation_k_fold}")

        dummy_train_index, dummy_test_index = skf.split(self.X_train, self.y_train).__next__()
        self._print_splitting_stats(
            y_train=self.y_train.iloc[dummy_train_index],
            y_val=self.y_train.iloc[dummy_test_index],
        )
        
        return skf.split(self.X_train, self.y_train)
    
    def _print_splitting_stats(self, y_train=None, y_val=None):
        table = Table(title="Train/Val sets - Class Distribution", show_edge=True,show_lines=True,expand=True)

        table.add_column("Split type", justify="left", style="cyan", no_wrap=True)
        table.add_column("NOTHING", style="magenta")
        [table.add_column(class_name, style="magenta") for class_name in self.label]
        table.add_row('Train', *y_train.value_counts().astype(str).to_list())
        table.add_row('Val', *y_val.value_counts().astype(str).to_list())

        console = Console()
        console.print(table)