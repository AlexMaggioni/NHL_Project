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
    margin-bottom: 0px;
  }
</style>

# Graphiques interactif de l'excès moyen de tirs par emplacement en fonction de l'équipe et de la saison 

**Note importante concernant les prochains graphiques:**

>L'ensemble des coordonées de tirs ont été unifiées afin d'être sur une même orientation commune du terrain, et présentés sur un graphique montrant l'entièreté de la patinoire. Ainsi, cela n'ignore pas le fait qu'une équipe puisse effectuer un tir au but depuis leur zone défensive, ce qui est très peu commun mais est une stratégie fréquemment utilisée lorsqu'un but est vide (pour créer un avantage numérique artificiel.)

## Saison 2016
<div id="plot-container">
    <iframe src="./adv_viz_interactive_plot/seasons/season_2016.html" width="100%" height="100%" style="border: none;"></iframe>
</div>

## Saison 2017
<div id="plot-container">
    <iframe src="./adv_viz_interactive_plot/seasons/season_2017.html" width="100%" height="100%" style="border: none;"></iframe>
</div>

## Saison 2018
<div id="plot-container">
    <iframe src="./adv_viz_interactive_plot/seasons/season_2018.html" width="100%" height="100%" style="border: none;"></iframe>
</div>

## Saison 2019
<div id="plot-container">
    <iframe src="./adv_viz_interactive_plot/seasons/season_2019.html" width="100%" height="100%" style="border: none;"></iframe>
</div>

## Saison 2020
<div id="plot-container">
    <iframe src="./adv_viz_interactive_plot/seasons/season_2020.html" width="100%" height="100%" style="border: none;"></iframe>
</div>


La carte des taux de tirs est une représentation visuelle fascinante de la performance d'une équipe sur le terrain, en particulier en ce qui concerne sa capacité à générer des occasions de tir. Les zones teintées de rouge sur la carte indiquent des régions où l'équipe en question réalise davantage de tirs que la moyenne de la ligue. Cela pourrait indiquer que l'équipe parvient à se démarquer et à trouver des opportunités de tirer au but plus fréquemment que d'autres équipes. Plusieurs facteurs pourraient expliquer cette tendance : la présence de joueurs exceptionnellement talentueux, la capacité de l'équipe à créer des occasions de haute qualité, ou une combinaison des deux.

De plus, la distribution des zones chaudes sur la carte donne un aperçu précieux de la stratégie offensive employée par l'équipe au cours d'une saison. Une prévalence de zones rouges dans certaines régions du terrain suggère une intention délibérée de cibler ces zones pour créer des occasions de marquer. C'est une indication claire d'un style de jeu spécifique adopté par l'équipe, que ce soit pour exploiter les faiblesses de l'adversaire ou pour jouer sur ses propres points forts.

Finalement, un autre angle d'interprétation que cette carte des taux de tirs peut offrir concerne les réactions et la dynamique défensive des équipes adverses. Si une équipe présente des zones rouges très prononcées dans certaines régions, cela pourrait aussi révéler comment les équipes adverses la perçoivent et se positionnent défensivement contre elle. Par exemple, si une équipe privilégie les tirs de loin et que cela est représenté par une concentration de zones rouges à distance, cela pourrait suggérer que les défenseurs adverses se replient plus profondément, offrant ainsi de l'espace pour des tirs lointains. Inversement, une concentration de zones rouges près du but pourrait indiquer que les équipes adverses ont du mal à défendre les assauts rapprochés, soit en raison de la qualité des attaquants, soit à cause de faiblesses défensives. Ainsi, cette carte peut aussi servir d'outil pour analyser non seulement les forces d'une équipe, mais également comment elle est perçue et combattue par ses adversaires.

# Comparaison des saisons 2016 et 2020 pour l'Avalanche du Colorado

<div id="plot-container">
    <iframe src="./adv_viz_interactive_plot/teams/colorado.html" width="100%" height="100%" style="border: none;"></iframe>
</div>

En examinant l'analyse des années 2016 et 2020, on observe une évolution significative dans la performance offensive de l'Avalanche du Colorado. En 2016, l'équipe a terminé dernière au classement, tandis qu'en 2020, elle a terminé en tête.

En 2016, en regardant le graphique, on constate une grande zone bleue qui domine devant le filet de l'équipe adverse. Ceci indique que l'Avalanche du Colorado tirait moins souvent que la moyenne de la ligue depuis cet emplacement critique. Une petite zone rouge, éloignée et un peu excentrée par rapport au but, suggère que, bien qu'ils aient pu tirer davantage depuis cet endroit spécifique par rapport à la moyenne de la ligue, ce n'est pas un emplacement idéal pour marquer. Comme nous l'avons discuté précédemment, la proximité du but est souvent corrélée à des chances accrues de marquer. Tirer depuis une position plus excentrée et éloignée signifie généralement des angles plus difficiles et une plus grande distance, et donc des chances de marquer réduites.

