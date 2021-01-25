import streamlit as st
import numpy as np
import pandas as pd
import os


cTime = 900. # cache time


@st.cache(allow_output_mutation=True, ttl=cTime)
def dataloader(url):
    return pd.read_csv(url)


@st.cache()
def pagemaker():
    p = {'intro': 'Введение',
    'cases': 'Динамика заражения', 
    'infection rate': 'Infection Rate', 
    'deaths': 'Данные об умерших', 
    'exits': 'Данные о выписке', 
    'capacity': 'Нагрузка на систему', 
    'tests': 'Тестирование', 
    'vaccination': 'Вакцинация',
    'regions': 'Регионы',
    'demographics': 'Демография',
    'correlations': 'Корреляции'
    }
    paginator = [n for n in p.keys()]

    return p, paginator


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


@st.cache(ttl=cTime)
def invitroCases(data):
    data['shape'] = data['positive'] * 100 / data['total']
    data['shape'] = data['shape'].astype(np.float16)
    data['shape'] = data['shape'].apply(lambda x: round(x, 2))
    return data


@st.cache()
def regDistr(data):
    _cols = [col for col in data.columns if 'округ' in col]
    _cols.append('дата')
    _cols.append('Калининград')
    return _cols


@st.cache(ttl=cTime)
def slicedData(data, query):
    df = data.query(query)
    df.set_index('дата', inplace=True)
    df = df[(df.T != 0).any()]
    df.reset_index(inplace=True)
    return df.replace(0, np.nan)


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
