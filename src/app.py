import numpy as np
import pandas as pd
from scipy.optimize import minimize
import dash
from dash import dcc, html
import plotly.graph_objs as go

# Expected returns, volatilities, and correlation matrix (replace with actual data as needed)
expected_returns = np.array([0.028, 0.048, 0.075, 0.064, 0.069, 0.075, 0.025])
volatilities = np.array([0.0044, 0.0461, 0.1315, 0.1247, 0.1397, 0.1589, 0.1488])
correlation_matrix = np.array([
    [1.00, 0.21, -0.09, -0.11, -0.12, 0.02, 0.00],
    [0.21, 1.00, 0.17, 0.33, 0.37, 0.26, -0.07],
    [-0.09, 0.17, 1.00, 0.64, 0.69, 0.35, 0.13],
    [-0.11, 0.33, 0.64, 1.00, 0.59, 0.54, 0.15],
    [-0.12, 0.37, 0.69, 0.59, 1.00, 0.43, 0.13],
    [0.02, 0.26, 0.35, 0.54, 0.43, 1.00, 0.15],
    [0.00, -0.07, 0.13, 0.15, 0.13, 0.15, 1.00]
])

# Calculate covariance matrix
cov_matrix = np.outer(volatilities, volatilities) * correlation_matrix

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
    bounds = tuple((0, 1) for _ in range(num_assets))
    initial_weights = np.ones(num_assets) / num_assets
    result = minimize(portfolio_risk, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)
    return result.x if result.success else None

# Generate efficient frontier data
target_returns = np.linspace(min(expected_returns), max(expected_returns), 20)
efficient_risks = []
efficient_returns = []

for target_return in target_returns:
    weights = efficient_portfolio(target_return)
    if weights is not None:
        efficient_risks.append(portfolio_risk(weights))
        efficient_returns.append(target_return)

# Set up the Dash app
app = dash.Dash(__name__)

app.layout = html.Div(style={'width': '50%', 'margin': 'auto'}, children=[
    html.H2(style={'textAlign': 'center', 'fontFamily': 'Arial', 'color': 'slategray', 'fontWeight': 'normal'}, children="Philippe Pepin"),
    html.H3(style={'textAlign': 'center', 'fontFamily': 'Arial', 'color': 'slategray', 'fontWeight': 'normal'}, children="GESTION DE PORTEFEUILLE FEC 564"),
    html.Hr(style={"width": "50%", "border": "1px solid lightgrey"}),
    html.H1(style={'textAlign': 'center', 'color': 'green', 'fontFamily': 'Arial'}, children="Frontière efficiente du portefeuille"),
    dcc.Graph(
        id='efficient-frontier',
        figure={
            'data': [
                go.Scatter(
                    x=efficient_risks,
                    y=efficient_returns,
                    mode='lines+markers',
                    name='Frontière efficiente',
                    line=dict(color='black')
                )
            ],
            'layout': go.Layout(
                title='Frontière efficiente',
                xaxis={'title': 'Risque (Volatilité)'},
                yaxis={'title': 'Rendement attendu'},
                hovermode='closest',
                height=700  # Increase the height of the graph to 800 pixels
            )
        }
    )
])

# Expose the server
server = app.server
if __name__ == '__main__':
    app.run_server(debug=True)