import streamlit as st
import requests
import numpy as np
import pandas as pd

st.write("""Hello world!""")

file_id = '1iAgNVDOUa-g22_VcuEAedR2tcfTlUcbFnXV5fMiqCR8'
file_url = 'https://docs.google.com/spreadsheets/d/{file_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
sheets = ['destrib', 'data', 'places', 'childs', 'rosstat']

all_data = {}
for sheet_name in sheets:
    url = file_url.format_map(vars())

    if __name__ == "__main__":
        get = requests.get(url)
        print(file_url.format_map(vars()))
        print(url, 'get status:', get.status_code, get.encoding)

    all_data[sheet_name] = pd.read_csv(url)

    st.write(sheet_name)
    st.write(all_data[sheet_name].head())

if __name__ == "__main__":

    print(all_data)