In this directory, you can find the configuration files that you will to update to run the experiments.

* `OmegaConf-based` : yaml are read by `hydra` library, and especially we use special syntax and heritage between yaml files.

At time of writing, we have only two **MAIN** type of experiments.

1. `hp_opt_main_conf.yaml` : main file containing parameters for hyperparameter optimization research associated to [hp_opt_main_conf.py](../Milestone2/hp_opt_main_conf.py)

2. `main_conf.yaml` : main file containing parameters for a training run associated to [training_main.py](../Milestone2/training_main.py)

* `data_pipeline/*.yaml` : contains yaml file related to the data-processing pipeline

* `model/*.yaml` : contains yaml file related to the model parameters

* `hp_optimizer/*.yaml` : contains yaml file related to define the hyperparameter optimization parameters

**We tried to partitionate every independant of the execution flow as a YAML file... Every Yaml file is commented and so self-explanatory.**