import streamlit as st
import plotly.graph_objects as go

from datetime import datetime
from conf import configs

from pages.summary import sidebar_summarize, get_data, set_state_params_none
from csv_handler import CsvHandler
import os
db_csv = CsvHandler()
conf = configs()

def show_delete(state, all_data):
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
            isDeleted, id_deleted = db_csv.delete_one_file(id_)
            if isDeleted:
                c1,c2=st.beta_columns((1,1))
                state.default = db_csv.get_default_value()
                print(state.default)
                set_state_params_none(state)

                st.sidebar.success(f'Delete {id_deleted}')
                st.sidebar.warning(f'Please Refresh or  \'R\'')
            else:
                st.sidebar.write('Not Data Deleted!')


def delete_page(state):
    if os.path.exists('db_ffbs.csv') == False:
        st.warning(' No Data ')
        return
    if db_csv.get_length_data() <=0:
        st.warning(' No Data ')
        return

    params = sidebar_summarize(state)
    if params['filter'].lower() == 'all':
        st.write('## Last 5 Data')
        all_data = get_data()
        start = params.get('start_date')
        end = params.get('end_date')
        st.write(f"## Data {start.day}/{start.month}/{start.year} - {end.day}/{end.month}/{end.year}")
    else:
        start = params.get('start_date')
        end = params.get('end_date')
        st.write(f"## Data {start.day}/{start.month}/{start.year} - {end.day}/{end.month}/{end.year}")
        
        all_data = db_csv.get_data_by_filter(**params)
    show_delete(state, all_data)
