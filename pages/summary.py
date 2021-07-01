import streamlit as st
import plotly.graph_objects as go

from datetime import datetime, timedelta
from collections import Counter
from conf import configs
from csv_handler import CsvHandler

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
                    'autosize':True,
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
        place.write(fig)

    def xy_data(all_data, category):
        # cat = [data.get(category) for data in all_data]
        print('asd',all_data )
        cat_count = Counter(all_data[category].values.tolist())
        # st.write(gradeffb_count)
        X = list(cat_count.keys())
        Y = list(cat_count.values())
        X = ["[empty]" if x == '' else x for x in X ]
        return X,Y

    col = st.beta_columns((1,1))
    # cols = ['date',  'grader_name', 'grade_ffb', 'temp_raw', 'lux_raw', 'pest_damaged', 'long_stalk', 'wet', 'dirty', 'dura', 'old', 'unfresh', 'notes', 'tags',  'msp_path', 'rgb_path']

    ls_cat = ['grader_name','grade_ffb']
    for i, cat in enumerate(ls_cat):
        X_cat, Y_cat = xy_data(all_data, cat)
        bar_graph(f'## {cat}', X_cat, Y_cat, col[i%2])
    # ls_cat = ['unfresh','old', 'dura', 'dirty', 'wet', 'long_stalk', 'pest_damaged']
    col = st.beta_columns((1,1,1))
    ls_cat = ['temp_raw', 'lux_raw', 'pest_damaged', 'long_stalk', 'wet', 'dirty', 'dura', 'old', 'unfresh']
    for i, cat in enumerate(ls_cat):
        X_cat, Y_cat = xy_data(all_data, cat)
        bar_graph(f'## {cat}', X_cat, Y_cat, col[i%3])

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
    default = db_csv.get_default_value()
    state.sel_filter = sb.radio('filter', option_filter, option_filter.index(state.sel_filter) if state.sel_filter else 0)
    params['filter'] = state.sel_filter

    if state.sel_filter == option_filter[1] :

        col_1, col_2 = sb.beta_columns((1,1))

        state.st_date = col_1.date_input('start date', value= state.st_date if state.st_date else default['start_time'])
        state.end_date = col_2.date_input('end date', value= state.end_date if state.end_date else default['end_time'] + timedelta(days=1))
        state.sel_grader_name = sb.multiselect('Grader Name', default['grader_name'], state.sel_grader_name if state.sel_grader_name else default['grader_name'])
        state.sel_grade = sb.multiselect('Grades (Maturity)', default['grade_ffb'], state.sel_grade if state.sel_grade else default['grade_ffb'])

        col_1, col_2 = sb.beta_columns((1,1))
        state.sel_unfresh= col_1.multiselect('unfresh', default['unfresh'], state.sel_unfresh if state.sel_unfresh else default['unfresh'])
        state.sel_old = col_2.multiselect('old', default['old'], state.sel_old if state.sel_old else default['old'])
        
        col_1, col_2 = sb.beta_columns((1,1))
        state.sel_dura = col_1.multiselect('dura', default['dura'], state.sel_dura if state.sel_dura else default['dura'])
        state.sel_dirty = col_2.multiselect('dirty', default['dirty'], state.sel_dirty if state.sel_dirty else default['dirty'])
        
        col_1, col_2 = sb.beta_columns((1,1))
        state.sel_wet = col_1.multiselect('wet', default['wet'], state.sel_wet if state.sel_wet else default['wet'])
        state.sel_long_stalk = col_2.multiselect('long_stalk', default['long_stalk'], state.sel_long_stalk if state.sel_long_stalk else default['long_stalk'])

        col_1, col_2 = sb.beta_columns((1,1))
        state.sel_pest_damaged = col_1.multiselect('pest_damaged', default['pest_damaged'], state.sel_wet if state.sel_wet else default['pest_damaged'])
        state.sel_temp_range = st.sidebar.slider('temp', min_value=default['temp_low_high'][0], max_value=default['temp_low_high'][1],value= state.sel_temp_range if state.sel_temp_range else default['temp_low_high'])
        state.sel_lux_range = st.sidebar.slider('lux', min_value=default['lux_low_high'][0], max_value=default['lux_low_high'][1],value=state.sel_lux_range if state.sel_lux_range else default['lux_low_high'])

        params.update(get_params_filter(state))
    else:
        start_date =  default['start_time']
        end_date =  default['end_time']
        params['start_date'] = datetime(start_date.year, start_date.month, start_date.day)
        params['end_date'] = datetime(end_date.year, end_date.month, end_date.day)
        if params['end_date'] == params['start_date']:
            params['end_date'] += timedelta(days=1)
    return params



def summarize_page(state):
    len_Data = db_csv.get_length_data()
    if  len_Data <=0:
        st.warning(' No Data ')
        return

    params = sidebar_summarize(state)
    start = params.get('start_date')
    end = params.get('end_date')
    if params['filter'].lower() == 'all':
        st.write('## All Data')
        all_data = db_csv.get_data()
        st.write(f"## Data {start.day}/{start.month}/{start.year} - {end.day}/{end.month}/{end.year}")
    else:
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
