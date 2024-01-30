# NHL Data Science Project

Authors:
*	Loic Mandine
*	Alex Maggioni

# Repo Filetree Structure

`blog_website`: contains the blog website files to run the website locally. See below for more details.

`instructions_files`: contains the instructions for the project

`Milestone1`: contains the python (ready-to-run/reproducible) scripts and notebooks for the first milestone

`Milestone2`: contains the python (ready-to-run/reproducible) scripts and notebooks for the second milestone

`.env` : contains the environment variables for the project, that you need to modify before runnning the python scripts/notebooks (!!!!!! SPECIFY ONLY ABSOLUTE PATH !!!!!!)

`requirements.txt` : contains the python packages needed to run the python scripts/notebooks

`data` : contains the data used for the project (we only pushed the .csv file (43.3 MB), the .json files were too heavy (5GB))

`assets` : contains the images used for the notebook/blog website

`conf` : contains the yaml files for the experiment parameters. Every yaml file is commented and so self-explanatory + a README.md file.

`sh_scripts` : contains the bash scripts for several purposes

`utils` : contains the python scripts for several purposes

`Makefile` : use here to launch very useful commands (not as a build file)

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

There is a README.md [file](./Milestone1/README.md) in the Milestone1 folder that explains how to run the python scripts/notebooks.

# Milestone 2 - How to run python scripts/notebooks

There is a README.md [file](./Milestone2/README.md) in the Milestone1 folder that explains how to run the python scripts/notebooks.

# DATA VERSIONING 

There is a README.md [file](./data/README.md) in the data folder that explains how we decided to keep track of our data in complement of COMETML.
