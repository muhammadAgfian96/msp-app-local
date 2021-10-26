import streamlit as st
import plotly.graph_objects as go

from datetime import datetime, timedelta
from collections import Counter
from conf import configs
from csv_handler import CsvHandler
# from easydict import Easydict as edict
import os
import numpy as np

db_csv = CsvHandler()
conf = configs()


def get_data():
    return db_csv.get_data()

def data_viz(all_data):
    def bar_graph( title, X, Y, place=st):
        # place.write(title)
        layout_custom =  {
                "title": title.split(' ')[-1].upper(),
                "xaxis": {"title": title.split(' ')[-1], 'side': 'bottom'},
                "yaxis": {"title": "count"},
                'width': 500,
                'height':400,
                'autosize':False,
        }
        if 'grader_name' in title or 'grade_ffb' in title:
            layout_custom =  {
                    "title": title.split(' ')[-1].upper(),
                    "xaxis": {"title": title.split(' ')[-1], 'side': 'bottom'},
                    "yaxis": {"title": "count"},
                    'autosize': True,
            }
        fig = go.Figure(
            [go.Bar(
                x=X, y=Y,
                marker_color=conf['colors_graph_gradient'][i],
                marker_line_color='rgb(17, 69, 126)',
                marker_line_width=1,
                opacity=0.7
                )],
            layout = layout_custom
            )
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
        place.write(fig)

    def histogram_graph( title, X, Y, place=st):
        # place.write(title)
        layout_custom =  {
                "title": title.split(' ')[-1].upper(),
                "xaxis": {"title": title.split(' ')[-1], 'side': 'bottom'},
                "yaxis": {"title": "count"},
                'width': 500,
                'height':400,
                'autosize':False,
        }
        if 'grader_name' in title or 'grade_ffb' in title:
            layout_custom =  {
                    "title": title.split(' ')[-1].upper(),
                    "xaxis": {"title": title.split(' ')[-1], 'side': 'bottom'},
                    "yaxis": {"title": "count"},
                    'autosize':True,
                    
            }
        fig=   go.Figure(
            data=[
                go.Histogram(
                    x=X,
                    y=Y,
                    marker_color=conf['colors_graph_gradient'][i],
                    marker_line_color='rgb(17, 69, 126)',
                    marker_line_width=1,
                    opacity=0.7,
                    nbinsx=100
                    )], 
                layout = layout_custom)
        # fig = go.Figure(
        #     [go.Bar(
        #         x=X, y=Y,
        #         marker_color=conf['colors_graph_gradient'][i],
        #         marker_line_color='rgb(17, 69, 126)',
        #         marker_line_width=1,
        #         opacity=0.7
        #         )],
        #     layout = layout_custom
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')

        place.write(fig)


    
    def xy_data(all_data, category):
        # cat = [data.get(category) for data in all_data]
        # print('asd',all_data )
        cat_count = Counter(all_data[category].values.tolist())
        # st.write(gradeffb_count)
        X = list(cat_count.keys())
        Y = list(cat_count.values())
        X = ["[empty]" if x == '' else x for x in X ]
        return X,Y

    def xy_data_float(all_data, category):
        # cat = [data.get(category) for data in all_data]
        # print('asd',all_data )
        cat_count = Counter(all_data[category].values.tolist())
        # st.write(gradeffb_count)
        X = list(cat_count.keys())
        Y = list(cat_count.values())
        print(type(Y[0]))
        X = [np.nan if x == '' else float(x) for x in X ]
        return X,Y

    def xy_data_int(all_data, category):
        # cat = [data.get(category) for data in all_data]
        # print('asd',all_data )
        cat_count = Counter(all_data[category].values.tolist())
        # st.write(gradeffb_count)
        X = list(cat_count.keys())
        Y = list(cat_count.values())
        print(type(Y[0]))
        X = [np.nan if x == '' else int(x) for x in X ]
        return X,Y

    col = st.columns((1,1))

    ls_cat = ['grader_name','grade_ffb']
    for i, cat in enumerate(ls_cat):
        X_cat, Y_cat = xy_data(all_data, cat)
        bar_graph(f'## {cat}', X_cat, Y_cat, col[i%2])

    col = st.columns((1,1,1))
    ls_cat = ['temp_raw', 'lux_raw', 'pest_damaged', 'long_stalk', 'wet', 'dirty', 'dura', 'old', 'unfresh']
    for i, cat in enumerate(ls_cat):
        if cat  == 'temp_raw':
            X_cat, Y_cat = xy_data_float(all_data, cat)
            histogram_graph( f'## {cat}', X_cat, Y_cat, place=col[i%3])
        elif cat == 'lux_raw':
            X_cat, Y_cat = xy_data_int(all_data, cat)
            histogram_graph( f'## {cat}', X_cat, Y_cat, place=col[i%3])
        else:
            X_cat, Y_cat = xy_data(all_data, cat)
            bar_graph(f'## {cat}', X_cat, Y_cat, col[i%3])


