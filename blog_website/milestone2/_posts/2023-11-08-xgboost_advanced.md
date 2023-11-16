---
layout: post
author: Équipe A07
title: XGBoost avancés
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

Dans ce rapport, nous nous concentrons sur l'élaboration et la comparaison de deux modèles avancés XGBoost, une approche de pointe en matière de machine learning. Le premier modèle englobe l'ensemble des caractéristiques développées, y compris celles issues de la section sur l'ingénierie des caractéristiques II. Le second modèle se base exclusivement sur les caractéristiques sélectionnées dans l'article sur la sélection des caractéristiques. Ces deux modèles sont conçus pour surpasser les performances des modèles de base XGBoost établis précédemment. 

Par ailleurs, nous avions initialement l'intention de mener une exploration des modèles XGBoost dans le cadre de la question 6 sur l'exploration des modèles. Nous avons donc saisi cette opportunité pour entraîner un modèle utilisant l'ensemble des caractéristiques, qui sera réutilisé ultérieurement lors de la section 6.

# XGBoost sur l'ensemble des caractéristiques

Dans notre approche, nous avons combiné deux stratégies principales : l'optimisation bayésienne des hyperparamètres et l'ajustement du poids des classes. Ces méthodes ont été appliquées aux deux modèles XGBoost développés pour améliorer leurs performances.

L'optimisation bayésienne des hyperparamètres est une méthode statistique qui vise à trouver la combinaison optimale d'hyperparamètres pour un modèle. Elle utilise un modèle probabiliste pour prédire la performance d'un modèle avec différents hyperparamètres et sélectionne ceux qui maximisent cette performance. Cette approche est particulièrement efficace pour gérer les grands espaces de paramètres et trouver le meilleur équilibre entre exploration et exploitation.

Dans le cadre de notre projet, nous avons ciblé spécifiquement les hyperparamètres suivants pour l'optimisation :

- **`min_child_weight`** : Ce paramètre, de type entier et variant entre 0 et 10, joue un rôle crucial dans la prévention du surapprentissage. Il détermine le nombre minimum de poids requis dans un enfant, c'est-à-dire dans un nœud résultant d'une division dans l'arbre de décision. Des valeurs plus élevées rendent le modèle plus conservateur en évitant des divisions trop spécifiques qui pourraient mener à un modèle trop complexe pour les données.

- **`colsample_bytree`** : De type flottant et commençant à 0.5, ce paramètre spécifie la proportion de caractéristiques à utiliser pour construire chaque arbre. Une valeur inférieure signifie qu'un plus petit nombre de caractéristiques est sélectionné, ce qui peut aider à réduire le surapprentissage en limitant la complexité de chaque arbre individuel.

- **`max_depth`** : Il s'agit d'un paramètre entier dont les valeurs varient de 3 à 18. Ce paramètre détermine la profondeur maximale de chaque arbre. Une valeur plus élevée permet au modèle de mieux saisir les relations complexes dans les données, mais augmente également le risque de surapprentissage. Trouver le bon équilibre avec ce paramètre est essentiel pour obtenir un modèle précis et généralisable.

- **`max_leaves`** : Avec une gamme allant de 0 à 10, ce paramètre entier détermine le nombre maximal de feuilles, ou nœuds terminaux, dans chaque arbre. Contrôler ce nombre aide à réguler la complexité de chaque arbre, influençant directement la complexité globale du modèle.

Voici un graphique présentant les hyperparamètres et leurs performances associées:
![SCREENSHOT OF Comparaison des types de tirs](xgboost_advanced/2023-10-08-val_roc_auc_score.jpeg)

Les meilleures hyperparamètres que nous avons obtenus sont les suivants :
- colsample_bytree : 0.728.
- learning_rate : 0.01. 
- max_depth : 11. 
- max_leaves : 0 (ici cela veut dire un nombre iliimité de feuilles).
- min_child_weight : 10. 
- reg_lambda : 1. 
- subsample : 0.5.

Lien vers l'expérience : (https://www.comet.com/nhl-project/hp-opt-xgboostclassifier/681d72f44e2f406abdf00973e21e906a?experiment-tab=params)

