---
layout: post
author: Équipe A07
title: Ingénierie des données I
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

Nous avons réalisé une ingénierie des caractéristiques de base pour créer des métriques spécifiques telles que la distance et l'angle des tirs. Ces métriques sont essentielles pour comprendre en profondeur les dynamiques du jeu et les stratégies des joueurs. Ci-dessous, nous analyserons ces caractéristiques en détail, en examinant leurs impacts sur la fréquence et l'efficacité des tirs, ainsi que sur la probabilité de marquer des buts.

# Analyse du nombre de tirs en fonction de la distance par rapport au but

![SCREENSHOT OF Comparaison des types de tirs](feature_engineering_1/2023-10-08-Shot_vs_Distance.png)

L'analyse du graphique intitulé "Nombre de Tirs par Distance au But" révèle des tendances intéressantes sur la fréquence des tirs en hockey en fonction de leur distance par rapport au but. L'utilisation d'une échelle logarithmique est cruciale ici pour représenter de manière appropriée la grande variation de fréquence entre les tirs effectués près du but et ceux tentés de loin.

En observant les données, on note sans surprise que les tirs effectués à moins de 60 pieds sont extrêmement fréquents, avec une fréquence dépassant les 10 000. Cette zone, étant proche du but, est logiquement la plus sollicitée pour tenter de marquer. En revanche, à mesure que la distance augmente, la fréquence des tirs diminue significativement, atteignant un creux pour les tirs résultant en buts et ceux n'ayant pas abouti entre 75 et 125 pieds. Cette zone correspond à la partie centrale de la glace, où le jeu est fortement contesté et la pression défensive est à son comble, rendant les tirs de qualité nettement plus difficiles à réaliser.

Il est également pertinent de remarquer que pour les distances supérieures à 125 pieds, il y a une légère augmentation de la fréquence des tirs et, de façon plus marquée, des buts. Cette tendance pourrait correspondre aux stratégies de fin de match où une équipe retire son gardien de but pour ajouter un joueur de champ et ainsi créer un avantage numérique. En conséquence, l'équipe en infériorité numérique se retrouve souvent à tirer depuis sa propre zone défensive vers un but vide, ce qui pourrait expliquer l'augmentation observée dans ces situations particulières.

# Analyse du nombre de tirs en fonction de l'angle de tir

![SCREENSHOT OF Comparaison des types de tirs](feature_engineering_1/2023-10-08-Shot_vs_Angle.png)

Ce graphique présente la distribution des tirs en fonction de leur angle par rapport au but. L'échelle logarithmique est utilisée ici pour mieux visualiser les données étant donné la disparité des fréquences de tirs à différents angles.

L'analyse montre que la très grande majorité des tirs et des buts sont effectués face au filet, avec une distribution des angles de tir s'étendant de -150 à 150 degrés, ce qui représente effectivement presque la totalité de l'arc possible devant le but. La symétrie de la distribution autour de l'angle zéro indique que les tirs sont répartis de manière assez uniforme de chaque côté du filet.

La concentration des tirs dans cette zone angulaire est logique, car les angles extrêmes rendraient les tirs non seulement techniquement difficiles mais aussi moins susceptibles de surprendre le gardien. Le pic central suggère que les angles proches de la perpendiculaire au plan du but sont les plus communs et les plus propices à marquer, ce qui est cohérent avec la stratégie de jeu générale visant à maximiser les chances de réussite en tirant face au but. L'utilisation d'une échelle logarithmique permet de distinguer clairement les variations de fréquence entre les angles de tir fréquemment utilisés et ceux moins courants, qui sans cela pourraient être masqués par l'échelle importante des valeurs centrales.


# Histogramme 2D mettant en relation l'angle et la distance du tir

![SCREENSHOT OF Comparaison des types de tirs](feature_engineering_1/2023-10-08-2D_Histogram_Distance_Angle.png)

Ce graphique présente la distribution des tirs en fonction de leur angle par rapport au but dans un sport comme le hockey. L'échelle logarithmique est utilisée ici pour mieux visualiser les données étant donné la disparité des fréquences de tirs à différents angles.

L'analyse montre que la très grande majorité des tirs et des buts sont effectués face au filet, avec une distribution des angles de tir s'étendant de -150 à 150 degrés, ce qui représente effectivement presque la totalité de l'arc possible. La symétrie de la distribution autour de l'angle zéro indique que les tirs sont répartis de manière assez uniforme de chaque côté du filet.

La concentration des tirs dans cette zone angulaire est logique, car les angles extrêmes rendraient les tirs non seulement techniquement difficiles mais aussi moins susceptibles de surprendre le gardien. Le pic central suggère que les angles proches de la perpendiculaire au plan du but sont les plus communs et les plus propices à marquer, ce qui est cohérent avec la stratégie de jeu générale visant à maximiser les chances de réussite en tirant face au but. 

