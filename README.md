# NHL Data Science Project

Equipe A07:
*	Loic MANDINE
*	Alex Maggioni

# Repo Filetree Structure

`blog_website`: contains the blog website files to run the website locally. See below for more details.

`instructions_files`: contains the instructions for the project

`Milestone1`: contains the python (ready-to-run/reproducible) scripts and notebooks for the first milestone

`.env` : contains the environment variables for the project, that you need to modify before runnning the python scripts/notebooks (!!!!!! SPECIFY ONLY ABSOLUTE PATH !!!!!!)

`requirements.txt` : contains the python packages needed to run the python scripts/notebooks

`data` : contains the data used for the project (we only pushed the .csv file (43.3 MB), the .json files were too heavy (5GB))

`assets` : contains the images used for the notebook/blog website

# How to use Jekyll

```bash
	cd blog_website
```

## To run the blog website:

```
bundle exec jekyll serve
```

## To add a new blog:

```
bundle exec jekyll serve autoreload &
```

You will be prompt with an URL...

Then to add a new blog :

* create a new dir `{new_category_posts}/_posts` and **`.md` files needs to start with this format `YYYY-MM-DD-filename.md` to be recognized as new blog**


# Milestone 1 - How to run python scripts/notebooks

# Before Running Anything

*	Modifier les variables d'environnement du fichier `.env` !!!!!! SPECIFY ONLY ABSOLUTE PATH !!!!!!
* 	Construisez votre python venv : `pip install -r requirements.txt`

## Acquisition des données (json files) depuis l'API de la NHL (requêtes GET) 

```bash
# télécharge chaque play de chaque match, que ce soit des playoffs ou de la saison régulière, pour chaque saison de 2016 à 2020
python Milestone1/nhl_rest_api_fetcher.py --years $(seq -s ' ' 2016 2020)
```

## Nettoyer les données (.json to pandas dataframe)

```bash
# Scrappe tous les jsons file pour créer un fichier csv; concatenation of the .env\'s DATA_FOLDER var + arg given
python Milestone1/json_scrapper.py --path_to_csv clean_data.csv
```

## Notebooks pour les visualisation simples/avancées et débuggage des fichiers .json

* The notebooks are ready off-the-shelf for execution, so just choose a kernel and run them.


# Milestone 2 - How to run python scripts/notebooks

## Before Running Anything

* Initialiser CometML : `comet init`

## Run experiment

* Update the yaml files in conf/ with your desired parameters. Every yaml file is commented and so self-explanatory.

* Run the experiment with the following command:

```bash
# Run experiment
python Milestone2/main.py
```

## Run hyperparameter optimization