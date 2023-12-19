"""Librairies nécessaires"""

import pandas as pd
from pandas import json_normalize
import geopandas as gpd

import numpy as np

import matplotlib.pyplot as plt

import json

from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points

from tqdm import tqdm

"""Données administratives géographiques de la région parisienne"""

paris_arrondissement = gpd.read_file('2) Visualisation/Données_carto/paris_arrondissements.geojson')
paris_quartiers = gpd.read_file('2) Visualisation/Données_carto/paris_quartiers.geojson')
paris_quartiers = paris_quartiers[['c_quinsee', 'l_qu', 'geometry']]
petite_couronne = gpd.read_file('2) Visualisation/Données_carto/petite_couronne.geojson')
idf = gpd.read_file('2) Visualisation/Données_carto/idf.geojson')

"""Changement de directory pour lire les fichiers"""
import os
os.getcwd() #trouver le directory actuel 
os.chdir('/home/onyxia/work/Projet-python-2A')


"""
1) ESPACES VERTS
"""

"""Coordonnées des jardins manquants"""
coord_jardin_du_luxembourg = [
    [48.848583, 2.332634],
    [48.849056, 2.338542],
    [48.847234, 2.340275],
    [48.844127, 2.338816],
    [48.844720, 2.332550]
]

coord_jardin_des_plantes = [
    [48.846779, 2.360882],
    [48.843693, 2.364841],
    [48.841292, 2.356097],
    [48.843813, 2.355056]
]

coord_jardin_des_tuileries = [
    [48.866346, 2.323663],
    [48.863713, 2.331903],
    [48.861017, 2.329972],
    [48.863854, 2.321604]
]

def ajout_3_parcs():
    # Convertir les coordonnées au format WGS 84
    """Lecture du fichier des parcs"""
    emplacement_parcs = '3.0) Enrichissement données/Données/Espaces_verts_parisiens.geojson'
    df_espaces_verts_brut = gpd.read_file(emplacement_parcs, low_memory=False, index_col=0)
    
    coord_jardin_des_plantes_wgs84 = [(lon, lat) for lat, lon in coord_jardin_des_plantes]
    coord_jardin_des_tuileries_wgs84 = [(lon, lat) for lat, lon in coord_jardin_des_tuileries]
    coord_jardin_du_luxembourg_wgs84 = [(lon, lat) for lat, lon in coord_jardin_du_luxembourg]
    
    # Créer un GeoDataFrame avec le jardin des plantes
    nouveau_jardin = gpd.GeoDataFrame({
        'nom_ev': ['JARDIN DES PLANTES'],
        'geometry': [Polygon(coord_jardin_des_plantes_wgs84)]
    }, geometry='geometry')
    nouveau_jardin.crs = "EPSG:4326"
    nouveau_jardin['poly_area'] = nouveau_jardin['geometry'].to_crs(epsg=2154).area  # Conversion en mètres carrés
    nouveau_jardin['adresse_codepostal'] = '75'
    nouveau_jardin['categorie'] = 'Parc'
    nouveau_jardin.crs = "EPSG:4326"
    
    nouveau_jardin2 = gpd.GeoDataFrame({
        'nom_ev': ['JARDIN DES TUILERIES'],
        'geometry': [Polygon(coord_jardin_des_tuileries_wgs84)]
    }, geometry='geometry')
    nouveau_jardin2.crs = "EPSG:4326"
    nouveau_jardin2['poly_area'] = nouveau_jardin2['geometry'].to_crs(epsg=2154).area
    nouveau_jardin2['adresse_codepostal'] = '75'
    nouveau_jardin2['categorie'] = 'Parc'
    nouveau_jardin2.crs = "EPSG:4326"
    
    nouveau_jardin3 = gpd.GeoDataFrame({
        'nom_ev': ['JARDIN DU LUXEMBOURG'],
        'geometry': [Polygon(coord_jardin_du_luxembourg_wgs84)]
    }, geometry='geometry')
    nouveau_jardin3.crs = "EPSG:4326"
    nouveau_jardin3['poly_area'] = nouveau_jardin3['geometry'].to_crs(epsg=2154).area #ajout de l'aire en m^2
    nouveau_jardin3['adresse_codepostal'] = '75'
    nouveau_jardin3['categorie'] = 'Parc'
    nouveau_jardin3.crs = "EPSG:4326"
    
    # Ajouter le nouveau jardin au GeoDataFrame existant
    df_espaces_verts_brut = gpd.GeoDataFrame(pd.concat([df_espaces_verts_brut, nouveau_jardin], ignore_index=True))
    df_espaces_verts_brut = gpd.GeoDataFrame(pd.concat([df_espaces_verts_brut, nouveau_jardin2], ignore_index=True))
    df_espaces_verts_brut = gpd.GeoDataFrame(pd.concat([df_espaces_verts_brut, nouveau_jardin3], ignore_index=True))

    return df_espaces_verts_brut

"""
2) TRANSPORTS
"""

