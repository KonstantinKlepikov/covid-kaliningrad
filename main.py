import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from abc import ABC, abstractmethod
import os


__version__ = '1.2.6'


class DrawChart(ABC):

    """Type of available interpolation

        basis
        basis-open
        basis-closed
        bundle
        cardinal
        cardinal-open
        cardinal-closed
        catmull-rom
        linear
        linear-closed
        monotone
        natural
        step
        step-before
        step-after
    """

    def __init__(self, title, data, target='дата', type_='quantitative', interpolate='linear', point=False, height=600, width=800, scheme='category10', level=False, poly=None):
        self.title = title
        self.target = target
        self.data = data.melt(target, var_name='показатель', value_name='y')
        self.type_ = type_
        self.interpolate = interpolate
        self.point = point
        self.width = width
        self.height = height
        self.scheme = scheme
        self.level = level
        self.poly = poly

    @abstractmethod
    def draw(self):
        pass

    def select(self):
        # Create a selection that chooses the nearest point & selects based on x-value
        nearest = alt.selection(
            type='single',
            nearest=True,
            on='mouseover',
            fields=[self.target],
            empty='none'
            )

        # Selection in a legend
        self.leg = alt.selection_multi(fields=['показатель'], bind='legend')

        # Draw a chart
        self.line = self.draw.encode(
            alt.X(self.target, 
                type='temporal', 
                title=' ', 
                axis=alt.Axis(grid=True, offset=10)
                ),
            alt.Y('y', 
                type=self.type_, 
                title='количество', 
                scale=alt.Scale(zero=False),
                axis=alt.Axis(grid=True, offset=10)
                ),
            alt.Color('показатель:N',
                scale=alt.Scale(scheme=self.scheme),
                legend=alt.Legend(
                    labelFontSize=16, 
                    labelColor='#808080', 
                    orient='top-left', title='', 
                    labelLimit=320
                    )
                ),
            opacity=alt.condition(self.leg, 
                alt.value(1), 
                alt.value(0.2)
                )
        )

        # Transparent selectors across the chart. This is what tells us
        # the x-value of the cursor
        self.selectors = alt.Chart(self.data).mark_point().encode(
                            alt.X(self.target, type='temporal'),
                            opacity=alt.value(0),
                        ).add_selection(
                            nearest
                        )
        
        # Draw points on the line, and highlight based on selection
        self.points = self.line.mark_point().encode(
            opacity=alt.condition(nearest, alt.value(1), alt.value(0))
        )

        # Draw text labels near the points, and highlight based on selection
        self.text = self.line.mark_text(
            align='right', 
            dx=-5, 
            fill='#000000', 
            fontSize=16, 
            clip=False).encode(
                text=alt.condition(nearest, 'y', alt.value(''), type=self.type_)
        )

        # Draw X value on chart
        self.x_text = self.line.mark_text(
            align="left", 
            dx=-5, dy=15, 
            fill='#808080', 
            fontSize=16).encode(
                text=alt.condition(nearest, self.target, alt.value(''), type='temporal', format='%Y-%m-%d')
        )

        # Draw a rule at the location of the selection
        self.rules = alt.Chart(self.data).mark_rule(color='gray').encode(
            alt.X(self.target, type='temporal')
        ).transform_filter(
            nearest
        )

    def leanchart(self):
        self.chart = alt.layer(
            self.line, self.selectors, self.rules
        ).properties(
            title=self.title,
            width=self.width,
            height=self.height
        ).add_selection(
            self.leg
        )

    def richchart(self):
        self.chart = alt.layer(
            self.line, self.selectors, self.points, self.rules, self.text, self.x_text
        ).properties(
            title=self.title,
            width=self.width,
            height=self.height
        ).add_selection(
            self.leg
        )

    def selectionchart(self):
        brush = alt.selection(type='interval', encodings=['x'])
        upper = self.chart.encode(
            alt.X('date:T', scale=alt.Scale(domain=brush))
        )
        inline = self.draw.encode(
            alt.X(self.target, 
                type='temporal',
                title=' ', 
                axis=alt.Axis(grid=False)
                ),
            alt.Y('y', 
                type=self.type_, 
                scale=alt.Scale(zero=False),
                title=' ',
                axis=alt.Axis(grid=False, labels=False)
                ),
            alt.Color('показатель:N',
                scale=alt.Scale(scheme=self.scheme)
                ),
            opacity=alt.condition(self.leg, 
                alt.value(1), 
                alt.value(0.2)
                )
        )
        lower = alt.layer(
            inline, self.rules
        ).properties(
            width=self.width,
            height=20
        ).add_selection(
            brush
        )
        return upper & lower

    def baselinechart(self):
        # Create a chart
        # With baseline == level
        rule = alt.Chart(pd.DataFrame({'y': [self.level]})
            ).mark_rule().encode(
                y='y',
                size=alt.value(0.5),
                )
        return self.chart + rule

    def polynomialchart(self):
        degree_list = self.poly,
        polynomial_fit = [
            self.line.transform_regression(
                self.target, 'y', method='poly', order=order, as_=[self.target, str(order)]
            ).mark_line(
            ).transform_fold(
                [str(order)], as_=['регрессия', 'y']
            ).encode(alt.Color('регрессия:N'))
            for order in degree_list
        ]
        return alt.layer(self.chart, *polynomial_fit)

    def emptychart(self):
        return self.chart

