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


# Milestone 1 - How to run python scripts/notebooks realted to Milestone 1

# Before Running Anything

*	Modifier les variables d'environnement du fichier `.env` !!!!!! SPECIFY ONLY ABSOLUTE PATH !!!!!!
* 	Construisez votre python venv : `pip install -r requirements.txt`

## Acquisition de données (json files) depuis l'API de la NHL (requêtes GET) 

* `python Milestone1/nhl_rest_api_fetcher.py --years $(seq -s ' ' 2016 2020)`

## 