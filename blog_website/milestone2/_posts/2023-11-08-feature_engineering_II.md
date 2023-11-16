---
layout: post
author: Équipe A07
title: 4. Ingénierie des données II
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

# Introduction 

Dans la continuité de notre analyse statistique avancée du hockey, nous avons mis en œuvre une ingénierie des caractéristiques sophistiquée pour mieux comprendre les nuances et les dynamiques du jeu. Cette deuxième partie se concentre sur l'élaboration et l'exploration de variables spécifiques qui nous permettent de déchiffrer plus finement les stratégies, les décisions et les probabilités derrière chaque action sur la glace. Les caractéristiques que nous avons développées sont essentielles pour prédire les issues des tirs et comprendre les comportements des joueurs en fonction de différentes situations de jeu.

# Caractéristiques avancées explorées

Voici les caractéristiques que nous avons développées pour cette section :

- **`distanceToGoal`** : Cette mesure indique la distance entre le tireur et le but adverse. C'est un prédicteur clé de la probabilité de marquer, car les tirs de plus courte distance ont généralement de meilleures chances de succès.

- **`angleToGoal`** : L'angle sous lequel le tir est effectué par rapport au cadre du but. Un - angle optimal peut augmenter significativement les chances de marquer.

- **`isGoal`** : Un indicateur booléen qui précise si la tentative de tir s'est conclue par un but.

- **`emptyNet`** : Signale si le but est vide au moment du tir. Un but vide change radicalement les attentes autour de la probabilité de marquer.

- **`periodTimeSeconds`** : Le temps précis de l'événement, converti en secondes, offrant une mesure uniforme et précise du timing du jeu.

- **`lastEventType`** : Le dernier événement survenu avant le tir, fournissant un contexte essentiel pour comprendre les décisions prises par les joueurs.

- **`lastCoordinateX` et `lastCoordinateY`** : Les coordonnées de l'action précédant le tir, importantes pour analyser le mouvement de la rondelle et la position des joueurs.

- **`timeElapsed`** : Le temps écoulé depuis la dernière action, offrant des indices sur le rythme et l'intensité du jeu à ce moment précis.

- **`distanceFromLastEvent`** : La distance parcourue par la rondelle depuis le dernier événement, illustrant le dynamisme et la rapidité du jeu.

- **`rebound`** : Indique si le tir suit directement un autre tir, ce qui peut créer des opportunités de marquer imprévues et difficiles à défendre.

- **`changeAngle`** : Mesure la variation d'angle par rapport au tir précédent, en cas de rebond. Un changement d'angle important peut désorienter le gardien et augmenter les chances de marquer.

- **`speed`** : Estime la vitesse entre deux événements, capturant la rapidité et l'intensité de l'action.

- **`elapsedPowerPlay`** : Cette métrique ne se limite pas à mesurer le temps total des pénalités, mais identifie également un avantage numérique réel en prenant en compte la différence effective de joueurs sur la glace. Prenez l'exemple des pénalités consécutives à une bataille sur la glace — un scénario où deux joueurs se voient attribuer une pénalité majeure de 5 minutes. Dans ce cas, bien que chaque équipe se retrouve avec un joueur en moins, il n'y a pas de situation de supériorité numérique car les effectifs restent égaux à 4 contre 4. Ainsi, elapsedPowerPlay offre une perspective plus précise des avantages numériques, reflétant fidèlement les dynamiques changeantes du jeu.

- **`homeSkaters` et `awaySkaters`** : Ces deux indicateurs donnent le nombre de joueurs de l'équipe à domicile (home) et de l'équipe adverse (away) présents sur la glace. Ces données sont cruciales pour comprendre la composition de l'équipe et les stratégies déployées en fonction du nombre de joueurs en action.

Ces caractéristiques avancées seront utilisées dans nos modèles à venir. Elles vont nous aider à mieux analyser les données et à améliorer la précision de nos prédictions.

# Téléchargement du jeu de donnée unifiée pour le match Winnipeg et Washington du 12 mars 2018

Pour cette tâche, nous avons filtré notre jeu de données pour se concentrer sur un match spécifique : la rencontre entre Winnipeg et Washington du 12 mars 2018, ayant l'ID de jeu "2017021065". Ce filtrage a permis de créer un sous-ensemble détaillé de notre ensemble de données final, incluant toutes les caractéristiques avancées que nous avons développées.

Nous avons ensuite téléchargé ce DataFrame filtré, avec toutes ses caractéristiques, en tant que fichier CSV en utilisant la méthode log_dataframe_profile(...) de Comet.ml. Le nom du fichier a été conservé sous 'wpg_v_wsh_2017021065'. 

Il est crucial de souligner que le fichier téléchargé renferme des données unifiées, qui se distinguent du cadre de données brut. Cette nuance revêt une importance majeure : les données unifiées ont été spécifiquement traitées pour tenir compte de l'orientation du jeu, assurant ainsi leur alignement dans un sens unique et cohérent. Ce raffinement est déterminant, car il garantit que l'analyse tient compte de la direction du jeu sur la glace, offrant une perspective plus uniforme et précise, essentielle pour des analyses détaillées et des interprétations fiables.

Vous pouvez trouver ce jeu de donnée à ce lien Comet : (https://www.comet.com/nhl-project/feature-engineering-output/fd71d1239ca64e309dcc9c2bcc185f61?experiment-tab=panels&showOutliers=true&smoothing=0&xAxis=step)


