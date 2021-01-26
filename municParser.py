import numpy as np
import pandas as pd
import dataLoader as dl


"""Clean and convert pandas DataFrame data of municipality infection cases destribution, 
and save it as .csv.
"""

file_id = '1Gt8Rn8Md4FJRJ7f44h53v1uvCCpYh-qmZVe5mayedCA'
file_url = 'https://docs.google.com/spreadsheets/d/{file_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
sheets = ['munic']

loaded = {}
for sheet_name in sheets:
    loaded[sheet_name] = dl.loader(file_id, file_url, sheet_name)


# table data preparing
data = loaded['munic']

# transform data
data.drop('ID', axis=1, inplace=True)
data = data.pivot(index='Дата', columns='Регион', values='Выявлено')
data.loc['2020-05-19'] = 0
data.index = pd.to_datetime(data.index, dayfirst=True)
data.sort_index(inplace=True)
data.fillna(method='ffill', inplace=True)
data = data.diff()
data.fillna(method='ffill', inplace=True)
data.fillna(0, inplace=True)
data = data.astype(np.int16)
data.reset_index(inplace=True)

# flush
data.to_csv(dl.pathMaker('munic'), index=False)
