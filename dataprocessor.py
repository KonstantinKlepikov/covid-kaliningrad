import requests
import numpy as np
import pandas as pd
import os


def loader(file_id, file_url, sheet_name):

    url = file_url.format_map(vars())
    get = requests.get(url)
    if get.status_code == 200:
        if sheet_name == 'data':
            table = pd.read_csv(url, parse_dates=['дата'], dayfirst=True)
        else:
            table = pd.read_csv(url)
    return table

def pathMaker(slug):

    return os.path.join('data', slug + '.csv')


def main():

    file_id = '1iAgNVDOUa-g22_VcuEAedR2tcfTlUcbFnXV5fMiqCR8'
    file_url = 'https://docs.google.com/spreadsheets/d/{file_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    sheets = ['data', 'destrib', 'rosstat']

    loaded = {}
    for sheet_name in sheets:
        loaded[sheet_name] = loader(file_id, file_url, sheet_name)

    # data
    loaded['data'].fillna(0, inplace=True)
    loaded['data']['infection rate'] = loaded['data']['infection rate'].apply(lambda x: str(x))
    loaded['data']['infection rate'] = loaded['data']['infection rate'].apply(lambda x: x.replace(',', '.'))
    loaded['data']['infection rate'] = loaded['data']['infection rate'].astype(np.float16)  
#     loaded['data']['infection rate'] = loaded['data']['infection rate'].round(2)
    for i in loaded['data'].columns.difference(['дата', 'infection rate', 'учебные учреждения']):
        loaded['data'][i] = loaded['data'][i].astype(np.int16)
    loaded['data'].to_csv(pathMaker('data'), index=False)

    # destrib
    loaded['destrib'].fillna(0, inplace=True)
    for i in loaded['destrib'].columns.difference(['дата']):
        loaded['destrib'][i] = loaded['destrib'][i].astype(np.int8)
    loaded['destrib'].to_csv(pathMaker('destrib'), index=False)

    # rosstat
    loaded['rosstat'].fillna(0, inplace=True)
    for i in loaded['rosstat'].columns.difference(['Месяц']):
        loaded['rosstat'][i] = loaded['rosstat'][i].astype(np.int16)
    loaded['rosstat'].to_csv(pathMaker('rosstat'), index=False)
    

if __name__ == "__main__":

    main()