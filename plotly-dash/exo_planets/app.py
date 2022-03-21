import dash
from dash import dcc
from dash import html

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

# инициализация программы
app = dash.Dash(__name__)

""" LAYOUT """

# внешний вид приложения. Тут использую dcc html
app.layout = html.Div([
    html.H1("Kepler Project"),
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


""" CALLBACKS """

# оболочка над функцией, для динамической работы с переменными
@app.callback(
    # Output задает то, что будет возвращать наша функция
    # первый параметр - это куда мы будем передавать данные, а второй параметр это форма показа(форма сущности, тип сущности)
    Output(component_id="responsive-graph", component_property="figure"),
    # первый параметр - откуда мы берем данные, второй параметр говорит конкретно, что мы будем передавать
    Input(component_id="range-slider", component_property="value")
)

# value передается и мы называем это radius_range
# функция для обновления графика
def update_graph(radius_range):
    # данные для графика
    graph_data = df[(df["RPLANET"] > radius_range[0]) &
                    (df["RPLANET"] < radius_range[1])
                    ]
    fig = px.scatter(graph_data, x="TPLANET",  y="A")

    return fig


# запуск программы
if __name__ == "__main__":
    # запуск сервера в тестовом режиме
    app.run_server(debug=True)




#главная полуось планеты, они движуться по элиптической оси и эти данные говорят нам о том насколько далео в среднем
# эта планета находится от своей звезды и мы строим зависимость меджу расстоянием и температурой
# x это температура, а y это расстояние
# задание добавить фильтр на основе радиуса планеты