from sklearn.preprocessing import LabelEncoder
import seaborn as sns

#lecture fichier
emplacement = '3.0) Enrichissement données/Données/Transports_idf.geojson'
df_transport = gpd.read_file(emplacement, low_memory=False, index_col=0)

#modifications du fichier
var_interet = ['nom_gares', 'nom_so_gar', 'nom_su_gar', 'idrefligc', 'res_com', 'indice_lig', 'mode', 'tertrain', 'terrer',
       'termetro', 'tertram', 'terval', 'exploitant', 'idf', 'geometry']
df_transport = df_transport.loc[:, var_interet]

#création de sous dataframes selon le type de transport
df_metro = df_transport.loc[df_transport['mode']=='METRO']
df_rer = df_transport.loc[df_transport['mode']=='RER']
df_tram = df_transport.loc[df_transport['mode']=='TRAMWAY']

#réduction du df
df_transport = df_transport.loc[df_transport['mode'].isin(['METRO', 'RER', 'TRAMWAY'])]

"""Deux fonctions qui tracent les cartes"""

def plot_rer_stations():

    fig, ax = plt.subplots(figsize=(8, 10))

    # Filtrer les stations de RER dans la petite couronne
    df_rer_petite_couronne = df_rer[df_rer['geometry'].within(petite_couronne.unary_union)].copy()

    # Créer la colonne 'indice_lig_encoded'
    le = LabelEncoder()
    df_rer_petite_couronne['indice_lig_encoded'] = le.fit_transform(df_rer_petite_couronne['indice_lig'])

    # Tracer les frontières
    petite_couronne.boundary.plot(ax=ax, linewidth=0.3)
    paris_arrondissement.boundary.plot(ax=ax, edgecolor="red", linewidth=0.7)

    # Utilisation de scatter avec les couleurs codées
    scatter = ax.scatter(df_rer_petite_couronne['geometry'].x, df_rer_petite_couronne['geometry'].y, 
                         c=df_rer_petite_couronne['indice_lig_encoded'], cmap='Set1', s=50, edgecolors='black', alpha=0.7)

    # Ajouter une légende pour 'indice_lig'
    correspondance = {val: chr(ord('A') + num) for num, val in enumerate(le.classes_)}
    legend_labels = [correspondance[val] for val in le.classes_]
    legend = ax.legend(handles=scatter.legend_elements()[0], title='Ligne RER', labels=legend_labels)
    ax.add_artist(legend)

    # Ajustements d'axes et titre
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title('Carte des stations de RER dans la petite couronne')

    plt.show()

def carte_metro():

    # Filtrer les stations de métro qui sont situées à l'intérieur de Paris
    df_metro_paris = df_metro[df_metro['geometry'].within(paris_arrondissement.unary_union)].copy()
    
    fig, ax = plt.subplots(figsize=(8, 10))
    
    # Tracer les frontières des arrondissements de Paris
    paris_arrondissement.boundary.plot(ax=ax, edgecolor="black", linewidth=0.7)
    
    # Utilisation de LabelEncoder pour convertir les catégories en nombres
    le = LabelEncoder()
    df_metro_paris['indice_lig_encoded'] = le.fit_transform(df_metro_paris['indice_lig'])
    
    # Utilisation de scatter avec les couleurs codées et une palette de couleurs vive
    ax.scatter(df_metro_paris['geometry'].x, df_metro_paris['geometry'].y,
               c=df_metro_paris['indice_lig_encoded'], cmap='Set1',
               s=30, edgecolors='black', alpha=0.7)
    
    # Supprimer les axes
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Ajouter un titre
    ax.set_title('Carte des stations de métro parisiennes')
    
    plt.show()
    

"""Fonction qui merge les data set en trouvant la station (point) la plus proche et 
enregistre la distance (en km)"""

def ajout_stat_trans(dvf, df_transport):

    #sélection des variables
    var_transport = ['nom_gares', 'indice_lig', 'geometry']
    df_transport = df_transport[var_transport].copy()
    df_transport = df_transport.drop_duplicates(['geometry'])

    
    #Passer en projection 2D
    proj_lambert = 'EPSG:3942'
    dvf = dvf.to_crs(proj_lambert)
    df_transport = df_transport.to_crs(proj_lambert)

    #jointure spatiale
    merged_nearest = gpd.sjoin_nearest(dvf, df_transport, how="left", max_distance=5000, distance_col="dist_min_stat")

    #dist en km
    merged_nearest['dist_min_stat'] = merged_nearest['dist_min_stat']/1000

    #repasser en système de projection wgs 84
    dvf_avec_transport = merged_nearest.to_crs('EPSG:4326')

    #supprimer et renommer colonnes
    dvf_avec_transport = dvf_avec_transport.drop(['index_right'], axis=1)    
    dvf_avec_transport = dvf_avec_transport.rename(columns={'nom_gares': 'nom_stat', 'indice_lig': 'num_ligne'})

    return dvf_avec_transport