# XGBoost sur les caractéristiques sélectionnées

Nous avons aussi élaboré un modèle XGBoost sur les caractéristiques sélectionnées dans l'article à ce sujet. 

Les meilleures hyperparamètres que nous avons obtenus sont les suivants :
- colsample_bytree : 0.671.
- learning_rate : 0.01. 
- max_depth : 8. 
- max_leaves : 0 (ici cela veut dire un nombre iliimité de feuilles).
- min_child_weight : 10. 
- reg_lambda : 1. 

Lien vers l'expérience : (https://www.comet.com/nhl-project/hp-opt-xgboostclassifier/692478f3adeb4524b4a810f760ca86eb?experiment-tab=params)

# Comparaisons des modèles 

Nous allons maintenant comparé les performances de ces deux modèles aux baselines établies précédement :

## Courbe ROC
![SCREENSHOT OF Comparaison des types de tirs](xgboost_advanced/2023-10-08-ROC.png)

Dans l'analyse comparative des modèles XGBoost présentée dans la courbe ROC, il est particulièrement encourageant de constater que les modèles exploitant la totalité des caractéristiques ainsi que ceux se basant sur un ensemble de caractéristiques sélectionnées surpassent nettement les baselines établies. Cette observation est une preuve tangible de l'efficacité de nos méthodes d'apprentissage automatique.

Le modèle incorporant l'ensemble des caractéristiques se distingue légèrement avec un AUC de 0.78, dépassant de peu celui qui se repose sur les caractéristiques sélectionnées, lequel affiche un AUC de 0.77. Cette différence minime est significative car elle valide l'efficience de notre processus de sélection des caractéristiques. Il ressort de cette analyse que nous avons réussi à concilier un haut niveau de performance avec un modèle plus épuré, presque aussi performant que le modèle intégrant la totalité des données.

Dans un scénario où nous serions confrontés à un volume de données massif ou à des exigences de temps d'inférence réduit, le choix se porterait indubitablement sur le modèle avec caractéristiques sélectionnées en raison de sa simplicité et de sa rapidité. Toutefois, étant donné l'envergure modérée de notre projet actuel et notre aspiration à atteindre la performance optimale, il semble judicieux de privilégier le modèle qui utilise l'ensemble des caractéristiques disponibles.

## Taux de but comme fonction du centile de la probabilité de tir donnée par les modèles
![SCREENSHOT OF Comparaison des types de tirs](xgboost_advanced/2023-10-08-goal_prop-percentile.png)

Le graphique met en lumière les performances relatives de plusieurs modèles XGBoost par rapport à la prédiction de buts, en fonction des probabilités estimées. Il est évident que même les meilleurs modèles, 'XGBoost_best_all_features' et 'XGBoost_feat_select', bien qu'ils surpassent les autres variantes et les baselines aléatoires, sont loin d'être parfaits. Ils montrent cependant une tendance encourageante dans les centiles supérieurs, où les prédictions sont plus souvent correctes pour des probabilités de but élevées. Cela dit, la performance globale indique qu'il reste une marge d'amélioration, en particulier dans la calibration des probabilités sur l'ensemble du spectre de prédictions.

Il est important de noter que ces modèles, même avec des AUC respectables, ne parviennent pas à atteindre un taux de prédiction de buts uniformément élevé. Les résultats mettent en évidence la complexité inhérente à la tâche de prédiction dans ce domaine, soulignant qu'il y a encore des facteurs non capturés par les modèles actuels qui pourraient améliorer la précision des prédictions.

Les autres modèles, incluant ceux basés uniquement sur l'angle, la distance, ou leur combinaison, présentent des taux de buts inférieurs dans les probabilités élevées, suggérant que l'inclusion de l'ensemble complet des caractéristiques ou d'un ensemble soigneusement sélectionné est préférable pour des prédictions précises. Les classificateurs aléatoires, comme attendu, maintiennent un taux de buts constant et faible à travers tous les centiles, confirmant qu'ils ne possèdent aucune capacité discriminative.

## Proportion cumulée de buts comme fonction du centile de la probabilité de tir donnée par les modèles
![SCREENSHOT OF Comparaison des types de tirs](xgboost_advanced/2023-10-08-cummulative_prop-percentile.png)

