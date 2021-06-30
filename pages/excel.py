import pandas as pd
import streamlit as st
import os

from PIL import  Image
from db_helper import DB_Handler
from datetime import datetime
from collections import Counter
from conf import configs
from easydict import EasyDict as edict


def data_preprocessing(df):
    # get columns that we need [row, cols]
    # df = df.iloc[:, 1:17]

    # convert to date_time type
    df.date = pd.to_datetime(df.date,dayfirst=True)
    # df.set_index(df.id)
    return df

def read_file(file_path):
    df = pd.read_csv(file_path, index_col='id')
    df.date = pd.to_datetime(df.date,dayfirst=True)

    print(list(df.columns.values))
    ['id', 'grade_ffb', 'temp_raw', 'lux_raw', 'pest_damaged', 'long_stalk', 'wet', 'dirty', 'dura', 'old', 'unfresh', 'notes', 'tags', 'grader_name', 'date', 'msp_path', 'rgb_path']
    cols = [ 'date',  'grader_name', 'grade_ffb', 'temp_raw', 'lux_raw', 'pest_damaged', 'long_stalk', 'wet', 'dirty', 'dura', 'old', 'unfresh', 'notes', 'tags',  'msp_path', 'rgb_path']
    # st.write(df[['date', 'id','grader_name', 'grade_ffb', 'temp_raw', 'lux_raw','pest_damaged', 'long_stalk', 'wet', 'dirty', 'dura', 'old', 'unfresh', 'notes', 'tags',  'msp_path', 'rgb_path']])
    # st.write(df[cols])
    
    return df[cols]

def excel_page(state):
    st.warning('Ooopsss! This Page is Not Yet Ready!')
    new_df = read_file(file_path='db_ffbs.csv')
    df = data_preprocessing(new_df)
    st.write(df)
