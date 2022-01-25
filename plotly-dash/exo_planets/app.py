import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd

import plotly.express as px
import plotly.io as poi

# вывод результата в браузер
poi.renderers.default = "browser"

# Считывание и конвертация данных в dataframe
df = pd.read_csv("asterank_exo.csv")

# описываем вид графика
fig = px.scatter(df, x="RPLANET", y="TPLANET")

# инициализация программы
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Hello Dash!"),
    html.Div("Exoplanets chart"),
    dcc.Graph(figure=fig)
])

# запуск программы
if __name__ == "__main__":
    app.run_server(debug=True)