class Linear(DrawChart):

    def draw(self):
        self.draw = alt.Chart(self.data).mark_line(interpolate=self.interpolate, point=self.point)
        self.select()

class Point(DrawChart):

    def draw(self):
        self.draw = alt.Chart(self.data).mark_point(interpolate=self.interpolate)
        self.select()

class Area(DrawChart):

    def draw(self):
        self.draw = alt.Chart(self.data).mark_area(interpolate=self.interpolate)
        self.select()

class Bar(DrawChart):

    def draw(self):
        self.draw = alt.Chart(self.data).mark_bar()
        self.select()


cTime = 900. # cache time

@st.cache(allow_output_mutation=True, ttl=cTime)
def dataloader(url):
    return pd.read_csv(url)

@st.cache(suppress_st_warning=True, ttl=cTime)
def asidedata(data, people=1012512):
    ds = {}
    ds['sick'] = data['всего'].sum()
    ds['proc'] = round(ds['sick'] * 100 / people, 2)
    ds['dead'] = data['умерли от ковид'].sum()
    ds['let'] = round(ds['dead'] * 100 / ds['sick'], 2)
    ds['ex'] = data['выписали'].sum()
    ds['update'] = data['дата'].iloc[-1]

    return ds

@st.cache()
def pagemaker():
    p = {'intro': 'Введение',
    'cases': 'Динамика заражения', 
    'infection rate': 'Infection Rate', 
    'deaths': 'Данные об умерших', 
    'exits': 'Данные о выписке', 
    'capacity': 'Нагрузка на систему', 
    'tests': 'Тестирование', 
    'regions': 'Регионы',
    'demographics': 'Демография',
    'correlations': 'Корреляции'
    }
    paginator = [n for n in p.keys()]

    return p, paginator

@st.cache()
def regDistr(data):
    _cols = [col for col in data.columns if 'округ' in col]
    _cols.append('дата')
    _cols.append('Калининград')
    return _cols

@st.cache(ttl=cTime)
def hospitalPlaces(data):
    df = data[['дата', 'доступно под ковид', 'занято под ковид', 'доступно ИВЛ', 'занято ИВЛ', 'доступно под ковид и пневмонию', 'занято под ковид и пневмонию']].query("'2020-11-01' <= дата ")
    df.set_index('дата', inplace=True)
    df = df[(df.T != 0).any()]
    df.reset_index(inplace=True)
    return df

