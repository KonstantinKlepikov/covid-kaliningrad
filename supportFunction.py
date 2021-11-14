import streamlit as st
import numpy as np
import pandas as pd
from drawTools import Linear


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
    'capacity': 'Нагрузка на систему', 
    'tests': 'Тестирование', 
    'vaccination': 'Вакцинация',
    'regions': 'Регионы',
    'regions detail': 'Регионы (детально)',
    'demographics': 'Демография',
    'demographics detail': 'Демография (детально)'
    }
    paginator = [n for n in p.keys()]

    return p, paginator


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
def nonzeroData(data):
    """Remove zeros for point sparced charts

    Args:
        data (pandas DataFrame): main data

    Returns:
        pandas DataFrame: prepared data
    """
    data.set_index('дата', inplace=True)
    data = data[(data.T != 0).any()]
    data.reset_index(inplace=True)
    return data.replace(0, np.nan)


@st.cache(suppress_st_warning=True, ttl=cTime)
def asidedata(data, rstat, people=1012512):
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
    pr = slicedData(data[['дата', 'компонент 1', 'компонент 2']], "'2020-08-01' <= дата ")
    ds['pr1'] = int(pr['компонент 1'].iloc[-1])
    ds['pr2'] = int(pr['компонент 2'].iloc[-1])
    ds['prproc1'] = round(ds['pr1']* 100 / people, 2)
    ds['prproc2'] = round(ds['pr2']* 100 / people, 2)
    ds['rstat_dead'] = rstat['умерли от ковид, вирус определен'].sum() + rstat['предположительно умерли от ковид'].sum() + rstat['умерли не от ковид, вирус оказал влияние'].sum() + rstat['умерли не от ковид, не оказал влияние'].sum()
    # rosstat lerality
    d = rstat['Месяц'].iloc[-1].split('.')
    d.reverse()
    ds['rstat_date'] = '-'.join(d)
    ds['rstat_sick'] = data.set_index('дата').loc[:ds['rstat_date'], 'всего'].sum()
    ds['rstat_let'] = round(ds['rstat_dead'] * 100 / ds['rstat_sick'], 2)
    # covid/pneumonia letality
    lock = data.loc[data['умерли в палатах для ковид/пневмония с 1 апреля'].idxmax()]
    ds['cov_pnew_dead'] = lock['умерли в палатах для ковид/пневмония с 1 апреля']
    ds['cov_pnew_date'] = lock['дата']
    cov_all = data.set_index('дата').loc[:lock['дата'], 'всего'].sum()
    ds['cov_pnew_let'] = round(ds['cov_pnew_dead'] * 100 / cov_all, 2)
    # vaccinated letality
    ds['vacc_cases']  = data['привитых'].max()
    ds['vacc_proc_full'] = round(ds['vacc_cases'] * 100 / people , 2)
    ds['vacc_proc'] = round(ds['vacc_cases']  * 100 / ds['sick'] , 2)
    ds['vacc_proc_vac'] = round(ds['vacc_cases']  * 100 / ds['pr2'] , 2)
    ds['vacc_dead']  = data['привитых умерло'].max()
    ds['vacc_let']  = round(ds['vacc_dead'] * 100 / ds['vacc_cases'], 2)

    return ds


@st.cache(ttl=cTime)
def ratio(data, above, below):
    """Ratio of dara

    Args:
        data (pandas DataFrame): main data
        above (str): above column name
        below (str: below column name)

    Returns:
        pandas DataFrame: prepared data
    """
    data['shape'] = data[above] * 100 / data[below]
    data['shape'] = data['shape'].astype(np.float16)
    data['shape'] = data['shape'].apply(lambda x: round(x, 2))
    return data[['дата', 'shape']]


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

@st.cache(allow_output_mutation=True)
def precision(title, data):
    ch = Linear(
        title, 
        data, 
        height=120,
        grid=False
        )
    ch.legend=None
    ch.draw()
    ch.richchart()
    return ch.emptychart()
