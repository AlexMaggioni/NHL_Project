---
layout: post
author: Equipe A07
title: Brief Tutorial on Data Acquisition
---

# Comment télécharger les données play-by-play de la LNH pour les saisons 2016-2021

Les passionnés de hockey le savent bien : avoir accès à des données détaillées peut faire toute la différence. Dans ce guide, je vais vous montrer comment extraire les données play-by-play des matchs de la saison régulière et des séries éliminatoires pour les saisons 2016-2021 de la LNH. La logique de telechargement des donnees est completement gere par le fichier `nhl_rest_api_fetcher.py`.

## Comprendre la stucture de l'API

### 1. Décryptons le gameID:

Un gameID typique a l'apparence suivante: `2023020001`.

* Les 4 premiers chiffres déterminent la saison du jeu.
* Les 2 chiffres suivants représentent le type de jeu (saison régulière, playoffs, etc.).
* Les 4 derniers chiffres sont un identifiant unique pour chaque match.

Avec ces informations en main, notre mission est de récupérer tous les matchs ayant une structure `[2016 à 2020]-[02 ou 03]-[ID]`.

### 2. L'API de la NHL, notre allié:

L'API de la NHL nous permet d'accéder à une multitude de données. Nous commençons par utiliser l'endpoint `https://statsapi.web.nhl.com/api/v1/schedule` pour obtenir les gameIDs. Nous pouvons spécifier la saison et le type de match avec des paramètres comme `?season={season}` et `?gameType={Type of game}`. Cette logique a été implémentée dans notre classe `nhl_rest_api_fetcher.py::Schedule_endpoints_Fetcher`.

Ensuite, avec les gameIDs obtenus, nous interrogeons l'endpoint `https://statsapi.web.nhl.com/api/v1/game/[GAME_ID]/feed/live/` pour récupérer les données play-by-play. Cette logique a été implémenter dans notre classe `nhl_rest_api_fetcher.py::Game_endpoints_Fetcher`.

## Fonctionnement de notre code

### `Base_Fetcher`: La Classe Mère

La classe Base_Fetcher sert de fondation pour nos opérations de récupération de données. Elle offre la structure de base et les méthodes essentielles qui seront héritées et possiblement étendues par les sous-classes.

Les trois principales fonctions de Base_Fetcher:

* `fetch()`:

Cette méthode est le cœur de la classe. Elle effectue la requête GET vers l'API NHL. Elle prend en charge différents formats de sortie tels que "json", "binary", "text", et "raw". La méthode offre également une fonctionnalité pour sauvegarder localement la réponse. Si un chemin est fourni et qu'un fichier existe déjà à ce chemin, la requête GET est évitée.

* `_read_content_from_local()`:

Si la méthode fetch() trouve qu'un fichier existe déjà localement, cette méthode est appelée pour lire le contenu du fichier. Elle gère différents formats tels que "json", "binary" et "text".

* `_save_local()`:

Cette méthode est utilisée pour sauvegarder la réponse de la requête GET localement. Elle peut gérer différents formats de données, et lancer une erreur si elle ne sait pas comment sérialiser un objet particulier. 

### Les Sous-Classes: Ajouter des Vérifications
Même si la Base_Fetcher est très puissante par elle-même, il est nécessaire d'avoir des vérifications supplémentaires pour des cas spécifiques. C'est là que les sous-classes comme Game_endpoints_Fetcher et Schedule_endpoints_Fetcher entrent en jeu. Ces sous-classes héritent de Base_Fetcher et ajoutent des vérifications sur les entrées des utilisateurs. Cela garantit que l'URL est correcte avant de faire la requête et guident l'utilisateur pour une utilisation plus fluide et plus intuitive.

Nous avons vraiment commenté et expliqué chaque partie du code, autant que possible. Donc, pour référence, vous pouvez directement aller lire le code si jamais il vous manque de détails.

## Comment utiliser notre outil? 

Télécharger des données détaillées peut sembler une tâche compliquée. Cependant, avec notre script, c'est un jeu d'enfant ! Suivez ces étapes simples et obtenez les données dont vous avez besoin en un rien de temps.

### 1. Préparation de l'environnement :

Avant de plonger dans le téléchargement, préparez votre environnement. Commencez par installer les exigences nécessaires :

```bash
python -m venv venv_NHL_API_fetcher
pip install -r requirements.txt
```

### 2. Configuration de vos préférences :

Ensuite, c'est le moment de personnaliser les paramètres selon vos besoins. Ouvrez le fichier .env et ajustez les valeurs :

```bash
# .env file example
DATA_FOLDER = 'ABSOLUTE_PATH_TOWARDS_DATA_DIR' # folder where data will be stored
LOGGING_FILE = 'ABSOLUTE_PATH_TOWARDS_LOG_DIR' # folder where logs file will be stored
```

### 3. Lancement du script :

Une fois tout en place, lancez le script avec cette simple commande :

```bash
# télécharge chaque play de chaque match, que ce soit des playoffs ou de la saison régulière, pour chaque saison de 2016 à 2020
python Milestone1/nhl_rest_api_fetcher.py --years $(seq -s ' ' 2016 2020)
```

Et voilà, aussi simple que ça !

***Le script se charge de télécharger chaque play de chaque match, que ce soit des playoffs ou de la saison régulière, pour chaque saison de 2016 à 2020.***

**<u>Structure des données résultante:</u>**

Vos données seront soigneusement organisées dans le dossier DATA_FOLDER selon la structure suivante :

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

Chaque fichier est un document JSON contenant toutes les données play-by-play d'un match. Et bonne nouvelle ! **Si un fichier JSON existe déjà, le script n'effectuera pas de téléchargement redondant**. Vous pouvez donc lancer le script autant de fois que vous le souhaitez sans vous soucier de télécharger les mêmes données.

Petite note : Lors de la première utilisation, attendez-vous à un téléchargement d'environ 4,3 Go de fichiers JSON. La durée sera d'environ 10 minutes (testé sur un laptop OMEN HP avec une connexion Wi-Fi moyenne). Mais ce n'est pas tout ! Pour plus de transparence, notre script génère également des fichiers de logs dans le dossier log_file, vous permettant ainsi de suivre l'évolution des téléchargements.

**Voilà, c'est tout ! Avec ces étapes faciles à suivre, plongez dans les profondeurs des données de la LNH et exploitez-les comme bon vous semble. Bonne analyse !**
