import dash
import dash_core_components as dcc
import dash_html_components as html

# чтобы график мог реагировать на действия
from dash.dependencies import Input, Output
# библиотека пандас нужна для того чтобы данные с запроса превратить в dataframe
import pandas as pd
# библиотека для постройки графиков
import plotly.express as px


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

# внешний вид приложения. Тут использую dcc html
app.layout = html.Div([
    html.H1("Hello Dash!"),
    html.Div("Select planet main semi-axis range"),
    html.Div(rplanet_selector, style={"width": "500px", "margin-left": "auto", "margin-right": "auto",
                                      "margin-top": "10px", "margin-bottom": "20px"}),
    html.Div("Planet Temperature ~ Distance to the Star"),
    # просто вывести график
    # dcc.Graph(figure=fig)
    # чтобы график был responsive
    dcc.Graph(id="responsive-graph", figure=fig)
],
    style={"margin-left": "80px",
           "margin-right": "80px",
           "text-align": "center"})

# запуск программы
if __name__ == "__main__":
    # запуск сервера в тестовом режиме
    app.run_server(debug=True)

# оболочка над функцией, для динамической работы с переменными
@app.callback(
    # первый параметр - это куда мы будем передавать данные, а второй параметр это форма показа(форма сущности)
    Output(component_id="responsive-graph", component_property="figure"),
    # первый параметр - откуда мы берем данные, второй параметр говорит конкретно, что мы будем передевать
    Input(component_id="range-slider", component_property="value")
)
#     value передается и мы назыаем это radius_range
def update_graph(radius_range):


#главная полуось планеты, они движуться по элиптической оси и эти данные говорят нам о том насколько далео в среднем
# эта планета находится от своей звезды и мы строим зависимость меджу расстоянием и температурой
# x это температура, а y это расстояние
# задание добавить фильтр на основе радиуса планеты