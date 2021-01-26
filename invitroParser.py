import os
import re
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import dataLoader as dl

path = 'parse_invitro/invitro.html'
forparse = os.path.realpath(path)

def htmlParse(path):
    """[Parse data from html (Invitro clinic data)

    Returns:
        pandas DataFrame: parsed data
    """

    column_names = ['date', 'total', 'negative', 'positive']
    df = pd.DataFrame(columns = column_names)

    with open(path, 'r', encoding='utf-8') as file_open:
        html_obj = BeautifulSoup(file_open, 'html.parser', from_encoding='utf-8')

        for tag in html_obj.find_all('div', id=re.compile('^group-')):
            month = tag.find('div', class_=re.compile('-month'))

            for sub in tag.find_all('div', id=re.compile('^day-')):
                total = sub.find('div', class_=re.compile('-total'))
                negative = sub.find('div', class_=re.compile('-negative'))
                positive = sub.find('div', class_=re.compile('-positive'))

                df = df.append(
                    {'date': month.get_text() + '-' + sub['id'],
                    'total': total.get_text(),
                    'negative': negative.get_text(),
                    'positive': positive.get_text()
                    }, ignore_index=True
                )

    return df


if __name__ == '__main__':

    data = htmlParse(forparse)
    data.to_csv(dl.pathMaker('invitro'), index=False)
    