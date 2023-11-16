# Before Running Anything

*	Modifier les variables d'environnement du fichier `.env` !!!!!! SPECIFY ONLY ABSOLUTE PATH !!!!!!
* 	Construisez votre python venv : `pip install -r requirements.txt`

## Acquisition des données (json files) depuis l'API de la NHL (requêtes GET) 

```bash
# télécharge chaque play de chaque match, que ce soit des playoffs ou de la saison régulière, pour chaque saison de 2016 à 2020
python Milestone1/nhl_rest_api_fetcher.py --years $(seq -s ' ' 2016 2020)
```

## Nettoyer les données (.json to pandas dataframe)

*<u>IMPORTANT NOTE:</u>* For sake of data reproducibility/lineage, filename of the newly generated .csv file MUST contain a *git commit id* in which `json_scrapper.py` was modified. 

To retreive such, do:
```bash
git log -1 --pretty=format:"%h" Milestone1/json_scrapper.py

# ouput: 1a2b3c4d
```

Then, you can run the following command:

```bash
# Scrappe tous les jsons file pour créer un fichier csv; concatenation of the .env\'s DATA_FOLDER var + arg given
python Milestone1/json_scrapper.py --path_to_csv clean_data.csv
```

## Notebooks pour les visualisation simples/avancées et débuggage des fichiers .json

* The notebooks are ready off-the-shelf for execution, so just choose a kernel and run them.