Le graphique de la proportion cumulée de buts par centile de probabilité illustre un aspect crucial de la performance d'un modèle prédictif : sa capacité à concentrer les prédictions les plus confiantes—celles avec la plus haute probabilité—sur les cas réellement positifs. Idéalement, on voudrait voir une pente abrupte pour chaque modèle dans les premiers percentiles, ce qui indiquerait que le modèle identifie correctement et rapidement une grande partie des cas positifs réels. Une telle pente témoignerait d'un modèle à la fois confiant et précis, capable de distinguer efficacement entre les résultats positifs et négatifs.

Dans le graphique présenté, le modèle 'XGBoost_best_all_features' montre une courbe qui s'approche de cet idéal, avec une montée relativement rapide dans les percentiles les plus élevés, bien qu'elle ne soit pas aussi abrupte que ce que l'on pourrait espérer d'un modèle parfait. Ceci indique que, tandis que le modèle est compétent pour identifier les cas de buts, il y a une opportunité d'amélioration pour augmenter sa confiance et sa précision, particulièrement dans le haut de la distribution de probabilité.

Le modèle 'XGBoost_feat_select' démontre également une capacité similaire à capturer les cas positifs, mais avec une pente légèrement moins raide, suggérant que la sélection des caractéristiques a peut-être écarté certaines informations qui auraient pu rendre le modèle plus assertif dans les tranches de haute probabilité.

Les autres modèles montrent des pentes plus graduelles, particulièrement le 'XGBoost_baseline_angle' et le 'XGBoost_distance', ce qui souligne une confiance moindre dans leurs prédictions et une capacité réduite à regrouper les cas positifs parmi les probabilités les plus élevées.

Les classificateurs aléatoires, quant à eux, ont des courbes qui montent linéairement, reflétant l'absence de discrimination prédictive et confirmant leur inadéquation pour la tâche.

En résumé, bien que 'XGBoost_best_all_features' et 'XGBoost_feat_select' ne présentent pas une pente aussi abrupte que l'idéal théorique, ils restent des modèles robustes comparés aux autres variantes et nettement plus performants que le hasard. Il reste cependant un espace significatif pour améliorer leur capacité à prédire avec confiance et précision, particulièrement pour les prédictions avec une haute probabilité de but.

## Diagramme de fiabilité des modèles
![SCREENSHOT OF Comparaison des types de tirs](xgboost_advanced/2023-10-08-calibration.png)

Ce graphique de calibration illustre la relation entre les probabilités prédites de buts par les modèles et les fréquences réelles observées. Un modèle parfaitement calibré devrait se situer sur la ligne pointillée, où la probabilité prédite et la fraction de positifs sont égales.

Le modèle 'XGBoost_best_all_features' montre une tendance à surestimer la probabilité de buts, particulièrement dans la moitié supérieure de la plage de probabilité. Cela est indiqué par la courbe qui se situe en-dessous de la ligne de calibration parfaite. Malgré cette surestimation, il couvre de manière plus complète l'étendue des probabilités, se démarquant nettement du classifieur aléatoire et indiquant une amélioration substantielle par rapport à la baseline.

En ce qui concerne le modèle 'XGBoost_feat_select', la courbe suggère une sous-estimation des probabilités, en particulier dans le segment de probabilité supérieur. Cela pourrait signifier que bien que le modèle soit prudent dans ses prédictions, il pourrait ne pas reconnaître suffisamment certains tirs ayant une forte chance de devenir des buts. Cependant, cette tendance à la prudence pourrait être avantageuse dans certains contextes où il est préférable d'éviter des faux positifs.

Il est important de noter que tous les modèles sont comparés à un classifieur aléatoire et une baseline aléatoire, qui montrent une absence de corrélation entre les probabilités prédites et les résultats observés, comme en témoigne leur ligne plate proche de zéro.

En résumé, tandis que le modèle 'XGBoost_best_all_features' montre une surestimation et le modèle 'XGBoost_feat_select' une sous-estimation, les deux offrent une performance significativement meilleure que les baselines.