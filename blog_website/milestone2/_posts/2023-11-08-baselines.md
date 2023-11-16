---
layout: post
author: Équipe A07
title: Baselines logistique et XGBoost
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

Dans l'article précédent, la génération de caractéristiques de distance et d'angle a été abordée. Nous allons maintenant explorés l'utilisation des caractéristiques de distance et d'angle de tir dans le cadre de la prédiction de résultats binaires. Nous allons tester trois types de baselines pour chaque modèle : régression logistique et XGBoost. Pour la régression logistique, nous considérons un modèle basé uniquement sur la distance, un autre uniquement sur l'angle de tir, et un troisième combinant les deux. La même approche est adoptée pour les modèles XGBoost. En plus de ces modèles, nous incluons un classifieur aléatoire comme point de comparaison pour évaluer la pertinence de nos modèles.

Cette méthode permet une évaluation initiale des performances potentielles de ces caractéristiques. L'application de ces modèles simples est cruciale pour établir une référence avant de passer à des analyses plus avancées et détaillées.


# L'exactitude, une bonne mesure de performance? 

Nous avons mis en place une régression logistique, normalisant les coordonnées pour les aligner dans une direction de jeu commune. Nous nous sommes concentrés sur la distance du tir comme caractéristique principale pour l'un des modèles. Durant la phase d'entraînement, le jeu de données a été divisé en un ensemble d'entraînement et un ensemble de validation.

Nous avons obtenu une exactitude de 90% avec la régression logistique. Cependant, en examinant de plus près les prédictions du modèle, nous avons remarqué qu'il prédit systématiquement 0 pour chaque exemple de l'ensemble de validation. Cette observation indique que, malgré une exactitude apparente élevée, le modèle pourrait avoir un biais significatif, ignorant potentiellement la classe minoritaire (les tirs aboutissant à un but).

Ce constat souligne l'importance de ne pas se fier uniquement à l'exactitude comme mesure de performance dans des scénarios avec des classes déséquilibrées. En effet, dans notre cas, une faible proportion des tirs aboutit à un but, rendant la précision une mesure peu fiable. Pour illustrer, prenons un modèle hypothétique conçu pour détecter une maladie rare présente chez seulement 0,5% de la population. Un tel modèle, optimisé pour maximiser l'exactitude, pourrait simplement prédire l'absence de maladie pour chaque cas, atteignant ainsi une exactitude de 99,5%, mais manquant complètement son objectif.

Pour une évaluation appropriée de notre modèle dans un contexte de classes déséquilibrées, il est crucial de se concentrer sur des métriques telles que la précision, le rappel, le score F1, et l'AUC. Ces mesures fournissent une perspective plus complète sur la performance du modèle, allant au-delà de la simple exactitude. De plus, l'analyse de la courbe ROC est bénéfique pour comprendre le compromis entre les taux de vrais positifs et de faux positifs. Une telle analyse globale est indispensable pour une évaluation précise et équilibrée de la performance du modèle. Dans la section suivante, nous explorerons en détail ces aspects à travers divers graphiques et mesures.

# Visualisations des performances pour les baselines de régréssion logistique

Nous avons testé trois modèles de base différents : un modèle de régression logistique utilisant uniquement la distance, un autre se basant exclusivement sur l'angle de tir, et un dernier combinant à la fois la distance et l'angle de tir. Pour contextualiser ces performances, un classifieur aléatoire a également été utilisé comme point de comparaison.

Les détails de ces modèles, ainsi que les graphiques associés, sont disponibles dans les artéfacts de cette expérience sur Comet, accessible via le lien suivant : https://www.comet.com/nhl-project/logisticregression-single-training/view/new/panels.

Vous trouverez les différents modèles sous l'onglet 'models' et les graphiques sous l'onglet 'images'. Pour une compréhension approfondie de la manière dont nos expériences ont été documentées sur Comet, veuillez consulter l'article correspondant.

Ci-après sont présentés les graphiques relatifs à ces expériences :

