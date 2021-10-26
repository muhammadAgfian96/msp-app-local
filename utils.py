import streamlit as st
from streamlit import session_state as state


def init_state(key, value):
    if key not in state:
        state[key] = value

def delete_state(key):
    del state[key]

def set_state(key, value):
    state[key] = value

def manage_state():
    # main
    init_state('data_ffbs', {})
    init_state('grade_ffb', 'Empty')
    init_state('temp_raw', 0.0)
    init_state('lux_raw', 0.0)
    init_state('pest_damaged', 'NA')
    init_state('long_stalk', 'NA')
    init_state('wet', 'NA')
    init_state('dirty', 'NA')
    init_state('dura', 'NA')
    init_state('old', 'NA')
    init_state('unfresh', 'NA')
    init_state('notes', '')
    init_state('tags', '')

    
    # form
    init_state('cap_open', False)
    init_state('frame_rgbs', [None, None, None, None])
    init_state('frame_msps', [None, None, None, None])
    init_state('isSuccesInput', False)

    # post processing input
    init_state('pp_dst_folder', '')
    init_state('pp_file_stapiraw', '')
    init_state('pp_put_text', '')
    init_state('pp_folder_stapiraw', '')
    init_state('pp_hist_type', '')
    init_state('pp_max_y', '')

    # summary
    init_state('sel_filter', 0)
    init_state('st_date', 0)
    init_state('end_date', 0)
    init_state('sel_grader_name', 0)
    init_state('sel_grade', 0)
    init_state('sel_unfresh', 0)
    init_state('sel_old', 0)
    init_state('sel_dura', 0)
    init_state('sel_dirty', 0)
    init_state('sel_wet', 0)
    init_state('sel_long_stalk', 0)
    init_state('sel_temp_range', 0)
    init_state('sel_lux_range', 0)


    return state


