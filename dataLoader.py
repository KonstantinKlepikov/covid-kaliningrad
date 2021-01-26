import requests
import numpy as np
import pandas as pd
import os


def loader(file_id, file_url, sheet_name):
    """Load the data from google sheets

    Args:
        file_id (string): id of table on google sheets service
        file_url (string): public url of table on google sheets service
        sheet_name (string): name of sheet tab

    Returns:
        pandas DataFrame: loaded data
    """

    url = file_url.format_map(vars())
    get = requests.get(url)
    if get.status_code == 200:
        if sheet_name == 'data':
            table = pd.read_csv(url, parse_dates=['дата'], dayfirst=True)
        else:
            table = pd.read_csv(url)
    return table

def pathMaker(slug):
    """Make a path for local data save/load

    Args:
        slug (string): path slug to folder

    Returns:
        string: path for load/save
    """

    return os.path.join('data', slug + '.csv')
