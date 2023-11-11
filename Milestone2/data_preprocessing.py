from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold

from rich.console import Console
from rich.table import Table

from utils.utils import unify_coordinates_referential, init_logger, verify_dotenv_file

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
    ) -> None:
        
        self.df_train = df_train
        self.df_test = df_test
        self.cross_validation_k_fold = cross_validation_k_fold
        self.shuffle_before_splitting = shuffle_before_splitting
        self.seed = seed

        self.X_train = self.df_train.drop(columns=["is_goal"])
        self.y_train = self.df_train["is_goal"]

        self.X_test = self.df_test.drop(columns=["is_goal"])
        self.y_test = self.df_test["is_goal"]

    def _print_splitting_stats(self, y_train=None, y_val=None):
        table = Table(title="Train/Val sets - Class Distribution", show_edge=True,show_lines=True,expand=True)

        table.add_column("Split type", justify="left", style="cyan", no_wrap=True)
        table.add_column("NO_GOAL", style="magenta")
        table.add_column('GOAL', style="magenta")
        table.add_row('Train', *y_train.value_counts().astype(str).to_list())
        table.add_row('Val', *y_val.value_counts().astype(str).to_list())

        console = Console()
        console.print(table)

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