from typing import Union, Any

import dash
from dash import dcc
from dash import html

import dash_bootstrap_components as dbc
from dash import dash_table
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
import plotly.graph_objects as go
from numpy import ndarray
from pandas import Series, DataFrame
from pandas.core.generic import NDFrame

from dash_iconify import DashIconify

""" READ DATA"""

df = pd.read_csv("asterank_exo.csv")

# добавлен фильтр по данным PER, которые отвечают за показатель направления вращения планеты
# отфильтровано так, чтобы были показаны планеты крутящиеся по часовой стрелке, а не против нее
df = df[df["PER"] > 0]
# данные с колонки коi будут показаны как инт значение
df["KOI"] = df["KOI"].astype(int, errors="ignore")

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
            html.Div(id="celestial-graph")], md=6)], className="tabs"),
    dbc.Row([
        dbc.Col([
            html.Div(id="relative-dist-graph")
        ], md=6),
        dbc.Col([
            html.Div(id="mstar-tstar-graph")
        ], md=6)
    ])
]

tab2_content = [
    dbc.Row([
        html.Div(id="data-table")
    ])
]

table_header = [
    html.Thead(
        html.Tr([
            html.Th("Field Name"),
            html.Th("Details")
        ])
    )
]

expl = {
    "KOI": "Object of Interest number",
    "A": "Semi-major axis (AU)",
    "RPLANET": "Planetary radius (Earth radii)",
    "RSTAR": "Stellar radius (Sol radii)",
    "TSTAR": "Effective temperature of host star as reported in KIC (k)",
    "KMAG": "Kepler magnitude (kmag)",
    "TPLANET": "Equilibrium temperature of planet, per Borucki et al. (k)",
    "T0": "Time of transit center (BJD-2454900)",
    "UT0": "Uncertainty in time of transit center (+-jd)",
    "UT0": "Uncertainty in time of transit center (+-jd)",
    "PER": "Period (days)",
    "UPER": "Uncertainty in period (+-days)",
    "DEC": "Declination (@J200)",
    "RA": "Right ascension (@J200)",
    "MSTAR": "Derived stellar mass (msol)",
}

tbl_rows = []
for i in expl:
    tbl_rows.append(html.Tr([html.Td(i), html.Td(expl[i])]))

table_body = [html.Tbody(tbl_rows)]

table = dbc.Table(table_header + table_body, bordered=True)

text = "Data are sourced from Kepler API via asterank.com"
tab3_content = [
    dbc.Row([
        html.A(text, href="https://www.asterank.com/kepler")
    ], className="tabs"),
    dbc.Row(html.Div(children=table), className="tabs"),

]

# Global design settings
CHARTS_TEMPLATE = go.layout.Template(
    layout=dict(
        font=dict(family="Century Gothic",
                  size=14),
        legend=dict(orientation="h",
                    title_text="",
                    x=0, y=1.1)

    )
)

COLORS_STATUS_VALUES = ["lightgray", "#1f85de", "#22D744"]

# инициализация программы
app = dash.Dash(__name__,
                # подключение бутстрепа
                external_stylesheets=[dbc.themes.BOOTSTRAP])

""" LAYOUT """

app.layout = html.Div([
    # Header
    html.Header(
        dbc.Row([
            dbc.Col(
                html.Img(src=app.get_asset_url("images/satellite.png"),
                         style={"width": "200px"}), width={"size": 2, "offset": 0}
            ),
            dbc.Col([
                html.H1("Exoplanet Data Visualization"),
                html.A("Read about exoplanets", href="https://spaceplace.nasa.gov/all-about-exoplanets/en/")
            ], width={"size": 7, "offset": 0})
        ], className="app-header"), className="app-sticky"),

    dcc.Store(id="filtered-data", storage_type="session"),

    # Body
    html.Main(
        html.Div([
            dbc.Row(
                [dbc.Col([
                    html.Div("Select planet main semi-axis range", className="selector",),
                    html.Div(rplanet_selector)
                ], width={"size": 3, "offset": 0}),
                    dbc.Col([
                        html.Div("Select Star size", className="selector",),
                        html.Div(star_size_selector)
                    ], width={"size": 3, "offset": 1}),
                    dbc.Col(dbc.Button("Apply all changes", id="btn-submit", outline=True, color="secondary",
                                       className="me-1", n_clicks=0), className="btn")
                ],
                className="main-selectors",
            ),
            dbc.Tabs([
                dbc.Tab(tab1_content, label="Charts"),
                dbc.Tab(tab2_content, label="Data"),
                dbc.Tab(tab3_content, label="About")
            ])
        ])
    ),

    html.Footer(
        dbc.Col([
            html.A(DashIconify(icon="ion:logo-github", width=30, ), href="https://github.com/dpaguba"),
            html.A("dpaguba", href="https://github.com/dpaguba")
        ], className="app-footer")
    )
])

