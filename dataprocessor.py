import numpy as np
import pandas as pd
import dataLoader as dl


def main():
    """Clean and convert pandas DataFrame main data, and save it as .csv. Function is used
    in github acrion. For details look at .github/workflows/dataloader.yml
    """

    file_id = '1iAgNVDOUa-g22_VcuEAedR2tcfTlUcbFnXV5fMiqCR8'
    file_url = 'https://docs.google.com/spreadsheets/d/{file_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    sheets = ['data', 'destrib', 'rosstat']

    loaded = {}
    for sheet_name in sheets:
        loaded[sheet_name] = dl.loader(file_id, file_url, sheet_name)


    # table data preparing
    data = loaded['data']

    # replace nan to zeros
    data.fillna(0, inplace=True)

    # replace , by . in float numeric
    data['infection rate'] = data['infection rate'].apply(lambda x: str(x))
    data['IR7'] = data['IR7'].apply(lambda x: str(x))
    data['infection rate'] = data['infection rate'].apply(lambda x: x.replace(',', '.'))
    data['IR7'] = data['IR7'].apply(lambda x: x.replace(',', '.'))

    # calculate cumulative metrics
    data['кумул. случаи'] = data['всего'].cumsum()
    data['кумул.умерли'] = data['умерли от ковид'].cumsum()
    data['кумул.выписаны'] = data['выписали'].cumsum()
    data['кумул.активные'] = data['кумул. случаи'].sub(data['кумул.выписаны']).sub(data['кумул.умерли'])

    # scaling for tests
    data['кол-во тестов / 10'] = data['кол-во тестов'] / 10

    # region columns
    data['все кроме Калининграда'] = data.filter(regex='округ').sum(axis=1)

    # drop textual data
    data.drop(['учебные учреждения'], axis=1, inplace=True)

    # calculate attitude for infection rate
    data['infection rate'] = data['infection rate'].astype(np.float16) 
    data['plus'] = data[data['infection rate'] >= 1]['infection rate']
    data['minus'] = data[data['infection rate'] < 1]['infection rate']
    data['plus'] = data['plus'].mask(data['plus'] >= 0, 1)
    data['minus'] = data['minus'].mask(data['minus'] >= 0, 1)
    data['plus'] = data['plus'].cumsum()
    data['minus'] = data['minus'].cumsum()
    data[['plus', 'minus']] = data[['plus', 'minus']].astype("object").fillna(method='ffill')
    data['отношение'] = data['plus'] / data['minus']
    data.drop(['plus', 'minus'], axis=1, inplace=True)

    # minimize numerics memory sizes
    data['IR7'] = data['IR7'].astype(np.float16)
    data['отношение'] = data['отношение'].astype(np.float16)
    data['отношение'] = data['отношение'].apply(lambda x: round(x, 2))
    data['кол-во тестов кумул'] = data['кол-во тестов кумул'].astype(np.int32)
    for i in data.columns.difference(['дата', 'infection rate', 'IR7', 'отношение', 'кол-во тестов / 10', 'кол-во тестов кумул']):
        data[i] = data[i].astype(np.int16)


    # flush
    data.to_csv(dl.pathMaker('data'), index=False)


    # table destrib preparing
    destrib = loaded['destrib']

    destrib.fillna(0, inplace=True)
    for i in destrib.columns.difference(['дата']):
        destrib[i] = destrib[i].astype(np.int8)
    destrib.to_csv(dl.pathMaker('destrib'), index=False)

    # table rosstat preparing
    rosstat = loaded['rosstat']

    rosstat.fillna(0, inplace=True)
    for i in rosstat.columns.difference(['Месяц']):
        rosstat[i] = rosstat[i].astype(np.int16)
    rosstat.to_csv(dl.pathMaker('rosstat'), index=False)


main()
