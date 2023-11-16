---
layout: post
author: Équipe A07
title: Exploration des modèles
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


</style>

# Exploration des modèles pour la prédiction des buts

Notre exploration pour affiner la prédiction des buts nous a menés à tester une série de modèles distincts. Nous avons mis à l'épreuve un modèle XGBoost, qui s'est appuyé sur son succès antérieur pour une compréhension plus profonde des données. Un réseau de neurones a également été entraîné, exploitant sa capacité à modéliser des interactions complexes. À cela s'ajoute un classifieur bayésien naïf gaussien, choisi pour sa simplicité et son approche probabiliste. Enfin, une régression logistique a été appliquée, un choix classique pour la classification binaire. Chacun de ces modèles a été entraîné sur la totalité des caractéristiques disponibles, cherchant à maximiser la richesse des informations extraites.

# Méthodologie

Pour affiner nos modèles prédictifs, nous avons adopté une méthodologie d'optimisation bayésienne des hyperparamètres couplée à une stratégie de validation croisée. Cette méthode d'optimisation utilise des modèles probabilistes pour prédire la performance d'un modèle avec différents hyperparamètres, sélectionnant ceux qui maximisent la performance prévue. Contrairement à d'autres techniques d'optimisation qui explorent l'espace des paramètres de manière aléatoire ou par grille, l'optimisation bayésienne vise à être plus efficace en choisissant intelligemment les hyperparamètres à tester en se basant sur les résultats précédents. Cela augmente les chances de trouver l'optimum global dans un espace de recherche complexe et de haute dimension.

Conscients de la menace que représente le surapprentissage, surtout lorsqu'on travaille avec un grand nombre de caractéristiques, nous avons inclus des paramètres de régularisation parmi les hyperparamètres à optimiser. La régularisation ajoute une pénalité pour la complexité du modèle dans la fonction de coût, favorisant ainsi des modèles plus simples qui sont moins susceptibles de mémoriser les données d'entraînement et plus à même de bien généraliser sur des données inédites.

Pour les algorithmes sensibles à l'échelle des données, tels que la régression logistique et le réseau de neurones multicouches (MLP), une étape de standardisation a été effectuée. Cette procédure a pour but de normaliser les caractéristiques en les recentrant autour de zéro et en les redimensionnant à une variance unitaire. Cela assure que les gradients et les étapes d'optimisation sont effectués de manière équilibrée et appropriée sur l'ensemble des caractéristiques.

Il est également essentiel de souligner l'importance des étapes préliminaires de prétraitement des données qui constituent la fondation de nos modèles prédictifs. Nous encourageons vivement les lecteurs à consulter notre article détaillé sur le prétraitement des données, si ce n'est déjà fait. Dans cet article, nous discutons des transformations et des encodages cruciaux appliqués à notre jeu de données, qui sont indispensables pour comprendre la structure et la performance des modèles présentés ici.

En intégrant à la fois l'optimisation bayésienne, la régularisation, et la standardisation dans notre pipeline de développement de modèles, nous nous sommes assurés que les modèles sélectionnés offrent un équilibre optimal entre la précision des prédictions et la capacité à généraliser à de nouvelles données, réduisant efficacement les risques de surapprentissage.

# Description et sélection des hyperparamètres optimaux post-optimisation bayésienne

L'application de l'optimisation bayésienne a conduit à une convergence vers un ensemble d'hyperparamètres spécifiques pour chaque modèle, représentant le compromis idéal entre performance et complexité. Voici les hyperparamètres finaux choisis pour nos modèles après le processus d'optimisation :

## XGBoost 

Lien vers l'expérience Comet : https://www.comet.com/nhl-project/hp-opt-xgboostclassifier/692478f3adeb4524b4a810f760ca86eb?experiment-tab=panels&showOutliers=true&smoothing=0&xAxis=step

![SCREENSHOT OF Comparaison des types de tirs](best_models/hyperparameters/xgboost_hp_research_space.png)