Les tirs avec des angles supérieurs à 90 degrés ou inférieurs à -90 degrés sont rares et techniquement difficiles à réaliser, car ils impliquent un tir depuis un point situé presque derrière le but. Néanmoins, des tirs sont tentés depuis ces angles extrêmes. Une explication plausible est que, vu le caractère imprévisible des rebonds de la rondelle en hockey, les joueurs peuvent tenter de tirer depuis ces positions non optimales dans l'espoir d'un rebond favorable qui pourrait mener à un but. Cela peut se produire lorsque les joueurs sont pressés par l'adversaire et cherchent à exploiter chaque occasion, même les moins prometteuses, pour diriger la rondelle vers le but et créer une chance de marquer grâce à une déviation ou un rebond inattendu. La nature aléatoire de ces rebonds peut parfois déjouer la défense et le gardien, conduisant à des buts improbables.

# Taux de buts en fonction de la distance
![SCREENSHOT OF Comparaison des types de tirs](feature_engineering_1/2023-10-08-Goal_Distance_Binned.png)

Le graphique illustre le rapport entre la distance des tirs au but et la probabilité de marquer. L'axe des abscisses montre les distances au but regroupées en intervalles (ou "bins") exprimés en pieds, et l'axe des ordonnées représente le taux de buts, indiquant la fréquence à laquelle les tirs de chaque intervalle se convertissent en buts.

L'analyse révèle que le taux de buts est le plus élevé pour les tirs effectués de très près, plus précisément dans la plage de 0 à 10 pieds du but, avec un taux touchant les 2%. Cela suggère que les tirs effectués à courte distance ont une probabilité significativement plus élevée de se transformer en buts, ce qui est intuitif étant donné la proximité du tireur au but et la moindre réaction disponible pour le gardien.

À mesure que la distance augmente, le taux de buts diminue de façon assez régulière, ce qui est attendu puisque les tirs deviennent plus difficiles à cadrer et offrent plus de temps de réaction au gardien. Après la distance de 50 pieds, le taux de buts chute sous la barre des 0.25% et continue de diminuer, indiquant que les chances de marquer depuis une longue distance sont faibles.

Ce que nous pouvons interpréter de cette tendance, c'est que les stratégies offensives privilégient les tirs rapprochés, qui sont plus susceptibles de résulter en un but, tandis que les tentatives lointaines sont nettement moins efficaces. Cette information pourrait être utilisée pour optimiser les tactiques de jeu, en encourageant les joueurs à chercher à se rapprocher du but avant de tirer ou à créer des situations de jeu qui favorisent des tirs de plus courte distance.

L'échelle logarithmique n'a pas été utilisée. Cette représentation met en évidence la chute rapide et constante du taux de buts à mesure que la distance augmente. La distribution présentée dans le graphique est nettement asymétrique, avec une concentration élevée de taux de buts pour les tirs effectués à proximité du but et une diminution rapide pour les tirs à longue distance. Cette asymétrie correspond aux conclusions tirées des analyses précédentes : les tirs effectués près du but ont non seulement une fréquence plus élevée mais aussi une probabilité plus grande de se transformer en buts.

# Taux de but en fonction de l'angle
![SCREENSHOT OF Comparaison des types de tirs](feature_engineering_1/2023-10-08-Goal_Angle_Binned.png)

Le graphique "Taux de Buts par Angle Biné du Tir" illustre la probabilité de marquer un but en fonction de l'angle de tir en degrés. Les données sont regroupées en intervalles d'angles, et le taux de buts pour chaque intervalle est représenté sur l'axe vertical.

L'analyse de ce graphique montre que le taux de buts est nettement plus élevé pour les angles proches de zéro, ce qui correspond à des tirs effectués face au but. Cette zone centrale, où les tirs sont plus directs et donc plus susceptibles de réussir, présente un pic de probabilité, avec un taux de buts dépassant 0.0120 pour les angles compris entre -10 et 10 degrés.

À mesure que l'angle s'éloigne de cette zone centrale, le taux de buts diminue progressivement, ce qui indique que les tirs pris avec un angle plus aigu par rapport au plan frontal du but ont moins de chance de se transformer en buts. Cela est cohérent avec la logique du jeu : plus l'angle est fermé, plus il est difficile de trouver une ouverture pour marquer.

Les tirs effectués avec des angles extrêmement élevés, supérieurs à 90 ou inférieurs à -90 degrés, ont un taux de buts significativement plus bas, ce qui est visible par les faibles hauteurs des barres dans ces intervalles. Ces tirs représentent des situations moins idéales pour marquer, souvent résultant de rebonds ou de tentatives désespérées.

