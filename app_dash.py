import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import requests
import plotly.graph_objs as go

app = dash.Dash(__name__)

introduction = html.Div([
    html.H1('Bienvenido a la Predicción de Cantidad'),
    html.P('Esta aplicación utiliza un modelo de machine learning entrenado para predecir la cantidad '
           'en función de varios factores como el departamento, el mes, el año, la población y la pobreza monetaria.'),
    html.P('Ingrese los valores correspondientes a cada factor en los campos a continuación y haga clic en "Predecir" '
           'para ver la predicción.'),
    html.P('Los datos ingresados se enviarán al servidor Flask, donde se realizará la predicción utilizando el modelo '
           'entrenado. La predicción se mostrará en la sección de resultados, junto con los valores ingresados.'),
    html.P('Además, se mostrarán gráficas que representan la relación entre las variables y la predicción.')
])

app.layout = html.Div([
    introduction,
    html.Hr(),  # Línea divisoria
    html.H2('Predicción de Cantidad'),
    dcc.Input(id='departamento', type='number', placeholder='Departamento'),
    dcc.Input(id='cai_departamentos', type='number', placeholder='CAI Departamentos'),
    dcc.Input(id='mes', type='number', placeholder='Mes', min=1, max=12),
    dcc.Input(id='ano', type='number', placeholder='Año', min=2000, max=2100),
    dcc.Input(id='poblacion', type='number', placeholder='Población'),
    dcc.Input(id='pobreza_monetaria', type='number', placeholder='Pobreza Monetaria', min=0, max=100, step=1),
    html.Button('Predecir', id='submit-val', n_clicks=0),
    dcc.ConfirmDialog(
        id='prediction-dialog',
        message='',
    ),
    html.Button('Continuar', id='continue-button', n_clicks=0, style={'display': 'none'}),
    html.Div(id='prediction-output', style={'display': 'none'}),
    html.Div([
        dcc.Graph(id='scatter-graph'),
        dcc.Graph(id='line-graph')
    ])
])

@app.callback(
    Output('prediction-dialog', 'message'),
    Output('prediction-dialog', 'displayed'),
    [Input('submit-val', 'n_clicks')],
    [State('departamento', 'value'),
     State('cai_departamentos', 'value'),
     State('mes', 'value'),
     State('ano', 'value'),
     State('poblacion', 'value'),
     State('pobreza_monetaria', 'value')]
)
def show_prediction_dialog(n_clicks, departamento, cai_departamentos, mes, ano, poblacion, pobreza_monetaria):
    if n_clicks > 0:
        data = {
            'Departamento': departamento,
            'CAI_Departamentos': cai_departamentos,
            'Mes': mes,
            'Ano': ano,
            'Poblacion': poblacion,
            'Pobreza_Monetaria': pobreza_monetaria
        }
        response = requests.post('http://127.0.0.1:5000/api/prediction', json=data)
        if response.status_code == 200:
            prediction = response.json()['prediction']
            return f'Predicción: {prediction}', True
        else:
            return 'Error al realizar la predicción', True
    return '', False

@app.callback(
    Output('prediction-output', 'children'),
    Output('prediction-output', 'style'),
    Output('continue-button', 'style'),
    [Input('continue-button', 'n_clicks')],
    [State('departamento', 'value'),
     State('cai_departamentos', 'value'),
     State('mes', 'value'),
     State('ano', 'value'),
     State('poblacion', 'value'),
     State('pobreza_monetaria', 'value')]
)
def show_full_prediction(n_clicks, departamento, cai_departamentos, mes, ano, poblacion, pobreza_monetaria):
    if n_clicks > 0:
        data = {
            'Departamento': departamento,
            'CAI_Departamentos': cai_departamentos,
            'Mes': mes,
            'Ano': ano,
            'Poblacion': poblacion,
            'Pobreza_Monetaria': pobreza_monetaria
        }
        response = requests.post('http://127.0.0.1:5000/api/prediction', json=data)
        if response.status_code == 200:
            prediction = response.json()['prediction']
            return html.Div([
                html.H3('Resultado de la Predicción'),
                html.P(f'Predicción: {prediction}'),
                html.P(f'Departamento: {departamento}'),
                html.P(f'CAI Departamentos: {cai_departamentos}'),
                html.P(f'Mes: {mes}'),
                html.P(f'Año: {ano}'),
                html.P(f'Población: {poblacion}'),
                html.P(f'Pobreza Monetaria: {pobreza_monetaria}')
            ]), {'display': 'block'}, {'display': 'none'}
        else:
            return 'Error al realizar la predicción', {'display': 'block'}, {'display': 'none'}
    return '', {'display': 'none'}, {'display': 'block'}

@app.callback(
    [Output('scatter-graph', 'figure'), Output('line-graph', 'figure')],
    [Input('submit-val', 'n_clicks')],
    [State('departamento', 'value'),
     State('cai_departamentos', 'value'),
     State('mes', 'value'),
     State('ano', 'value'),
     State('poblacion', 'value'),
     State('pobreza_monetaria', 'value')]
)
def update_graphs(n_clicks, departamento, cai_departamentos, mes, ano, poblacion, pobreza_monetaria):
    if n_clicks > 0:
        # Hacer una solicitud HTTP al servidor Flask para obtener los datos para los gráficos
        response = requests.get('http://127.0.0.1:5000/api/data')
        if response.status_code == 200:
            data = response.json()
            categories = data['categories']
            values = data['values']
            
            # Crear gráfico de dispersión
            scatter_trace = go.Scatter(
                x=categories,
                y=values,
                mode='markers',
                marker=dict(color='blue'),
                name='Dispersión'
            )
            scatter_layout = go.Layout(
                title='Valor promedio (Gráfico de dispersión)',
                xaxis=dict(title='Variable'),
                yaxis=dict(title='Valor Promedio')
            )
            scatter_fig = go.Figure(data=[scatter_trace], layout=scatter_layout)
            
            # Crear gráfico de líneas
            line_trace = go.Scatter(
                x=categories,
                y=values,
                mode='lines',
                marker=dict(color='red'),
                name='Línea'
            )
            line_layout = go.Layout(
                title='Valor promedio (Gráfico de Líneas)',
                xaxis=dict(title='Variable'),
                yaxis=dict(title='Valor Promedio')
            )
            line_fig = go.Figure(data=[line_trace], layout=line_layout)
            
            return scatter_fig, line_fig

    return {'data': [], 'layout': {}}, {'data': [], 'layout': {}}

if __name__ == '__main__':
    app.run_server(debug=True)
