import dash
import dash_core_components as dcc
import dash_html_components as html

import requests
# чтобы пробразовать запрос в датафрейм нужно импорт pandas
import pandas as pd
# график строим с помощью библиотеки plotly
import plotly.express as px
# для вывода прямо в бразуер
import plotly.io as poi
# результат plotly нужно выводить в браузер
poi.renderers.default = "browser"

# Из параметров в запросе у нас query (мы оставляем пустым, потому что хотим получить все данные)
# и кол-во строк мы ограничим в 2000
# результат запроса будет сохранен в переменную response как JSON-file
response = requests.get("http://asterank.com/api/kepler?query={}&limit={2000}")
# превращаем данные из json формата в dataframe
df = pd.json_normalize(response.json())

# test
# print(df.head())

fig = px.scatter(df, x="RPLANET", y="TPLANET")

# отобразить
# fig.show()


# инициализация
app = dash.Dash(__name__)

# фронтенд приложения - описание как будет выглядеть приложение
app.layout = html.Div("Hello")


# запуск приложения
if __name__ == "__main__":
    app.run_server(debug=True)