## Courbe ROC
![SCREENSHOT OF Comparaison des types de tirs](logistic_baseline/2023-10-08-Logistic_ROC_Curves_Val.png)

Le graphique présente trois courbes représentatives de trois modèles distincts, ainsi qu'un classifieur aléatoire. La courbe du modèle qui ne prend en compte que l'angle de tir affiche un AUC de 0.5, révélant une performance équivalente à celle d'une sélection aléatoire. Cela indique que, pris isolément, l'angle de tir ne fournit aucune information significative pour prédire l'issue d'un tir.

Par contraste, les modèles qui intègrent la distance comme variable prédictive, que ce soit de manière isolée ou conjointement avec l'angle de tir, affichent tous les deux un AUC de 0.69. Cette valeur dépasse nettement le seuil de l'aléatoire et suggère que la distance du tir constitue un indicateur fiable de la probabilité de marquer. L'absence d'amélioration de l'AUC avec l'ajout de l'angle de tir implique que cette caractéristique n'apporte aucune amélioration significative au modèle qui inclut déjà la distance.

Il est essentiel de remarquer que les courbes pour les modèles basés uniquement sur la distance et ceux combinant distance et angle sont superposées, rendant la courbe bleue invisible sur le graphique car elle est masquée par l'autre. Ce détail souligne que l'angle de tir, lorsqu'il est combiné à la distance, ne renforce pas la capacité prédictive du modèle.

## Taux de but comme fonction du centile de la probabilité de tir donnée par les modèles
![SCREENSHOT OF Comparaison des types de tirs](logistic_baseline/2023-10-08-Logistic_Ratio_Goal_Percentile_Curves_Val.png)

Le graphique illustre le taux de buts en fonction des percentiles de probabilité prédits par différents modèles de classification. Sur l'axe horizontal, nous trouvons les percentiles de probabilité, décroissants du 100ème percentile à gauche vers le 0ème percentile à droite. L'axe vertical montre le pourcentage de tirs qui se sont concrétisés par un but pour chaque percentile de probabilité.

Les courbes bleue, orange et verte représentent les modèles qui exploitent respectivement uniquement la distance, uniquement l'angle et une combinaison des deux. La courbe en pointillés rouge symbolise un classifieur aléatoire.

Les modèles qui prennent en compte la distance se distinguent, leurs courbes suggérant une relation plus linéaire entre les percentiles de probabilité élevés et les taux de buts réels. Un modèle précis devrait en effet montrer une corrélation directe entre une haute probabilité prédite de marquer et un taux de buts observé supérieur. Bien que non parfaits, ces modèles surpassent nettement celui basé exclusivement sur l'angle.

Le modèle vert, qui combine distance et angle, n'offre aucune amélioration notable par rapport au modèle bleu, qui se concentre uniquement sur la distance. Cette observation s'aligne avec les résultats de la courbe ROC, où l'inclusion de l'angle n'a pas augmenté l'AUC.

Quant au modèle orange, se basant uniquement sur l'angle, il se rapproche des performances du classifieur aléatoire rouge, renforçant l'idée que l'angle seul est un prédicteur inefficace pour la réalisation de buts.

Ce graphique s'avère également utile pour déterminer les seuils de probabilité où le modèle excelle ou échoue. Cette information peut s'avérer cruciale pour affiner le modèle ou pour élaborer des stratégies décisionnelles s'appuyant sur les probabilités prédites.


## Proportion cumulée de buts comme fonction du centile de la probabilité de tir donnée par les modèles
![SCREENSHOT OF Comparaison des types de tirs](logistic_baseline/2023-10-08-Logistic_Proportion_Goal_Percentile_Curves_Val.png)

