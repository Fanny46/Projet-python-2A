"""Librairies nécessaires"""
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go


"""Changement de directory pour lire les fichiers"""
import os
os.getcwd() #trouver le directory actuel 
os.chdir('/home/onyxia/work/Projet-python-2A')


"""Données administratives géographiques de paris intra muros"""

paris_arrondissement = gpd.read_file('2) Visualisation/Données_carto/paris_arrondissements.geojson')
paris_quartiers = gpd.read_file('2) Visualisation/Données_carto/paris_quartiers.geojson')
paris_quartiers = paris_quartiers[['c_quinsee', 'l_qu', 'geometry']]


def evolution_prix_mensuel(dvf):
    #dvf : dataframe avec une colonne date_mutation et prix
    import geopandas as gpd
    #ne garder que les colonnes utiles
    dvf = dvf.loc[:,['prix', 'date_mutation']]
    
    # Création d'une colonne au format datetime
    dvf['date_time'] = pd.to_datetime(dvf['date_mutation'])
    
    # Conversion de la colonne 'date_time' en format de période mensuelle
    dvf['mois'] = dvf['date_time'].dt.to_period('M')
    
    # Grouper par mois et calculer la moyenne des prix
    dvf_grouped = dvf.groupby('mois')['prix'].mean().reset_index()
    
    # Tracer l'évolution mensuelle des prix avec Plotly Express
    fig = px.line(dvf_grouped, x='mois', y='prix', markers=True, line_shape='linear', labels={'prix': 'Prix moyen (€)'}, title='Évolution mensuelle du prix moyen des appartements vendus à Paris depuis 2018')
    
     # Ajouter une ligne rouge représentant la moyenne sur toute la période
    fig.add_trace(go.Scatter(x=dvf_grouped['mois'], y=[moyenne_totale] * len(dvf_grouped),
                             mode='lines', line=dict(dash='dash', color='red'), name='Moyenne totale'))

    # Configurer l'affichage des étiquettes de l'axe 'mois'
    fig.update_xaxes(tickangle=45, tickmode='array', tickvals=['2018-07','2019-01','2019-07','2020-01','2020-07','2021-01','2021-07','2022-01','2022-07','2023-01','2023-07'],ticktext=['2018-07','2019-01','2019-07','2020-01','2020-07','2021-01','2021-07','2022-01','2022-07','2023-01','2023-07'])

    # Configurer l'affichage des valeurs au survol de la souris
    fig.update_traces(hovertemplate='%{y:.2f}', hoverinfo='y+name')

    # Afficher le graphique interactif
    fig.show()


def evolution_nombre(dvf, freq):
    #dvf : dataframe avec une colonne date_mutation et prix
    # freq = "Année" ou "Mois"
    
    #ne garder que les colonnes utiles
    dvf = dvf.loc[:,['date_mutation']]
    
    #on met à jour la periode
    period = ''
    if freq == "Année":
        period = "Y"
    elif freq == "Mois":
        period = "M"

    #fréquence qui apparaîtra dans le titre du graphique 
    freq_titre = ''
    if freq == "Année":
        freq_titre = "annuelle"
    elif freq == "Mois":
        freq_titre = "mensuelle"

    #création d'une colonne au format date_time
    dvf['date_time'] = pd.to_datetime(dvf['date_mutation'])

    # Convertir la colonne 'date_time' en format de périodes mensuelles ou annuelles
    dvf[freq] = dvf['date_time'].dt.to_period(period)
    
    # Grouper par mois et calculer la moyenne des prix
    dvf_grouped = dvf.groupby(freq).size().reset_index(name='nombre de ventes')

    # Convertir en str
    dvf_grouped[freq] = dvf_grouped[freq].astype(str)

    # Calculer la moyenne sur toute la période
    moyenne = dvf_grouped['nombre de ventes'].mean()

    # Tracer l'évolution mensuelle des prix avec Plotly Express
    fig = px.line(dvf_grouped, x=freq, y='nombre de ventes', markers=True, line_shape='linear', labels={'nombre de ventes'},
              title=f"Évolution {freq_titre} du nombre de ventes d'appartements à Paris depuis 2018")
    
     # Ajouter une ligne rouge représentant la moyenne sur toute la période
    fig.add_trace(go.Scatter(x=dvf_grouped[freq], y=[moyenne] * len(dvf_grouped),
                             mode='lines', line=dict(dash='dash', color='red'), name='Moyenne'))

    # Configurer l'affichage des étiquettes de l'axe 'mois'
    if freq=="Mois" :
        fig.update_xaxes(tickangle=45, tickmode='array', tickvals=['2018-07','2019-01','2019-07','2020-01','2020-07','2021-01','2021-07','2022-01','2022-07','2023-01','2023-07'],ticktext=['2018-07','2019-01','2019-07','2020-01','2020-07','2021-01','2021-07','2022-01','2022-07','2023-01','2023-07'])
    else : pass

    # Configurer l'affichage des valeurs au survol de la souris
    fig.update_traces(hovertemplate='%{y:.0f}', hoverinfo='y+name')

    # Afficher le graphique interactif
    fig.show()



