import streamlit as st
import numpy as np
import pandas as pd
import os


class Processor:

    def __getattr__(self, attr):
        if attr == 'data':
            return self._data
        else:
            raise AttributeError(attr)

    def __setattr__(self, attr, value):
        if attr == 'data':
            attr = '_data'
        self.__dict__[attr] = value

    def reduce_mem_usage(self, df):
        """
        Reduce numeric 
        
        Parameters
        ----------
        :param df: pandas data frame
            pd.DataFrame object

        Return
        ------

        Pandas data frame object

        Future
        ------

        - optimisation by transfer float to int
        - reduce objects
        """
        numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']

        for col in df.columns:
            col_type = df[col].dtypes
            if col_type in numerics:
                c_min = df[col].min()
                c_max = df[col].max()
                if str(col_type)[:3] == 'int':
                    if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                        df[col] = df[col].astype(np.int8)
                    elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                        df[col] = df[col].astype(np.int16)
                    elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                        df[col] = df[col].astype(np.int32)
                    elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                        df[col] = df[col].astype(np.int64)  
                else:
                    if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                        df[col] = df[col].astype(np.float16)
                    elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                        df[col] = df[col].astype(np.float32)
                    else:
                        df[col] = df[col].astype(np.float64)

        return df

def loader():

    all_data = {}
    names = os.listdir('data')

    for name in names:
        file_name, file_extension = os.path.splitext(name)
        if file_extension == '.csv':
            all_data[file_name] = pd.read_csv(os.path.join('data', name))

    return all_data


def main():

    page = st.sidebar.selectbox('Представление данных', ['В виде графиков', 'В виде таблиц'])

    all_data = loader()

    if page == 'В виде графиков':
        st.header('Графики')
    elif page == "В виде таблиц":
        st.header('Таблицы')
        for i in all_data.items():
            st.write(i[0])
            st.table(i[1])

if __name__ == "__main__":

    main()
