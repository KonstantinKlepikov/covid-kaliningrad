import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import os


def buildchart(title, data, type_='quantitative', interpolate='step', height=600, level=False, poly=False, tchart='linear'):
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
    scales = alt.selection_interval(bind='scales')

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
        line = alt.Chart(source).mark_line(interpolate=interpolate
        ).encode(
            alt.X('дата', 
                type='temporal', 
                title='дата', 
                axis=alt.Axis(grid=False, offset=10)
                ),
            alt.Y('y', 
                type=type_, 
                title='количество', 
                axis=alt.Axis(grid=False, offset=10)
                ),
            alt.Color('показатель:N',
                scale=alt.Scale(scheme='dark2')
                ),
            opacity=alt.condition(leg, 
                alt.value(1), 
                alt.value(0.2)
                )
        )

    if tchart == 'point':
        line = alt.Chart(source).mark_point(interpolate=interpolate
        ).encode(
            alt.X('дата', 
                type='temporal', 
                title='дата', 
                axis=alt.Axis(grid=False, offset=10)
                ),
            alt.Y('y', 
                type=type_, 
                title='количество', 
                scale=alt.Scale(zero=False),
                axis=alt.Axis(grid=False, offset=10)
                ),
            alt.Color('показатель:N',
                scale=alt.Scale(scheme='dark2')
                ),
            opacity=alt.condition(leg, 
                alt.value(1), 
                alt.value(0.2)
                )
        )

    if tchart == 'area':
        line = alt.Chart(source).mark_area(interpolate=interpolate
        ).encode(
            alt.X('дата', 
                type='temporal', 
                title='дата', 
                axis=alt.Axis(grid=False, offset=10)
                ),
            alt.Y('y', 
                type=type_, 
                title='количество', 
                scale=alt.Scale(zero=False),
                axis=alt.Axis(grid=False, offset=10)
                ),
            alt.Color('показатель:N',
                scale=alt.Scale(scheme='dark2')
                ),
            opacity=alt.condition(leg, 
                alt.value(1), 
                alt.value(0.2)
                )
        )

    if tchart == 'bar':
        pass

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
    text = line.mark_text(align='right', dx=-5, dy=-10).encode(
        text=alt.condition(nearest, 'y:Q', alt.value(' '))
    )

    # Draw X value on chart
    x_text = line.mark_text(align="left", dx=5, dy=10).encode(
        text=alt.condition(nearest, "дата:T", alt.value(" "), format='%Y-%m-%d')
    )

    # Draw a rule at the location of the selection
    rules = alt.Chart(source).mark_rule(color='gray').encode(
        alt.X('дата', type='temporal')
    ).transform_filter(
        nearest
    )

    # Put the five layers into a chart and bind the data
    chart = alt.layer(
        line, selectors, points, rules, text, x_text
    ).properties(
        title=title,
        width=900,
        height=height
    ).add_selection(
        scales, leg
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
    else:
        return chart


def main():

    data = pd.read_csv('https://raw.githubusercontent.com/KonstantinKlepikov/covid-kaliningrad/datasets/data/data.csv')
    paginator = ['Динамика случаев заражения', 'Infection Rate', 'Данные об умерших', 'Данные о выписке', 'Корреляции (долгая загрузка)']

    data['кумул. случаи'] = data['всего'].cumsum()
    data['кумул.умерли'] = data['умерли от ковид'].cumsum()
    data['кумул.выписаны'] = data['выписали'].cumsum()
    

    page = st.sidebar.radio('Графики', paginator)

    # cases
    if page == paginator[0]:
        st.sidebar.header(paginator[0])
        line_chart = buildchart(paginator[0], 
                            data[['дата', 'всего', 'ОРВИ', 'пневмония', 'без симптомов']], 
                            interpolate='linear')
        st.altair_chart(line_chart)

        # cumsum 
        line_chart = buildchart('Случаи заражения кумулятивно', 
                            data[['дата', 'кумул. случаи']], 
                            height=400,
                            interpolate='linear')
        st.altair_chart(line_chart)

    # ir
    elif page == paginator[1]:
        st.sidebar.header(paginator[1])
        line_chart = buildchart(paginator[1], 
                            data[['дата', 'infection rate']], 
                            interpolate='step', 
                            height=600,
                            level=1)
        st.altair_chart(line_chart)
        st.table(data[['дата', 'infection rate']])

    # death
    elif page == paginator[2]:
        st.sidebar.header(paginator[2])
        line_chart = buildchart('умерли от ковид', 
                            data[['дата', 'умерли от ковид']], 
                            height=400, 
                            poly=7,
                            tchart='area')
        st.altair_chart(line_chart)

        # cumsum 
        line_chart = buildchart('Смертельные случаи кумулятивно', 
                            data[['дата', 'кумул.умерли']], 
                            height=400,
                            interpolate='linear')
        st.altair_chart(line_chart)

        line_chart1 = buildchart('умерли в палатах для ковид/пневмонии', 
                            data[['дата', 'умерли в палатах для ковид/пневмония с 1 апреля']].query("'2020-11-01' <= дата & `умерли в палатах для ковид/пневмония с 1 апреля` > 0"),
                            height=300,
                            poly=2,
                            tchart='point')
        st.altair_chart(line_chart1)

    # exit
    elif page == paginator[3]:
        st.sidebar.header(paginator[3])
        line_chart = buildchart('выписали', 
                            data[['дата', 'всего', 'выписали']], 
                            interpolate='linear')
        st.altair_chart(line_chart)

        # cumsum 
        line_chart = buildchart('Выписаны из больниц кумулятивно', 
                            data[['дата', 'кумул. случаи', 'кумул.выписаны']], 
                            height=400,
                            interpolate='linear')
        st.altair_chart(line_chart)

    elif page == 'Корреляции (долгая загрузка)':
        st.subheader('Корреляции')
        # report = ProfileReport(data.drop(['учебные учреждения'], axis=1))
        # st_profile_report(report)


main()
