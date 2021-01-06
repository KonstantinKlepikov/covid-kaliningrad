import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import os


def reduce_mem_usage(df):
    """Reduce numeric

    Args:
        df (pandas data frame object): 

    Returns:
        obj: reduced pandas data frame
    """
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']

    for col in df.columns:
        col_type = df[col].dtypes
        if col_type in numerics:
            c_min = df[col].min()
            c_max = df[col].max()
            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)  
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)
    return df


def linechart(title, data, type_='quantitative', interpolate='step', height=600, level=False, poly=False):
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

    # Create main chart
    line = alt.Chart(source).mark_line(interpolate=interpolate
    ).encode(
        alt.X('дата', type='temporal', title='дата', axis=alt.Axis(grid=False, offset=10)),
        alt.Y('y', type=type_, title='количество', axis=alt.Axis(grid=False, offset=10)),
        color='показатель:N'
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
        opacity=alt.condition(nearest,alt.value(1), alt.value(0))
    )

    # Draw text labels near the points, and highlight based on selection
    text = line.mark_text(align='left', dx=5, dy=-5).encode(
        text=alt.condition(nearest, 'y:Q', alt.value(' '))
    )

    # Draw a rule at the location of the selection
    rules = alt.Chart(source).mark_rule(color='gray').encode(
        alt.X('дата', type='temporal')
    ).transform_filter(
        nearest
    )

    # Put the five layers into a chart and bind the data
    chart = alt.layer(
        line, selectors, points, rules, text
    ).properties(
        title=title,
        width=900,
        height=height
    ).add_selection(
        scales
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
                [str(order)], as_=['degree', 'y']
            ).encode(alt.Color('degree:N'))
            for order in degree_list
        ]
        return alt.layer(chart, *polynomial_fit)
    # Empty
    else:
        return chart


def main():

    data = pd.read_csv('https://raw.githubusercontent.com/KonstantinKlepikov/covid-kaliningrad/datasets/data/data.csv')
    paginator = ['Динамика случаев заражения', 'Infection Rate', 'Данные об умерших', 'Корреляции (долгая загрузка)']

    page = st.sidebar.radio('Графики', paginator)

    # cases
    if page == paginator[0]:
        st.sidebar.header(paginator[0])
        line_chart = linechart(paginator[0], data[['дата', 'всего', 'ОРВИ', 'пневмония', 'без симптомов']], interpolate='linear')
        st.altair_chart(line_chart)

    # ir
    elif page == paginator[1]:
        st.sidebar.header(paginator[1])
        line_chart = linechart(paginator[1], data[['дата', 'infection rate']], interpolate='step', height=400, level=1)
        st.altair_chart(line_chart)
        st.table(data[['дата', 'infection rate']])

    # death
    elif page == paginator[2]:
        st.sidebar.header(paginator[2])
        line_chart = linechart('умерли от ковид', data[['дата', 'умерли от ковид']], height=400, poly=5)
        st.altair_chart(line_chart)

        line_chart1 = linechart('умерли в палатах для ковид/пневмонии', data[['дата', 'умерли в палатах для ковид/пневмония с 1 апреля']].query("'2020-11-01' <= дата"), height=300)
        st.altair_chart(line_chart1)

    elif page == 'Корреляции (долгая загрузка)':
        st.subheader('Корреляции')
        # report = ProfileReport(data.drop(['учебные учреждения'], axis=1))
        # st_profile_report(report)


main()
