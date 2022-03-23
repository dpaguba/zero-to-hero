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

df = pd.read_csv("asterank_exo.csv")
# добавлен фильтр по данным PER, которые отвечают за показатель направления вращения планеты
# отфильтровано так, чтобы были показаны планеты крутящиеся по часовой стрелке, а не против нее
df = df[df["PER"] > 0]

# создание колонки StarSize, которая содержит в себе разбитую колонку RSTAR на "small", "similar", "bigger"
bins = [0, 0.8, 1.2, 100]
names = ["small", "similar", "bigger"]
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

# Относительная дистанция (Дистанция к солнцу/ радиус солнца)
df.loc[:, "Relative_dist"] = df["A"] / df["RSTAR"]

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

# Tabs content
tab1_content = [
    dbc.Row([
        dbc.Col([
            html.Div(id="responsive-graph")], md=6),
        dbc.Col([
            html.Div(id="celestial-graph")], md=6)], style={"margin-top": "20px", "margin-bottom": "10px"}),
    dbc.Row([
        dbc.Col([
            html.Div(id="relative-dist-graph")
        ], md=6),
        dbc.Col([
            html.Div(id="mstar-tstar-graph")
        ], md=6)
    ])
]

# инициализация программы
app = dash.Dash(__name__,
                # подключение бутстрепа
                external_stylesheets=[dbc.themes.BOOTSTRAP])

""" LAYOUT """

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
        dbc.Tabs([
            dbc.Tab(tab1_content, label="Charts"),
            dbc.Tab(html.Div("Tab 2 Content!"), label="Tab2"),
            dbc.Tab(html.Div("About Page"), label="About")
        ])
    ], style={"margin-left": "80px",
              "margin-right": "80px",
              "text-align": "center"}
)

""" CALLBACKS """


@app.callback(
    [Output(component_id="responsive-graph", component_property="children"),
     Output(component_id="celestial-graph", component_property="children"),
     Output(component_id="relative-dist-graph", component_property="children"),
     Output(component_id="mstar-tstar-graph", component_property="children")],
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
                        style={"font-size": "250%", "margin-top": "40px"}), html.Div(), html.Div(), html.Div()

    fig1 = px.scatter(graph_data, x="TPLANET", y="A", color="StarSize")
    html1 = [html.Div("Planet Temperature ~ Distance to the Star"), dcc.Graph(figure=fig1)]

    fig2 = px.scatter(graph_data, x="RA", y="DEC", size="RPLANET", color="status")
    html2 = [html.Div("Position on the Celestial Sphere"), dcc.Graph(figure=fig2)]

    # как будут наложены гистрограммы
    fig3 = px.histogram(graph_data, x="Relative_dist", color="status", barmode="overlay", marginal="violin")
    fig3.add_vline(x=1, annotation_text="Earth", line_dash="dot")
    html3 = [html.Div("Relative Distance (AU/Sol radii)"), dcc.Graph(figure=fig3)]

    fig4 = px.scatter(graph_data, x="MSTAR", y="TSTAR", size="RPLANET", color="status")
    html4 = [
        html.Div("Star Mass ~ Star Temperature"),
        dcc.Graph(figure=fig4)
    ]

    return html1, html2, html3, html4


# запуск программы
if __name__ == "__main__":
    # запуск сервера в тестовом режиме
    app.run_server(debug=True)
