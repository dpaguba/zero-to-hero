import dash
import dash_core_components as dcc
import dash_html_components as html
# чтобы график мог реагировать на действия
from dash.dependencies import Input, Output

import pandas as pd

import plotly.express as px
# import plotly.io as poi
#
# # вывод результата в браузер
# poi.renderers.default = "browser"

# Считывание и конвертация данных в dataframe
df = pd.read_csv("asterank_exo.csv")

# описываем вид графика
# fig = px.scatter(df, x="RPLANET", y="TPLANET")

# новый график
fig = px.scatter(df, x="TPLANET", y="A")

rplanet_selector = dcc.RangeSlider(
    id="range-slider",
    min=min(df["RPLANET"]),
    max=max(df["RPLANET"]),
    marks={5: "5", 10: "10", 25: "25", 50: "50"},
    step=1,
    value=[5, 50]
)

# инициализация программы
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Hello Dash!"),
    html.Div("Select planet main semi-axis range"),
    html.Div(rplanet_selector, style={"width": "500px", "margin-left": "auto", "margin-right": "auto",
                                      "margin-top": "10px", "margin-bottom": "20px"}),
    html.Div("Planet Temperature ~ Distance to the Star"),
    dcc.Graph(id="graph", figure=fig)
],
    style={"margin-left": "80px",
           "margin-right": "80px",
           "text-align": "center"})

# запуск программы
if __name__ == "__main__":
    app.run_server(debug=True)


# главная полуось планеты, они движуться по элиптической оси и эти данные говорят нам о том насколько далео в среднем
# эта планета находится от своей звезды и мы строим зависимость меджу расстоянием и температурой
# x это температура, а y это расстояние
# задание добавить фильтр на основе радиуса планеты