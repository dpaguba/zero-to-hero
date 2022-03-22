import dash
from dash import dcc
from dash import html

import dash_bootstrap_components as dbc

# чтобы график мог реагировать на действия
from dash.dependencies import Input, Output
# библиотека pandas нужна для того чтобы данные с запроса превратить в dataframe
import pandas as pd
# библиотека для постройки графиков
import plotly.express as px

""" READ DATA"""

# Считывание и конвертация данных в dataframe
df = pd.read_csv("asterank_exo.csv")
# добавлен фильтр по данным PER, которые отвечают за показатель направления вращения планеты
# отфильтровано так, чтобы были показаны планеты крутящиеся по часовой стрелке, а не против нее
df = df[df["PER"] > 0]

# описываем вид графика. отношеине радиуса к температуре планеты
# fig = px.scatter(df, x="RPLANET", y="TPLANET")

# новый график. Отношение температуры планеты к большой и малой полуоси
# поскольу мы обновляем график в callback, то непосредственное декларирование графика в теле программы
# является лишним
# fig = px.scatter(df, x="TPLANET", y="A")

# создание категория по размеру звезды
# 0.8 - планеты по размеру до 80% от размеров солнца - маленькие звезды/планеты
# 1.2 - планеты по размеру до 120% от размеров солнца - сопоставимые звезды/планеты
# 0.8 - планеты по размеру до 10000% от размеров солнца - большие звезды/планеты
bins = [0, 0.8, 1.2, 100]

# декларация имен для вышеперечисленных данных
names = ["small", "similar", "bigger"]

# создание колонки StarSize, которая содержит в себе разбитую колонку RSTAR на "small", "similar", "bigger"
df["StarSize"] = pd.cut(df["RSTAR"], bins, labels=names)

# создание опий выбора для дропдаун меню
options = []
for s in names:
    options.append({"label": s, "value": s})


# слайдер
rplanet_selector = dcc.RangeSlider(
    # название слайдера
    id="range-slider",

    # минимальное и максимальное значение будут браться из данных rplanet
    min=min(df["RPLANET"]),
    max=max(df["RPLANET"]),
    # отметки - надписи
    marks={5: "5", 10: "10", 25: "25", 50: "50"},
    step=1,
    # дефольтные значения
    value=[5, 50]
)

# дроп даун меню
star_size_selector = dcc.Dropdown(
    id="star-size-dropdown",
    options=options,
    value=["small", "similar"],
    multi=True
)


# инициализация программы
app = dash.Dash(__name__,
                # подключение бутстрепа
                external_stylesheets=[dbc.themes.BOOTSTRAP])

""" LAYOUT """

# Cтарый layout
# внешний вид приложения. Тут использую dcc html
# app.layout = html.Div([
#     html.H1("Kepler Project"),
#     html.Div("Select planet main semi-axis range"),
#     html.Div(rplanet_selector, style={"width": "500px", "margin-left": "auto", "margin-right": "auto",
#                                       "margin-top": "10px", "margin-bottom": "20px"}),
#
#     html.Div("Select Star size"),
#     html.Div(star_size_selector, style={"width": "300px", "margin-left": "auto", "margin-right": "auto",
#                                       "margin-top": "10px", "margin-bottom": "20px"}),
#
#     html.Div("Planet Temperature ~ Distance to the Star"),
#     # просто вывести график
#     # dcc.Graph(figure=fig)
#     # чтобы график был responsive
#     # dcc.Graph(id="responsive-graph", figure=fig) - внесенные изменения из-за того, что график декларируется в callback
#     dcc.Graph(id="responsive-graph")
# ],
#     style={"margin-left": "80px",
#            "margin-right": "80px",
#            "text-align": "center"})

app.layout = html.Div(
    [
        dbc.Row(html.H1("Kepler Project"), style={"margin-top": "10px", "margin-bottom": "20px"}),
        dbc.Row(
            [dbc.Col([
                html.Div("Select planet main semi-axis range"),
                html.Div(rplanet_selector)
                ], width={"size": 4, "offset": 1}),
             dbc.Col([
                html.Div("Select Star size"),
                html.Div(star_size_selector)
                ], width={"size": 4, "offset": 2})
             ],  style={"margin-top": "10px", "margin-bottom": "20px"},
        ),
        dbc.Row(dbc.Col([
                html.Div("Planet Temperature ~ Distance to the Star"),
                dcc.Graph(id="responsive-graph")
                ]),  style={"margin-top": "20px", "margin-bottom": "10px"})

    ], style={"margin-left": "80px",
              "margin-right": "80px",
              "text-align": "center"}
)

""" CALLBACKS """

# оболочка над функцией, для динамической работы с переменными
@app.callback(
    # Output задает то, что будет возвращать наша функция
    # первый параметр - это куда мы будем передавать данные, а второй параметр это форма показа(форма сущности, тип сущности)
    Output(component_id="responsive-graph", component_property="figure"),
    # первый параметр - откуда мы берем данные, второй параметр говорит конкретно, что мы будем передавать
    [Input(component_id="range-slider", component_property="value"),
     Input(component_id="star-size-dropdown", component_property="value")]
)

# value передается и мы называем это radius_range
# функция для обновления графика
def update_graph(radius_range, star_size):
    # данные для графика
    graph_data = df[(df["RPLANET"] > radius_range[0]) &
                    (df["RPLANET"] < radius_range[1]) &
                    (df["StarSize"].isin(star_size))
                    ]
    # создание графика
    fig = px.scatter(graph_data, x="TPLANET",  y="A", color="StarSize")

    return fig


# запуск программы
if __name__ == "__main__":
    # запуск сервера в тестовом режиме
    app.run_server(debug=True)




#главная полуось планеты, они движуться по элиптической оси и эти данные говорят нам о том насколько далео в среднем
# эта планета находится от своей звезды и мы строим зависимость меджу расстоянием и температурой
# x это температура, а y это расстояние
# задание добавить фильтр на основе радиуса планеты