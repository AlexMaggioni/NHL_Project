---
layout: post
author: Equipe A07
title: Data Cleaning
---

# Raw json data to Dataframe

![SCREENSHOT OF THE DATAFRAME](image/2023-10-06-data_cleaning/1697482322088.png "Dataframe head exctract")

## Handling of 'strength' value

Pour ajouter des informations quantitatives (savoir plus que si le play sa passe en contexte de **sur-nombre, sous-nombre, ou egal**) pour le **strength** d'un play, on pourrait acceder a la liste des `penaltyPlays`  (disponible sous  `['liveData']['plays']['penaltyPlays']`). 

Un `penaltyPlay` possede le temps auquel la penalite s'est realise, la duree de la penalite, et le joueur impacte. 

Donc, comme chaque play possede le temps auquel le play s'est realise, on peut savoir si le play s'est deroule pendant une penalite affectant son equipe (**sous-nombre**) ou non (**sur-nombre**).

Ainsi, il serait facile de rajouter une colonne *numerical_strength* de type **str** avec comme valeurs ('4vs1',...)

## Additional characteristics

Plusieurs caracteristiques peuvent etre interessantes a rajouter:

1. `dist_from_goal` : Distance par rapport au but . Tout d'abord, en utilisant la fonction  `utils.py::unify_coordinates_referential`, unifier les coordonnees selon un meme sens de jeu et calculer au but (qui serait pris au point **[98,0]**)
2. `is_counter_attack_goal` : Boolean Column , "True" si un play de type **GOAL qui s'est realise dans un contexte de contre-attaque.** On pourrait avoir cette information lors de la construction du Dataframe, par exemple, en regardant si le play juste avant le **GOAL** :
   * est de type **TAKEAWAY** et (`["result"]["eventTypeId"]`)
   * que le **TAKEAWAY** passe dans le cote defensif de la team qui a fait le play de type **GOAL** (facile a determiner via les coordonnees et la cle `rinkSide` )
3. `is_shot_rebound` : Boolean Column , "True" si un play de type **SHOT a donne lieu a un GOAL sur le prochain PLAY.**
