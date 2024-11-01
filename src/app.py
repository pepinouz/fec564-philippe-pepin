import numpy as np
import pandas as pd
from scipy.optimize import minimize
import dash
from dash import dcc, html, dash_table
import plotly.graph_objs as go

# Données du portefeuille actuel de la caisse
current_portfolio_return = 0.0585  # Rendement de 4.5%
current_portfolio_risk = 0.0707  # Risque de 4.2%
current_portfolio_weights = [0.05, 0.40, 0.20, 0.25, 0.10, 0.0, 0.0, 0.0]  # Pondérations du portefeuille actuel

# Rendements attendus, volatilités et matrice de corrélation
expected_returns = np.array([0.028, 0.048, 0.075, 0.064, 0.069, 0.075, 0.025, 0.062]) 
volatilities = np.array([0.0044, 0.0461, 0.1315, 0.1247, 0.1397, 0.1589, 0.1488, 0.1012]) 
correlation_matrix = np.array([
    [1.00, 0.21, -0.09, -0.11, -0.12, 0.02, 0.00, 0.10],
    [0.21, 1.00, 0.17, 0.33, 0.37, 0.26, -0.07, 0.15],
    [-0.09, 0.17, 1.00, 0.64, 0.69, 0.35, 0.13, 0.20],
    [-0.11, 0.33, 0.64, 1.00, 0.59, 0.54, 0.15, 0.25],
    [-0.12, 0.37, 0.69, 0.59, 1.00, 0.43, 0.13, 0.30],
    [0.02, 0.26, 0.35, 0.54, 0.43, 1.00, 0.15, 0.18],
    [0.00, -0.07, 0.13, 0.15, 0.13, 0.15, 1.00, 0.08],
    [0.10, 0.15, 0.20, 0.25, 0.30, 0.18, 0.08, 1.00]
])

# Calculer la matrice de covariance à partir des volatilités et de la matrice de corrélation
cov_matrix = np.outer(volatilities, volatilities) * correlation_matrix

# Définir les poids actuels et les limites basées sur la règle de ±10%
current_weights = np.array([0.05, 0.40, 0.20, 0.25, 0.10, 0.0, 0.0, 0.0])  # Exemple de poids actuels
bounds = [
    (0.05, 0.2),    # Canadian Cash
    (0.23, 0.43),   # Canadian Universe Bonds
    (0.10, 0.30),   # Canadian Large Cap
    (0.15, 0.35),   # Developed World Equity
    (0.05, 0.18),   # US REITs
    (0.05, 0.12),   # Emerging Market Equity
    (0.05, 0.12),   # Commodities
    (0.05, 0.1)     # U.S. Core Real Estate
]

def portfolio_return(weights):
    return np.dot(weights, expected_returns)

def portfolio_risk(weights):
    return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

def efficient_portfolio(target_return):
    num_assets = len(expected_returns)
    constraints = (
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
        {'type': 'eq', 'fun': lambda x: portfolio_return(x) - target_return}
    )
    initial_weights = current_weights  # Commencer avec l'allocation actuelle comme estimation initiale
    result = minimize(portfolio_risk, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)
    return result.x if result.success else None

# Générer les données de la frontière efficiente avec 20 portefeuilles
target_returns = np.linspace(min(expected_returns) * 1.1, max(expected_returns) * 0.9, 70)
portfolios = []

for i, target_return in enumerate(target_returns, 1):
    weights = efficient_portfolio(target_return)
    if weights is not None:
        portfolios.append({
            'Titre': f'Portefeuille   {i - 38}',
            'Rendement': target_return,
            'Risque (Volatilité)': portfolio_risk(weights),
            'Poids': weights
        })

# Créer un DataFrame pour le tableau
portfolios_df = pd.DataFrame({
    'Titre': [p['Titre'] for p in portfolios],
    # 'Poids': [p['Poids'] for p in portfolios],
    'Rendement': [p['Rendement'] for p in portfolios],
    'Risque (Volatilité)': [p['Risque (Volatilité)'] for p in portfolios]
    
})
weights_df = pd.DataFrame([p['Poids'] for p in portfolios], columns=[
    'Canadian Cash', 'Canadian Universe Bonds', 'Canadian Large Cap',
    'Developed World Equity', 'US REITs', 'Emerging Market Equity', 'Commodities', 'U.S. Core Real Estate'
])
efficient_frontier_df = pd.concat([portfolios_df, weights_df], axis=1)