Ces motifs pourraient suggérer un certain nombre de problèmes tactiques pour l'Avalanche cette année-là. Peut-être que l'équipe a eu du mal à pénétrer dans des zones à haute dangerosité ou que leur stratégie les a orientés vers des tirs depuis des positions moins optimales.

En revanche, en 2020, le paysage est radicalement différent. Une vaste zone rouge englobe l'avant du filet, indiquant une quantité élevée de tirs provenant de cet emplacement crucial. Ceci est le signe d'une équipe qui a réussi à se placer dans des positions de scoring optimales. On remarque aussi une zone bleue à l'extérieur de la zone de tirs de haute dangerosité, ce qui pourrait signifier que l'équipe privilégie des tirs plus proches et potentiellement plus dangereux plutôt que des tirs de loin.

La présence massive de rouge directement devant le filet montre non seulement une augmentation des tirs depuis cet emplacement, mais aussi une indication claire de la dominance offensive de l'équipe cette saison. Les chances de marquer sont nettement plus élevées depuis ces zones, et cela démontre une amélioration significative par rapport à 2016.

Cette transformation pourrait suggérer un changement dans la stratégie offensive de l'équipe, peut-être une plus grande emphase sur la possession de la rondelle dans la zone offensive ou des schémas de jeu conduisant à des tirs de qualité.

En comparant les deux années, il est évident que l'Avalanche a subi une transformation considérable en termes de performance offensive. Alors qu'en 2016, ils semblaient lutter pour obtenir des tirs de qualité, en 2020, ils dominaient clairement ces zones clés, augmentant ainsi leurs chances de succès. Cette amélioration a été si marquée que l'équipe est passée de la dernière place en 2016 à la première place au classement en 2020.

# Comparaison Sabres de Buffalo

## Sabres de Buffalo

<div id="plot-container">
    <iframe src="./adv_viz_interactive_plot/teams/buffalo.html" width="100%" height="100%" style="border: none;"></iframe>
</div>


## Lightning de Tampa Bay

<div id="plot-container">
    <iframe src="./adv_viz_interactive_plot/teams/tampa.html" width="100%" height="100%" style="border: none;"></iframe>
</div>

En examinant les plans de tir pour les Sabres de Buffalo et le Lightning de Tampa Bay, plusieurs observations pertinentes peuvent être faites.

Le Lightning de Tampa Bay démontre une habileté particulière à diriger leurs tirs depuis des zones rapprochées du but, signifiant non seulement leur capacité à déjouer la défense adverse, mais aussi à positionner leurs joueurs de façon stratégique. Cette concentration de tirs près du but témoigne d'une offensive bien orchestrée, sachant exploiter les faiblesses de l'adversaire pour se créer des opportunités de marquer. Les zones situées directement devant le gardien sont généralement celles où les tirs ont le plus de chances de se transformer en buts, étant donné la proximité et l'angle restreint pour le gardien pour parer le tir. C'est une indication claire de la stratégie du Lightning pour maximiser leurs opportunités de marquer.

À l'opposé, les Sabres de Buffalo semblent contraints par les défenses adverses à opter pour des tirs lointains. Un grand nombre de leurs tirs provient de la périphérie, en particulier de la ligne bleue et des points. Bien que ces tirs puissent parfois surprendre le gardien, surtout s'ils sont déviés, ils sont généralement plus faciles à arrêter en raison de la distance accrue, offrant au gardien plus de temps pour réagir. Cette tendance suggère que les Sabres pourraient rencontrer des difficultés à franchir la barrière défensive des équipes adverses ou à mettre en place des jeux offensifs élaborés pour se rapprocher du but. Cela pourrait indiquer un besoin de revoir leur stratégie offensive pour augmenter leurs chances de succès.

Ces différences dans le style de jeu et l'efficacité offensive se reflètent également dans le classement des deux équipes. Au cours des trois dernières saisons, Tampa Bay s'est constamment hissé dans le top 10 des équipes de la ligue, démontrant une régularité et une dominance sur la glace. En revanche, le meilleur classement atteint par les Sabres a été une modeste 25ème place, ce qui indique des lacunes dans leur jeu et une nécessité de repenser certains aspects de leur stratégie pour améliorer leurs performances.

Cependant il est important de noter que l'analyse actuelle du graphique ne prend pas en considération la dangerosité des tirs, limitant ainsi notre capacité à formuler des conclusions précises. Supposer que ces seules données graphiques nous offrent une vision complète des réussites ou des difficultés d'une équipe serait une méprise. Le hockey, avec sa complexité remarquable, ne peut être résumé par une simple métrique comme l'excès de tirs par heure pour juger de l'efficacité offensive. Une telle approche néglige également l'aspect défensif, pivot central pour le succès de toute équipe. Pour vraiment appréhender la performance d'une équipe, il est impératif de considérer une multitude de facteurs.