def set_state_params_none(state):
    if state.sel_grader_name not in state.default['grader_name']:
        state.sel_grader_name = None
    
    if state.sel_grade not in state.default['grade_ffb']:
        state.sel_grade = None
    
    if state.sel_unfresh not in state.default['unfresh']:
        state.sel_unfresh = None
    
    if state.sel_old not in state.default['old']:
        state.sel_old = None
    
    if state.sel_dura not in state.default['dura']:
        state.sel_dura = None
    
    if state.sel_dirty not in state.default['dirty']:
        state.sel_dirty = None
    
    if state.sel_wet not in state.default['wet']:
        state.sel_wet = None
    
    if state.sel_pest_damaged not in state.default['pest_damaged']:
        state.sel_pest_damaged = None
    
    if state.sel_long_stalk not in state.default['long_stalk']:
        state.sel_long_stalk = None

    if (int(state.sel_temp_range[0]) == state.default['temp_low_high'][0]) or (int(state.sel_temp_range[1]) == state.default['temp_low_high'][1]):
        state.sel_temp_range = [state.default['temp_low_high'][0], state.default['temp_low_high'][1]]

    if (int(state.sel_lux_range[0]) == state.default['lux_low_high'][0]) or (int(state.sel_lux_range[1]) == state.default['lux_low_high'][1]):
        state.sel_lux_range = [state.default['lux_low_high'][0], state.default['lux_low_high'][1]]

def get_params_filter(state):
    params = {}
    params['start_date'] = datetime(state.st_date.year, state.st_date.month, state.st_date.day)
    params['end_date']= datetime(state.end_date.year, state.end_date.month, state.end_date.day)
    params["grader_name"] = state.sel_grader_name
    params["grade_ffb"] = state.sel_grade
    params["unfresh"] = state.sel_unfresh
    params["old"] = state.sel_old
    params["dura"] = state.sel_dura
    params["dirty"] = state.sel_dirty
    params["wet"] = state.sel_wet
    params["pest_damaged"] = state.sel_pest_damaged
    params["long_stalk"] = state.sel_long_stalk
    params["temp_low_high"] = state.sel_temp_range
    params["lux_low_high"] = state.sel_lux_range
    return params