# Convertir les colonnes 'Rendement' et 'Risque (Volatilité)' en format pourcentage
efficient_frontier_df['Rendement'] = (efficient_frontier_df['Rendement'] * 100).round(2)
efficient_frontier_df['Risque (Volatilité)'] = (efficient_frontier_df['Risque (Volatilité)'] * 100).round(2)

# Convertir les poids des actifs en format pourcentage
for col in ['Canadian Cash', 'Canadian Universe Bonds', 'Canadian Large Cap',
            'Developed World Equity', 'US REITs', 'Emerging Market Equity', 'Commodities', 'U.S. Core Real Estate']:
    efficient_frontier_df[col] = (efficient_frontier_df[col] * 100).round(2)
    
# Ajouter le portefeuille actuel au DataFrame
current_portfolio_data = {
    'Titre': 'Portefeuille actuel',
    'Rendement': current_portfolio_return,
    'Risque (Volatilité)': current_portfolio_risk,
    **{col: weight for col, weight in zip(weights_df.columns, current_portfolio_weights)}
}

# Convertir le dictionnaire de données du portefeuille actuel en DataFrame
current_portfolio_data['Rendement'] = round(current_portfolio_data['Rendement'] * 100, 2)
current_portfolio_data['Risque (Volatilité)'] = round(current_portfolio_data['Risque (Volatilité)'] * 100, 2)
current_portfolio_df = pd.DataFrame([current_portfolio_data])

risk_free_rate = 0.028
efficient_frontier_df['Ratio de Sharpe'] = (efficient_frontier_df['Rendement'] - risk_free_rate) / efficient_frontier_df['Risque (Volatilité)']

# Sélection du portefeuille 17 dans le DataFrame efficient_frontier_df
portfolio_17 = efficient_frontier_df.iloc[16]

# Formater le DataFrame pour inclure les pourcentages dans toutes les colonnes sauf la première et la dernière
for col in efficient_frontier_df.columns[1:-1]:
    efficient_frontier_df[col] = efficient_frontier_df[col].apply(lambda x: f"{x} %")
    
# Limiter le ratio de Sharpe à trois décimales
efficient_frontier_df['Ratio de Sharpe'] = efficient_frontier_df['Ratio de Sharpe'].apply(lambda x: f"{x:.3f}")


# Extraction des poids pour le portefeuille 17 (index 16 pour le 17e portefeuille)
portfolio_17_weights = efficient_frontier_df.iloc[16][['Canadian Cash', 'Canadian Universe Bonds', 'Canadian Large Cap',
                                                       'Developed World Equity', 'US REITs', 'Emerging Market Equity', 
                                                       'Commodities', 'U.S. Core Real Estate']].apply(lambda x: float(str(x).replace('%', '')))

# Création du graphique en camembert (Pie chart) pour le portefeuille 17
portfolio_17_pie_chart = dcc.Graph(
    id='portfolio-17-pie-chart',
    figure={
        'data': [
            go.Pie(
                labels=portfolio_17_weights.index,
                values=portfolio_17_weights.values,
                hole=.3  # Donut-style chart; remove if you prefer a classic pie chart
            )
        ],
        'layout': go.Layout(
            title='Répartition des Actifs - Portefeuille 17'
        )
    }
)

