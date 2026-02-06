import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import requests
import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================

# Configuration de l'API
API_BASE_URL = "http://localhost:8000"

# Coordonnées des pays européens (latitude, longitude)
EUROPEAN_COUNTRIES = {
    'France': {'lat': 46.2276, 'lon': 2.2137},
    'Allemagne': {'lat': 51.1657, 'lon': 10.4515},
    'Espagne': {'lat': 40.4637, 'lon': -3.7492},
    'Italie': {'lat': 41.8719, 'lon': 12.5674},
    'Royaume-Uni': {'lat': 55.3781, 'lon': -3.4360},
    'Portugal': {'lat': 39.3999, 'lon': -8.2245},
    'Pays-Bas': {'lat': 52.1326, 'lon': 5.2913},
    'Belgique': {'lat': 50.5039, 'lon': 4.4699},
    'Suisse': {'lat': 46.8182, 'lon': 8.2275},
    'Autriche': {'lat': 47.5162, 'lon': 14.5501},
    'Grèce': {'lat': 39.0742, 'lon': 21.8243},
    'Pologne': {'lat': 51.9194, 'lon': 19.1451},
    'Suède': {'lat': 60.1282, 'lon': 18.6435},
    'Norvège': {'lat': 60.4720, 'lon': 8.4689},
    'Danemark': {'lat': 56.2639, 'lon': 9.5018},
    'Finlande': {'lat': 61.9241, 'lon': 25.7482},
    'Irlande': {'lat': 53.4129, 'lon': -8.2439},
    'Croatie': {'lat': 45.1, 'lon': 15.2},
    'République tchèque': {'lat': 49.8175, 'lon': 15.4730},
    'Hongrie': {'lat': 47.1625, 'lon': 19.5033},
    'Roumanie': {'lat': 45.9432, 'lon': 24.9668},
    'Bulgarie': {'lat': 42.7339, 'lon': 25.4858},
    'Slovaquie': {'lat': 48.6690, 'lon': 19.6990},
    'Slovénie': {'lat': 46.1512, 'lon': 14.9955},
    'Estonie': {'lat': 58.5953, 'lon': 25.0136},
    'Lettonie': {'lat': 56.8796, 'lon': 24.6032},
    'Lituanie': {'lat': 55.1694, 'lon': 23.8813},
    'Luxembourg': {'lat': 49.8153, 'lon': 6.1296},
    'Islande': {'lat': 64.9631, 'lon': -19.0208},
    'Malte': {'lat': 35.9375, 'lon': 14.3754},
    'Chypre': {'lat': 35.1264, 'lon': 33.4299},
    'Albanie': {'lat': 41.1533, 'lon': 20.1683},
    'Andorre': {'lat': 42.5063, 'lon': 1.5218},
    'Monaco': {'lat': 43.7384, 'lon': 7.4246},
    'Vatican': {'lat': 41.9029, 'lon': 12.4534},
}

# Codes ISO des pays pour Plotly
COUNTRY_ISO_CODES = {
    'France': 'FRA', 'Allemagne': 'DEU', 'Espagne': 'ESP', 'Italie': 'ITA',
    'Royaume-Uni': 'GBR', 'Portugal': 'PRT', 'Pays-Bas': 'NLD', 'Belgique': 'BEL',
    'Suisse': 'CHE', 'Autriche': 'AUT', 'Grèce': 'GRC', 'Pologne': 'POL',
    'Suède': 'SWE', 'Norvège': 'NOR', 'Danemark': 'DNK', 'Finlande': 'FIN',
    'Irlande': 'IRL', 'Croatie': 'HRV', 'République tchèque': 'CZE',
    'Hongrie': 'HUN', 'Roumanie': 'ROU', 'Bulgarie': 'BGR', 'Slovaquie': 'SVK',
    'Slovénie': 'SVN', 'Estonie': 'EST', 'Lettonie': 'LVA', 'Lituanie': 'LTU',
    'Luxembourg': 'LUX', 'Islande': 'ISL', 'Malte': 'MLT', 'Chypre': 'CYP',
    'Albanie': 'ALB', 'Andorre': 'AND', 'Monaco': 'MCO', 'Vatican': 'VAT',
}