Le graphique dépeint la proportion cumulée de buts en fonction des percentiles de probabilité prédits par différents modèles de classification. Chaque point sur les courbes correspond à la proportion cumulée de buts pour les tirs avec une probabilité de marquer supérieure ou égale à celle indiquée par le percentile correspondant. L'axe horizontal expose les percentiles de probabilité des modèles, s'étendant de la probabilité la plus élevée (100ème percentile) à gauche vers la probabilité la plus basse (0ème percentile) à droite. L'axe vertical, quant à lui, représente la proportion cumulée de buts.

Dans l'idéal, pour un modèle parfait, la courbe serait extrêmement pentue au début, indiquant que tous les buts sont prédits avec des probabilités élevées, puis elle deviendrait plate, témoignant qu'aucun tir avec une faible probabilité n'est marqué. Ainsi, la performance d'un modèle est meilleure lorsque sa courbe est abrupte au départ et s'aplanit en se rapprochant du 0ème percentile.

Les modèles qui intègrent la distance présentent des courbes qui s'élèvent plus rapidement que celles des autres modèles, suggérant qu'ils accumulent une plus grande proportion de buts dans les percentiles élevés. Cela indique que ces modèles prédisent plus efficacement les tirs qui seront convertis en buts.

Les courbes orange et verte, représentant respectivement le modèle basé uniquement sur l'angle et le modèle combinant la distance et l'angle, sont presque superposées. Cette observation suggère que l'inclusion de l'angle de tir ne confère pas d'avantage significatif pour capturer les buts réels dans les tranches de probabilité les plus élevées.

Enfin, la courbe rouge du classifieur aléatoire illustre une progression linéaire, comme prévu, puisqu'il attribue des probabilités de manière aléatoire, sans considération pour les données. 


## Courbe de calibration des modèles
![SCREENSHOT OF Comparaison des types de tirs](logistic_baseline/2023-10-08-Logistic_Calibration_Curves.png)

Le diagramme de fiabilité affiché indique que les probabilités moyennes prédites par les modèles n'excèdent pas 0.2, suggérant une incapacité des modèles à prédire avec confiance l'occurrence de buts. En effet, dans un contexte idéal, les prédictions des modèles devraient couvrir une gamme plus large de probabilités si des distinctions claires entre les classes positives (buts) et négatives (non-buts) étaient identifiées.

Le modèle basé uniquement sur la distance montre une légère augmentation des points bleus au début de la courbe, mais ces derniers ne s'élèvent pas au-dessus de la probabilité de 0.2. Cela peut indiquer que bien que le modèle soit calibré de manière acceptable dans cette gamme de probabilités, il demeure globalement très incertain quant à l'issue des tirs, limitant ainsi son utilité dans des situations où une prédiction plus affirmée est requise.

Le modèle basé uniquement sur l'angle est absent du graphique, ce qui suggère que les probabilités prédites par ce modèle sont uniformément basses ou qu'elles ne varient pas significativement à travers les différentes tranches, donnant ainsi une prédiction moyenne constante. Cela révèle un manque considérable de pouvoir prédictif de l'angle lorsqu'il est utilisé par un modèle linéaire. La constance des prédictions moyennes par tranche, indépendamment des exemples de validation, renforce cette notion. Il serait intéressant d'essayer un modèle avec une capacité plus élevée, qui pourraient potentiellement extraire et utiliser des interactions non linéaires ou des caractéristiques cachées que les modèles linéaires ne parviennent pas à capturer.

Le classifieur aléatoire (courbe rouge) reste aligné le long de la base, comme attendu pour un modèle qui ne possède aucune capacité discriminative.

En conclusion, ce diagramme de fiabilité démontre que la distance peut offrir une certaine mesure de calibration dans un modèle linéaire, bien que limitée. Cependant, l'angle seul ne semble pas fournir d'informations prédictives valables. 

# Visualisations des performances pour les baselines XGBoost

Nous allons désormais évaluer la puissance prédictive des caractéristiques de distance et d'angle de tir à l'aide de modèles XGBoost, reconnus pour leur efficacité dans la gestion des interactions complexes entre les variables. Les modèles XGBoost ont été configurés pour optimiser à la fois la précision et la calibration des probabilités prédites.

