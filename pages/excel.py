import enum
import pandas as pd
import streamlit as st
import os
import shutil
from datetime import datetime as dt
from zipfile import ZipFile

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
    if os.path.exists('db_ffbs.csv') == False:
        st.warning(' No Data ')
        return
    # st.warning('Ooopsss! This Page is Not Yet Ready!')
    new_df = read_file(file_path='db_ffbs.csv')
    df = data_preprocessing(new_df)
    st.write(df.head(10))
    clean_db_images()
    status_zip = st.sidebar.empty()
    if st.button('Zip and Delete'):
        now_= dt.now()
        now_str = now_.strftime("%m%d%Y_%H%M%S")
        folder_dst = os.path.join(now_str, 'db_images')
        os.makedirs(now_str, exist_ok=True)
        shutil.copytree('db_images', folder_dst)
        shutil.copy('db_ffbs.csv', now_str)
        shutil.make_archive(now_str, 'zip', now_str)
        status_zip.success(f'Success created {now_str}!')
        shutil.rmtree('db_images')
        os.remove('db_ffbs.csv')
        status_zip.success(f'Old Data Deleted!')






# --------------- section --------------------------
def clean_db_images():
    path = os.path.join('db_images')
    ls_img = os.listdir(path)
    
    ls_img_to_delete = []

    new_df = read_file(file_path='db_ffbs.csv')
    df = data_preprocessing(new_df)
    ls_id = list(df.index)
    
    count_match = 0
    for img_id in ls_img:
        if img_id not in ls_id:
            ls_img_to_delete.append(img_id)
        else:
            count_match += 1

    ls_images_delete = [os.path.join(path, file) for file in ls_img_to_delete]
    st.write('Matched:', count_match, '| Junk:', len(ls_images_delete))
    if st.button('Clean This Junk'):
        prog = st.progress(0.0)
        for i, img_path in enumerate(ls_images_delete):
            shutil.rmtree(path=img_path)
            prog.progress((i+1)/(len(ls_images_delete)))


    col_1, col_2 = st.beta_columns((1,1))
    col_1.write('Matched: ')
    col_1.write(ls_id)

    col_2.write('Junk: ')
    col_2.write(ls_images_delete)