# Application Dash
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.Div(
        children=[
            html.Img(
                src="https://www.destinationuniversites.ca/wp-content/uploads/UdeS_logo_rgbHR.png",
                style={
                    'width': '300px',
                    'height': '100px',
                'margin': 'auto'
                }
            ),
        ],
        style={'width': '300px', 'margin': 'auto'}
    ),
    html.H3(style={'textAlign': 'center', 'fontFamily': 'Arial', 'color': 'black', 'fontWeight': 'normal', 'marginTop': '50px'}, children="GESTION DE PORTEFEUILLE FEC 564"),
    html.H1(style={'textAlign': 'center', 'color': 'green', 'fontFamily': 'Arial'}, children="Frontière efficiente du portefeuille"),
    html.Hr(style={"width": "30%", "border": "1px solid lightgrey"}),
    dcc.Graph(
        style={'width': '50%', 'margin': 'auto'},
        id='efficient-frontier',
        figure={
            'data': [
                go.Scatter(
                    x=efficient_frontier_df['Risque (Volatilité)'],
                    y=efficient_frontier_df['Rendement'],
                    mode='lines+markers',
                    name='Frontière efficiente',
                    line=dict(color='black')
                ),
                go.Scatter(
                    x=[current_portfolio_risk * 100],
                    y=[current_portfolio_return * 100],
                    mode='markers',
                    marker=dict(color='red', size=10, symbol='diamond'),
                    name='Portefeuille actuel'
                )
            ],
            'layout': go.Layout(
                title='Frontière efficiente',
                xaxis={'title': 'Risque (Volatilité)'},
                yaxis={'title': 'Rendement'},
                hovermode='closest',
                height=700
            )
        }
    ),
    html.H1(style={'textAlign': 'center', 'fontFamily': 'Arial','marginTop': '80px', 'marginBottom': '30px'}, children="Tableau des portefeuilles (en %)"),
    html.P(style={'textAlign': 'center', 'fontFamily': 'Arial', 'margin-bottom': '30px', 'color': 'darkslategray', 'max-width': '600px', 'margin': 'auto'}, children="Voici les rendements et les risques des portefeuilles de la frontière efficiente, ainsi que leur composition. Les pourcentages sont arrondis à la deuxième décimale."),
    dash_table.DataTable(
        id='portfolio-table',
        columns=[{"name": i, "id": i} for i in current_portfolio_df.columns],
        data=current_portfolio_df.to_dict('records'),
        style_table={'overflowX': 'auto', 'width': '70%', 'margin': 'auto', 'margin-bottom': '60px', 'margin-top': '50px'},
        style_cell={'textAlign': 'center', 'padding': '15px', 'border-right': 'none', 'border-left': 'none'},
        style_header={
            'backgroundColor': '#f8f9fa',
            'border': '1px solid grey',
            'border-right': 'none',
            'border-left': 'none',
            'border-top': 'none',
            'padding': '20px',
            'fontWeight': 'bold',
            'fontFamily': 'Arial'
        },
        style_data_conditional=[
            {
                'if': {'column_id': 'Titre'},
                'border-right': '1px solid lightgrey',
                'fontWeight': 'bold'
            }
        ]
    ),
    dash_table.DataTable(
        id='portfolio-table',
        columns=[{"name": i, "id": i} for i in efficient_frontier_df.columns],
        data=efficient_frontier_df.to_dict('records'),
        style_table={'overflowX': 'auto', 'width': '70%', 'margin': 'auto'},
        style_cell={'textAlign': 'center', 'padding': '15px', 'border-right': 'none', 'border-left': 'none'},
        style_header={
            'backgroundColor': '#f8f9fa',
            'border': '1px solid grey',
            'border-right': 'none',
            'border-left': 'none',
            'border-top': 'none',
            'padding': '20px',
            'fontWeight': 'bold',
            'fontFamily': 'Arial'
        },
        style_data_conditional=[
            {
                'if': {'column_id': efficient_frontier_df.columns[0]},  # First column
                'paddingRight': '42px',
                'fontWeight': 'bold',
                'border-right': '1px solid lightgrey'
        },
        {
            'if': {'filter_query': '{Titre} = "Portefeuille   17"'},
            'backgroundColor': '#f0f1f2',
            'color': 'black',
            'fontWeight': 'bold'
        }
    ]
    ),
    html.Div(style={'display': 'flex', 'flex-direction': 'row', 'gap': '0px', 'align-items': 'center', 'justify-content': 'center', 'padding-top': '60px'}, children=[
        html.Div(   
            className="optimal-portfolio-card",
            children=[
                html.Div(
                    style={'display': 'flex', 'flex-direction': 'row', 'gap': '10px', 'align-items': 'center'},
                    children=[
                        html.Img(
                            src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTa3cRTInobdxdEveQUrQtJ28uKgEdFrJEQCw&s",
                            style={
                                'width': '40px',
                                'height': '40px',
                                'border-radius': '50%',
                                'border': '1px solid green'
                            }
                        ),
                        html.H2("Portefeuille optimal :", style={'text-align': 'left', "fontFamily": "Arial", "fontWeight": "bold"}),
                        html.H2("Portefeuille 17", style={'text-align': 'left', "fontFamily": "Arial", "fontWeight": "bold", 'color': 'green'})
                    ]
                ),  
                html.Hr(style={"width": "100%", "border": "1px solid lightgrey"}),
                html.Div(   
                    style={'display': 'flex', 'flex-direction': 'row', 'gap': '10px', 'justify-content': 'space-between', 'padding-top': '30px'},
                    children=[
                        html.Div(
                            style={'display': 'flex', 'flex-direction': 'column', 'gap': '5px', 'border-right': '1px solid lightgrey', 'padding-right': '30px'},
                            children=[
                                html.Div(   
                                    style={'display': 'flex', 'flex-direction': 'row', 'gap': '5px'},
                                    children=[
                                        html.P("Rendement:", style={'text-align': 'left', "fontFamily": "Arial", "fontWeight": "bold", 'font-size': '20px'}),
                                        html.P(f"{portfolio_17['Rendement']}%", style={'text-align': 'left', "fontFamily": "Arial", "fontWeight": "normal", 'font-size': '20px', 'color': 'darkslategray'}),
                                    ]
                                ),  
                                html.Div(
                                    style={'display': 'flex', 'flex-direction': 'row', 'gap': '5px'},
                                    children=[
                                        html.P("Risque:", style={'text-align': 'left', "fontFamily": "Arial", "fontWeight": "bold", 'font-size': '20px'}),
                                        html.P(f"{portfolio_17['Risque (Volatilité)']}%", style={'text-align': 'left', "fontFamily": "Arial", "fontWeight": "normal", 'font-size': '20px', 'color': 'darkslategray'}),
                                    ]
                                ),
                                html.Div(
                                    style={'display': 'flex', 'flex-direction': 'row', 'gap': '5px'},
                                    children=[
                                        html.P("Ratio de Sharpe:", style={'text-align': 'left', "fontFamily": "Arial", "fontWeight": "bold", 'font-size': '20px'}),
                                        html.P(f"{portfolio_17['Ratio de Sharpe']:.2f}", style={'text-align': 'left', "fontFamily": "Arial", "fontWeight": "normal", 'font-size': '20px', 'color': 'darkslategray'}),
                                    ]
                                )
                            ]
                        ),
                        html.Div(   
                            style={'display': 'flex', 'flex-direction': 'column', 'padding-left': '30px'},
                            children=[
                                html.P("Composition:", style={'text-align': 'left', "fontFamily": "Arial", "fontWeight": "bold", 'font-size': '20px'}),
                                html.Ul([
                                    html.Li(f"{col}: {portfolio_17[col]}%", style={'text-align': 'left', "fontFamily": "Arial", "fontWeight": "normal", 'margin-bottom': '10px', 'font-size': '18px', 'color': 'darkslategray'})
                                    for col in weights_df.columns
                                ])
                            ]
                        )
                    ],
                ),
            ],
            style={ 
                'padding': '30px',
                'width': 'fit-content',
                'background-color': 'white',
                'border': '1px solid #dee2e6',
                'border-radius': '8px',
            }
        ),
        html.Div(
            children=[
                portfolio_17_pie_chart
    ],
            style={'width': '40%',}
        )
    ]),
    html.Div(
        className="card",
        children=[
            html.H3(style={'textAlign': 'center', 'fontFamily': 'Arial', 'color': 'black', 'fontWeight': 'bold'}, children="Philippe Pepin"),
            html.H4("Project Repository", style={'margin-bottom': '30px', 'fontFamily': 'Arial', 'color': 'black', 'fontWeight': 'normal'}),
            html.A("Voir sur GitHub", href="https://github.com/pepinouz/fec564-philippe-pepin", target="_blank", 
                   style={'color': 'black', 'text-decoration': 'none', 'border': '1px solid lightgrey', 'padding': '10px', 'border-radius': '5px'}),
            html.Div(style={'margin-top': '30px'}),
            html.Hr(style={"width": "50%", "border": "1px solid lightgrey"}),
            html.Img(
                src="https://avatars.githubusercontent.com/u/65675136?v=4",
                style={
                    'width': '100px',
                    'height': '100px',
                    'border-radius': '50%',
                    'margin-top': '15px',
                    'border': '1px solid black'
                }
            ),

        ],
        style={
            'width': '300px',
            'padding': '30px',
            'margin': '30px auto',
            'text-align': 'center',
            # 'border': '1px solid lightgrey',
            'color': 'black',
            "fontFamily": "Arial",
            "fontWeight": "normal",
            'backgroundColor': 'white',
            'border-radius': '8px',
        }
    ),
])

# Exposer le serveur
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)