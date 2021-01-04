import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from pandas_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report
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


def linechart(title, data, type_='quantitative', interpolate='step', height=600):

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

    scales = alt.selection_interval(bind='scales')
    source = data.melt('дата', var_name='category', value_name='y')
    chart = alt.Chart(source).mark_line(interpolate=interpolate
    ).encode(
        alt.X('дата', type='temporal', title='Дата'),
        alt.Y('y', type=type_, title='Количество'),
        color='category:N',
        tooltip=['дата:T', 'y:N']
    ).properties(
        title=title,
        width=900,
        height=height
    ).add_selection(
        scales
    )

    return chart


# def servloader():

#     page = st.sidebar.selectbox('Представление данных', ['В виде графиков', 'В виде таблиц'])

#     all_data = {}
#     names = os.listdir('data')

#     for name in names:
#         file_name, file_extension = os.path.splitext(name)
#         if file_extension == '.csv':
#             all_data[file_name] = pd.read_csv(os.path.join('data', name))

#     if page == 'В виде графиков':
#         st.header('Графики')
#     elif page == "В виде таблиц":
#         st.header('Таблицы')
#         for i in all_data.items():
#             st.write(i[0])
#             st.table(i[1])


def main():

    data = pd.read_csv('https://raw.githubusercontent.com/KonstantinKlepikov/covid-kaliningrad/main/data/data.csv')
    data = reduce_mem_usage(data)
    paginator = ['Динамика случаев заражения', 'Infection Rate', 'Данные об умерших', 'Корреляции (долгая загрузка)']

    page = st.sidebar.radio('Графики', paginator)

    if page == paginator[0]:
        # cases

        st.sidebar.header(paginator[0])
        line_chart = linechart(paginator[0], data[['дата', 'всего', 'ОРВИ', 'пневмония', 'без симптомов']], interpolate='linear')
        st.altair_chart(line_chart)

    elif page == paginator[1]:
        # ir
        
        st.sidebar.header(paginator[1])
        df = data[['дата', 'infection rate']]
        df['infection rate'] = df['infection rate'].apply(lambda x: x.replace(',', '.'))
        df['infection rate'] = df['infection rate'].apply(lambda x: float(x))
        line_chart = linechart(paginator[1], df, interpolate='step', height=400)
        st.altair_chart(line_chart)
        st.table(data['infection rate'])

    elif page == paginator[2]:
        # death
     
        st.sidebar.header(paginator[2])
        line_chart = linechart('умерли от ковид', data[['дата', 'умерли от ковид']], height=400)
        st.altair_chart(line_chart)

        line_chart1 = linechart('умерли в палатах для ковид/пневмонии', data[['дата', 'умерли в палатах для ковид/пневмония с 1 апреля']], height=300)
        st.altair_chart(line_chart1)

    elif page == 'Корреляции (долгая загрузка)':
        st.subheader('Корреляции')
        # report = ProfileReport(data.drop(['учебные учреждения'], axis=1))
        # st_profile_report(report)


main()
