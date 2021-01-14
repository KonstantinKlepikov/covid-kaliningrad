import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import os

__version__ = '1.2.1'


def buildchart(title, data, type_='quantitative', interpolate='step', height=600, width=800, level=False, poly=False, tchart='linear', point=False, empty=False, scheme='category10'):
    """linearchart

    type of interpolation of linechart

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

    str, default

    Returns:
        obj: linechart object
    """
    # Prepare data
    source = data.melt('дата', var_name='показатель', value_name='y')

    # Create chart scaling
    # scales = alt.selection_interval(bind='scales')

    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(type='single',
                            nearest=True,
                            on='mouseover',
                            fields=['дата'],
                            empty='none'
                            )

    # Selection in a legend
    leg = alt.selection_multi(fields=['показатель'], bind='legend')

    # Create main chart
    if tchart == 'linear':
        lchart = alt.Chart(source).mark_line(interpolate=interpolate, point=point)

    if tchart == 'point':
        lchart = alt.Chart(source).mark_point(interpolate=interpolate)

    if tchart == 'area':
        lchart = alt.Chart(source).mark_area(interpolate=interpolate)

    if tchart == 'bar':
        pass

    line = lchart.encode(
            alt.X('дата', 
                type='temporal', 
                title=' ', 
                axis=alt.Axis(grid=False, offset=10)
                ),
            alt.Y('y', 
                type=type_, 
                title='количество', 
                scale=alt.Scale(zero=False),
                axis=alt.Axis(grid=False, offset=10)
                ),
            alt.Color('показатель:N',
                scale=alt.Scale(scheme=scheme)
                ),
            opacity=alt.condition(leg, 
                alt.value(1), 
                alt.value(0.2)
                )
        )    

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = alt.Chart(source).mark_point().encode(
        alt.X('дата', type='temporal'),
        opacity=alt.value(0),
    ).add_selection(
        nearest
    )

    # Draw points on the line, and highlight based on selection
    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    # Draw text labels near the points, and highlight based on selection
    text = line.mark_text(align='right', dx=-5, fill='#000000').encode(
        text=alt.condition(nearest, 'y:Q', alt.value(' '))
    )

    # Draw X value on chart
    x_text = line.mark_text(align="right", dx=-5, dy=12).encode(
        text=alt.condition(nearest, "дата:T", alt.value(" "), format='%Y-%m-%d')
    )

    # Draw a rule at the location of the selection
    rules = alt.Chart(source).mark_rule(color='gray').encode(
        alt.X('дата', type='temporal')
    ).transform_filter(
        nearest
    )

    # Put the five layers into a chart and bind the data
    if interpolate == 'step':
        chart = alt.layer(
            line, selectors, rules
        ).properties(
            title=title,
            width=width,
            height=height
        ).add_selection(
            leg
        )
    else:
        chart = alt.layer(
            line, selectors, points, rules, text, x_text
        ).properties(
            title=title,
            width=width,
            height=height
        ).add_selection(
            leg
        )

    # Interval selection chart
    brush = alt.selection(type='interval', encodings=['x'])
    upper = chart.encode(
        alt.X('date:T', scale=alt.Scale(domain=brush))
    )
    inline = lchart.encode(
        alt.X('дата', 
            type='temporal',
            title=' ', 
            axis=alt.Axis(grid=False)
            ),
        alt.Y('y', 
            type=type_, 
            scale=alt.Scale(zero=False),
            title=' ',
            axis=alt.Axis(grid=False, labels=False)
            ),
        alt.Color('показатель:N',
            scale=alt.Scale(scheme=scheme)
            ),
        opacity=alt.condition(leg, 
            alt.value(1), 
            alt.value(0.2)
            )
    )
    lower = alt.layer(
        inline, rules
    ).properties(
        width=width,
        height=20
    ).add_selection(
        brush
    )

    # Create a chart
    # With baseline == level
    if level:
        rule = alt.Chart(pd.DataFrame({'y': [level]})
            ).mark_rule().encode(
                y='y',
                size=alt.value(0.5),
                )
        return chart + rule
    # With polynomial regressiuon
    # to-do: cant work with color mapping
    elif poly:
        degree_list = poly,
        polynomial_fit = [
            line.transform_regression(
                'дата', 'y', method='poly', order=order, as_=['дата', str(order)]
            ).mark_line(
            ).transform_fold(
                [str(order)], as_=['регрессия', 'y']
            ).encode(alt.Color('регрессия:N'))
            for order in degree_list
        ]
        return alt.layer(chart, *polynomial_fit)
    # Empty
    elif empty:
        return chart
    # Interval selection
    else:
        return upper & lower

