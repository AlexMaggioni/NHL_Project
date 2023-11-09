from pathlib import Path
import pandas as pd
import numpy as np
from utils import unify_coordinates_referential, init_logger, verify_dotenv_file, GOAL_POSITION

verify_dotenv_file(Path(__file__).parent.parent)
logger = init_logger("feature_engineering.log")

class NHL_Feature_Engineering:
    
    def __init__(
            self, 
            df: pd.DataFrame,
            distance_to_goal: bool,
            angle_to_goal: bool,
            is_goal: bool,
            empty_net: bool,
            verbose: bool,
            input_rinkSide: bool
        ):
        self.df = df
        self.verbose = verbose
        self.input_rinkSide = input_rinkSide
        self.GOAL_POSITION = GOAL_POSITION
        logger.info(f"Calculations of distance/angle done w.r.t GOAL_POSITION = {self.GOAL_POSITION}")

        self.distance_to_goal = distance_to_goal
        self.angle_to_goal = angle_to_goal
        self.is_goal = is_goal
        self.empty_net = empty_net
        self.df_unify = pd.DataFrame()

        if self.distance_to_goal or self.angle_to_goal:
            self.df_unify = self._print_na_stats_before_unifying()
            logger.info("UNIFIYING THE DATAFRAME ON ONE RINKSIDE")
            self.df_unify = unify_coordinates_referential(self.df_unify, self.input_rinkSide)

        if self.distance_to_goal:
            logger.info("CALCULATING DISTANCE TO GOAL - ADDING COLUMN distance_to_goal TO DATAFRAME")
            self.df['distance_to_goal'] = self.calculate_distance_to_goal()
            self.df_unify['distance_to_goal'] = self.df.loc[self.df_unify.index, 'distance_to_goal']
            
        if self.angle_to_goal:
            logger.info("CALCULATING ANGLE TO GOAL - ADDING COLUMN angle_to_goal TO DATAFRAME")
            self.df['angle_to_goal'] = self.calculate_angle_to_goal()
            self.df_unify['angle_to_goal'] = self.df.loc[self.df_unify.index, 'angle_to_goal']
        
        if self.is_goal:
            logger.info("CALCULATING IS GOAL - ADDING COLUMN is_goal TO DATAFRAME")
            self.df['is_goal'] = self.calculate_is_goal()
            self.df_unify['is_goal'] = self.df.loc[self.df_unify.index, 'is_goal']

        if self.empty_net:
            logger.info("CALCULATING EMPTY NET - ADDING COLUMN empty_net TO DATAFRAME")
            self.df['emptyNet'] = self.calculate_empty_net()
            self.df_unify['emptyNet'] = self.df.loc[self.df_unify.index, 'emptyNet']

        self.df_unify = self.df_unify.reset_index(drop=True)

    def _print_na_stats_before_unifying(self):
        shots_without_x_coords = set(self.df[self.df['coordinateX'].isna()].index)
        shots_without_y_coords = set(self.df[self.df['coordinateY'].isna()].index)
        coords_to_select = self.df.loc[list(set(self.df.index) - shots_without_x_coords.union(shots_without_y_coords))]

        rinkSide_na = coords_to_select[coords_to_select['rinkSide'].isna()].index

        logger.info(f"Found {len(coords_to_select)} shots with coordinates and rinkSide specified.")
        if self.verbose:
            na_X_and_Y_set_index = shots_without_x_coords.intersection(shots_without_y_coords)
            na_only_X_set_index = shots_without_x_coords - shots_without_y_coords
            na_only_Y_set_index = shots_without_y_coords - shots_without_x_coords
            logger.info(f"""
                Coordinates NA stats:
                    {len(self.df) - len(coords_to_select)} shots without coordinates.
                    {len(na_X_and_Y_set_index)} shots without both X and Y coordinates.
                    {len(na_only_X_set_index)} shots without X coordinates.
                    {len(na_only_Y_set_index)} shots without Y coordinates.
                
                RinkSide NA stats:
                    {len(rinkSide_na)} shots without rinkSide specified. Use input_rinkSide == True to handle missing 
                    values based on mean X coordinates in a period for a given team and gameId.

                ROWS WITH MISSING COORDINATES ARE DROPPED IN THE UNIFIED DATAFRAME.
            """)
        return coords_to_select

    def calculate_empty_net(self):
        '''
        Calculate if the net was empty for each shot.
        '''
        self.df['emptyNet'] = self.df['emptyNet'].fillna(0)
        return (self.df['emptyNet'] == 1).astype(int)

    def calculate_distance_to_goal(self):
        '''
        Calculate the distance to the goal for each shot.
        '''
        unified_coordinates_df = unify_coordinates_referential(self.df, True)
        dists =  np.linalg.norm(self.GOAL_POSITION - unified_coordinates_df[['coordinateX','coordinateY']], axis=1)
        dists = pd.Series(dists, index=unified_coordinates_df.index)
        # fill with NA values the shots without coordinates in the dists Series
        res = dists.reindex(self.df.index)
        return res

    def calculate_angle_to_goal(self):
        '''
        Calculate the angle to the goal for each shot.
        ''' 
        unified_coordinates_df = unify_coordinates_referential(self.df, True)
        atan_values = np.degrees(np.arctan2(
            self.GOAL_POSITION[1] - unified_coordinates_df['coordinateY'],
            self.GOAL_POSITION[0] - unified_coordinates_df['coordinateX']
        ))
        res = atan_values.reindex(self.df.index)
        return res

    def calculate_is_goal(self):
        '''
        Calculate if the shot was a goal.
        '''
        return (self.df['eventType'] == 'GOAL').astype(int)