Comme pour les modèles précédents, les détails complets des baselines XGBoost, ainsi que les graphiques pertinents, sont consignés et accessibles via les artéfacts de cette expérience sur Comet. Vous pouvez les consulter en suivant le lien fourni : [https://www.comet.com/nhl-project/train-xgboostclassifier-baseline/view/new/panels].

Dans les sections suivantes, nous présenterons une série de visualisations, incluant des courbes ROC, des diagrammes de calibration, et des graphiques de taux de buts par percentile de probabilité. 

## Courbe ROC
![SCREENSHOT OF Comparaison des types de tirs](xgboost_baseline/2023-10-08-XGB_ROC_Curves_Val.png)


La courbe ROC pour les modèles XGBoost révèle des différences notables par rapport aux performances des modèles logistiques précédemment analysés. Ce graphique montre que le modèle XGBoost utilisant la caractéristique d'angle présente un AUC de 0.59, ce qui est significativement meilleur qu'un classifieur aléatoire dont l'AUC est de 0.50. Cela suggère que, contrairement aux modèles logistiques, le modèle XGBoost est capable d'extraire un certain pouvoir prédictif de la caractéristique d'angle.

Par ailleurs, le modèle XGBoost qui utilise uniquement la distance a un AUC de 0.70, confirmant que la distance reste un prédicteur plus robuste que l'angle pour cette tâche de prédiction.

De façon plus marquante, le modèle XGBoost qui combine les deux caractéristiques surpasse légèrement les modèles univariés avec un AUC de 0.71. Cela indique que XGBoost a réussi à capitaliser sur l'interaction entre la distance et l'angle pour améliorer la prédiction des résultats binaires. Cette synergie entre les variables peut être attribuée à la capacité de XGBoost à modéliser des relations non linéaires et des hiérarchies de caractéristiques, ce qui n'est pas possible avec les modèles logistiques plus simples.

Ces résultats mettent en lumière la flexibilité et la puissance de XGBoost dans l'exploitation des relations complexes au sein des données, ce qui peut se traduire par une meilleure performance prédictive dans des tâches de classification sophistiquées.


## Taux de but comme fonction du centile de la probabilité de tir donnée par les modèles
![SCREENSHOT OF Comparaison des types de tirs](xgboost_baseline/2023-10-08-XGB_Ratio_Goal_Percentile_Curves_Val.png)


Le graphique illustre comment les différents modèles XGBoost prédisent le taux de buts en fonction des probabilités. L'axe horizontal organise les probabilités prédites en percentiles, du plus élevé au plus bas, et l'axe vertical montre le taux réel de buts pour ces percentiles.

Le modèle qui utilise la distance, représenté par la courbe bleue, démontre une corrélation positive entre les probabilités prédites et les taux de buts réels, surtout pour les tirs avec les plus hautes probabilités de marquer. Cela signifie que le modèle est relativement capable d'identifier les occasions de buts probables.

La courbe orange, correspondant au modèle qui prend en compte uniquement l'angle, suit une trajectoire similaire à celle de la distance mais avec une pente moins prononcée, ce qui suggère que l'angle, bien qu'utile, est un prédicteur moins puissant que la distance.

La courbe verte indique que le modèle combinant à la fois la distance et l'angle la pente la plus prononcée parmi les modèles, ce qui met en évidence la capacité de XGBoost à extraire des informations utiles de l'interaction des deux caractéristiques. Ce modèle dépasse les autres modèles, indiquant que la combinaison des deux caractéristiques fournit une prédiction plus précise des tirs qui résulteront en buts, bien que c'est un gain de performance modeste.

La courbe rouge pointillée du classifieur aléatoire quant à elle révèle sans surprise un taux de but constant et bas à travers tous les percentiles, confirmant qu'il n'utilise aucune donnée significative pour ses prédictions.

Ces observations démontrent l'efficacité du modèle XGBoost combinant la distance et l'angle, qui surpasse les modèles univariés et le classifieur aléatoire. Le graphique souligne l'importance de l'exploitation des interactions entre les variables pour améliorer la précision des prédictions dans des modèles de classification avancés.

## Proportion cumulée de buts comme fonction du centile de la probabilité de tir donnée par les modèles
![SCREENSHOT OF Comparaison des types de tirs](xgboost_baseline/2023-10-08-XGB_Proportion_Goal_Percentile_Curves_Val.png)

Le graphique présente la proportion cumulée de buts réels par rapport aux prédictions des modèles, segmentées en percentiles. Le modèle vert, qui combine les caractéristiques de distance et d'angle, se distingue en affichant la courbe la plus haute, indiquant que cette combinaison de caractéristiques donne les prédictions les plus précises pour les tirs les plus susceptibles de résulter en buts, notamment dans les tranches de haute probabilité.

La courbe bleue, représentant le modèle fondé uniquement sur la distance, suit de près, suggérant que la distance à elle seule est un indicateur robuste pour prédire les buts. Bien qu'elle soit légèrement inférieure au modèle combiné, elle dépasse nettement la performance du modèle basé sur l'angle, illustré par la courbe orange, qui, tout en surclassant le classifieur aléatoire, n'atteint pas les niveaux de prédiction des modèles qui prennent en compte la distance.

Le classifieur aléatoire est représenté par la courbe rouge et montre une progression linéaire, soulignant l'absence d'une véritable capacité prédictive, car il attribue des probabilités uniformes sans discernement.

Dans un scénario idéal, un modèle parfait aurait une courbe qui monte rapidement vers le percentile le plus élevé et se maintient ensuite, reflétant une précision absolue dans la prédiction des buts. Bien que les modèles présentés n'atteignent pas cet idéal, le modèle combinant distance et angle se rapproche le plus de ce comportement, montrant ainsi sa supériorité en termes de capture des tirs à fort potentiel de buts.

## Diagramme de fiabilité des modèles
![SCREENSHOT OF Comparaison des types de tirs](xgboost_baseline/2023-10-08-XGB_Calibration_Curves.png)

Le graphique de calibration pour les modèles XGBoost montre une tendance nettement différente de celle observée dans les graphiques correspondants pour les modèles de régression logistique. Ici, les probabilités moyennes prédites par les tranches s'étendent presque jusqu'à 0.6 pour le modèle le plus performant, ce qui contraste avec la plage plus limitée des probabilités moyennes observées dans les modèles de régression logistique.

Pour les probabilités inférieures à 0.2, les trois modèles XGBoost présentent une bonne performance de calibration, leurs courbes respectives s'alignant de près avec la ligne de calibration parfaite. Cela indique une estimation fiable des probabilités pour les tirs moins susceptibles de devenir des buts. Cependant, à mesure que nous nous déplaçons vers des probabilités plus élevées, des divergences apparaissent.

Notamment, le modèle basé sur la distance ne produit des estimations que jusqu'à une probabilité prédite d'environ 0.3, après quoi il n'y a plus de données, suggérant une limitation dans la capacité du modèle à prédire des tirs avec des probabilités plus élevées de réussite. D'un autre côté, le modèle combiné, qui intègre à la fois la distance et l'angle, continue de produire des estimations pour des probabilités plus élevées. Ce modèle montre cependant une grande variabilité dans les prédictions pour les probabilité prédite moyennes plus élevés, montrant une grande incertitude quant aux prédictions.

La performance globale du modèle combiné représente une amélioration significative par rapport aux baselines de régression logistique. Cette amélioration est particulièrement notable dans la capacité du modèle à fournir des estimations de probabilité pour un éventail plus large de situations de tir, ainsi que dans la précision accrue des prédictions pour les probabilités plus élevées. Cela démontre l'avantage des modèles XGBoost dans la modélisation de phénomènes complexes où les interactions entre les variables jouent un rôle clé.