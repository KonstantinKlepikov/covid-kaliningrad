import requests
import numpy as np
import pandas as pd
import os


def loader(file_id, file_url, sheets):

    for sheet_name in sheets:
        url = file_url.format_map(vars())
        get = requests.get(url)
        if get.status_code == 200:
            table = pd.read_csv(url)
            table.fillna(-1, inplace=True)
            path = os.path.join('data', sheet_name + '.csv')
            table.to_csv(path, index=False)


def main():

    file_id = '1iAgNVDOUa-g22_VcuEAedR2tcfTlUcbFnXV5fMiqCR8'
    file_url = 'https://docs.google.com/spreadsheets/d/{file_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    sheets = ['data', 'destrib', 'rosstat']

    loader(file_id, file_url, sheets)


if __name__ == "__main__":

    main()