"""
3) Ajout lycées
"""

def ajout_meilleurs_lycées(dvf, df_lycees):

    #sélection des variables
    var_lycees = ['patronyme', 'geometry']
    df_lycees = df_lycees[var_lycees].copy()
    
    #Passer en projection 2D
    proj_lambert = 'EPSG:3942'
    dvf = dvf.to_crs(proj_lambert)
    df_lycees = df_lycees.to_crs(proj_lambert)

    #jointure spatiale
    merged_nearest = gpd.sjoin_nearest(dvf, df_lycees, how="left", max_distance=5000, distance_col="dist_min_lycee")

    #dist en km
    merged_nearest['dist_min_lycee'] = merged_nearest['dist_min_lycee']/1000

    #repasser en système de projection wgs 84
    dvf_avec_lycees = merged_nearest.to_crs('EPSG:4326')

    #supprimer et renommer colonnes
    dvf_avec_lycees = dvf_avec_lycees.drop(['index_right'], axis=1)    
    dvf_avec_lycees = dvf_avec_lycees.rename(columns={'patronyme': 'nom_lycee'})

    return dvf_avec_lycees

"""
4) Ajout Sites historiques/touristiques
"""

"""Fonction qui merge les data set en trouvant le site historique (point) le plus proche 
et enregistre la distance (en km)"""

def ajout_sites_histo(dvf, df_monuments):

    #sélection des variables
    var_monuments = ['immeuble', 'geometry']
    df_monuments = df_monuments[var_monuments].copy()
    
    #Passer en projection 2D
    proj_lambert = 'EPSG:3942'
    dvf = dvf.to_crs(proj_lambert)
    df_monuments = df_monuments.to_crs(proj_lambert)

    #jointure spatiale
    merged_nearest = gpd.sjoin_nearest(dvf, df_monuments, how="left", max_distance=5000, distance_col="dist_min_site_histo")

    #dist en km
    merged_nearest['dist_min_site_histo'] = merged_nearest['dist_min_site_histo']/1000

    #repasser en système de projection wgs 84
    dvf_avec_sites_histo = merged_nearest.to_crs('EPSG:4326')

    #supprimer et renommer colonnes
    dvf_avec_sites_histo = dvf_avec_sites_histo.drop(['index_right'], axis=1)    
    dvf_avec_sites_histo = dvf_avec_sites_histo.rename(columns={'immeuble': 'nom_site_histo'})

    return dvf_avec_sites_histo


"""
5) Ajout voies d'eau
"""

"""Fonction qui merge les data set en trouvant la voie d'eau la plus proche 
et enregistre la distance (en km)"""

def ajout_voies_eau(dvf, df_eau):

    #sélection des variables
    var_eau = ['geometry']
    df_eau = df_eau[var_eau].copy()
    
    #Passer en projection 2D
    proj_lambert = 'EPSG:3942'
    dvf = dvf.to_crs(proj_lambert)
    df_eau = df_eau.to_crs(proj_lambert)

    #jointure spatiale
    merged_nearest = gpd.sjoin_nearest(dvf, df_eau, how="left", max_distance=6000, distance_col="dist_min_voie_eau")

    #dist en km
    merged_nearest['dist_min_voie_eau'] = merged_nearest['dist_min_voie_eau']/1000

    #repasser en système de projection wgs 84
    dvf_avec_voie_eau = merged_nearest.to_crs('EPSG:4326')

    #supprimer colonnes
    dvf_avec_voie_eau = dvf_avec_voie_eau.drop(['index_right'], axis=1)  

    #retirer les doublons
    #dvf_avec_voie_eau = dvf_avec_voie_eau.drop_duplicates(['id_mutation', 'log_prix', 'geometry'])

    return dvf_avec_voie_eau


"""
5) Ajout distance centre paris
"""

"""Fonction qui merge les data set en trouvant la distance minimale au centre de Paris en km"""

def ajout_centre_paris(dvf, centre_paris_gdf):

    #Passer en projection 2D
    proj_lambert = 'EPSG:3942'
    dvf = dvf.to_crs(proj_lambert)
    centre_paris_gdf = centre_paris_gdf.to_crs(proj_lambert)

    #jointure spatiale
    merged_nearest = gpd.sjoin_nearest(dvf, centre_paris_gdf, how="left", max_distance=6000, distance_col="dist_min_paris_centre")

    #dist en km
    merged_nearest['dist_min_paris_centre'] = merged_nearest['dist_min_paris_centre']/1000

    #repasser en système de projection wgs 84
    dvf_avec_dist_centre = merged_nearest.to_crs('EPSG:4326')

    #supprimer colonnes
    dvf_avec_dist_centre = dvf_avec_dist_centre.drop(['index_right'], axis=1)  

    #retirer les doublons
    #dvf_avec_voie_eau = dvf_avec_voie_eau.drop_duplicates(['id_mutation', 'log_prix', 'geometry'])

    return dvf_avec_dist_centre














