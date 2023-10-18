---
layout: post
author: Equipe A07
title: Advanced Data visualisation
---

<style>
  #plot-container {
    justify-content: center;
    align-items: center;
    width: 100vw; 
    height: 100vh;
  }
</style>

**Note importante concernant nos cartes de tirs:**
> Même si il y a 2 buts sur le plot, tous les tirs sont bels et bien se référent à un seul but (à un même sens de jeu). Ce dernier étant la cage de droite. Donc, vous pouvez négliger la cage de droite (*nous n'avons juste pas trouver l'image adéquat ^^*) 

# Interprétabilité de la carte des taux de tirs

De nombreuses interprétations sont possibles à partir de ce graphique, par exemple les caractéristiques offensives d'une équipe pourraient être :

1. **Qualité des tirs** : La heatmap peut donner un aperçu de la qualité des tirs effectués par l'équipe. Les zones où les taux de tirs sont plus élevés (couleurs chaudes) indiquent que l'équipe prend en moyenne plus de tirs à partir de ces endroits que les autres equipes de la ligue. Cela peut suggérer que l'équipe trouve de meilleures opportunités de tir ou/et qu'elle a des joueurs avec de meilleurs (en moyenne par rapport aux autres joueurs de la ligue) compétences de tir dans ces zones.

2. **Stratégie offensive** : La heatmap donne aussi un aperçu de la stratégie offensive employée par une équipe au cours d'une saison. Si certaines zones de la heatmap affichent des taux de tirs significativement plus élevés, cela suggère que l'équipe cible intentionnellement ces zones pour générer des occasions de marquer. Cela peut indiquer un style de jeu spécifique.


<div id="plot-container">
    <iframe src="./adv_viz_interactive_plot/seasons/season_2016.html" width="100%" height="100%" style="border: none;"></iframe>
</div>

<div id="plot-container">
    <iframe src="./adv_viz_interactive_plot/seasons/season_2017.html" width="100%" height="100%" style="border: none;"></iframe>
</div>

<div id="plot-container">
    <iframe src="./adv_viz_interactive_plot/seasons/season_2018.html" width="100%" height="100%" style="border: none;"></iframe>
</div>

<div id="plot-container">
    <iframe src="./adv_viz_interactive_plot/seasons/season_2019.html" width="100%" height="100%" style="border: none;"></iframe>
</div>

<div id="plot-container">
    <iframe src="./adv_viz_interactive_plot/seasons/season_2020.html" width="100%" height="100%" style="border: none;"></iframe>
</div>

# Analysis Colorado Avalanche

<div id="plot-container">
    <iframe src="./adv_viz_interactive_plot/teams/colorado.html" width="100%" height="100%" style="border: none;"></iframe>
</div>

**Analyse de la carte de tir au cours de la saison 2016**:
> On voit une zone bleue très répandue autour des buts. On sait que les zones bleues sont caractéristiques d'une sous-performance offensive. On en déduit donc, que l'équipe du Colorado au cours de la saison 2016, a pris beaucoup (car le bleu est quand même très foncé) moins de tirs que les autres équipes de la ligue et ce en plus, dans un endroit stratégique qui est la zone devant les buts. 

> On percoit seulement une seule zone rouge, qui est, de plus, très localisé et assez excentrée des cages. On sait que les zones rouges sont caractéristiques d'une sur-performance offensive. Cependant, ici, la zone rouge est assez excentré donc il est difficile de croire qui tout ces tirs ont été transformés en but. On en déduit que, cette zone rouge étant trop restreinte (peu répandue) et "mal placé", les sur-performances offensives de cette équipe au cours de cette saison sont peu nombreuses et apparamment de piètres qualités (taux buts/tirs vraisemblablement faibles pour cette zone)

> D'un point de vue général la différence de proportion de zones bleues et de proportion de zones rouges est grande. 

Ainsi, de par les points précédents on en conclut a sous-performée offensivement par rapport aux autres équipes. 

En regardant le classement de cette équipe pour la saison 2016, on voit que ils ont fini derniers. Ceci est logique car la NHL étant indéniablement la meilleur mondiale ligue de hockey, les sous-performances offensives se payent très chères et sont immédiatement sanctionnées !!

**Analyse de la carte de tir au cours de la saison 2020**:

> On voit une zone rouge très répandue autour des buts. On en déduit donc, que l'équipe du Colorado au cours de la saison 2020, a pris beaucoup (car le rouge est très foncé) plus de tirs que les autres équipes de la ligue et ce en plus, dans un endroit stratégique qui est la zone devant les buts.  Ainsi, cette zone rouge étant très répandue et "stratégiquement bien placé", les sur-performances offensives de cette équipe au cours de cette saison sont nombreuses et apparamment fructifiantes (taux buts/tirs vraisemblablement élevé pour cette zone)

>On percoit seulement une seule zone bleue foncée, qui est, de plus, très localisé et assez excentrée des cages. Donc on peut en déduire, que les sous-performances offensives de cette équipe au cours de cette saison n'ont pas été préjudiciable pour cette dernière. 

D'un point de vue général, de par les points précédents et la différence de proportion de zones rouges et de proportion de zones rouges, on en conclut que l'équipe a sur-performée offensivement par rapport aux autres équipes.

Il s'agit là, presque, de la tendance opposée au graphique précédent de la saison 2016.

En regardant le classement de cette équipe pour la saison 2020, on voit que ils ont fini premiers. Ceci est logique la carte de tir pour cette saison est très positive quantitativement (beaucoup de zones rouges foncées) et qualitativement (zones rouges situées à des endroits offensivement stratégiques) !!

<u>Notre analyse est cohérente

# Comparaison Buffalo / Tampa Bay

## Buffalo

<div id="plot-container">
    <iframe src="./adv_viz_interactive_plot/teams/buffalo.html" width="100%" height="100%" style="border: none;"></iframe>
</div>


## Tampa Bay

<div id="plot-container">
    <iframe src="./adv_viz_interactive_plot/teams/tampa.html" width="100%" height="100%" style="border: none;"></iframe>