- **`colsample_bytree`** : 0.728 - Indique la fraction des caractéristiques à utiliser pour construire chaque arbre. Un taux plus élevé permet de considérer plus de caractéristiques, offrant ainsi une diversité plus grande lors de la construction des arbres, mais peut augmenter le risque de surapprentissage.
- **`max_depth`** : 11 - Définit la profondeur maximale de chaque arbre. Une profondeur plus élevée permet au modèle de capturer des relations plus complexes mais augmente le risque de surapprentissage.
- **`max_leaves`** : 0 - Un nombre illimité de feuilles pour chaque arbre, offrant une flexibilité maximale dans la structuration des arbres.
- **`min_child_weight`** : 10 - Spécifie le poids minimum requis des instances dans un enfant (nœud) pour effectuer une nouvelle partition, jouant un rôle crucial dans le contrôle du surapprentissage.
- **`reg_lambda`** : 1 - Terme de régularisation L2 sur les poids, aidant à réduire le surapprentissage en pénalisant les modèles trop complexes.
- **`subsample`** : 0.5 - Détermine la fraction des échantillons à utiliser pour construire chaque arbre, permettant de réduire le surapprentissage en introduisant un peu plus de randomisation dans la construction des arbres.

## Réseau de neurones  

Lien vers l'expérience Comet : https://www.comet.com/veralex1000/hp-opt-mlpclassifier/0d96d4f95eae4c03b56f9569304842a3?experiment-tab=assetStorage

![SCREENSHOT OF Comparaison des types de tirs](best_models/hyperparameters/mlp_classifier_hp_research_space.png)

- **`hidden_layer_sizes`** : [5] - Le processus d'optimisation a exploré diverses configurations de couches cachées et de neurones. Étonnamment, le modèle le plus performant s'est avéré être celui avec une seule couche cachée contenant seulement 5 neurones, ce qui indique que la structure du problème est capturée efficacement avec un modèle plus simple, évitant ainsi la complexité inutile et le surapprentissage potentiel.
- **`activation`** : "relu" - La fonction d'activation 'relu', ou unité linéaire rectifiée, a été choisie pour les neurones du réseau. Cette fonction est populaire car elle permet de modéliser des non-linéarités efficacement sans être affectée par les problèmes de disparition ou d'explosion du gradient, courants avec d'autres fonctions d'activation.
- **`alpha`** : 0 - Spécifie qu'aucune pénalité L2 supplémentaire n'est appliquée pour la régularisation, suggérant que le modèle a atteint un bon équilibre sans nécessiter de régularisation additionnelle.

## Naive Bayes gaussien 

Lien vers l'expérience Comet : https://www.comet.com/nhl-project/hp-opt-gaussiannb/c16293244c564bd8b26dcc09361490b1?experiment-tab=panels&showOutliers=true&smoothing=0&xAxis=wall

![SCREENSHOT OF Comparaison des types de tirs](best_models/hyperparameters/gaussianNB_hp_research_sapce.png)

- **`var_smoothing`** : 1.0001300742532178e-09 - Un paramètre pour lisser la variance des prédictions, améliorant ainsi la stabilité numérique du modèle et aidant à éviter les problèmes liés à la distribution des caractéristiques.
- **`priors`** : [0.7174365135012996, 0.28256348649870044] - Ces probabilités a priori des classes sont ajustées pour refléter la distribution observée dans le jeu de données, assurant ainsi que le modèle prend en compte la fréquence relative des classes de buts et de non-buts lors de la formation de ses prédictions.

## Régression logistique

Lien vers l'expérience Comet : https://www.comet.com/nhl-project/hp-opt-logisticregression/7322f83be0144c268c0bbef02ca991be?experiment-tab=panels&showOutliers=true&smoothing=0&xAxis=wall

![SCREENSHOT OF Comparaison des types de tirs](best_models/hyperparameters/logistic_regr_hp_research_space.png)

- **`C`** : 0.848056038771621 - Cet hyperparamètre contrôle la force de la régularisation inverse dans notre modèle de régression logistique. Un C plus faible signifie une régularisation plus forte, ce qui peut aider à prévenir le surapprentissage en pénalisant les poids plus grands. La valeur optimisée ici suggère un équilibre qui permet au modèle d'être suffisamment flexible pour apprendre des données tout en étant assez contrôlé pour ne pas s'adapter excessivement au bruit.
- **`penalty`** : "elasticnet" - Utilise une combinaison de L1 et L2 pour la régularisation, offrant un équilibre entre la sélection de caractéristiques et la régularisation du modèle.
- **`l1_ratio`** : 0.5 - Le ratio entre la régularisation L1 et L2, indiquant un équilibre égal entre les deux types de pénalité.

# Comparaison des performances à l'aide de certaines métriques

La comparaison des performances des différents modèles est essentielle pour comprendre leur efficacité dans un contexte de classes déséquilibrées. Les métriques suivantes mettent en évidence des aspects clés des performances des modèles en dehors de l'exactitude, qui n'est pas fiable dans des situations de classes imbalancées.