""" CALLBACKS """


@app.callback(
    [Output(component_id="responsive-graph", component_property="children"),
     Output(component_id="celestial-graph", component_property="children"),
     Output(component_id="relative-dist-graph", component_property="children"),
     Output(component_id="mstar-tstar-graph", component_property="children"),
     Output(component_id="data-table", component_property="children")],
    [Input(component_id="btn-submit", component_property="n_clicks")],
    [State(component_id="range-slider", component_property="value"),
     State(component_id="star-size-dropdown", component_property="value")]
)
def update_graph(n, radius_range, star_size):
    graph_data: Union[Union[Series, DataFrame, None, NDFrame, ndarray], Any] = df[(df["RPLANET"] > radius_range[0]) &
                                                                                  (df["RPLANET"] < radius_range[1]) &
                                                                                  (df["StarSize"].isin(star_size))
                                                                                  ]

    if len(graph_data) == 0:
        return html.Div("Please select more data!",
                        style={"font-size": "250%", "margin-top": "40px"}), html.Div(), html.Div(), html.Div()

    fig1 = px.scatter(graph_data, x="TPLANET", y="A", color="StarSize")
    fig1.update_layout(template=CHARTS_TEMPLATE)
    html1 = [html.H5("Planet Temperature ~ Distance to the Star"), dcc.Graph(figure=fig1)]

    fig2 = px.scatter(graph_data, x="RA", y="DEC", size="RPLANET",
                      color="status", color_discrete_sequence=COLORS_STATUS_VALUES)
    fig2.update_layout(template=CHARTS_TEMPLATE)
    html2 = [html.H5("Position on the Celestial Sphere"), dcc.Graph(figure=fig2)]

    # как будут наложены гистрограммы
    fig3 = px.histogram(graph_data, x="Relative_dist", color="status", barmode="overlay", marginal="violin")
    fig3.update_layout(template=CHARTS_TEMPLATE)
    fig3.add_vline(x=1, annotation_text="Earth", line_dash="dot")
    html3 = [html.H5("Relative Distance (AU/Sol radii)"), dcc.Graph(figure=fig3)]

    fig4 = px.scatter(graph_data, x="MSTAR", y="TSTAR", size="RPLANET",
                      color="status", color_discrete_sequence=COLORS_STATUS_VALUES)
    fig4.update_layout(template=CHARTS_TEMPLATE)
    html4 = [
        html.H5("Star Mass ~ Star Temperature"),
        dcc.Graph(figure=fig4)
    ]
    # Raw data table
    # удаляем добавленые колонки
    raw_data = graph_data.drop(["Relative_dist", "StarSize", "Gravity", "status", "Temp", "ROW"], axis=1)
    # строим таблицу, переводим данные графика в словарь и записываем данные потом в колонки таблицы
    tbl = dash_table.DataTable(data=graph_data.to_dict("records"),
                               columns=[{"name": i, "id": i} for i in raw_data.columns],
                               style_data={"width": "93px", "maxWidth": "93px", "minWidth": "93px"},
                               style_header={"textAlign": "center"},
                               page_size=40
                               )

    html5 = [html.P("Raw Data"), tbl]

    return html1, html2, html3, html4, html5


# запуск программы
if __name__ == "__main__":
    # запуск сервера в тестовом режиме
    app.run_server(debug=True)
