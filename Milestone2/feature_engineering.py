from pathlib import Path
import pandas as pd
import numpy as np
from utils import unify_coordinates_referential, init_logger, verify_dotenv_file

verify_dotenv_file(Path(__file__).parent.parent)
logger = init_logger("feature_engineering.log")

class NHL_Feature_Engineering:
    
    def __init__(
            self, 
            df : pd.DataFrame,
            distance_to_goal : bool,
            angle_to_goal : bool,
            is_goal : bool,
            empty_net : bool,
        ):
        self.df = df

        from utils import GOAL_POSITION
        self.GOAL_POSITION = GOAL_POSITION
        logger.info(f"Calculations of distance/goal done w.r.t GOAL_POSITION = {self.GOAL_POSITION}")

        self.distance_to_goal = distance_to_goal
        if distance_to_goal:
            logger.info(f"CALCULATING DISTANCE TO GOAL - ADDING COLUMN distance_to_goal TO DATAFRAME")
            self.df['distance_to_goal'] = self.calculate_distance_to_goal()
        
        self.angle_to_goal = angle_to_goal
        if angle_to_goal:
            logger.info(f"CALCULATING ANGLE TO GOAL - ADDING COLUMN angle_to_goal TO DATAFRAME")
            self.df['angle_to_goal'] = self.calculate_angle_to_goal()
        
        self.is_goal = is_goal
        if is_goal:
            logger.info(f"CALCULATING IS GOAL - ADDING COLUMN is_goal TO DATAFRAME")
            self.df['is_goal'] = self.calculate_is_goal()

        self.empty_net = empty_net
        if empty_net:
            logger.info(f"CALCULATING EMPTY NET - ADDING COLUMN empty_net TO DATAFRAME")
            self.df['empty_net'] = self.calculate_empty_net()

    def calculate_empty_net(self):
        '''
        Calculate if the net was empty for each shot.
        '''
        return self.df['goalieId'] == 0

    def calculate_distance_to_goal(self):
        '''
        Calculate the distance to the goal for each shot.
        '''
        unified_coordinates_df = unify_coordinates_referential(self.df[['coordinateX', 'coordinateY', 'rinkSide']])
        return np.sqrt((self.GOAL_POSITION[0] - unified_coordinates_df['coordinateX'])**2 + (self.GOAL_POSITION[1] - unified_coordinates_df['coordinateY'])**2)

    def calculate_angle_to_goal(self):
        '''
        Calculate the angle to the goal for each shot.
        ''' 
        unified_coordinates_df = unify_coordinates_referential(self.df[['coordinateX', 'coordinateY', 'rinkSide']])
        atan_values = np.arctan2(self.GOAL_POSITION[1] - unified_coordinates_df['coordinateY'], self.GOAL_POSITION[0] - unified_coordinates_df['coordinateX'])
        return np.degrees(atan_values)

    def calculate_is_goal(self):
        '''
        Calculate if the shot was a goal.
        '''
        return self.df['eventType'] == 'GOAL'