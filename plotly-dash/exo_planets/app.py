import dash
from dash import dcc
from dash import html

import dash_bootstrap_components as dbc
import numpy as np

# чтобы график мог реагировать на действия
# Каждый раз когда меняется значение в инпуте в компонент айди, то вызывается полностью целый колбек,
# а если мы передаем параметры инпута через стейт, то ничего не тригерится и не вызывается колбек, а мы
# можем их применить, когда нажмем на кнопку - триггер
from dash.dependencies import Input, Output, State
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

# Декларация требований для поиска пригодной для жизни планеты
# Температура
tp_bins = [0, 200, 400, 500, 5000]
tp_labels = ["low", "optimal", "high", "extreme"]
df["Temp"] = pd.cut(df["TPLANET"], tp_bins, labels=tp_labels)

# Размер и гравитация
rp_bins = [0, 0.5, 2, 4, 100]
rp_labels = ["low", "optimal", "high", "extreme"]
df["Gravity"] = pd.cut(df["RPLANET"], rp_bins, labels=rp_labels)

# задать статус объекта
# np.where((condition), исход если true, исход если else)
df["status"] = np.where((df["Temp"] == "optimal") & (df["Gravity"] == "optimal"), "promising", None)

# loc отвечает за извлечение данных. на месте : может быть лист с индексами или значениями. В данном случае мы извлекаем
# диапазон строк
df.loc[:, "status"] = np.where((df["Temp"] == "optimal") & (df["Gravity"].isin(["low", "high"])),
                               "challenging", df["status"])
df.loc[:, "status"] = np.where((df["Temp"].isin(["low", "high"])) &
                               (df["Gravity"] == "optimal"),
                               "challenging", df["status"])
# запоолняет значения NaN в df на "extreme"
df["status"] = df.status.fillna("extreme")

# вывод в консоль
# print(df.groupby("status")["ROW"].count())


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
    value=[min(df["RPLANET"]), max(df["RPLANET"])]
)

# дроп даун меню
star_size_selector = dcc.Dropdown(
    id="star-size-dropdown",
    options=options,
    value=["small", "similar", "bigger"],
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
        dbc.Row(dbc.Col(html.H1("Kepler Project"),
                        style={"text-align": "center", "margin-top": "10px", "margin-bottom": "20px"})),
        dbc.Row(
            [dbc.Col([
                html.Div("Select planet main semi-axis range"),
                html.Div(rplanet_selector)
            ], width={"size": 3, "offset": 0}),
                dbc.Col([
                    html.Div("Select Star size"),
                    html.Div(star_size_selector)
                ], width={"size": 3, "offset": 1}),
                dbc.Col(dbc.Button("Apply", id="btn-submit", color="success", className='me-1', n_clicks=0))
            ],
            style={"margin-top": "10px", "margin-bottom": "20px"}
        ),
        dbc.Row([dbc.Col([html.Div(id="responsive-graph")],
                         width={"size": 6, "offset": 0}),
                 dbc.Col([html.Div(id="celestial-graph")]
                         )],
                style={"margin-top": "20px", "margin-bottom": "10px"})

    ], style={"margin-left": "80px",
              "margin-right": "80px",
              "text-align": "center"}
)

""" CALLBACKS """


# оболочка над функцией, для динамической работы с переменными
# @app.callback(
#     # Output задает то, что будет возвращать наша функция первый параметр - это куда мы будем передавать данные,
#     # а второй параметр это форма показа(форма сущности, тип сущности)
#     Output(component_id="responsive-graph", component_property="figure"),
#     # первый параметр - откуда мы берем данные, второй параметр говорит конкретно, что мы будем передавать
#     [Input(component_id="range-slider", component_property="value"),
#      Input(component_id="star-size-dropdown", component_property="value")]
# )
# value передается и мы называем это radius_range
# функция для обновления графика
# def update_graph(radius_range, star_size):
#     # данные для графика
#     graph_data = df[(df["RPLANET"] > radius_range[0]) &
#                     (df["RPLANET"] < radius_range[1]) &
#                     (df["StarSize"].isin(star_size))
#                     ]
#     # создание графика
#     fig = px.scatter(graph_data, x="TPLANET", y="A", color="StarSize")
#
#     return fig
# @app.callback(
#     # Output задает то, что будет возвращать наша функция первый параметр - это куда мы будем передавать данные,
#     # а второй параметр это форма показа(форма сущности, тип сущности)
#     Output(component_id="celestial-graph", component_property="figure"),
#     # первый параметр - откуда мы берем данные, второй параметр говорит конкретно, что мы будем передавать
#     [Input(component_id="range-slider", component_property="value"),
#      Input(component_id="star-size-dropdown", component_property="value")]
# )
# def update_celestial_graph(radius_range, star_size):
#     # данные для графика
#     graph_data = df[(df["RPLANET"] > radius_range[0]) &
#                     (df["RPLANET"] < radius_range[1]) &
#                     (df["StarSize"].isin(star_size))
#                     ]
#     # создание графика
#     # параметр size делает из точек пузырки на графике
#     fig = px.scatter(graph_data, x="RA", y="DEC", size="RPLANET", color="status")
#
#     return fig


# чтобы програма не крашилась, если ни одного параметра из фильтров не будет выбрано, переделываем вывод программы
# раньше мы возвращали figure, а теперь html.Div - это children. После этого мы добавляем проверку
# на отсутствие выбранных данных, если она успешна, то выводом будет сообщение, если же нет, то графики
@app.callback(
    Output(component_id="responsive-graph", component_property="children"),
    Output(component_id="celestial-graph", component_property="children"),
    [Input(component_id="btn-submit", component_property="n_clicks")],
    [State(component_id="range-slider", component_property="value"),
     State(component_id="star-size-dropdown", component_property="value")]
)
def update_graph(n, radius_range, star_size):
    graph_data = df[(df["RPLANET"] > radius_range[0]) &
                    (df["RPLANET"] < radius_range[1]) &
                    (df["StarSize"].isin(star_size))
                    ]

    if len(graph_data) == 0:
        return html.Div("Please select more data!",
                        style={"font-size": "250%", "margin-top": "40px"}), html.Div()

    fig1 = px.scatter(graph_data, x="TPLANET", y="A", color="StarSize")
    html1 = [html.Div("Planet Temperature ~ Distance to the Star"), dcc.Graph(figure=fig1)]

    fig2 = px.scatter(graph_data, x="RA", y="DEC", size="RPLANET", color="status")
    html2 = [html.Div("Position on the Celestial Sphere"), dcc.Graph(figure=fig2)]

    return html1, html2


# запуск программы
if __name__ == "__main__":
    # запуск сервера в тестовом режиме
    app.run_server(debug=True)