def carte_prix_moyen_arrodissement(dvf):
    #dvf : geodataframe avec une colonne 'geometry'

    #on ne garde que les colonnes prix au m^2 et geometry
    dvf = dvf[['prix_au_m2_carrez', 'prix_au_m2_reel_bati', 'geometry']]  

    #on ajoute à chaque appartement les données administratives de son arrondissement
    dvf_geo = gpd.sjoin(dvf, paris_arrondissement, predicate = 'within')

    #regroupement selon les arrondissements et prix moyen au m2 carrez
    dvf_geo_group_carrez = (dvf_geo
      .groupby("INSEE_COG")
      .agg({"prix_au_m2_carrez": "mean"})
      .reset_index())

    #regroupement selon les arrondissements et prix moyen au m2 réel
    dvf_geo_group_reel = (dvf_geo
      .groupby("INSEE_COG")
      .agg({"prix_au_m2_reel_bati": "mean"})
      .reset_index())

    #on ajoute aux données administratives les prix moyens
    paris_arrondissement_count_carrez = paris_arrondissement.merge(
        dvf_geo_group_carrez
    ).to_crs(2154)

    paris_arrondissement_count_reel = paris_arrondissement.merge(
        dvf_geo_group_reel
    ).to_crs(2154)

    # Créer la première carte du prix du m^2 carrez
    fig1 = px.choropleth_mapbox(
        paris_arrondissement_count_carrez,
        geojson=paris_arrondissement.geometry,
        locations=paris_arrondissement.index,
        color="prix_au_m2_carrez",
        color_continuous_scale="ylorbr",
        mapbox_style="carto-positron",
        center={"lat": 48.8566, "lon": 2.3522},
        zoom=10.5,
        opacity=1,
        title="Prix moyen du m² carrez par arrondissement (en €)",
        height=400,
        custom_data=[paris_arrondissement.NOM, paris_arrondissement_count_carrez['prix_au_m2_carrez']]  # Ajoutez les données personnalisées ici
    )

    # Créer la deuxième carte du prix du m^2 réel
    fig2 = px.choropleth_mapbox(
        paris_arrondissement_count_reel,
        geojson=paris_arrondissement.geometry,
        locations=paris_arrondissement.index,
        color="prix_au_m2_reel_bati",
        color_continuous_scale="ylorbr",
        mapbox_style="carto-positron",
        center={"lat": 48.8566, "lon": 2.3522},
        zoom=10.5,
        opacity=1,
        title="Prix moyen du m² réel par arrondissement (en €)",
        height=400,
        custom_data=[paris_arrondissement.NOM, paris_arrondissement_count_reel['prix_au_m2_reel_bati']]  # Ajoutez les données personnalisées ici
      )

    # Ajouter les étiquettes personnalisées pour le survol
    fig1.update_traces(hovertemplate="%{customdata[0]}<br>Prix moyen du m² : %{customdata[1]:.0f}")
    fig2.update_traces(hovertemplate="%{customdata[0]}<br>Prix moyen du m² : %{customdata[1]:.0f}")
    
    # Ajuster les marges
    fig1.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
    fig2.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})

    # Afficher les cartes interactives
    fig1.show()
    fig2.show()


def carte_prix_moyen_quartier(dvf):
    
    #dvf : geodataframe avec une colonne 'geometry'

    #on ne garde que les colonnes prix au m^2 et geometry
    dvf = dvf[['prix_au_m2_carrez', 'prix_au_m2_reel_bati', 'geometry']]

    #on ajoute à chaque appartement les données administratives de son arrondissement
    dvf_geo = gpd.sjoin(dvf, paris_quartiers, predicate = 'within')

    #regroupement selon les arrondissements et prix moyen au m2 carrez
    dvf_geo_group_carrez = (dvf_geo
      .groupby("l_qu")
      .agg({"prix_au_m2_carrez": "mean"})
      .reset_index())

    #regroupement selon les arrondissements et prix moyen au m2 réel
    dvf_geo_group_reel = (dvf_geo
      .groupby("l_qu")
      .agg({"prix_au_m2_reel_bati": "mean"})
      .reset_index())

    #on ajoute aux données administratives les prix moyens
    paris_quartiers_count_carrez = paris_quartiers.merge(
        dvf_geo_group_carrez
    ).to_crs(2154)

    paris_quartiers_count_reel = paris_quartiers.merge(
        dvf_geo_group_reel
    ).to_crs(2154)

    # Créer la première carte du prix du m^2 carrez
    fig1 = px.choropleth_mapbox(
        paris_quartiers_count_carrez,
        geojson=paris_quartiers.geometry,
        locations=paris_quartiers.index,
        color="prix_au_m2_carrez",
        color_continuous_scale="ylorbr",
        mapbox_style="carto-positron",
        center={"lat": 48.8566, "lon": 2.3522},
        zoom=10.5,
        opacity=1,
        title="Prix moyen du m² carrez par quartier (en €)",
        height=400,
        custom_data=[paris_quartiers.l_qu, paris_quartiers_count_carrez['prix_au_m2_carrez']]  # Ajoutez les données personnalisées ici
    )

    # Créer la deuxième carte du prix du m^2 réel
    fig2 = px.choropleth_mapbox(
        paris_quartiers_count_reel,
        geojson=paris_quartiers.geometry,
        locations=paris_quartiers.index,
        color="prix_au_m2_reel_bati",
        color_continuous_scale="ylorbr",
        mapbox_style="carto-positron",
        center={"lat": 48.8566, "lon": 2.3522},
        zoom=10.5,
        opacity=1,
        title="Prix moyen du m² réel par quartier (en €)",
        height=400,
        custom_data=[paris_quartiers.l_qu, paris_quartiers_count_reel['prix_au_m2_reel_bati']]  # Ajoutez les données personnalisées ici
      )

    # Ajouter les étiquettes personnalisées pour le survol
    fig1.update_traces(hovertemplate="%{customdata[0]}<br>Prix moyen du m² : %{customdata[1]:.0f}")
    fig2.update_traces(hovertemplate="%{customdata[0]}<br>Prix moyen du m² : %{customdata[1]:.0f}")
    
    # Ajuster les marges
    fig1.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
    fig2.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})

    # Afficher les cartes interactives
    fig1.show()
    fig2.show()