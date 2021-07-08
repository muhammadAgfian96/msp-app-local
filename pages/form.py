
import cv2
import os
import uuid
import numpy as np
from numpy.lib.utils import info
import streamlit as st

import pandas as pd
from openpyxl import load_workbook

from datetime import datetime
from conf import configs
# Import DictWriter class from CSV module
from csv import DictWriter
from uuid import uuid4
import pandas as pd
from datetime import datetime
import time
from csv_handler import CsvHandler
from camera_handler import  *
from msp_cam.save_msp import save_img as save_msp_now
from PIL import Image

conf = configs()
db_csv = CsvHandler()

def section_details(state):
    cat_grade = ['Empty', 'Unripe', 'Underripe', ' Ripe', 'Overripe', 'Rotten']
    cat_val = ['Yes', 'No', 'NA']
    st.write('## Detail Data')
    st.text(state.data_ffbs.get('id'))
    sb = st.beta_columns((2,1,1))
    grade_ffb = sb[0].selectbox('Grades', cat_grade,)
    temp_raw = sb[1].text_input('Temperature (Celcius)', state.data_ffbs.get('temp_raw') if state.data_ffbs.get('temp_raw') else '')
    lux_raw = sb[2].text_input('Light Intensity (Lux)', state.data_ffbs.get('lux_raw') if state.data_ffbs.get('lux_raw') else '')


    sb = st.beta_columns((1,1,1,1))
    pest_damaged = sb[0].selectbox('Pest Damaged', cat_val, len(cat_val)-1)
    long_stalk = sb[1].selectbox('Long Stalk', cat_val, len(cat_val)-1)
    wet = sb[2].selectbox('Wet', cat_val, len(cat_val)-1)
    dirty = sb[3].selectbox('Dirty', cat_val, len(cat_val)-1)
    dura = sb[0].selectbox('Dura', cat_val, len(cat_val)-1)
    old = sb[1].selectbox('Old', cat_val, len(cat_val)-1)
    unfresh = sb[2].selectbox('Unfresh', cat_val, len(cat_val)-1)


    sb_1, sb_2 = st.beta_columns((1,1))
    notes = sb_1.text_area('Notes (optional)')
    tags = sb_2.text_area('Tags (optional)')
    tags = tags.split('\n')
    state.data_ffbs.update({
        'grade_ffb' : grade_ffb,
        'temp_raw':temp_raw,
        'lux_raw':lux_raw,
        'pest_damaged':pest_damaged,
        'long_stalk':long_stalk,
        'wet':wet,
        'dirty':dirty,
        'dura':dura,
        'old':old,
        'unfresh':unfresh,
        'notes': '|'.join(notes.split('\n')),
        'tags': '|'.join(tags)
    })

def section_image(state):
    st.write('## Images Data')
    colss = st.beta_columns((1,1,1,1))
    sb_1, sb_2 = st.beta_columns((1,1))
    # img_rgb = sb_1.file_uploader('Images',type=['.jpg', '.jpeg', '.png'])
    # img_msp = sb_2.file_uploader('Multispectral',type=['.jpg', '.jpeg', '.png'], accept_multiple_files=True)
    frameST1 = sb_1.empty()
    frameST2 = sb_2.empty()

    state.start_rgb = colss[0].button('Start Capture RGB')
    state.stop_rgb = colss[1].button('Capture RGB')
    if state.start_rgb:
        state.frame_rgb = start_capturing(state, frameST1)
        print('capture')
    if state.frame_rgb is not None:
        frameST1.image(state.frame_rgb, channels="BGR")
        

    state.start_msp = colss[2].button('Take Capture MSP')
    # state.stop_msp = colss[3].button('Capture MSP')
    if state.start_msp:
        save_msp_now()
        # state.frame_msp = start_capturing_msp(state, frameST2)
        file_msp_loc = os.path.join('temp_msp',
                                    'temporary_msp' + ".jpg")
        state.frame_msp = Image.open(file_msp_loc)

    if state.frame_msp is not None:
        frameST2.image(state.frame_msp) # only single channels (gray)

def form(state):
    uni_id = uuid4().hex
    state.data_ffbs.update({'id':str(uni_id)})
    with st.beta_expander('Settings Once'):
        st.write('## Grader Info')
        sb_1, sb_2 = st.beta_columns((1,1))
        date_start = sb_1.date_input('Date Input')
        grader = sb_2.text_input('Grader Name', state.data_ffbs.get('grader_name') if state.data_ffbs.get('grader_name') else "")
        state.root_path_img = sb_1.text_input('img folder','db_image')
        state.data_ffbs.update({'grader_name' : grader})

    sb = st.beta_columns((1,1))
    with sb[0].beta_expander('Settings Camera RGB'):
        st.write('## Camera RGB Settings')
        ls_resolution = [(640, 480), (1280, 720), (1920,1080)]
        ls_camera, info_cam = list_camera()
        st.write(info_cam)
        state.value_brightness = st.number_input('brightness', 0, 100)
        state.sel_resolution_camera = st.selectbox('Resolution', ls_resolution)
        state.sel_port_camera = st.selectbox('List Devices', ls_camera)


    with sb[1].beta_expander('Settings Camera MSP'):
        st.write('## Camera MSP Settings')

    with st.beta_expander('Camera', False):

        section_image(state)

    section_details(state)

    st.write(state.data_ffbs)

def isThereImage(state):
    valid_img = True
    if state.frame_msp is None or state.frame_rgb is None:
        valid_img = False
    return valid_img

def form_page(state):
    # state.isSuccesInput = None
    form(state)

    # valid_img = image_validation(data)
    btn_submit = st.button('Submit Data')
    


    valid_img = isThereImage(state)
    is_complete = True

    if state.data_ffbs.get('grader_name') == "":
        st.sidebar.warning('👶 Pls fill the **grader name**!')
        # print('Pls fill the grader name!')
        is_complete=False
    elif state.data_ffbs.get('grader_name'):
        st.sidebar.info(f'hi, **{state.data_ffbs.get("grader_name")}**')
    
    if valid_img == False:
        is_complete = False
        st.sidebar.warning('🖼️ Pls fill **image**!')
        # print('Please fill image!')

    if state.data_ffbs.get('temp_raw') == "":
        st.sidebar.warning('🌡️ Pls fill the **Temperature** Value!')
        # print('Pls fill the Temperature Value!')
        is_complete=False

    if state.data_ffbs.get('lux_raw') == "":
        st.sidebar.warning('☀️ Pls fill the **Lux** Value!')
        # print('Please fill the Lux Value!')
        is_complete=False

    if btn_submit and is_complete:
        # print('input data')
        st.write(state.data_ffbs)
        isSuccesInput, resetData = db_csv.submit(
                data_ffbs = state.data_ffbs.copy(),
                frame_rgb = state.frame_rgb
            )
        st.success('Succes!')
        
        if isSuccesInput:
            state.frame_rgb = None
            state.frame_msp = None
            state.raw_img = None
            grader_name = state.data_ffbs.get('grader_name')
            state.data_ffbs = {}
            time.sleep(0.5)
            state.data_ffbs.update({'id':'here_id', 'grader_name' : grader_name})
            state.isSuccesInput = True
        else:
            state.isSuccesInput = False
    else:
        if state.isSuccesInput is None:
            st.sidebar.info('Please input!')
        elif state.isSuccesInput == False:
            st.sidebar.error('Failed To Submit!')
            state.isSuccesInput = None
        elif state.isSuccesInput:
            st.sidebar.success('Succes Submit')
            state.isSuccesInput = None
