# Before Running Anything

* Initialiser CometML : `comet init`

There two actually 2 entrypoints in this dir :

* `hp_opt_main_conf.py` : entrypoint for hyperparameter optimization research
* `training_main.py` : entrypoint for training run

**Useful tip:** when you want to know the parameters coming the yaml files with which the python script will run, you can use the commands in the Makefile (see file) `make see_hp_opt_conf` and `make see_main_conf` to see the parameters of the yaml files. (requires `apt install yq` before)

# Run single-training style experiment

* Update the yaml files in conf/ with your desired parameters. Every yaml file is commented and so self-explanatory.

* Run the experiment with the following command:

```bash
# Run experiment
python Milestone2/training_main.py
```

## Run hyperparameter optimization

* Update the yaml files in conf/ with your desired parameters. Every yaml file is commented and so self-explanatory.

* Run the experiment with the following command:

```bash
# Run experiment
python Milestone2/hp_opt_main_conf.py
```