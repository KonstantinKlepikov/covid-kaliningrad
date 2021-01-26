import streamlit as st
import numpy as np
import pandas as pd


"""Support functions for data visualistion, wraped with cache decorator
reduces app loading time
"""


cTime = 900. # cache time


@st.cache(allow_output_mutation=True, ttl=cTime)
def dataloader(url):
    """Load .csv data

    Args:
        url (string): public url for load

    Returns:
        pandas DataFrame: loaded data
    """
    return pd.read_csv(url)


@st.cache()
def pagemaker():
    """Make a site paginator

    Returns:
        dict, list: dict, where keys are names for tabs of paginator, values are strings for headers of pages
        list of keys is used for create streamlit paginator
    """
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
    """Create data for sidebar

    Args:
        data (pandas DataFrame): main data
        people (int, optional): number of people, who leaves in region. Defaults to 1012512.

    Returns:
        dict: where keys are name ofe fields, and values are values
    """
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
    """Invitro data prepairing

    Args:
        data (pandas DataFrame): main data

    Returns:
        pandas DataFrame: prepared data
    """
    data['shape'] = data['positive'] * 100 / data['total']
    data['shape'] = data['shape'].astype(np.float16)
    data['shape'] = data['shape'].apply(lambda x: round(x, 2))
    return data


@st.cache()
def regDistr(data):
    """Make list of columns name for creating region cases destribution

    Args:
        data (pandas DataFrame): main data

    Returns:
        list of strings: list of columns name
    """
    _cols = [col for col in data.columns if 'округ' in col]
    _cols.append('дата')
    _cols.append('Калининград')
    return _cols


@st.cache(ttl=cTime)
def slicedData(data, query):
    """Slice data and remove zeros for point sparced charts

    Args:
        data (pandas DataFrame): main data

    Returns:
        pandas DataFrame: prepared data
    """
    df = data.query(query)
    df.set_index('дата', inplace=True)
    df = df[(df.T != 0).any()]
    df.reset_index(inplace=True)
    return df.replace(0, np.nan)


@st.cache(ttl=cTime)
def irDestrib(data):
    """Calculate destribution of Infection Rate

    Args:
        data (pandas DataFrame): main data

    Returns:
        pandad DataFrames: two frames with destribution of Infection Rate
    """
    df = data[['дата', 'infection rate']]
    high = df[df['infection rate'] >= 1].shape[0]
    low = df[df['infection rate'] < 1].shape[0]
    return high, low


@st.cache(ttl=cTime)
def profession(data):
    """Make list of columns name for creating profession cases destribution

    Args:
        data (pandas DataFrame): main data

    Returns:
        list of strings: list of columns name
    """
    _cols = [col for col in data.columns if '>' in col]
    _cols.append('дата')
    return _cols


@st.cache()
def ageDestr(data):
    """Make list of ages for age destribution chart

    Args:
        data (pandas DataFrame): main data

    Returns:
        list of strings: list of ages
    """
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
