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
            verbose : bool,
            unify : bool
        ):
        self.df = df
        self.verbose = verbose

        from utils import GOAL_POSITION
        self.GOAL_POSITION = GOAL_POSITION
        logger.info(f"Calculations of distance/angle done w.r.t GOAL_POSITION = {self.GOAL_POSITION}")

        self.distance_to_goal = distance_to_goal
        self.angle_to_goal = angle_to_goal

        self.unify = unify
        if unify:
            logger.info(f"UNIFIYING THE DATAFRAME ON ONE RINKSIDE")
            self.df = unify_coordinates_referential(self.df)

        if distance_to_goal:
            logger.info(f"CALCULATING DISTANCE TO GOAL - ADDING COLUMN distance_to_goal TO DATAFRAME")
            self.df['distance_to_goal'] = self.calculate_distance_to_goal()
        
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
            self.df['emptyNet'] = self.calculate_empty_net()

    def calculate_empty_net(self):
        '''
        Calculate if the net was empty for each shot.
        '''
        self.df['emptyNet'] = self.df['emptyNet'].fillna(0)
        return self.df['emptyNet'] == 1

    def calculate_distance_to_goal(self):
        '''
        Calculate the distance to the goal for each shot.
        '''
        dists =  np.linalg.norm(self.GOAL_POSITION - self.df[['coordinateX','coordinateY']], axis=1)
        dists = pd.Series(dists, index=self.df.index)
        # fill with NA values the shots without coordinates in the dists Series
        res = dists.reindex(self.df.index)
        return res


    def calculate_angle_to_goal(self):
        '''
        Calculate the angle to the goal for each shot.
        ''' 
        atan_values = np.degrees(np.arctan2(
            self.GOAL_POSITION[1] - self.df['coordinateY'],
            self.GOAL_POSITION[0] - self.df['coordinateX']
        ))
        res = atan_values.reindex(self.df.index)
        return res

    def calculate_is_goal(self):
        '''
        Calculate if the shot was a goal.
        '''
        return (self.df['eventType'] == 'GOAL').astype(int)