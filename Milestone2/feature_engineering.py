from pathlib import Path
import pandas as pd
import numpy as np
from utils import unify_coordinates_referential, init_logger, verify_dotenv_file, GOAL_POSITION

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
            inputRinkSide: bool,
            seconds: bool,
            lastEventFeatures: bool,
            rebound: bool,
            changeOfAngle: bool,
            speed: bool,
        ):
        
        self.df = df
        self.dfUnify = pd.DataFrame()
        self.verbose = verbose
        self.inputRinkSide = inputRinkSide
        self.GOAL_POSITION = GOAL_POSITION
        logger.info(f"Calculations of distance/angle done w.r.t GOAL_POSITION = {self.GOAL_POSITION}")

        self.distanceToGoal = distanceToGoal
        self.angleToGoal = angleToGoal
        self.isGoal = isGoal
        self.emptyNet = emptyNet
        self.seconds = seconds
        self.lastEventFeatures = lastEventFeatures
        self.rebound = rebound
        self.changeOfAngle = changeOfAngle
        self.speed = speed

        if self.distanceToGoal or self.angleToGoal:
            self.dfUnify = self._printNaStatsBeforeUnifying()
            logger.info("UNIFYING THE DATAFRAME ON ONE RINKSIDE")
            self.dfUnify = unify_coordinates_referential(self.dfUnify, self.inputRinkSide)

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

        if self.seconds:
            logger.info("CALCULATING PERIOD TIME IN SECONDS - ADDING COLUMN periodTimeSeconds TO DATAFRAME")
            self.df['periodTimeSeconds'] = self.calculatePeriodTimeSeconds()
            self.dfUnify['periodTimeSeconds'] = self.df.loc[self.dfUnify.index, 'periodTimeSeconds']

        if self.lastEventFeatures:
            logger.info("CALCULATING LAST EVENT FEATURES - ADDING COLUMNS {LastEventType, LastCoordinateX, LastCoordinateY, timeElapsed and distanceFromLastEvent} TO DATAFRAME")
            valuesDict = self.calculateLastEventFeatures()
            for key, value in valuesDict.items():
                self.df[key] = value
                self.dfUnify[key] = self.df.loc[self.dfUnify.index, key]

        if self.rebound:
            logger.info("CALCULATING REBOUND - ADDING COLUMN isRebound TO DATAFRAME")
            self.df['isRebound'] = self.calculateRebound()
            self.dfUnify['isRebound'] = self.df.loc[self.dfUnify.index, 'isRebound']

        if self.changeOfAngle:
            logger.info("CALCULATING CHANGE OF ANGLE - ADDING COLUMN changeOfAngle TO DATAFRAME")
            self.df['changeOfAngle'] = self.calculateChangeOfAngle()
            self.dfUnify['changeOfAngle'] = self.df.loc[self.dfUnify.index, 'changeOfAngle']

        if self.speed:
            logger.info("CALCULATING SPEED - ADDING COLUMN speed TO DATAFRAME")
            self.df['speed'] = self.calculateSpeed()
            self.dfUnify['speed'] = self.df.loc[self.dfUnify.index, 'speed']

        self.dfUnify = self.dfUnify.reset_index(drop=True)

    def _printNaStatsBeforeUnifying(self):
        shotsWithoutXCoords = set(self.df[self.df['coordinateX'].isna()].index)
        shotsWithoutYCoords = set(self.df[self.df['coordinateY'].isna()].index)
        coordsToSelect = self.df.loc[list(set(self.df.index) - shotsWithoutXCoords.union(shotsWithoutYCoords))]

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
                    {len(rinkSideNa)} shots without rinkSide specified. Use inputRinkSide == True to handle missing 
                    values based on mean X coordinates in a period for a given team and gameId.

                ROWS WITH MISSING COORDINATES ARE DROPPED IN THE UNIFIED DATAFRAME.
            """)
        return coordsToSelect

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
        dists =  np.linalg.norm(self.GOAL_POSITION - unifiedCoordinatesDf[['coordinateX','coordinateY']], axis=1)
        dists = pd.Series(dists, index=unifiedCoordinatesDf.index)
        # fill with NA values the shots without coordinates in the dists Series
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
        seconds = self.df['periodTime'].apply(lambda x: int(x.split(':')[0])*60 + int(x.split(':')[1]))
        return seconds

    def calculateLastEventFeatures(self):
        '''
        Calculate the last event features.
        '''
        # Ensure dataframe is sorted by gameId, period, and periodTime
        dfSorted = self.df.sort_values(by=['gameId', 'period', 'periodTime'])

        # Calculate period time in seconds if not already done
        if not self.seconds:
            dfSorted["periodTimeSeconds"] = self.calculatePeriodTimeSeconds()

        # Calculate angle to goal if not already done
        if not self.angleToGoal:
            dfSorted["angleToGoal"] = self.calculateAngleToGoal()

        # Shift the relevant columns to get last event values
        dfSorted['LastEventType'] = dfSorted['eventType'].shift(1)
        dfSorted['LastCoordinateX'] = dfSorted['coordinateX'].shift(1)
        dfSorted['LastCoordinateY'] = dfSorted['coordinateY'].shift(1)
        dfSorted['LastAngleToGoal'] = dfSorted['angleToGoal'].shift(1)
        dfSorted['timeElapsed'] = dfSorted['periodTimeSeconds'] - dfSorted['periodTimeSeconds'].shift(1)

        # Calculate distance from last event using unified coordinates
        # Need to unify the coordinates for the entire dataframe first
        unifiedCoordinatesDf = unify_coordinates_referential(dfSorted, self.inputRinkSide)
        dfSorted['LastUnifiedX'] = unifiedCoordinatesDf['coordinateX'].shift(1)
        dfSorted['LastUnifiedY'] = unifiedCoordinatesDf['coordinateY'].shift(1)
        
        # Calculate distance using unified coordinates
        dfSorted['distanceFromLastEvent'] = np.linalg.norm(
            unifiedCoordinatesDf[['coordinateX', 'coordinateY']] - dfSorted[['LastUnifiedX', 'LastUnifiedY']],
            axis=1
        )

        # Handle edge cases where timeElapsed can be negative at the period start
        dfSorted.loc[dfSorted['timeElapsed'] < 0, 'timeElapsed'] = None

        # Extract the calculated columns to return as a dictionary
        values = {
            'LastEventType': dfSorted['LastEventType'],
            'LastCoordinateX': dfSorted['LastCoordinateX'],
            'LastCoordinateY': dfSorted['LastCoordinateY'],
            'LastAngleToGoal': dfSorted['LastAngleToGoal'],
            'timeElapsed': dfSorted['timeElapsed'],
            'distanceFromLastEvent': dfSorted['distanceFromLastEvent']
        }

        return values

    def calculateRebound(self):
        '''
        Calculate if the shot was a rebound.
        '''
        # Initialize valuesDict as None to check if it gets assigned later
        valuesDict = None

        # If last event features are not pre-calculated, calculate them
        if not self.lastEventFeatures:
            valuesDict = self.calculateLastEventFeatures()

        # Now check if valuesDict was assigned. If not, it means last event features should be present in self.df
        if valuesDict is None:
            # Assuming that the last event features are already in self.df if self.lastEventFeatures is True
            return (self.df['LastEventType'] == "SHOT").astype(int)
        else:
            # Using valuesDict if it was assigned by calculateLastEventFeatures
            return (valuesDict['LastEventType'] == "SHOT").astype(int)


    def calculateChangeOfAngle(self):
        '''
        Calculate the change of angle between the events, if the last event was a shot.
        '''
        # Check if last event features are pre-calculated, if not, calculate them
        if not self.lastEventFeatures:
            valuesDict = self.calculateLastEventFeatures()
        else:
            # Extract last angle to goal from self.df if it's already calculated
            valuesDict = {
                'LastAngleToGoal': self.df['LastAngleToGoal']
            }

        # Check if angle to goal is pre-calculated, if not, calculate it
        if not self.angleToGoal:
            currentAngles = self.calculateAngleToGoal()
        else:
            # Use existing angle to goal values from self.df if they're already calculated
            currentAngles = self.df['angleToGoal']

        # Calculate the change of angle
        changeOfAngle = np.abs(currentAngles - valuesDict['LastAngleToGoal'])
        return changeOfAngle

    def calculateSpeed(self):
        '''
        Calculate the speed between two consecutive events.
        '''
        # Check if the last event features are already calculated
        if self.lastEventFeatures:
            # Use the existing last event features from self.df
            valuesDict = {
                'distanceFromLastEvent': self.df['distanceFromLastEvent'],
                'timeElapsed': self.df['timeElapsed']
            }
        else:
            # Calculate last event features since they are not pre-calculated
            valuesDict = self.calculateLastEventFeatures()
        
        # Protect against division by zero
        timeElapsed = valuesDict['timeElapsed'].replace(0, np.nan)
        
        # Calculate speed
        speed = valuesDict['distanceFromLastEvent'] / timeElapsed
        return speed.replace(np.nan, 0)  # Replace NaN values with 0 for speed if timeElapsed was 0