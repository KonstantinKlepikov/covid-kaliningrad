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
