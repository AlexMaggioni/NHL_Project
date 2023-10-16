---
layout: post
author: Equipe A07
title: Brief Tutorial on Data Acquisition
---
# Telecharger les donnees play-by-play

La logique de telechargement des donnees est completement gere par le fichier `nhl_rest_api_fetcher.py`

## How to use it

* First of all, prepare your env by installing the requirements:

```bash
python -m venv venv_NHL_API_fetcher
pip install -r requirements.txt
```

* Then, you need to tweak the values inside the `.env` file.

```bash
# .env file example
DATA_FOLDER = './data/' # folder where data will be stored
LOGGING_FILE = './log_file/' # folder where logs file will be stored
```

* Then, you can run the script with the following command:

```bash
python nhl_rest_api_fetcher.py
```

This is simple as that!

The script will download for each season between 2016-2020, every plays of every playoffs and regular-season games.

The resulting data will be stored in the `DATA_FOLDER` folder, in the following structure:

```
data
├── 2016
│   ├── 2016030001.json
│   ├── 2016030002.json
...
├── 2017
│   ├── 2017030001.json
│   ├── 2017030002.json
...

```

where each file is a json file containing every play-by-play data of a game.
If a json file already exists, the script will not download it again, so you can run the script multiple times without worrying about downloading the same data twice.

When run for the first time, the script will download around 4.3GB of json files.
And take about 10min to run (on a OMEN HP laptop and a bad WIFI connection).

Besides this, the script will also outputs logging files in the `log_file` folder, so you can check how good downloads happened.

## How it works

> We really thoroughly commented and explains every part of the code, as much as we can,
> so we hope that by checking the code with a global overlook will be sufficient for more details.

But here is the header paragraph of the script giving a brief overview of the script scructure:

```python
"""
Inspired from the general structure of an URL:
    scheme://netloc/path;parameters?query#fragment.
In our case : 
    https://statsapi.web.nhl.com/api/v1/subpath?query.  

We choose an OOP approach to build the NHL REST API Fetcher objects, 
    with in mind a Base_Fetcher Class that will be inherited by other classes
    that corresponds to the different TYPES of endpoints of the NHL REST API.

For now, we have only leveraged two types of endpoints so we have two subclasses :
    - Game_endpoints_Fetcher
    - Schedule_endpoints_Fetcher

Mainly, the Base Class allows to factor out 
    the common attributes (such as part of urls that stays the same) 
    and methods (such as the one that actually make the GET request).

Especially, we delegate the verification of the endpoint path to the subclasses.
    Each subclass must a variable ALLOWED_ENDPOINT_PATH that is a regex that
    will be used to verify the endpoint path provided by the user.

This permits us to have a more flexible code that can be easily extended to other types of endpoints
if the following Milestones would require it.

For now, the script just needs an external config system (Hydra or CLI Interface) to be more flexible regarding Execution Parameters...
"""
```