La distribution des taux de buts par angle est symétrique autour de l'angle zéro, ce qui confirme que les tirs face au but sont les plus efficaces, tandis que les chances de marquer diminuent de manière similaire que l'on tire de la droite ou de la gauche. Cela souligne l'importance de la position et de l'orientation du joueur lorsqu'il effectue un tir pour maximiser ses chances de succès.

# Analyse du nombre de tirs en fonction de la distance par rapport au but
![SCREENSHOT OF Comparaison des types de tirs](feature_engineering_1/2023-10-08-Goal_Distance.png)

Le graphique présente le nombre de buts marqués à différentes distances du but, distinguant les buts sur un filet vide de ceux marqués sur un filet non vide, en utilisant une échelle logarithmique pour tenir compte des écarts d'échelle. L'échelle logarithmique permet de mieux visualiser les variations du nombre de buts sur des ordres de grandeur différents, et il est important de se référer à l'axe des ordonnées pour interpréter correctement les valeurs.

Comme attendu, les buts marqués sur un but non vide sont bien plus fréquents à des distances inférieures à 60 pieds, ceci correspondant à la zone directement en face du gardien où les joueurs ont plus de chances de marquer. On observe un minimum entre 100 et 125 pieds, qui correspond au milieu de la glace, une zone où il est habituellement plus difficile de tirer efficacement à cause de la pression défensive.

Ce qui est particulièrement intéressant, c'est la hausse notable du nombre de buts marqués sur un but non vide à des distances supérieures à 125 pieds, approchant presque 100 exemples. Cette augmentation est inhabituelle et est investiguée davantage dans la section suivante.

Concernant les buts sur un filet vide, la tendance est relativement stable, avec une légère diminution en fonction de la distance. Cela semble logique puisque, pour un joueur professionnel, marquer dans un but vide peut être réalisé avec une certaine facilité, et cela même depuis leur propre zone défensive, notamment en fin de partie quand l'équipe adverse a retiré son gardien pour ajouter un attaquant supplémentaire.

# Analyse des données aberrantes (buts net non-vide)

En analysant les cas inhabituels de buts marqués à des distances supérieures à 125 pieds (en filtrant pour les coordonnées X inférieures à 0), on découvre que ces anomalies représentent 373 cas au total dans les données d'entraînement, couvrant les saisons de 2016 à 2019, ce qui équivaut à 0.112% de l'ensemble des données. De manière surprenante, tous ces exemples proviennent exclusivement de la saison 2019, et une proportion significative de 85% sont issus des matchs des séries éliminatoires, comme indiqué dans le tableau suivant :

| Season | P | R | Total |
|:------:|:-----:|:-----:|:---------:|
| 2019 | 316   | 57    | 373   |


Cette concentration de données aberrantes sur une saison spécifique et pendant les séries éliminatoires indique vraisemblablement une erreur d'entrée des données. Prenons l'exemple du match du 27 septembre 2020 entre Tampa Bay et les Dallas Stars lors de la finale de la Coupe Stanley. Un but enregistré dans les données brutes semble provenir d'une erreur :

| GameId   | GameDate  | HomeTeam | AwayTeam | ByTeam | Period | PeriodTime | RinkSide | EventType | Shooter   | CoordinateX | CoordinateY | EmptyNet |
|--------------|---------------|--------------|--------------|------------|------------|----------------|--------------|---------------|---------------|-----------------|-----------------|--------------|
| 2019030415 | 2020-09-27 | TBL          | DAL          | DAL        | 1          | 17:52          | right        | GOAL          | Corey Perry   | 74.0            | -2.0            | False        |


Selon les données, 'rinkSide' est à droite, ce qui impliquerait que le but de Dallas se trouve à droite et que l'équipe attaque vers la gauche. Cependant, les coordonnées suggèrent que Corey Perry aurait marqué depuis sa propre zone défensive, ce qui est peu plausible.

En consultant le NHL Game Center pour une reprise vidéo de l'action (voir [https://www.nhl.com/gamecenter/dal-vs-tbl/2020/09/26/2019030415]), il apparaît clairement que Corey Perry attaque vers la droite, contredisant les données initiales. Ainsi, il semblerait que l'entrée 'rinkSide' soit incorrecte ou mal alignée avec la convention utilisée dans le reste des données.

La prédominance des erreurs détectées lors de la saison 2019 et plus particulièrement pendant les séries éliminatoires suggère une potentielle modification temporaire des méthodes d'enregistrement des 'rinkSide', nécessitant un ajustement pour maintenir la fiabilité des données.