@st.cache(ttl=180.)
def dataloader(url):
    return pd.read_csv(url)

@st.cache(suppress_st_warning=True, ttl=180.)
def asidedata(data, people=1012512):
    ds = {}
    ds['sick'] = data['всего'].sum()
    ds['proc'] = round(ds['sick'] * 100 / people, 2)
    ds['dead'] = data['умерли от ковид'].sum()
    ds['let'] = round(ds['dead'] * 100 / ds['sick'], 2)
    ds['ex'] = data['выписали'].sum()

    return ds


def main():

    st.sidebar.title('Данные о covid-19 в Калининградской области')
    st.sidebar.text('v' + __version__)

    data = dataloader('https://raw.githubusercontent.com/KonstantinKlepikov/covid-kaliningrad/datasets/data/data.csv')

    ds = asidedata(data)

    st.sidebar.markdown('Всего заболело: **{}**'.format(ds['sick']))
    st.sidebar.markdown('От всего населения: **{}%**'.format(ds['proc']))
    st.sidebar.markdown('Официально умерло: **{}**'.format(ds['dead']))
    st.sidebar.markdown('Общая летальность: **{}%**'.format(ds['let']))
    st.sidebar.markdown('Выписано: **{}**'.format(ds['ex']))

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
        st.markdown('**v1.2.1** Улушено отображение на мобильных устройствах.')
        st.markdown('**v1.1** Добавлена обработка данных и вывод основных визуализаций.')

        st.subheader('Контакты')
        st.markdown('[Мой блог про machine learning](https://konstantinklepikov.github.io/)')
        st.markdown('[Я на github](https://github.com/KonstantinKlepikov)')
        st.markdown('[Мой сайт немножко про маркетинг](https://yorb.ru/)')
        st.markdown('[Телеграм](https://t.me/KlepikovKonstantin)')
        st.markdown('[Фейсбук](https://facebook.com/konstatin.klepikov)')
    
    elif page == 'cases':
        st.header(p[page])

        # cases
        line_chart = buildchart(paginator[1], 
                            data[['дата', 'всего', 'ОРВИ', 'пневмония', 'без симптомов']],
                            interpolate='linear')
        st.altair_chart(line_chart)

        # area
        line_chart = buildchart('Количество случаев в общей динамике', 
                    data[['дата', 'ОРВИ', 'пневмония', 'без симптомов']], 
                    tchart='area')
        st.altair_chart(line_chart)

        # cumsum 
        line_chart = buildchart('Все случаи заражения кумулятивно', 
                            data[['дата', 'кумул. случаи']], 
                            height=400,
                            interpolate='linear',
                            empty=True,
                            scheme='set1')
        st.altair_chart(line_chart)

    elif page == 'infection rate':
        st.header(p[page])

        line_chart = buildchart(paginator[2], 
                            data[['дата', 'infection rate']], 
                            interpolate='linear', 
                            height=600,
                            level=1,
                            scheme='set1')
        st.altair_chart(line_chart)

    elif page == 'deaths':
        st.header(p[page])

        line_chart = buildchart('умерли от ковид', 
            data[['дата', 'умерли от ковид']], 
            height=400, 
            poly=7,
            tchart='area',
            scheme='set1')
        st.altair_chart(line_chart)

        # cumsum 
        line_chart = buildchart('смертельные случаи нарастающим итогом', 
            data[['дата', 'кумул.умерли']], 
            height=400,
            interpolate='linear',
            empty=True,
            scheme='set1')
        st.altair_chart(line_chart)

        # hospital death data
        st.markdown('Информация об умерших в палатах, отведенных для больных для больных пневмонией/covid предоставлялась мед.службами по запросу newkalingrad.ru')

        line_chart1 = buildchart('умерли в палатах для ковид/пневмонии', 
            data[['дата', 'умерли в палатах для ковид/пневмония с 1 апреля']].query("'2020-11-01' <= дата & `умерли в палатах для ковид/пневмония с 1 апреля` > 0"),
            height=300,
            interpolate='linear',
            point=True,
            empty=True)
        st.altair_chart(line_chart1)

    elif page == 'exits':
        st.header(p[page])

        st.markdown('Нет достоверной информации о том, что лечение выписанных больных в действительности закончено')

        line_chart = buildchart('Выписаны', 
            data[['дата', 'всего', 'выписали']], 
            interpolate='linear',
            scheme='set1')
        st.altair_chart(line_chart)

        # cumsum 
        line_chart = buildchart('Выписаны из больниц нарастающим итогом', 
            data[['дата', 'кумул. случаи', 'кумул.выписаны']], 
            height=400,
            interpolate='linear',
            empty=True,
            scheme='set1')
        st.altair_chart(line_chart)

    elif page == 'capacity':
        st.header(p[page])

        st.header(paginator[5])
        st.markdown('Активные случаи - это заразившиеся минус выписанные и умершие. Болеют ли эти люди в текущий момент на самом деле установить невозможно. Данные о загруженности больниц предоставлены мед.службами.')

        # cumsum minus exit
        line_chart = buildchart('Активные случаи нарастающим итогом', 
            data[['дата', 'кумул.активные']], 
            height=400,
            interpolate='linear',
            empty=True,
            scheme='set1')
        st.altair_chart(line_chart)

        # hospital places
        df = data[['дата', 'доступно под ковид', 'занято под ковид', 'доступно ИВЛ', 'занято ИВЛ', 'доступно под ковид и пневмонию', 'занято под ковид и пневмонию']].query("'2020-11-01' <= дата ")
        df.set_index('дата', inplace=True)
        df = df[(df.T != 0).any()]
        df.reset_index(inplace=True)
        line_chart = buildchart('Доступные места',
            df.replace(0, np.nan), 
            height=400,
            interpolate='linear',
            point=True,
            empty=True)
        st.altair_chart(line_chart)

    elif page == 'tests':
        st.header(p[page])

        line_chart = buildchart('Общее количество тестов', 
            data[['дата', 'кол-во тестов']], 
            height=600,
            interpolate='linear',
            scheme='accent')
        st.altair_chart(line_chart)

        # tesats and cases
        st.markdown('Для наглядности, количество тестов разделено на 10 для приведенных графиков.')

        line_chart = buildchart('Тестирование и распространение болезни', 
            data[['дата', 'ОРВИ', 'пневмония', 'без симптомов', 'кол-во тестов / 10']], 
            height=500,
            interpolate='linear')
        st.altair_chart(line_chart)

        # tests and exit
        line_chart = buildchart('Тестирование и выписка', 
            data[['дата', 'выписали', 'кол-во тестов / 10']], 
            height=600,
            interpolate='linear',
            scheme='set1')
        st.altair_chart(line_chart)

    elif page == 'regions':
        st.header(p[page])

        st.header(paginator[7])

        line_chart = buildchart('Калининград и регионы', 
            data[['дата', 'Калининград', 'все кроме Калининграда']], 
            height=400,
            tchart='area',
            scheme='set1')
        st.altair_chart(line_chart)

        _cols = [col for col in data.columns if 'округ' in col]
        _cols.append('дата')
        _cols.append('Калининград')
        line_chart = buildchart('Распределение случаев по региону', 
            data[_cols], 
            height=600,
            tchart='area',
            scheme='tableau20')
        st.altair_chart(line_chart)

    elif page == 'demographics':
        st.header(p[page])

        st.text('soon...')

    elif page == 'correlations':
        st.header(p[page])

        st.text('soon...')
        # report = ProfileReport(data.drop(['учебные учреждения'], axis=1))
        # st_profile_report(report)

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

main()
