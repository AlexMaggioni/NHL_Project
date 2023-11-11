from pathlib import Path
import pandas as pd
import numpy as np
from utils import unify_coordinates_referential, init_logger, verify_dotenv_file, GOAL_POSITION
from datetime import timedelta

verify_dotenv_file(Path(__file__).parent.parent)
logger = init_logger("feature_engineering.log")

class NHLFeatureEngineering:
    
    def __init__(
            self, 
            df: pd.DataFrame,
            distanceToGoal: bool,
            angleToGoal: bool,
            isGoal: bool,
            emptyNet: bool,
            verbose: bool,
            imputeRinkSide: bool,
            periodTimeSeconds: bool,
            lastEvent: bool,
            lastCoordinates: bool,
            timeElapsed: bool,
            distanceFromLastEvent: bool,
            rebound: bool,
            changeAngle: bool,
            speed: bool,
            computePowerPlayFeatures: bool,
        ):
        
        self.df = df
        self.dfUnify = pd.DataFrame()
        self.verbose = verbose
        self.imputeRinkSide = imputeRinkSide
        self.GOAL_POSITION = GOAL_POSITION
        logger.info(f"Calculations of distance/angle done w.r.t GOAL_POSITION = {self.GOAL_POSITION}")

        self.distanceToGoal = distanceToGoal
        self.angleToGoal = angleToGoal
        self.isGoal = isGoal
        self.emptyNet = emptyNet
        self.periodTimeSeconds = periodTimeSeconds
        self.lastEvent = lastEvent
        self.lastCoordinates = lastCoordinates
        self.timeElapsed = timeElapsed
        self.distanceFromLastEvent = distanceFromLastEvent
        self.rebound = rebound
        self.changeAngle = changeAngle
        self.speed = speed
        self.computePowerPlayFeatures = computePowerPlayFeatures

        if self.distanceToGoal or self.angleToGoal:
            self.dfUnify = self._printNaStatsBeforeUnifying()
            logger.info("UNIFYING THE DATAFRAME ON ONE RINKSIDE")
            self.dfUnify = unify_coordinates_referential(self.dfUnify, self.imputeRinkSide)

        if self.distanceToGoal:
            logger.info("CALCULATING DISTANCE TO GOAL - ADDING COLUMN distanceToGoal TO DATAFRAME")
            self.df['distanceToGoal'] = self.calculateDistanceToGoal()
            self.dfUnify['distanceToGoal'] = self.df.loc[self.dfUnify.index, 'distanceToGoal']

        if self.angleToGoal:
            logger.info("CALCULATING ANGLE TO GOAL - ADDING COLUMN angleToGoal TO DATAFRAME")
            self.df['angleToGoal'] = self.calculateAngleToGoal()
            self.dfUnify['angleToGoal'] = self.df.loc[self.dfUnify.index, 'angleToGoal']

        if self.isGoal:
            logger.info("CALCULATING IS GOAL - ADDING COLUMN isGoal TO DATAFRAME")
            self.df['isGoal'] = self.calculateIsGoal()
            self.dfUnify['isGoal'] = self.df.loc[self.dfUnify.index, 'isGoal']

        if self.emptyNet:
            logger.info("CALCULATING EMPTY NET - ADDING COLUMN emptyNet TO DATAFRAME")
            self.df['emptyNet'] = self.calculateEmptyNet()
            self.dfUnify['emptyNet'] = self.df.loc[self.dfUnify.index, 'emptyNet']

        if self.periodTimeSeconds:
            logger.info("CALCULATING PERIOD TIME IN SECONDS - ADDING COLUMN periodTimeSeconds TO DATAFRAME")
            self.df['periodTimeSeconds'] = self.calculatePeriodTimeSeconds()
            self.dfUnify['periodTimeSeconds'] = self.df.loc[self.dfUnify.index, 'periodTimeSeconds']

        if self.lastEvent:
            logger.info("CALCULATING LAST EVENT - ADDING COLUMN lastEventType TO DATAFRAME")
            self.df['lastEventType'] = self.calculateLastEvent()
            self.dfUnify['lastEventType'] = self.df.loc[self.dfUnify.index, 'lastEventType']

        if self.lastCoordinates:
            logger.info("CALCULATING LAST COORDINATES - ADDING COLUMNS lastCoordinateX AND lastCoordinateY TO DATAFRAME")
            self.df['lastCoordinateX'], self.df['lastCoordinateY'] = self.calculateLastCoordinates()
            self.dfUnify['lastCoordinateX'] = self.df.loc[self.dfUnify.index, 'lastCoordinateX']
            self.dfUnify['lastCoordinateY'] = self.df.loc[self.dfUnify.index, 'lastCoordinateY']

        if self.timeElapsed:
            logger.info("CALCULATING TIME ELAPSED - ADDING COLUMN timeElapsed TO DATAFRAME")
            self.df['timeElapsed'] = self.calculateTimeElapsed()
            self.dfUnify['timeElapsed'] = self.df.loc[self.dfUnify.index, 'timeElapsed']

        if self.distanceFromLastEvent:
            logger.info("CALCULATING DISTANCE FROM LAST EVENT - ADDING COLUMN distanceFromLastEvent TO DATAFRAME")
            self.df['distanceFromLastEvent'] = self.calculateDistanceFromLastEvent()
            self.dfUnify['distanceFromLastEvent'] = self.df.loc[self.dfUnify.index, 'distanceFromLastEvent']

        if self.rebound:
            logger.info("CALCULATING REBOUND - ADDING COLUMN rebound TO DATAFRAME")
            self.df['rebound'] = self.calculateRebound()
            self.dfUnify['rebound'] = self.df.loc[self.dfUnify.index, 'rebound']

        if self.changeAngle:
            logger.info("CALCULATING CHANGE ANGLE - ADDING COLUMN changeAngle TO DATAFRAME")
            self.df['changeAngle'] = self.calculateChangeAngle()
            self.dfUnify['changeAngle'] = self.df.loc[self.dfUnify.index, 'changeAngle']

        if self.speed:
            logger.info("CALCULATING SPEED - ADDING COLUMN speed TO DATAFRAME")
            self.df['speed'] = self.calculateSpeed()
            self.dfUnify['speed'] = self.df.loc[self.dfUnify.index, 'speed']

        if self.computePowerPlayFeatures:
            logger.info("COMPUTING POWER PLAY INFO - ADDING COLUMNS elapsedPowerPlay, homeSkaters and awaySkaters TO DATAFRAME")
            elapsedPowerPlay, homeSkaters, awaySkaters = self.calculatePowerPlayFeatures()
            self.df['elapsedPowerPlay'] = elapsedPowerPlay
            self.df['homeSkaters'] = homeSkaters
            self.df['awaySkaters'] = awaySkaters
            self.dfUnify['elapsedPowerPlay'] = self.df.loc[self.dfUnify.index, 'elapsedPowerPlay']
            self.dfUnify['homeSkaters'] = self.df.loc[self.dfUnify.index, 'homeSkaters']
            self.dfUnify['awaySkaters'] = self.df.loc[self.dfUnify.index, 'awaySkaters']

        self.dfUnify = self.dfUnify.reset_index(drop=True)

    def _printNaStatsBeforeUnifying(self):

        shotsWithoutXCoords = set(self.df[self.df['coordinateX'].isna()].index)
        shotsWithoutYCoords = set(self.df[self.df['coordinateY'].isna()].index)
        coordsToSelect = self.df.iloc[ list(set(self.df.index) - shotsWithoutXCoords.union(shotsWithoutYCoords)) ]

        rinkSideNa = coordsToSelect[coordsToSelect['rinkSide'].isna()].index

        logger.info(f"Found {len(coordsToSelect)} shots with coordinates and rinkSide specified.")
        if self.verbose:
            naXAndYSetIndex = shotsWithoutXCoords.intersection(shotsWithoutYCoords)
            naOnlyXSetIndex = shotsWithoutXCoords - shotsWithoutYCoords
            naOnlyYSetIndex = shotsWithoutYCoords - shotsWithoutXCoords
            logger.info(f"""
                Coordinates NA stats:
                    {len(self.df) - len(coordsToSelect)} shots without coordinates.
                    {len(naXAndYSetIndex)} shots without both X and Y coordinates.
                    {len(naOnlyXSetIndex)} shots without X coordinates.
                    {len(naOnlyYSetIndex)} shots without Y coordinates.
                
                RinkSide NA stats:
                    {len(rinkSideNa)} shots without rinkSide specified. Use imputeRinkSide == True to handle missing 
                    values based on mean X coordinates in a period for a given team and gameId.
            """)
        return self.df

    def calculateEmptyNet(self):
        '''
        Calculate if the net was empty for each shot.
        '''
        self.df['emptyNet'] = self.df['emptyNet'].fillna(0)
        return (self.df['emptyNet'] == 1).astype(int)

    def calculateDistanceToGoal(self):
        '''
        Calculate the distance to the goal for each shot.
        '''
        unifiedCoordinatesDf = unify_coordinates_referential(self.df, True)
        dists = np.linalg.norm(self.GOAL_POSITION - unifiedCoordinatesDf[['coordinateX', 'coordinateY']], axis=1)
        dists = pd.Series(dists, index=unifiedCoordinatesDf.index)
        # Fill with NA values the shots without coordinates in the dists Series
        res = dists.reindex(self.df.index)
        return res

    def calculateAngleToGoal(self):
        '''
        Calculate the angle to the goal for each shot.
        '''
        unifiedCoordinatesDf = unify_coordinates_referential(self.df, True)
        atanValues = np.degrees(np.arctan2(
            self.GOAL_POSITION[1] - unifiedCoordinatesDf['coordinateY'],
            self.GOAL_POSITION[0] - unifiedCoordinatesDf['coordinateX']
        ))
        res = atanValues.reindex(self.df.index)
        return res

    def calculateIsGoal(self):
        '''
        Calculate if the shot was a goal.
        '''
        return (self.df['eventType'] == 'GOAL').astype(int)

    def calculatePeriodTimeSeconds(self):
        '''
        Calculate the period time in seconds instead of MM:SS.
        '''
        df_sorted = self.df.sort_values(by=['gameId', 'period', 'periodTime']).copy()
        seconds = df_sorted['periodTime'].apply(lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))
        return seconds.reindex(self.df.index)

    def calculateLastEvent(self):
        '''
        Calculate the last event just before the current one.
        '''
        df_sorted = self.df.sort_values(by=['gameId', 'period', 'periodTime']).copy()
        return df_sorted["eventType"].shift(1).reindex(self.df.index)

    def calculateLastCoordinates(self):
        '''
        Calculate the last coordinates just before the current one.
        '''
        unifiedCoordinatesDf = unify_coordinates_referential(self.df, True)
        df_sorted = unifiedCoordinatesDf.sort_values(by=['gameId', 'period', 'periodTime']).copy()
        shiftedX = df_sorted["coordinateX"].shift(1)
        shiftedY = df_sorted["coordinateY"].shift(1)
        return shiftedX.reindex(self.df.index), shiftedY.reindex(self.df.index)

    def calculateTimeElapsed(self):
        '''
        Calculate the time elapsed since the last event.
        '''
        seconds = self.calculatePeriodTimeSeconds()
        return (seconds - seconds.shift(1)).reindex(self.df.index)

    def calculateDistanceFromLastEvent(self):
        '''
        Calculate the distance from the last event.
        '''
        unifiedCoordinatesDf = unify_coordinates_referential(self.df, True)
        df_sorted = unifiedCoordinatesDf.sort_values(by=['gameId', 'period', 'periodTime']).copy()
        shiftedX = df_sorted["coordinateX"].shift(1)
        shiftedY = df_sorted["coordinateY"].shift(1)
        distances = np.linalg.norm(
            df_sorted[["coordinateX", "coordinateY"]].values - np.array([shiftedX, shiftedY]).T,
            axis=1
        )
        distances_series = pd.Series(distances, index=df_sorted.index)
        return distances_series.reindex(self.df.index)

    def calculateRebound(self):
        '''
        Calculate if the shot was a rebound.
        '''
        df_sorted = self.df.sort_values(by=['gameId', 'period', 'periodTime']).copy()
        shiftedEvent = df_sorted["eventType"].shift(1)
        return (shiftedEvent == 'SHOT').astype(int).reindex(self.df.index)

    def calculateChangeAngle(self):
        '''
        Calculate the change of angle before the shot.
        Only calculate if the last event was a shot, else return 0.
        '''
        df_sorted = self.df.sort_values(by=['gameId', 'period', 'periodTime']).copy()
        shiftedAngle = df_sorted["angleToGoal"].shift(1)
        last_event_shot = (df_sorted["eventType"].shift(1) == "SHOT").astype(int)

        change_angle = np.abs(df_sorted["angleToGoal"] - shiftedAngle)
        change_angle = change_angle * last_event_shot

        return change_angle.reindex(self.df.index)

    def calculateSpeed(self):
        '''
        Calculate the speed of the player before the shot.
        '''
        df_sorted = self.df.sort_values(by=['gameId', 'period', 'periodTime']).copy()

        shiftedX = df_sorted["coordinateX"].shift(1)
        shiftedY = df_sorted["coordinateY"].shift(1)
        distances = np.linalg.norm(
            df_sorted[["coordinateX", "coordinateY"]].values - np.array([shiftedX, shiftedY]).T,
            axis=1
        )
        distances_series = pd.Series(distances, index=df_sorted.index)

        timeElapsed = df_sorted['periodTime'].apply(lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))
        timeElapsed = timeElapsed.replace(0, 1e-100)
        speed = (distances_series / timeElapsed).replace(np.inf, 0)
        return speed.reindex(self.df.index)

    def parse_period_time(self, time_str):
        """Convert period time string to a timedelta object."""
        minutes, seconds = map(int, time_str.split(':'))
        return timedelta(minutes=minutes, seconds=seconds)

    def calculatePowerPlayFeatures(self):
        '''
        Calculate power play features: elapsedPowerPlay, homeSkaters, awaySkaters.
        '''
        df = self.df.sort_values(by=['gameId', 'period', 'periodTime']).copy()
        df['periodTimeDelta'] = df['periodTime'].apply(self.parse_period_time)
        df['elapsedPowerPlay'] = 0

        current_game_id = None
        penalties = {'home': [], 'away': []}
        last_power_play_time = {'home': None, 'away': None}

        for index, row in df.iterrows():
            if row['gameId'] != current_game_id:
                current_game_id = row['gameId']
                penalties = {'home': [], 'away': []}
                last_power_play_time = {'home': None, 'away': None}
                df.at[index, 'homeSkaters'] = df.at[index, 'awaySkaters'] = 5

            current_time = row['periodTimeDelta'] + timedelta(minutes=20 * (row['period'] - 1))

            # Update skater counts and remove expired penalties
            for team in ['home', 'away']:
                penalties[team] = [penalty for penalty in penalties[team] if penalty[0] > current_time]
                df.at[index, f'{team}Skaters'] = 5 - len(penalties[team])
                df.at[index, f'{team}Skaters'] = max(df.at[index, f'{team}Skaters'], 3)

            # Handle penalty
            if pd.notna(row['penaltyMinutes']):
                penalized_team = 'home' if row['homeTeam'] == row['penalizedTeam'] else 'away'
                penalty_duration = timedelta(minutes=int(row['penaltyMinutes']))
                penalty_end_time = current_time + penalty_duration
                penalties[penalized_team].append((penalty_end_time, penalty_duration))

            # Determine if there's a power play
            if df.at[index, 'homeSkaters'] != df.at[index, 'awaySkaters']:
                if last_power_play_time['home'] is None and last_power_play_time['away'] is None:
                    last_power_play_time['home'] = last_power_play_time['away'] = current_time
                df.at[index, 'elapsedPowerPlay'] = (current_time - last_power_play_time['home']).total_seconds()
            else:
                last_power_play_time = {'home': None, 'away': None}
                df.at[index, 'elapsedPowerPlay'] = 0

        df.drop(columns=['periodTimeDelta'], inplace=True)
        return df["elapsedPowerPlay"].reindex(self.df.index), df["homeSkaters"].reindex(self.df.index), df["awaySkaters"].reindex(self.df.index)