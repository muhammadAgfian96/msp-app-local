import streamlit as st
import plotly.graph_objects as go
import os
import json
import time

from PIL import  Image
from db_helper import DB_Handler
from datetime import datetime
from collections import Counter
from conf import configs

from pages.summary import get_length_data, sidebar_summarize, get_data_by_filter, get_data


        
conf = configs()

def delete_one_file(filename, id_):
    exp_id = "04d2d438f41649058e933a6f39451de3"
    
    if len(id_) != len(exp_id):
        print("id is not complete!")
        return

    with open(filename, "r") as f:
        lines = f.readlines()
        len_old_data = len(lines)

    with open(filename, "w") as f:
        for line in lines:
            if id_ not in line:
                f.write(line)
            else:
                print(line)
                id_deleted = line.split(',')[0]

    with open(filename, "r") as f:
        lines = f.readlines()
        len_new_data = len(lines)        
                
    if len_old_data > len_new_data:
        print("succes delete")
        return True, id_deleted
    else:
        print("not delete any items/ id not found")
        return False, 0

def delete_id(id_):
    db = DB_Handler(**conf['db_setting'])
    result = db.delete_id(id_)
    db.close_connections()
    return result

def show_delete(all_data):
    all_data.sort_values(by=['date'], inplace=True, ascending=False)

    data_dict={}
    data_dict['grade_ffb'] = list(all_data['grade_ffb'].values.tolist())
    data_dict['grader_name'] = list(all_data['grader_name'].values.tolist())
    data_dict['rgb_path'] = list(all_data['rgb_path'].values.tolist())
    data_dict['msp_path'] = list(all_data['msp_path'].values.tolist())
    data_dict['time_input'] = list(all_data['date'].values)
    data_dict['id'] = list(all_data.index.tolist())
    print(data_dict['time_input'])
    status_btn = {}

    c = st.beta_columns((1,1,1,1,1,1))
    c[0].write('### **Date**')
    c[1].write('### **RGB Image**')
    c[2].write('### **MSP Image**')
    c[3].write('### **Grader Name**')
    c[4].write('### **Grade (Maturity)**')
    c[5].write('### **Delete Button**')
    # st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<hr>', unsafe_allow_html=True)

    for i, id_ in enumerate(data_dict['id']):
        c = st.beta_columns((1,1,1,1,1,1))
        # date_add = data['time_input'].strftime("%a, %d-%b-%Y, %I:%M %p")
        date_add = data_dict['time_input'][i].item()
        date_add = datetime.fromtimestamp(date_add/1e9)
        date_add = date_add.strftime("%a, %d-%b-%Y, %I:%M %p")

        c[0].write(date_add)
        # c[1].write(data['_id'])
        c[1].image(data_dict['rgb_path'][i], width=150)
        c[2].image(data_dict['msp_path'][i], width=150)
        c[3].write(data_dict['grader_name'][i])
        c[4].write(data_dict['grade_ffb'][i])
        state_btn = c[5].button(f'delete {str(data_dict["id"][i])[0:10]}')
        status_btn[str(data_dict["id"][i])] = state_btn
        st.markdown('<hr>', unsafe_allow_html=True)
        if i+1 >= 5:
            break

    for id_ in list(status_btn.keys()):
        if status_btn[id_]:
            isDeleted, id_deleted = delete_one_file('db_ffbs.csv',id_)
            if isDeleted:
                c1,c2=st.beta_columns((1,1))
                st.sidebar.success(f'Delete {id_deleted}')
                st.sidebar.warning(f'Please Refresh or Press \'R\'')
            else:
                st.sidebar.write('Not Data Deleted!')
    pass

def delete_page(state):
    # if get_length_data() <=0:
    #     st.warning(' No Data ')
    #     return
    params = sidebar_summarize(state)
    if params['filter'].lower() == 'all':
        st.write('## Last 5 Data')
        all_data = get_data()
    else:
        start = params.get('start_date')
        end = params.get('end_date')

        filters_param = {
            "start_date": start,
            "end_date": end,
            "grader_name" : params.get('grader_name'),
            "grade_ffb" : params.get('grade_ffb'),
            "unfresh" : params.get('unfresh'),
            "old" : params.get('old'),
            "dura" : params.get('dura'),
            "dirty" : params.get('dirty'),
            "wet" : params.get('wet'),
            "long_stalk" : params.get('long_stalk'),
        }
        st.write(f"## Data {start.day}/{start.month}/{start.year} - {end.day}/{end.month}/{end.year}")
        all_data = get_data_by_filter(**filters_param)
    show_delete(all_data)
