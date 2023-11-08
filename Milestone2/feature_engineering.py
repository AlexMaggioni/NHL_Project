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
            verbose : bool
        ):
        self.df = df
        self.verbose = verbose

        from utils import GOAL_POSITION
        self.GOAL_POSITION = GOAL_POSITION
        logger.info(f"Calculations of distance/angle done w.r.t GOAL_POSITION = {self.GOAL_POSITION}")

        self.distance_to_goal = distance_to_goal
        self.angle_to_goal = angle_to_goal

        if self.angle_to_goal or self.distance_to_goal:
            self.df_for_compute_with_goal = self._handle_na_values_for_coordinates_n_rinkside()

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
            self.df['empty_net'] = self.calculate_empty_net()

    def calculate_empty_net(self):
        '''
        Calculate if the net was empty for each shot.
        '''
        self.df['emptyNet'] = self.df['emptyNet'].fillna(0)
        return self.df['emptyNet'] == 0
    
    def _handle_na_values_for_coordinates_n_rinkside(self):
        shots_without_x_coords = set(self.df[self.df['coordinateX'].isna()].index)
        shots_without_y_coords = set(self.df[self.df['coordinateY'].isna()].index)
        coords_to_select = self.df.iloc[ list(set(self.df.index) - shots_without_x_coords.union(shots_without_y_coords)) ]

        rinkSide_na = coords_to_select[coords_to_select['rinkSide'].isna()].index
        coords_to_select = coords_to_select[~coords_to_select.index.isin(rinkSide_na)]
        logger.info(f"Found {len(coords_to_select)} shots with coordinates and rinkSide specified.")
        if self.verbose:
            na_X_and_Y_set_index = shots_without_x_coords.intersection(shots_without_y_coords)
            na_only_X_set_index = shots_without_x_coords - shots_without_y_coords
            na_only_Y_set_index = shots_without_y_coords - shots_without_x_coords
            logger.info(f"""
                Coordinates NA stats:
                    {len(self.df) - len(coords_to_select)} shots without coordinates.
                    {len(na_X_and_Y_set_index)} {na_X_and_Y_set_index} shots without X and Y coordinates.
                    {len(na_only_X_set_index)} {na_only_X_set_index} shots without X coordinates.
                    {len(na_only_Y_set_index)} {na_only_Y_set_index} shots without Y coordinates.
                
                RinkSide NA stats:
                    {len(rinkSide_na)} shots without rinkSide specified (so can know to which goal they refer).
    
                GONNA SKIP THEM FOR DISTANCE/ANGLE COMPUTE AND FILL DISTANCE/ANGLE WITH NA VALUES
            """)
        return coords_to_select

    def calculate_distance_to_goal(self):
        '''
        Calculate the distance to the goal for each shot.
        '''
        unified_coordinates_df = unify_coordinates_referential(
            self.df_for_compute_with_goal[['coordinateX', 'coordinateY', 'rinkSide']]
        )
        dists =  np.linalg.norm(self.GOAL_POSITION - unified_coordinates_df[['coordinateX','coordinateY']], axis=1)
        dists = pd.Series(dists, index=unified_coordinates_df.index)
        # fill with NA values the shots without coordinates in the dists Series
        res = dists.reindex(self.df.index)
        return res


    def calculate_angle_to_goal(self):
        '''
        Calculate the angle to the goal for each shot.
        ''' 
        unified_coordinates_df = unify_coordinates_referential(
            self.df_for_compute_with_goal[['coordinateX', 'coordinateY', 'rinkSide']]
        )
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