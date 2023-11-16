---
layout: post
author: Équipe A07
title: Évaluation des performances sur l'ensemble de test
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

# Évaluation des Performances des Modèles de Prédiction

Cet article se concentre sur l'évaluation des performances des modèles prédictifs que nous avons développés précédemment. Suite à l'article sur l'approfondissement de XGBoost, nous avons intégré l'ensemble des caractéristiques disponibles pour construire un modèle XGBoost performant. Cette approche s'est avérée fructueuse, notre modèle XGBoost étant également le plus performant dans la Partie 6 de notre étude. Cependant, pour une analyse complète, nous inclurons également le classifieur bayésien naïf gaussien, qui avait précédemment obtenu de bons résultats.

Nous testerons nos modèles non seulement sur les données de la saison régulière 2020/21 mais aussi sur les matchs des séries éliminatoires de la même année. Pour cela, nous utiliserons quatre types de graphiques : la courbe ROC/AUC, le taux de buts par rapport au centile de probabilité, la proportion cumulée de buts par rapport au centile de probabilité, et la courbe de fiabilité. Ces graphiques nous aideront à comparer les performances des modèles sur les ensembles de test par rapport à l'ensemble de validation.

Nous explorerons si les modèles conservent leur performance lorsqu'ils sont appliqués à l'ensemble de test et comment ils se comportent sur les données des séries éliminatoires. L'objectif est de comprendre la fiabilité et la flexibilité de nos modèles face à différents types de données et de situations de jeu.

# Performance sur la saison régulière 2020 

## Courbe ROC
![SCREENSHOT OF Comparaison des types de tirs](test_eval/regular_season/2023-10-08-ROC_curves_None.png)

Sur la base de l'analyse des courbes ROC pour la saison régulière 2020, il est remarquable de constater que les modèles testés non seulement généralisent bien à l'ensemble de données inédit mais, de manière surprenante, affichent même une légère amélioration de performance par rapport à l'ensemble d'entraînement. Cette observation suggère que les modèles ont été bien entraînés et possèdent une capacité robuste de généralisation, un indicateur positif de leur aptitude à être appliqués à de réelles situations de jeu.

Le modèle XGBoostClassifier, en particulier, montre une excellente performance avec une AUC de 0.79, le plaçant en tête des modèles évalués. Il est suivi par le GaussianNB qui, avec une AUC de 0.75, se révèle également être un modèle fiable pour la prédiction des buts. Ces résultats sont encourageants et indiquent que les approches utilisées pour développer ces modèles sont bien fondées et potentiellement très utiles pour des applications de prédiction dans le domaine sportif.

## Taux de but comme fonction du centile de la probabilité de tir donnée par les modèles
![SCREENSHOT OF Comparaison des types de tirs](test_eval/regular_season/2023-10-08-ratio_goal_percentile_curves_None.png)

À partir du graphique fourni, nous pouvons observer que le modèle XGBoostClassifier continue de montrer une robustesse remarquable, avec des performances très similaires aux graphiques générés à partir des données d'entraînement. Cela indique que le modèle n'est pas surajusté et qu'il généralise bien à de nouvelles données. Le modèle GaussianNB, bien qu'un peu moins performant que le XGBoost, suit une tendance similaire et confirme également sa robustesse.

Le fait que les performances observées sur l'ensemble de données de la saison régulière 2020 soient très proches de celles obtenues avec l'ensemble d'entraînement est une indication positive que les modèles ont appris les tendances générales plutôt que les particularités spécifiques aux données d'entraînement. Cette généralisation est essentielle pour la création de modèles prédictifs fiables dans un environnement dynamique et imprévisible comme les matchs de hockey.

## Proportion cumulée de buts comme fonction du centile de la probabilité de tir donnée par les modèles
![SCREENSHOT OF Comparaison des types de tirs](test_eval/regular_season/2023-10-08-proportion_goal_percentile_curves_None.png)

Encore une fois, je réitère la même observation. Les modèles entraînés ont été capables de très bien généraliser sur les données de la saison régulière 2020, ce qui est un signe de robustesse. Je vous invite à observer par vous-même la similitude entre ce graphique et ceux des articles précédents.

