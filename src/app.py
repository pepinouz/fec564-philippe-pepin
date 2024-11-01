import numpy as np
import pandas as pd
from scipy.optimize import minimize
import dash
from dash import dcc, html, dash_table
import plotly.graph_objs as go

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
    (max(0, w - 0.1), min(1, w + 0.1)) for w in current_weights[:-1]
] + [(0.0, 0.1)]

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
target_returns = np.linspace(min(expected_returns) * 1.1, max(expected_returns) * 0.9, 50)
portfolios = []

for target_return in target_returns:
    weights = efficient_portfolio(target_return)
    if weights is not None:
        portfolios.append({
            'Rendement': target_return,
            'Risque': portfolio_risk(weights),
            'Poids': weights
        })

# Créer un DataFrame pour le tableau
portfolios_df = pd.DataFrame({
    'Rendement': [p['Rendement'] for p in portfolios],
    'Risque': [p['Risque'] for p in portfolios]
})
weights_df = pd.DataFrame([p['Poids'] for p in portfolios], columns=[
    'Canadian Cash', 'Canadian Universe Bonds', 'Canadian Large Cap',
    'Developed World Equity', 'US REITs', 'Emerging Market Equity', 'Commodities', 'Global Infrastructure'
])
efficient_frontier_df = pd.concat([portfolios_df, weights_df], axis=1)

# Convertir les colonnes 'Rendement' et 'Risque (Volatilité)' en format pourcentage
efficient_frontier_df['Rendement'] = (efficient_frontier_df['Rendement'] * 100).round(2)
efficient_frontier_df['Risque'] = (efficient_frontier_df['Risque'] * 100).round(2)

# Convertir les poids des actifs en format pourcentage
for col in ['Canadian Cash', 'Canadian Universe Bonds', 'Canadian Large Cap',
            'Developed World Equity', 'US REITs', 'Emerging Market Equity', 'Commodities', 'Global Infrastructure']:
    efficient_frontier_df[col] = (efficient_frontier_df[col] * 100).round(2)
    
    
risk_free_rate = 0.02
efficient_frontier_df['Sharpe Ratio'] = (efficient_frontier_df['Rendement'] - risk_free_rate) / efficient_frontier_df['Risque']
optimal_portfolio = efficient_frontier_df.loc[efficient_frontier_df['Sharpe Ratio'].idxmax()]

# Application Dash
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.Div(
        className="card",
        children=[
            html.H3(style={'textAlign': 'center', 'fontFamily': 'Arial', 'color': 'black', 'fontWeight': 'normal'}, children="Philippe Pepin"),
            html.Hr(style={"width": "50%", "border": "1px solid lightgrey"}),
            html.Img(
                src="https://avatars.githubusercontent.com/u/65675136?v=4",  # Remplacer par l'URL de votre image
                style={
                    'width': '100px',
                    'height': '100px',
                    'margin-top': '15px',
                    'border-radius': '50%',
                    'margin-bottom': '15px'
                }
            ),
            html.H4("Project Repository", style={'margin-bottom': '10px'}),
            html.A("Voir sur GitHub", href="https://github.com/pepinouz/fec564-philippe-pepin", target="_blank", 
                   style={'color': 'black', 'text-decoration': 'none'}),

        ],
        style={
            'width': '300px',
            'padding': '15px',
            'margin': '30px auto',
            'text-align': 'center',
            'border': '1px solid lightgrey',
            'color': 'black',
            "fontFamily": "Arial",
            "fontWeight": "normal",
            'backgroundColor': 'white',
            'border-radius': '8px',
            'box-shadow': '0px 4px 8px rgba(0, 0, 0, 0.1)'
        }
    ),

    html.Hr(style={"width": "50%", "border": "1px solid lightgrey"}),
    html.H3(style={'textAlign': 'center', 'fontFamily': 'Arial', 'color': 'slategray', 'fontWeight': 'normal', 'marginTop': '50px'}, children="GESTION DE PORTEFEUILLE FEC 564"),
    html.H1(style={'textAlign': 'center', 'color': 'green', 'fontFamily': 'Arial'}, children="Frontière efficiente du portefeuille"),
    dcc.Graph(
        style={'width': '50%', 'margin': 'auto'},
        id='efficient-frontier',
        figure={
            'data': [
                go.Scatter(
                    x=efficient_frontier_df['Risque'],
                    y=efficient_frontier_df['Rendement'],
                    mode='lines+markers',
                    name='Frontière efficiente',
                    line=dict(color='black')
                )
            ],
            'layout': go.Layout(
                title='Frontière efficiente',
                xaxis={'title': 'Risque'},
                yaxis={'title': 'Rendement'},
                hovermode='closest',
                height=700
            )
        }
    ),
    html.H1(style={'textAlign': 'center', 'color': 'green', 'fontFamily': 'Arial'}, children="Tableau des portefeuilles (en %)"),
    dash_table.DataTable(
        id='portfolio-table',
        columns=[{"name": i, "id": i} for i in efficient_frontier_df.columns],
        data=efficient_frontier_df.to_dict('records'),
        style_table={'overflowX': 'auto', 'width': '70%', 'margin': 'auto'},
        style_cell={'textAlign': 'center'},
        style_header={
            'backgroundColor': 'lightgrey',
            'fontWeight': 'bold'
        },
    ),
    html.Div(
        className="optimal-portfolio-card",
        children=[
            html.H3("Portefeuille optimal (Ratio de Sharpe le plus élevé)", style={'text-align': 'left', "fontFamily": "Arial", "fontWeight": "bold"}),
            html.P(f"Rendement: {optimal_portfolio['Rendement']}%", style={'text-align': 'left', "fontFamily": "Arial", "fontWeight": "normal"}),
            html.P(f"Risque: {optimal_portfolio['Risque']}%", style={'text-align': 'left', "fontFamily": "Arial", "fontWeight": "normal"}),
            html.P(f"Ratio de Sharpe: {optimal_portfolio['Sharpe Ratio']:.2f}", style={'text-align': 'left', "fontFamily": "Arial", "fontWeight": "normal"}),
            html.P("Poids:", style={'text-align': 'left', 'font-weight': 'bold', "fontFamily": "Arial", "fontWeight": "normal"}),
            html.Ul([
                html.Li(f"{col}: {optimal_portfolio[col]}%", style={'text-align': 'left', "fontFamily": "Arial", "fontWeight": "normal"})
                for col in weights_df.columns
            ])
        ],
        style={
            'padding': '15px',
            'width': 'fit-content',
            'margin': '30px auto',
            'background-color': '#f8f9fa',
            'border': '1px solid #dee2e6',
            'border-radius': '8px',
            'box-shadow': '0px 4px 8px rgba(0, 0, 0, 0.1)'
        }
    )
])

# Exposer le serveur
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)