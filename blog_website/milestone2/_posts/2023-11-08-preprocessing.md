---
layout: post
author: Équipe A07
title: Prétraitement et encodage des données
---

<style>
  #plot-container {
    justify-content: center;
    align-items: center;
    width: 60vw; 
    height: 60vh;
    margin-bottom: 0px;
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }


  td, th {
    border: 1px solid #dddddd;
    text-align: left;
    padding: 8px;
  }

  tr:nth-child(even) {
    background-color: #f2f2f2;
  }

</style>

# Prétraitement et encodage des données

Bien que cette section n'ait pas été explicitement demandée dans le blog, nous considérons qu'il est important de mentionner les changements significatifs que nous avons apportés pour optimiser l'entraînement de nos modèles, y compris le modèle XGBoost entraîné sur l'ingénierie des caractéristiques II et dans nos tentatives de développer les meilleurs modèles possibles. Voici un aperçu des prétraitements les plus importants effectués :

- **`gameDate`** : Initialement très granulaire, presque aussi unique qu'un gameId, cette variable a été simplifiée pour ne refléter que le mois de la rencontre. Transformée en une variable ordinale de 1 à 12, elle débute en octobre (1), se poursuit en novembre (2), et ainsi de suite, en accord avec le calendrier de la saison NHL.

- **`gameType`** : Le type de match, un facteur crucial, différencie la pression des playoffs de celle de la saison régulière. Un encodage binaire a été utilisé : 1 pour les playoffs, 0 pour la saison régulière.

- **`byTeam`** : UUn encodage one-hot aurait augmenté notre jeu de données de 31 colonnes, une par équipe. Pour éviter cette expansion dimensionnelle, nous avons modifié notre fonction de traitement des données brutes pour ajouter une colonne winTeam, indiquant l'équipe victorieuse du match. À l'aide de cette colonne, un classement ordinal des équipes a été établi pour chaque saison. Ainsi, le modèle peut inférer si le tir vient d'une équipe forte ou faible.

- **`shooterId`** : La compétence du tireur influe sur le résultat du tir. Par exemple, Sydney Crosby aurait probablement plus de chances de marquer qu'un joueur moyen dans des conditions similaires. Un encodage one-hot n'étant pas envisageable, car il aurait créé des milliers de nouvelles colonnes, nous avons calculé la moyenne de buts par match pour chaque joueur, avec une mesure de certitude basée sur le nombre de matchs joués. Cela permet d'équilibrer cette moyenne individuelle avec la moyenne générale des joueurs pour la saison, offrant au modèle une indication sur la compétence du tireur.

- **`goalieId`** : Pour les gardiens, le taux d'arrêts a été ajusté avec une mesure de certitude basée sur le nombre de matchs joués, afin de mieux refléter la qualité réelle des gardiens au fil des saisons.

- **`shotType`** : Face à des données manquantes, nous avons choisi de les imputer par "Wrist shot", le type de tir le plus commun. Avec seulement sept dimensions, nous avons utilisé un encodage one-hot, préservant ainsi la diversité de cette variable à sept niveaux.

- **`strength`** : Nous avons remarqué que strength n'était renseignée que lorsqu'un but était marqué, ce qui posait problème pour notre objectif prédictif. Afin d'éviter un surajustement, nous avons requalifié strength pour qu'elle indique l'écart numérique entre les joueurs de l'équipe visée (byTeam avant le prétraitement) et ceux de l'équipe adverse, transformant une donnée conditionnelle en une métrique constante de l'avantage numérique.

- **`lastEventType`** : Devant une multitude d'événements possibles, nous avons regroupé ceux n'ayant pas d'impact sur la prédiction d'un but, comme "GAME_SCHEDULE" ou "PERIOD_START", dans une catégorie "OTHER". Un encodage one-hot a ensuite été appliqué aux catégories restantes.

- **`speed`** : Les valeurs manquantes dans cette colonne résultaient d'un timeElapsed égal à 0, impliquant une vitesse théoriquement infinie. Nous avons choisi d'imputer ces valeurs manquantes par le maximum de la distribution, simulant une action instantanée et explosive sur la glace.

En résumé, ce processus de prétraitement des données est crucial pour améliorer la qualité et l'efficacité de nos modèles.