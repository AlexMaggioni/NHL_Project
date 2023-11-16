---
layout: post
author: Équipe A07
title: Sélection des caractéristiques
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

# Sélections des caractéristiques

Dans le processus d'optimisation des modèles prédictifs, l'ingénierie des caractéristiques joue un rôle crucial. Après avoir méticuleusement traité les données au travers de l'ingénierie des caractéristiques I et II, nous avons entrepris une étape essentielle : la sélection des caractéristiques les plus pertinentes. Cette démarche vise à épurer notre modèle de données superflues, améliorant ainsi sa robustesse et sa simplicité, tout en conservant les informations les plus significatives.

Notre choix s'est porté sur une méthode de filtrage pour cette sélection. Son principal avantage est qu'elle est indépendante du modèle, ce qui s'avère particulièrement adapté à notre contexte où divers modèles sont en compétition. En effet, cette indépendance permet une évaluation objective des caractéristiques sans préjugés liés à un algorithme spécifique.

Il est crucial de souligner que notre sélection a été effectuée sur des caractéristiques déjà transformées et encodées. Les détails de ces transformations et encodages ont été préalablement exposés dans notre article dédié à ce sujet, fournissant ainsi une base solide pour la compréhension des caractéristiques finales sélectionnées.

Pour que la sélection soit efficace, il était impératif qu'elle tienne compte de la redondance des données. Les caractéristiques redondantes peuvent en effet brouiller le modèle et réduire sa performance. Nous avons également recherché une méthode qui soit simple d'utilisation pour faciliter son intégration dans notre chaîne de traitement des données. C'est pourquoi nous avons opté pour une méthode de sélection basée sur l'utilisation des arbres, reconnue pour sa capacité à évaluer l'importance des caractéristiques de manière intuitive. Pour ceci, nous avons utilisé le module `sklearn.tree` et `sklearn.ensemble`.

Voici les caractéristiques sélectionnées:
- `distanceToGoal`
- `angleToGoal`
- `shooterId`
- `goalieId`
- `coordinateX`
- `coordinateY`
- `lastCoordinateX`
- `lastCoordinateY`
- `timeElapsed`
- `distanceFromLastEvent`
- `speed`
- `periodTimeSeconds`
- `byTeam`
- `period`
- `gameDate`
- `emptyNet`

Et voici un graphique présentant les importances relatives dans la prédictions pour chacune des variable dans le modèle XGBoost avancé développé, donnant ainsi une idée de l'importance relative de chacune des variables : 

![SCREENSHOT OF Comparaison des types de tirs](feature_selection/2023-10-08-shap-summary_plot-1-99.png)

Le graphique illustre l'importance des caractéristiques, mesurées par la moyenne des valeurs absolues SHAP. Deux constatations notables émergent :

- `distanceToGoal` est la caractéristique la plus impactante, indiquant que la distance à laquelle un tir est effectué par rapport au but est un déterminant majeur du résultat prédit par le modèle.

- `shooterId` suit en importance, soulignant que l'identité du tireur, qui peut encapsuler des facteurs comme la performance historique ou la compétence relative d'un joueur, est un facteur significatif dans les prédictions du modèle.

Ces deux caractéristiques se détachent nettement des autres, suggérant qu'elles sont cruciales pour comprendre et prédire les issues des événements modélisés.