## Diagramme de fiabilité des modèles
![SCREENSHOT OF Comparaison des types de tirs](test_eval/regular_season/2023-10-08-calibration_curves_None.png)

Ici, bien que très similaire, on peut observer une légère différence dans le modèle naïf gaussien. Il semble se rapprocher, bien que très modestement, de la droite de calibration. Encore une fois, la tendance se maintient et les modèles restent robustes.

# Performance sur les séries éliminatoires de 2020

Nous venons de constater que les performances des modèles sont très robustes et qu'ils généralisent bien sur la saison régulière. Cependant, est-ce toujours le cas lors des séries éliminatoires ? Existe-t-il des différences significatives entre la saison régulière et les séries éliminatoires qui pourraient influencer nos résultats ? C'est ce que nous allons découvrir.

## Courbe ROC
![SCREENSHOT OF Comparaison des types de tirs](test_eval/playoffs/2023-10-08-ROC_curves_None.png)

Ici, on observe à nouveau la même tendance générale, mais il semble y avoir beaucoup plus de bruit dans les courbes. Cela est probablement dû à la petite quantité d'exemples disponibles pour les séries éliminatoires, soit 4847. De plus, il est intéressant de noter une baisse de la performance globale à travers les modèles. En effet, entre la saison régulière et les séries éliminatoires de 2020, le modèle XGBoost passe de 0,79 à 0,77 et le classifieur naïf gaussien de 0,75 à 0,73.

## Taux de but comme fonction du centile de la probabilité de tir donnée par les modèles
![SCREENSHOT OF Comparaison des types de tirs](test_eval/playoffs/2023-10-08-ratio_goal_percentile_curves_None.png)

Encore une fois, la même tendance générale se manifeste, mais avec des performances légèrement moins bonnes par rapport au jeu de test de la saison régulière. En effet, les modèles XGBoost et gaussien distinguent beaucoup mieux les buts pour les percentiles élevés de probabilité sur la saison régulière. Ici, le taux de but associé au percentile le plus élevé est juste en dessous de 40 %, alors qu'il était près de 45 % sur la saison régulière. Les pentes des modèles semblent globalement moins prononcées, indiquant ainsi que les modèles ont plus de difficulté à bien discerner les buts des non-buts.

## Proportion cumulée de buts comme fonction du centile de la probabilité de tir donnée par les modèles
![SCREENSHOT OF Comparaison des types de tirs](test_eval/playoffs/2023-10-08-proportion_goal_percentile_curves_None.png)

Les mêmes observations s'appliquent ici, la tendance générale se poursuit, mais avec des performances moindres que sur les données de la saison régulière.

## Diagramme de fiabilité des modèles
![SCREENSHOT OF Comparaison des types de tirs](test_eval/playoffs/2023-10-08-calibration_curves_None.png)

Ici, le graphique est très différent ! Heureusement, le modèle XGBoost maintient toujours la même tendance, preuve de sa robustesse. Cependant, le classifieur naïf gaussien semble avoir chuté en termes de qualité d'alignement. En effet, la fraction de valeurs positives par tranche est presque à zéro pour toutes les tranches de probabilité prédite moyenne. Ainsi, les prédictions de tous les modèles sont peu fiables, à l'exception du XGBoost (qui est loin d'être parfait). 

# Conclusion

En conclusion, les performances de notre modèle XGBoost sont relativement bonnes, mais dans l'ensemble, il a été difficile de créer un modèle très performant pour prédire les buts dans le hockey sur glace. Malgré les efforts déployés, il est possible que des améliorations supplémentaires puissent être obtenues en utilisant de l'ingénierie de caractéristiques supplémentaires ou en explorant des modèles à plus grande capacité, tout en affinant les hyperparamètres et l'architecture du modèle. L'analyse des performances sur la saison régulière et les séries éliminatoires a révélé que le modèle XGBoost est robuste, mais il existe toujours des défis à relever pour améliorer la précision des prédictions.