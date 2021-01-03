import streamlit as st
import numpy as np
import pandas as pd
from pandas_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report
import altair as alt
import matplotlib.pyplot as plt
plt.style.use('seaborn-white')
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

def servloader():

    page = st.sidebar.selectbox('Представление данных', ['В виде графиков', 'В виде таблиц'])

    all_data = {}
    names = os.listdir('data')

    for name in names:
        file_name, file_extension = os.path.splitext(name)
        if file_extension == '.csv':
            all_data[file_name] = pd.read_csv(os.path.join('data', name))

    if page == 'В виде графиков':
        st.header('Графики')
    elif page == "В виде таблиц":
        st.header('Таблицы')
        for i in all_data.items():
            st.write(i[0])
            st.table(i[1])


def main():

    data = pd.read_csv('https://raw.githubusercontent.com/KonstantinKlepikov/covid-kaliningrad/main/data/data.csv', index_col='дата')
    data.index = pd.to_datetime(data.index)
    # data['дата'] = pd.to_datetime(data['дата'])
    data = reduce_mem_usage(data)

    page = st.sidebar.selectbox('Представление данных', ['В виде графиков', 'В виде таблиц', 'Отчет о данных (долгая загрузка)'])

    if page == 'В виде графиков':
        st.header('Графики')

        st.subheader('Динамика случаев заражения')

        data_tech = data[['всего', 'ОРВИ', 'пневмония', 'без симптомов']]

        st.line_chart(data_tech, use_container_width=True)
        
        # st.vega_lite_chart(data[['дата', 'всего', 'ОРВИ', 'пневмония', 'без симптомов']], {
        #     'mark': 'trail',
        #     "width": 500, "height": 300,
        #     'encoding': {
        #         'x': {'field': 'дата', 'type': 'temporal'},
        #         'y': {'field': 'всего', 'type': 'quantitative'},
        #         'size': {'field': 'всего', 'type': 'quantitative'},
        #         },
        #         })

        fig, ax = plt.subplots(figsize=(12, 8))
        ax.plot(data.index, data['всего'], label='всего')
        st.pyplot(fig)

    elif page == "В виде таблиц":
        st.header('Таблицы')
        st.table(data)
    
    elif page == 'Отчет о данных (долгая загрузка)':
        st.subheader('Отчет о данных')
        # report = ProfileReport(data.drop(['учебные учреждения'], axis=1))
        # st_profile_report(report)


main()