@st.cache(ttl=cTime)
def irDestrib(data):
    df = data[['дата', 'infection rate']]
    high = df[df['infection rate'] >= 1].shape[0]
    low = df[df['infection rate'] < 1].shape[0]
    return high, low

@st.cache(ttl=cTime)
def proffesion(data):
    _cols = [col for col in data.columns if '>' in col]
    _cols.append('дата')
    return _cols

@st.cache()
def ageDestr(data):
    _cols = [
        'до года',
        'от 01 до 07', 
        'от 07 до 14',
        'от 15 до 17',
        'от 18 до 29',
        'от 30 до 49',
        'от 50 до 64',
        'от 65'
    ]
    _cols.append('дата')
    return _cols


def main(hidemenu=True):

    if hidemenu:
        hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>

        """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

    st.sidebar.title('Данные о covid-19 в Калининградской области')
    st.sidebar.text('v' + __version__)

    data = dataloader('https://raw.githubusercontent.com/KonstantinKlepikov/covid-kaliningrad/datasets/data/data.csv')    

    ds = asidedata(data)

    high, low = irDestrib(data)

    st.sidebar.markdown('Обновлено: {}'.format(ds['update']))
    st.sidebar.markdown('Всего выявлено: **{}**'.format(ds['sick']))
    st.sidebar.markdown('От населения области: **{}%**'.format(ds['proc']))
    st.sidebar.markdown('Официально умерло: **{}**'.format(ds['dead']))
    st.sidebar.markdown('Общая летальность: **{}%**'.format(ds['let']))
    st.sidebar.markdown('Выписано: **{}**'.format(ds['ex']))
    st.sidebar.markdown('IR4 >= 1 дней: **{}**'.format(high))
    st.sidebar.markdown('IR4 < 1 дней: **{}**'.format(low))

    p, paginator = pagemaker()

    page = st.radio('Данные', paginator)

    if page == 'intro':
        st.header(p[page])

        st.subheader('Описание проекта')
        st.markdown('Проект работает с открытыми данными, собранными из различных официальных источников. Актуальность информации зависит от скорости обновления таблицы и источника агрегации и может составлять от 15 минут до 8 часов с момента публикации. Предсталеные визуализированные данные не являются точными и не могут отражать истинную картину распространения covid-19 в Калининградской области. Автор проекта агрегирует данные с образовательной целью и не несет ответственности за их достоверность. Весь контент и код проекта предоставляется по [MIT лицензии](https://opensource.org/licenses/mit-license.php).')

        st.subheader('Как это сделано?')
        st.markdown('[Статья о том, как собрано это приложение](https://konstantinklepikov.github.io/2021/01/10/zapuskaem-machine-learning-mvp.html)')
        st.markdown('[Репозиторий проекта](https://github.com/KonstantinKlepikov/covid-kaliningrad)')
        st.markdown('[Данные](https://docs.google.com/spreadsheets/d/1iAgNVDOUa-g22_VcuEAedR2tcfTlUcbFnXV5fMiqCR8/edit#gid=1038226408)')

        st.subheader('Изменения в версиях')
        st.markdown('**v1.2** Улушено отображение на мобильных устройствах. Оптимизирована скорость загрузки страницы. Добавлены IR7 и распределение IR. Добавлены распределения. Добавлены данные Росстата.')
        st.markdown('**v1.1** Добавлена обработка данных и вывод основных визуализаций.')

        st.subheader('Контакты')
        st.markdown('[Мой блог про machine learning](https://konstantinklepikov.github.io/)')
        st.markdown('[Я на github](https://github.com/KonstantinKlepikov)')
        st.markdown('[Мой сайт немножко про маркетинг](https://yorb.ru/)')
        st.markdown('[Телеграм](https://t.me/KlepikovKonstantin)')
        st.markdown('[Фейсбук](https://facebook.com/konstatin.klepikov)')

        st.markdown('К сожалению официальные службы не поделились со мной имеющимися историческими данными. Буду благодарен за любой источник данных, если таковой имеется - пишите в [телеграм](https://t.me/KlepikovKonstantin).')
        st.image('https://raw.githubusercontent.com/KonstantinKlepikov/covid-kaliningrad/main/img/answer.png', use_column_width=True)
    
    elif page == 'cases':
        st.header(p[page])

        # cases
        ch = Linear(
            p[page], 
            data[['дата', 'всего', 'ОРВИ', 'пневмония', 'без симптомов']]
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.selectionchart())

        # area cases
        ch = Area(
            p[page], 
            data[['дата', 'ОРВИ', 'пневмония', 'без симптомов']]
            )
        ch.draw()
        ch.leanchart()
        st.altair_chart(ch.selectionchart())

        # cumsum cases
        ch = Linear(
            'Количество случаев аккумулировано', 
            data[['дата', 'кумул. случаи']], 
            height=400, 
            scheme='set1'
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.emptychart())

    elif page == 'infection rate':
        st.header(p[page])

        # ir4
        st.markdown('IR4 расчитывается по методике РосПотребНадзора - как отношение количества заболевших за прошедшие 4 дня к количеству заболевших за предыдущие прошедшие 4 дня.')
        ch = Linear(
            'Infection Rate 4 days', 
            data[['дата', 'infection rate']], 
            scheme='set1',
            level=1
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.baselinechart())

        # ir7
        ch = Linear(
            'Infection Rate 7 days', 
            data[['дата', 'IR7']], 
            level=1
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.baselinechart())

        # ir difference
        ch = Linear(
            'Распределение отношения количества дней с положительным ir4 к количеству дней с отрицательным ir4', 
            data[['дата', 'отношение']], 
            level=1
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.baselinechart())

    elif page == 'deaths':
        st.header(p[page])

        # deaths with polynomial
        ch = Area(
            'умерли от ковид', 
            data[['дата', 'умерли от ковид']],
            height=400, 
            scheme='set1', 
            poly=7,
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.polynomialchart())

        # death cumsum
        ch = Linear(
            'смертельные случаи нарастающим итогом', 
            data[['дата', 'кумул.умерли']], 
            height=400, 
            scheme='set1'
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.emptychart())

        # hospital death data
        st.markdown('Информация об умерших в палатах, отведенных для больных для больных пневмонией/covid предоставлялась мед.службами по запросу [newkaliningrad.ru](https://www.newkaliningrad.ru/)')
        ch = Linear(
            'умерли в палатах для ковид/пневмонии', 
            data[['дата', 'умерли в палатах для ковид/пневмония с 1 апреля']].query("'2020-11-01' <= дата & `умерли в палатах для ковид/пневмония с 1 апреля` > 0"), 
            height=600, 
            point=True, 
            scheme='set1'
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.emptychart())

        # rosstat death
        rosstat = dataloader('https://raw.githubusercontent.com/KonstantinKlepikov/covid-kaliningrad/datasets/data/rosstat.csv')
        rosstat['Месяц'] = pd.to_datetime(rosstat['Месяц'], dayfirst=True)
        ch = Area(
            'Данные Росстата о смертности с диагнозом COVID-19', 
            rosstat, 
            target='Месяц',
            height=600,
            width=600
            )
        ch.draw()
        ch.leanchart()
        st.altair_chart(ch.emptychart())

    elif page == 'exits':
        st.header(p[page])

        # exit
        st.markdown('Нет достоверной информации о том, что лечение выписанных больных в действительности закончено')
        ch = Linear(
            'Выписаны', 
            data[['дата', 'всего', 'выписали']], 
            scheme='set1'
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.selectionchart())

        # cumsum exit
        ch = Linear(
            'Выписаны из больниц нарастающим итогом', 
            data[['дата', 'кумул. случаи', 'кумул.выписаны']], 
            height=400, 
            scheme='set1'
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.emptychart())

    elif page == 'capacity':
        st.header(p[page])
        st.markdown('Активные случаи - это заразившиеся минус выписанные и умершие. Болеют ли эти люди в текущий момент на самом деле установить невозможно. Данные о загруженности больниц предоставлены мед.службами.')

        # cumsum minus exit
        ch = Linear(
            'Активные случаи нарастающим итогом', 
            data[['дата', 'кумул.активные']], 
            height=400, 
            scheme='set1'
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.emptychart())

        # hospital places
        df = hospitalPlaces(data)
        ch = Point(
            'Доступные места', 
            df.replace(0, np.nan), 
            height=800, 
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.emptychart())

    elif page == 'tests':
        st.header(p[page])

        # tests
        ch = Linear(
            'Общее количество тестов', 
            data[['дата', 'кол-во тестов']], 
            scheme='accent'
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.selectionchart())

        # tesats and cases
        st.markdown('Для наглядности, количество тестов разделено на 10 для приведенных графиков.')
        ch = Linear(
            'Тестирование и распространение болезни', 
            data[['дата', 'ОРВИ', 'пневмония', 'без симптомов', 'кол-во тестов / 10']], 
            height=500
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.selectionchart())

        # tests and exit
        ch = Linear(
            'Тестирование и выписка', 
            data[['дата', 'выписали', 'кол-во тестов / 10']], 
            height=500,
            scheme='set1'
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.selectionchart())

    elif page == 'regions':
        st.header(p[page])

        # Kaliningrad and regions
        ch = Area(
            'Калининград и регионы', 
            data[['дата', 'Калининград', 'все кроме Калининграда']], 
            interpolate='step', 
            height=400,
            scheme='set1'
            )
        ch.draw()
        ch.leanchart()
        st.altair_chart(ch.selectionchart())

        # All regions
        _cols = regDistr(data)
        ch = Area(
            'Распределение случаев по региону', 
            data[_cols], 
            interpolate='step', 
            height=600,
            scheme='tableau20'
            )
        ch.draw()
        ch.leanchart()
        st.altair_chart(ch.selectionchart())

    elif page == 'demographics':
        st.header(p[page])

        # activivty
        ch = Area(
            'Распределение случаев по статусу', 
            data[['дата', 'воспитанники/учащиеся', 'работающие', 'служащие', 'неработающие и самозанятые', 'пенсионеры']], 
            interpolate='step', 
            height=600,
            scheme='tableau20'
            )
        ch.draw()
        ch.leanchart()
        st.altair_chart(ch.selectionchart())

        # profession diagram
        _colsPro = proffesion(data)
        ch = Area(
            'Распределение случаев по роду деятельности', 
            data[_colsPro], 
            interpolate='step', 
            height=600,
            scheme='tableau20'
            )
        ch.draw()
        ch.leanchart()
        st.altair_chart(ch.selectionchart())

        # sex
        ch = Area(
            'Распределение случаев по полу', 
            data[['дата', 'мужчины', 'женщины']], 
            interpolate='step', 
            height=400,
            scheme='tableau20'
            )
        ch.draw()
        ch.leanchart()
        st.altair_chart(ch.selectionchart())

        # age destribution
        _colsAge = ageDestr(data)
        ch = Area(
            'Распределение случаев по возрасту', 
            data[_colsAge], 
            interpolate='step', 
            height=600,
            scheme='tableau20'
            )
        ch.draw()
        ch.leanchart()
        st.altair_chart(ch.selectionchart())

        # source
        ch = Area(
            'Распределение по источнику заражения', 
            data[['дата', 'завозные', 'контактные', 'не установлены']], 
            interpolate='step', 
            height=600,
            scheme='tableau20'
            )
        ch.draw()
        ch.leanchart()
        st.altair_chart(ch.selectionchart())

    elif page == 'correlations':
        st.header(p[page])

        st.text('soon...')
        # report = ProfileReport(data.drop(['учебные учреждения'], axis=1))
        # st_profile_report(report)

main()
