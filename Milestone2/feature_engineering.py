import pandas as pd

class NHL_Feature_Engineering:
    
    def __init__(
            self, 
            df : pd.DataFrame,
            distance_to_goal : bool,
            angle_to_goal : bool,
            is_goal : bool,
            
        ):
        self.df = df

    def 