## Balanced Accuracy
La balanced accuracy est une métrique intéressante dans ce contexte car elle tient compte de l'équilibre des classes.

| Modèle                  | Balanced Accuracy |
|-------------------------|-------------------|
| LogisticRegression      | 0.5               |
| GaussianNB              | 0.545             |
| MLPClassifier           | 0.5               |
| **XGBoostClassifier**   | **0.709**         |

Le **XGBoostClassifier** se démarque avec la meilleure balanced accuracy, suggérant qu'il est le plus apte à gérer l'imbalancement des classes.

## F1-Score (Macro)
Le F1-score macro est particulièrement pertinent dans le cas de jeux de données déséquilibrés car il donne la même importance à chaque classe, indépendamment de leur fréquence. 

| Modèle                  | F1-Score (Macro) |
|-------------------------|------------------|
| LogisticRegression      | 0.475            |
| GaussianNB              | 0.558            |
| MLPClassifier           | 0.475            |
| **XGBoostClassifier**   | **0.566**        |

Encore une fois, le **XGBoostClassifier** montre une performance supérieure en termes de F1-score macro.

## Matrice de Confusion
La matrice de confusion est une représentation utile pour voir le nombre de prédictions correctes et incorrectes.

| Modèle                  | TP    | FP    | TN    | FN    |
|-------------------------|-------|-------|-------|-------|
| LogisticRegression      | 0     | 0     | 58957 | 6165  |
| GaussianNB              | 651   | 891   | 58066 | 5514  |
| MLPClassifier           | 0     | 0     | 58957 | 6165  |
| **XGBoostClassifier**   | **4367** | **17126** | **41831** | **1798** |

Le **XGBoostClassifier** présente un nombre significativement plus élevé de vrais positifs (TP) par rapport aux autres modèles, ce qui est crucial pour la prédiction dans un contexte de classes déséquilibrées. Cependant, il est important de noter la présence de 17126 faux positifs. 

En résumé, le **XGBoostClassifier** est le modèle le plus performant selon ces métriques, montrant une meilleure capacité à identifier correctement les classes dans un contexte déséquilibré. Les modèles LogisticRegression et MLPClassifier semblent ne prédire que la classe majoritaire, tandis que le modèle GaussianNB montre une certaine capacité à identifier la classe minoritaire mais a tendance à produire plus de faux positifs (FP).


# Comparaisons graphiques des performances 

## Courbe ROC
![SCREENSHOT OF Comparaison des types de tirs](best_models/performance/2023-10-08-ROC.png)

Le graphique de la courbe ROC que nous examinons reflète des performances solides mais modérées des modèles dans la prédiction des buts. Le modèle XGBoost, avec une AUC de 0.78, se positionne comme le plus performant de notre série, montrant une bonne aptitude à distinguer les résultats positifs des négatifs. Cette performance, bien qu'efficace, indique tout de même des marges d'amélioration possibles.

Le classifieur bayésien naïf gaussien affiche une AUC de 0.74, ce qui est aussi un résultat respectable. Il prouve qu'une approche probabiliste relativement simple peut encore capturer suffisamment la structure sous-jacente des données pour être utile dans des prédictions réalistes.

La régression logistique obtient une AUC de 0.71, ce qui est honorable et met en lumière la pertinence des modèles traditionnels dans des scénarios de classification. Le réseau de neurones multicouches (MLP), malgré sa complexité intrinsèque et une AUC de 0.70, ne surpasse pas significativement les autres modèles. Cette observation peut suggérer que pour la tâche spécifique de prédiction des buts, la sophistication accrue d'un MLP n'apporte pas nécessairement une valeur ajoutée par rapport à des modèles plus simples et linéaires.

Ces résultats collectifs nous rappellent que, même si des modèles plus complexes comme le MLP ont le potentiel de modéliser des interactions non linéaires et complexes, cela ne se traduit pas toujours par une augmentation de la performance prédictive

## Taux de but comme fonction du centile de la probabilité de tir donnée par les modèles
![SCREENSHOT OF Comparaison des types de tirs](best_models/performance/2023-10-08-goal_prop-percentile.png)

Le graphique représentant le taux de buts par percentile de probabilité offre une perspective claire sur la capacité des modèles prédictifs à évaluer la probabilité de buts dans un contexte de hockey. À travers les percentiles, on peut observer comment chaque modèle estime la probabilité d'événements positifs, avec une attention particulière portée aux prédictions les plus confiantes.