# ============================================================
# FONCTIONS POUR RÉCUPÉRER LES DONNÉES DE L'API
# ============================================================

def check_api_connection():
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=2)
        return response.status_code == 200
    except Exception as e:
        print("API non accessible:", e)
        return False

def get_all_data():
    try:
        response = requests.get(f"{API_BASE_URL}/data?limit=1000", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print("Erreur de connexion à l'API")
        return None
    except Exception as e:
        print("Erreur:", e)
        return None

def get_stats():
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get('stats', {})
    except Exception as e:
        print("Erreur:", e)
        return None

# ============================================================
# INITIALISATION DE L'APPLICATION DASH
# ============================================================

app = dash.Dash(__name__)
app.title = "Visualisation Voyages Europe"

# Vérification initiale de la connexion
initial_connection = check_api_connection()

# ============================================================
# LAYOUT DE L'APPLICATION
# ============================================================

app.layout = html.Div([
    html.H1("Visualisation des Données de Voyage en Europe", 
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
    
    # Indicateur de connexion API
    html.Div(id='api-status', style={'textAlign': 'center', 'marginBottom': 20}),
    
    # Tabs pour organiser les différentes vues
    dcc.Tabs([
        # Tab 1: Carte des jours totaux par pays
        dcc.Tab(label='🗺️ Jours totaux par pays', children=[
            html.Div([
                html.H3("Nombre total de jours passés dans chaque pays", 
                        style={'textAlign': 'center', 'marginTop': 20}),
                dcc.Graph(id='map-total-days')
            ])
        ]),
        
        # Tab 2: Carte du nombre de visiteurs par pays
        dcc.Tab(label='👥 Nombre de visiteurs par pays', children=[
            html.Div([
                html.H3("Nombre de personnes ayant visité chaque pays", 
                        style={'textAlign': 'center', 'marginTop': 20}),
                dcc.Graph(id='map-visitors')
            ])
        ]),
        
        # Tab 3: Carte des flux de voyages
        dcc.Tab(label='✈️ Flux de voyages', children=[
            html.Div([
                html.H3("Flux de voyages entre pays d'origine et destinations", 
                        style={'textAlign': 'center', 'marginTop': 20}),
                dcc.Graph(id='map-flows')
            ])
        ]),
        
        # Tab 4: Top destinations par pays d'origine
        dcc.Tab(label='🏆 Top destinations', children=[
            html.Div([
                html.H3("Pays les plus visités selon le pays d'origine", 
                        style={'textAlign': 'center', 'marginTop': 20}),
                html.Div([
                    html.Label("Sélectionnez un pays d'origine:", 
                              style={'fontWeight': 'bold', 'marginRight': 10}),
                    dcc.Dropdown(
                        id='country-dropdown',
                        placeholder="Choisir un pays...",
                        style={'width': '300px', 'display': 'inline-block'}
                    )
                ], style={'textAlign': 'center', 'marginBottom': 30}),
                dcc.Graph(id='top-destinations')
            ])
        ]),
        
        # Tab 5: Statistiques
        dcc.Tab(label='📊 Statistiques', children=[
            html.Div([
                html.H3("Statistiques générales", 
                        style={'textAlign': 'center', 'marginTop': 20}),
                html.Div(id='stats-display', style={'padding': '20px'})
            ])
        ])
    ]),
    
    # Interval pour rafraîchir les données
    dcc.Interval(
        id='interval-component',
        interval=30*1000,  # 30 secondes
        n_intervals=0
    )
], style={'fontFamily': 'Arial, sans-serif', 'padding': '20px'})

# ============================================================
# CALLBACKS
# ============================================================

@app.callback(
    Output('api-status', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_api_status(n):
    is_connected = check_api_connection()
    
    if is_connected:
        return html.Div([
            html.Span("🟢 ", style={'fontSize': 20}),
            html.Span("API connectée", style={'color': 'green', 'fontWeight': 'bold'})
        ])
    else:
        return html.Div([
            html.Span("🔴 ", style={'fontSize': 20}),
            html.Span("API non connectée - ", style={'color': 'red', 'fontWeight': 'bold'}),
            html.Span(f"Vérifiez que l'API tourne sur {API_BASE_URL}", style={'color': 'red'}),
            html.Br(),
            html.Span("💡 Lancez: ", style={'fontSize': 12}),
            html.Code("python api_clean.py", style={'backgroundColor': '#f0f0f0', 'padding': '2px 5px', 'fontSize': 12})
        ])

@app.callback(
    Output('map-total-days', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_total_days_map(n):
    data = get_all_data()
    
    if data is None:
        return go.Figure().add_annotation(
            text="API non accessible<br>Lancez l'API avec: python api.py",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color='red')
        )
    
    if not data:
        return go.Figure().add_annotation(
            text="Aucune donnée disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    # Agrégation des données
    df = pd.DataFrame(data)
    country_days = df.groupby('pays_visite')['jours'].sum().reset_index()
    country_days.columns = ['country', 'total_days']
    
    # Ajout des codes ISO
    country_days['iso_code'] = country_days['country'].map(COUNTRY_ISO_CODES)
    
    # Création de la carte choroplèthe
    fig = go.Figure(data=go.Choropleth(
        locations=country_days['iso_code'],
        z=country_days['total_days'],
        text=country_days['country'],
        colorscale='YlOrRd',
        autocolorscale=False,
        reversescale=False,
        marker_line_color='darkgray',
        marker_line_width=0.5,
        colorbar_title="Jours totaux",
    ))
    
    fig.update_geos(
        scope='europe',
        showframe=False,
        showcoastlines=True,
        projection_type='mercator'
    )
    
    fig.update_layout(
        height=600,
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    
    return fig

@app.callback(
    Output('map-visitors', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_visitors_map(n):
    data = get_all_data()
    
    if data is None:
        return go.Figure().add_annotation(
            text="API non accessible<br>Lancez l'API avec: python api.py",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color='red')
        )
    
    if not data:
        return go.Figure().add_annotation(
            text="Aucune donnée disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    # Agrégation des données
    df = pd.DataFrame(data)
    country_visitors = df.groupby('pays_visite')['nom'].nunique().reset_index()
    country_visitors.columns = ['country', 'num_visitors']
    
    # Ajout des codes ISO
    country_visitors['iso_code'] = country_visitors['country'].map(COUNTRY_ISO_CODES)
    
    # Création de la carte choroplèthe
    fig = go.Figure(data=go.Choropleth(
        locations=country_visitors['iso_code'],
        z=country_visitors['num_visitors'],
        text=country_visitors['country'],
        colorscale='Blues',
        autocolorscale=False,
        reversescale=False,
        marker_line_color='darkgray',
        marker_line_width=0.5,
        colorbar_title="Nombre de visiteurs",
    ))
    
    fig.update_geos(
        scope='europe',
        showframe=False,
        showcoastlines=True,
        projection_type='mercator'
    )
    
    fig.update_layout(
        height=600,
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    
    return fig

@app.callback(
    Output('map-flows', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_flows_map(n):
    """Met à jour la carte des flux de voyages"""
    data = get_all_data()
    
    if data is None:
        return go.Figure().add_annotation(
            text="API non accessible<br>Lancez l'API avec: python api.py",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color='red')
        )
    
    if not data:
        return go.Figure().add_annotation(
            text="Aucune donnée disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    df = pd.DataFrame(data)
    
    # Agrégation des flux
    flows = df.groupby(['pays_origine', 'pays_visite']).size().reset_index(name='count')
    
    # Création de la figure
    fig = go.Figure()
    
    # Ajout des pays comme points
    countries_in_data = set(flows['pays_origine'].unique()) | set(flows['pays_visite'].unique())
    for country in countries_in_data:
        if country in EUROPEAN_COUNTRIES:
            coords = EUROPEAN_COUNTRIES[country]
            fig.add_trace(go.Scattergeo(
                lon=[coords['lon']],
                lat=[coords['lat']],
                mode='markers',
                marker=dict(size=8, color='red'),
                name=country,
                text=country,
                hoverinfo='text',
                showlegend=False
            ))
    
    # Ajout des lignes de flux
    for _, row in flows.iterrows():
        origin = row['pays_origine']
        destination = row['pays_visite']
        count = row['count']
        
        if origin in EUROPEAN_COUNTRIES and destination in EUROPEAN_COUNTRIES:
            origin_coords = EUROPEAN_COUNTRIES[origin]
            dest_coords = EUROPEAN_COUNTRIES[destination]
            
            fig.add_trace(go.Scattergeo(
                lon=[origin_coords['lon'], dest_coords['lon']],
                lat=[origin_coords['lat'], dest_coords['lat']],
                mode='lines',
                line=dict(width=min(count * 0.5, 10), color='blue'),
                opacity=0.4,
                hoverinfo='text',
                text=f"{origin} → {destination}: {count} voyages",
                showlegend=False
            ))
    
    fig.update_geos(
        scope='europe',
        showframe=False,
        showcoastlines=True,
        projection_type='mercator'
    )
    
    fig.update_layout(
        height=600,
        margin={"r":0,"t":0,"l":0,"b":0},
        showlegend=False
    )
    
    return fig

@app.callback(
    Output('country-dropdown', 'options'),
    Input('interval-component', 'n_intervals')
)
def update_dropdown_options(n):
    data = get_all_data()
    
    if not data or data is None:
        return []
    
    df = pd.DataFrame(data)
    countries = sorted(df['pays_origine'].unique())
    
    return [{'label': country, 'value': country} for country in countries]

@app.callback(
    Output('top-destinations', 'figure'),
    [Input('country-dropdown', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_top_destinations(selected_country, n):
    data = get_all_data()
    
    if data is None:
        return go.Figure().add_annotation(
            text="API non accessible<br>Lancez l'API avec: python api.py",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color='red')
        )
    
    if not selected_country:
        return go.Figure().add_annotation(
            text="Veuillez sélectionner un pays d'origine",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
    
    if not data:
        return go.Figure().add_annotation(
            text="Aucune donnée disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    df = pd.DataFrame(data)
    
    # Filtrer par pays d'origine
    df_filtered = df[df['pays_origine'] == selected_country]
    
    if df_filtered.empty:
        return go.Figure().add_annotation(
            text=f"Aucune donnée pour {selected_country}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    # Compter les visites par pays
    top_destinations = df_filtered.groupby('pays_visite').size().reset_index(name='visits')
    top_destinations = top_destinations.sort_values('visits', ascending=False).head(10)
    
    # Création du graphique à barres
    fig = go.Figure(data=[
        go.Bar(
            x=top_destinations['pays_visite'],
            y=top_destinations['visits'],
            marker_color='indianred',
            text=top_destinations['visits'],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title=f"Top destinations depuis {selected_country}",
        xaxis_title="Pays visité",
        yaxis_title="Nombre de visites",
        height=500,
        showlegend=False
    )
    
    return fig

@app.callback(
    Output('stats-display', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_stats(n):
    """Met à jour l'affichage des statistiques"""
    stats = get_stats()
    
    if stats is None:
        return html.Div([
            html.Div("API non accessible", 
                    style={'textAlign': 'center', 'fontSize': 18, 'color': 'red', 'marginBottom': 10}),
            html.Div("Lancez l'API avec: python api_clean.py", 
                    style={'textAlign': 'center', 'fontSize': 14})
        ])
    
    if not stats:
        return html.Div("Aucune statistique disponible", 
                       style={'textAlign': 'center', 'fontSize': 18})
    
    # Création de cartes de statistiques
    stats_cards = []
    
    # Pays le plus visité
    if 'pays_plus_visite' in stats:
        stats_cards.append(
            html.Div([
                html.H4("🏆 Pays le plus visité", style={'color': '#3498db'}),
                html.P(f"{stats['pays_plus_visite']['pays']}", 
                      style={'fontSize': 24, 'fontWeight': 'bold'}),
                html.P(f"{stats['pays_plus_visite']['nombre_visites']} visites")
            ], style={
                'border': '2px solid #3498db',
                'borderRadius': '10px',
                'padding': '20px',
                'margin': '10px',
                'display': 'inline-block',
                'width': '30%',
                'textAlign': 'center',
                'verticalAlign': 'top'
            })
        )
    
    # Personne ayant le plus voyagé
    if 'personne_plus_voyage' in stats:
        stats_cards.append(
            html.Div([
                html.H4("✈️ Grand voyageur", style={'color': '#e74c3c'}),
                html.P(f"{stats['personne_plus_voyage']['nom']}", 
                      style={'fontSize': 24, 'fontWeight': 'bold'}),
                html.P(f"{stats['personne_plus_voyage']['nombre_pays']} pays visités")
            ], style={
                'border': '2px solid #e74c3c',
                'borderRadius': '10px',
                'padding': '20px',
                'margin': '10px',
                'display': 'inline-block',
                'width': '30%',
                'textAlign': 'center',
                'verticalAlign': 'top'
            })
        )
    
    # Durée moyenne globale
    if 'duree_moyenne_globale' in stats:
        stats_cards.append(
            html.Div([
                html.H4("📅 Durée moyenne", style={'color': '#2ecc71'}),
                html.P(f"{stats['duree_moyenne_globale']:.1f}", 
                      style={'fontSize': 24, 'fontWeight': 'bold'}),
                html.P("jours par voyage")
            ], style={
                'border': '2px solid #2ecc71',
                'borderRadius': '10px',
                'padding': '20px',
                'margin': '10px',
                'display': 'inline-block',
                'width': '30%',
                'textAlign': 'center',
                'verticalAlign': 'top'
            })
        )
    
    # Nombre total de voyages et de personnes
    if 'nb_voyages' in stats and 'nb_personnes' in stats:
        stats_cards.append(
            html.Div([
                html.Div([
                    html.H4("🌍 Voyages totaux", style={'color': '#9b59b6'}),
                    html.P(f"{stats['nb_voyages']}", 
                          style={'fontSize': 24, 'fontWeight': 'bold'}),
                ], style={'display': 'inline-block', 'width': '45%', 'margin': '10px'}),
                html.Div([
                    html.H4("👥 Voyageurs", style={'color': '#f39c12'}),
                    html.P(f"{stats['nb_personnes']}", 
                          style={'fontSize': 24, 'fontWeight': 'bold'}),
                ], style={'display': 'inline-block', 'width': '45%', 'margin': '10px'}),
            ], style={
                'textAlign': 'center',
                'marginTop': 30
            })
        )
    
    # Tableau des durées moyennes par pays
    if 'duree_moyenne_par_pays' in stats and stats['duree_moyenne_par_pays']:
        table_data = stats['duree_moyenne_par_pays'][:10]  # Top 10
        
        table = html.Div([
            html.H4("Durée moyenne des séjours par pays (Top 10)", 
                   style={'marginTop': 30, 'textAlign': 'center'}),
            html.Table([
                html.Thead(
                    html.Tr([
                        html.Th("Rang", style={'padding': '10px', 'backgroundColor': '#34495e', 'color': 'white'}),
                        html.Th("Pays", style={'padding': '10px', 'backgroundColor': '#34495e', 'color': 'white'}),
                        html.Th("Durée moyenne (jours)", style={'padding': '10px', 'backgroundColor': '#34495e', 'color': 'white'})
                    ])
                ),
                html.Tbody([
                    html.Tr([
                        html.Td(f"#{i+1}", style={'padding': '10px', 'borderBottom': '1px solid #ddd', 'textAlign': 'center'}),
                        html.Td(item['pays'], style={'padding': '10px', 'borderBottom': '1px solid #ddd'}),
                        html.Td(f"{item['duree_moyenne']:.1f}", style={'padding': '10px', 'borderBottom': '1px solid #ddd', 'textAlign': 'center'})
                    ]) for i, item in enumerate(table_data)
                ])
            ], style={'width': '60%', 'margin': '20px auto', 'borderCollapse': 'collapse', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
        ])
        
        stats_cards.append(table)
    
    return html.Div(stats_cards)

# ============================================================
# LANCEMENT DE L'APPLICATION
# ============================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("LANCEMENT DE L'APPLICATION DASH")
    print("="*70)
    
    if initial_connection:
        print("API connectée avec succès!")
        print(f"URL de l'API: {API_BASE_URL}")
    else:
        print("ATTENTION: API non accessible!")
        print(f"Impossible de se connecter à: {API_BASE_URL}")
        print("\nPour démarrer l'API, dans un autre terminal:")
        print("   python api.py")
    
    print("\nApplication Dash disponible sur: http://localhost:8050")
    print("="*70 + "\n")
    
    app.run(debug=True, port=8050)