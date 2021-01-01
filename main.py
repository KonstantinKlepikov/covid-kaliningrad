import streamlit as st
import requests
import numpy as np
import pandas as pd


def loader(file_id, file_url, sheets):
    all_data = {}
    for sheet_name in sheets:
        url = file_url.format_map(vars())
        get = requests.get(url)
        if get.status_code == 200:
            table = pd.read_csv(url)
            all_data[sheet_name] = table
    return all_data

def main():

    file_id = '1iAgNVDOUa-g22_VcuEAedR2tcfTlUcbFnXV5fMiqCR8'
    file_url = 'https://docs.google.com/spreadsheets/d/{file_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    sheets = ['destrib', 'data', 'places', 'childs', 'rosstat']

    page = st.sidebar.selectbox('Представление данных', ['В виде графиков', 'В виде таблиц'])

    all_data = loader(file_id, file_url, sheets)

    if page == 'В виде графиков':
        st.header('Графики')
    elif page == "В виде таблиц":
        st.header('Таблицы')
        for i in all_data.items():
            st.write(i[0])
            st.table(i[1])

if __name__ == "__main__":

    main()