def sidebar_summarize(state):
    params = dict()
    option_filter = ['all', 'filter']
    sb = st.sidebar
    if db_csv.get_length_data() <=0:
        st.sidebar.warning('No Data')
        return
    state.default = db_csv.get_default_value()
    state.sel_filter = sb.radio('filter', 
        option_filter, 
        option_filter.index(state.sel_filter) if state['sel_filter'] is None else 0
    )
    params['filter'] = state.sel_filter
    if state.sel_filter == option_filter[1] :
        # set_state_params_none(state)
        col_1, col_2 = sb.columns((1,1))
        state.st_date = col_1.date_input('start date', value= state.st_date if state.st_date else state.default['start_time'])
        state.end_date = col_2.date_input('end date', value= state.end_date if state.end_date else state.default['end_time'] + timedelta(days=1))
        state.sel_grader_name = sb.multiselect('Grader Name', state.default['grader_name'], state.sel_grader_name if state.sel_grader_name else state.default['grader_name'])
        state.sel_grade = sb.multiselect('Grades (Maturity)', state.default['grade_ffb'], state.sel_grade if state.sel_grade else state.default['grade_ffb'])

        col_1, col_2 = sb.columns((1,1))
        state.sel_unfresh= col_1.multiselect('unfresh', state.default['unfresh'], state.sel_unfresh if state.sel_unfresh else state.default['unfresh'])
        state.sel_old = col_2.multiselect('old', state.default['old'], state.sel_old if state.sel_old else state.default['old'])
        
        col_1, col_2 = sb.columns((1,1))
        state.sel_dura = col_1.multiselect('dura', state.default['dura'], state.sel_dura if state.sel_dura else state.default['dura'])
        state.sel_dirty = col_2.multiselect('dirty', state.default['dirty'], state.sel_dirty if state.sel_dirty else state.default['dirty'])
        
        col_1, col_2 = sb.columns((1,1))
        state.sel_wet = col_1.multiselect('wet', state.default['wet'], state.sel_wet if state.sel_wet else state.default['wet'])
        state.sel_long_stalk = col_2.multiselect('long_stalk', state.default['long_stalk'], state.sel_long_stalk if state.sel_long_stalk else state.default['long_stalk'])

        col_1, col_2 = sb.columns((1,1))
        state.sel_pest_damaged = col_1.multiselect('pest_damaged', state.default['pest_damaged'], state.sel_wet if state.sel_wet else state.default['pest_damaged'])

        state.sel_temp_range = st.sidebar.slider('temp', min_value=state.default['temp_low_high'][0], max_value=state.default['temp_low_high'][1], value= state.sel_temp_range if state.sel_temp_range else state.default['temp_low_high'])
        state.sel_lux_range = st.sidebar.slider('lux',   min_value=state.default['lux_low_high'][0], max_value=state.default['lux_low_high'][1], value=state.sel_lux_range if state.sel_lux_range else state.default['lux_low_high'])

        params.update(get_params_filter(state))


    else:
        start_date =  state.default['start_time']
        end_date =  state.default['end_time']
        params['start_date'] = datetime(start_date.year, start_date.month, start_date.day)
        params['end_date'] = datetime(end_date.year, end_date.month, end_date.day)
        if params['end_date'] == params['start_date']:
            params['end_date'] += timedelta(days=1)
    return params



def summarize_page(state):
    if os.path.exists('db_ffbs.csv') == False:
        st.warning(' No Data ')
        return
    len_Data = db_csv.get_length_data()
    if  len_Data <=0:
        st.warning(' No Data ')
        return

    params = sidebar_summarize(state)
    start = params.get('start_date')
    end = params.get('end_date')
    if params['filter'].lower() == 'all':
        st.write('## All Data')
        state.default = db_csv.get_default_value()
        all_data = db_csv.get_data()
        st.write(f"## Data {start.day}/{start.month}/{start.year} - {end.day}/{end.month}/{end.year}")
    else:
        state.default = db_csv.get_default_value()

        st.write(f"## Data {start.day}/{start.month}/{start.year} - {end.day}/{end.month}/{end.year}")
        # all_data = get_data_by_date(params.get('start_date'), params.get('end_date'))
        all_data = db_csv.get_data_by_filter(**params)
    st.write(f'### We have {len_Data} data point')
    data_viz(all_data)
    st.write(all_data)

def sidebar(pages):
    st.sidebar.write('## Navigation')
    sel_page = st.sidebar.radio('Types', list(pages.keys()))
    return sel_page
