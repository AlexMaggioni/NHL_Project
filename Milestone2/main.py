import hydra
import os
from pathlib import Path
from omegaconf import DictConfig
import pandas as pd
from rich import print

from feature_engineering import NHL_Feature_Engineering
from utils import init_logger, verify_dotenv_file

verify_dotenv_file(Path(__file__).parent.parent)


@hydra.main(
    version_base=None, config_path=os.getenv("YAML_CONF_DIR"), config_name="main_config"
)
def run_experiment(cfg: DictConfig) -> None:
    # MODEL_CONFIG = cfg.model
    DATA_PIPELINE_CONFIG = cfg.data_pipeline
    print(cfg)
    # =================================Prepare Data==========================================================
    RAW_DATA_PATH = Path(os.getenv("DATA_FOLDER"))/ cfg.raw_train_data_path
    logger.info(f"Loading raw data from {RAW_DATA_PATH}")
    RAW_DATA_DF : pd.DataFrame = pd.read_csv(RAW_DATA_PATH)
    data = NHL_Feature_Engineering(
        df = RAW_DATA_DF,
        distance_to_goal = DATA_PIPELINE_CONFIG.distance_to_goal,
        angle_to_goal = DATA_PIPELINE_CONFIG.angle_to_goal,
        is_goal = DATA_PIPELINE_CONFIG.is_goal,
        empty_net = DATA_PIPELINE_CONFIG.empty_net,
    )


if __name__ == "__main__":
    logger = init_logger("run_experiments.log")
    run_experiment()