La courbe associée au modèle XGBoost indique une tendance encourageante, en particulier aux percentiles les plus élevés, où il semble distinguer avec plus de précision les tirs susceptibles de se transformer en buts. Cette performance suggère que le XGBoost est mieux calibré et offre une interprétation des données plus conforme à la réalité des matchs, le positionnant ainsi comme le meilleur modèle parmi ceux testés.

En revanche, le MLP déçoit quelque peu. Malgré sa complexité et le potentiel qu'il représente en théorie pour capturer des relations non linéaires complexes, sa performance est inférieure non seulement à celle du XGBoost mais également à celle des modèles GaussianNB et logistique. Cela pourrait refléter une inadéquation entre la structure du réseau de neurones et la nature des données ou peut-être une nécessité de réajuster les hyperparamètres ou la structure du réseau.

Les modèles GaussianNB et logistique, quant à eux, affichent des performances assez proches l'une de l'autre, avec une légère avance pour le modèle bayésien naïf. Bien que ne rivalisant pas avec le XGBoost, ils montrent néanmoins une capacité raisonnable à prédire les buts, indiquant que des approches plus traditionnelles et moins complexes conservent leur valeur dans certaines applications de prédiction.

En conclusion, le modèle XGBoost se distingue encore comme le plus performant, surtout dans la zone critique des probabilités élevées, ce qui est crucial pour les prédictions dans les situations de jeu à haut enjeu. La performance inférieure du MLP par rapport aux modèles plus simples rappelle l'importance de l'adéquation entre la complexité du modèle et la spécificité des données. Cette analyse nous guide vers le XGBoost comme étant le meilleur choix pour nos besoins de prédiction actuels, offrant une combinaison optimale de précision et de fiabilité.

## Proportion cumulée de buts comme fonction du centile de la probabilité de tir donnée par les modèles
![SCREENSHOT OF Comparaison des types de tirs](best_models/performance/2023-10-08-cummulative_prop-percentile.png)

Le modèle XGBoost maintient sa suprématie, offrant la meilleure estimation de la probabilité de buts sur l'ensemble des percentiles. Sa courbe, qui se trouve plus haut que les autres, démontre une capacité supérieure à cumuler les vrais positifs, en particulier dans les tranches de haute probabilité, ce qui est essentiel pour des prédictions fiables et précises.

Une observation intéressante est l'intersection des courbes de la régression logistique et du MLP. Jusqu'au 60e percentile, la régression logistique semble mieux performer, capturant une plus grande proportion de buts. Cependant, au-delà de ce point, le MLP commence à prendre l'avantage, indiquant qu'il pourrait être plus apte à identifier les tirs à haute probabilité de se convertir en buts dans la portion supérieure de la distribution.

Le modèle naïf bayésien gaussien se détache nettement de la régression logistique et se place confortablement en deuxième position derrière le XGBoost. Sa courbe montre une cohérence dans la capture des buts à travers les percentiles, indiquant une bonne calibration globale et une capacité fiable à estimer les probabilités de manière plus constante sur toute la gamme des prédictions.

## Diagramme de fiabilité des modèles
![SCREENSHOT OF Comparaison des types de tirs](best_models/performance/2023-10-08-calibration.png)

Le graphique de calibration examine la relation entre les probabilités prédites et les fréquences observées des résultats positifs (buts). Un modèle parfaitement calibré se situerait sur la ligne en pointillés, où la probabilité prédite correspond exactement à la fraction de positifs observée.

À l'analyse de ce graphique, on constate que les modèles MLP et logistique semblent sous-performer significativement, avec des moyennes de probabilités prédites presque égale à 0 pour l'ensemble des prédiction, indiquant une tendance à ne pas identifier correctement les instances positives. Cette sous-estimation systématique des probabilités suggère un fort biais dans le modèle.

Le modèle naïf bayésien gaussien présente un comportement atypique, tendant à surestimer les probabilités pour les probabilités prédites supérieures à 0.4. Cette surestimation suggère que le modèle a une confiance excessive dans ses prédictions, ce qui pourrait conduire à un nombre élevé de faux positifs dans la pratique.

Quant au modèle XGBoost, bien qu'il ne soit pas parfaitement calibré, il affiche une performance relativement meilleure que les autres modèles. Il surestime aussi les probabilités, mais dans une moindre mesure, ce qui suggère qu'il est plus proche d'une calibration idéale et qu'il est le plus fiable des modèles considérés pour estimer la probabilité des buts.
