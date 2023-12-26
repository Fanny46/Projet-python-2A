# **Projet Python 2A**

**Tony Lauze - Fanny Daubet**

*Ce projet est réalisé dans le cadre du cours de Python pour la data-science de Lino Galiana, pour l'année 2023-2024.*

## **Introduction**

Le but de ce projet est de **modéliser le prix de l'immobilier en région parisienne** et, plus précisément, des appartements dans Paris intra-muros.

La base de donnée principale qui sera utilisée, est le **fichier Demandes de Valeurs Foncières (DVF)**, produit par la direction générale des finances publiques, qui recense les transactions immobilières intervenues au cours des cinq dernières années en France, à partir des actes notariés.

Comme toutes les ventes de ce fichier sont géolocalisées, l'enrichissement principal qui sera apporté à la base de données sera l'ajout, pour chaque appartement, de la **distance minimale à certains lieux d'intérêt parisiens** (stations de métro, espaces verts, lieux historiques, etc.).

Pour la modélisation, on procédera d'abord à une approche "économétrique" utilisant des régressions simples et des régressions avec effets fixes, puis on abordera le problème d'un point de vue plus orienté prédiction et sélection de variables, avec les régressions LASSON et RIDGE (dont on verra les limites dans notre cas).

Les grandes étapes sont donc les suivantes :
- Etape 1 : Prise en main et nettoyage du fichier DVF, création d'une base de données de départ
- Etape 2 : Visualisation spatiale et temporelle
- Etape 3 : Enrichissement des données, en récupérant en open data et scrapping les localisations de plusieurs catégories de lieux d'intérêt parisiens
- Etape 4 : Modélisation, approche économétrique et prédiction
