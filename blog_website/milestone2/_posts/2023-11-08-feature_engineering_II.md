---
layout: post
author: Équipe A07
title: Ingénierie des données II
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

# Caractéristiques Avancées Explorées

Voici les caract.ristiques que nous avons développé pour cette section :

- **`distanceToGoal`**: Révèle la distance qui sépare le tireur du but adverse, un prédicteur essentiel de la probabilité de marquer.
- **`angleToGoal`**: L'angle du tir par rapport au cadre du but, qui influence les chances de succès.
- **`isGoal`**: Un flag indiquant l'issue ultime de la tentative — but ou pas.
- **`emptyNet`**: Signale si le gardien est absent, modifiant radicalement les attentes autour du tir.
- **`periodTimeSeconds`**: Le moment précis de l'événement, converti en une mesure temporelle uniforme.
- **`lastEventType`**: Le dernier événement avant le tir, contexte clé pour la prise de décision.
- **`lastCoordinateX`** et **`lastCoordinateY`**: Positionne le jeu juste avant le tir actuel, essentiel pour comprendre le mouvement de la rondelle.
- **`timeElapsed`**: Le temps écoulé depuis la dernière action, une piste sur l'intensité du jeu.
- **`distanceFromLastEvent`**: La distance parcourue depuis le dernier événement, illustrant le dynamisme du jeu.
- **`rebound`**: Indique si le tir suit un rebond, souvent source d'opportunités imprévues.
- **`changeAngle`**: La différence d'angle par rapport au tir précédent, si c'est un rebond. Un changement significatif peut désorienter le gardien.
- **`speed`**: Estimation de la vitesse entre deux événements, capturant la vélocité de la séquence.

## Décodage de `elapsedPowerPlay`

Prenez l'exemple des pénalités consécutives à une bataille sur la glace — un scénario où deux joueurs se voient attribuer une pénalité majeure de 5 minutes. Dans ce cas, bien que chaque équipe se retrouve avec un joueur en moins, il n'y a pas de situation de supériorité numérique car les effectifs restent égaux à 4 contre 4.

Notre caractéristique `elapsedPowerPlay` ne se contente pas de comptabiliser le temps cumulé des pénalités mais identifie un power play par une différence effective dans le nombre de joueurs sur la glace. Cette distinction est cruciale pour saisir la nature fluide et parfois contradictoire du jeu, où le nombre de joueurs actifs est plus parlant que la simple durée des pénalités.

En somme, ces caractéristiques déployées avec soin ouvrent la voie à des analyses poussées et des stratégies affinées, plaçant les données au cœur de la performance sportive.

# Petite commentaire sur le prétraitement des données




