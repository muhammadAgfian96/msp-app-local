
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
    temp_raw = sb[1].number_input(label= 'Temperature (Celcius)', 
                                value= state.data_ffbs.get('temp_raw') if state.data_ffbs.get('temp_raw') else 0.0, 
                                step=0.01, 
                                format="%.2f")
    lux_raw = sb[2].number_input(label= 'Light Intensity (Lux)', 
                                value= state.data_ffbs.get('lux_raw') if state.data_ffbs.get('lux_raw') else 0, 
                                step=1,
                                format="%.2f")


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
    sb11, sb12, sb21, sb22 = st.beta_columns((1,1,1,1))
    # img_rgb = sb_1.file_uploader('Images',type=['.jpg', '.jpeg', '.png'])
    # img_msp = sb_2.file_uploader('Multispectral',type=['.jpg', '.jpeg', '.png'], accept_multiple_files=True)


    state.start_rgb1 = sb11.button('Start Streaming 1')
    state.start_rgb2 = sb12.button('Start Streaming 2')
    state.start_rgb3 = sb11.button('Start Streaming 3')
    state.start_rgb4 = sb12.button('Start Streaming 4')

    state.start_msp1 = sb21.button('Capture MSP 1')
    state.start_msp2 = sb22.button('Capture MSP 2')
    state.start_msp3 = sb21.button('Capture MSP 3')
    state.start_msp4 = sb22.button('Capture MSP 4')
    state.capture = st.button('Capture')



    frameST_rgb_1 = sb11.empty()
    frameST_rgb_2 = sb12.empty()
    frameST_rgb_3 = sb11.empty()
    frameST_rgb_4 = sb12.empty()

    frameST_msp_1 = sb21.empty()
    frameST_msp_2 = sb22.empty()
    frameST_msp_3 = sb21.empty()
    frameST_msp_4 = sb22.empty()


    state.frame_rgbs = [None, None, None, None] if state.frame_rgbs is None else state.frame_rgbs
    state.frame_msps = [None, None, None, None] if state.frame_msps is None else state.frame_msps
    if state.start_rgb1:
        print('capture 1')
        state.frame_rgbs[0]= start_capturing(state, state.start_rgb1, 0, frameST_rgb_3)

    if state.start_rgb2:
        print('capture 2')
        state.frame_rgbs[1] = start_capturing(state, state.start_rgb2, 1, frameST_rgb_2)

    if state.start_rgb3:
        print('capture 3')
        state.frame_rgbs[2] = start_capturing(state, state.start_rgb3, 2, frameST_rgb_3)
    
    if state.start_rgb4:
        print('capture 3')
        state.frame_rgbs[3] = start_capturing(state, state.start_rgb4, 3, frameST_rgb_4)

    # display
    if state.frame_rgbs[0] is not None:
        frameST_rgb_1.image(state.frame_rgbs[0], channels="BGR", caption='RGB 1 (required)')
    if state.frame_rgbs[1] is not None:
        frameST_rgb_2.image(state.frame_rgbs[1], channels="BGR", caption='RGB 2 (optional)')
    if state.frame_rgbs[2] is not None:
        frameST_rgb_3.image(state.frame_rgbs[2], channels="BGR", caption='RGB 3 (optional)')
    if state.frame_rgbs[3] is not None:
        frameST_rgb_4.image(state.frame_rgbs[3], channels="BGR", caption='RGB 4 (optional)')
        

    # state.stop_msp = colss[3].button('Capture MSP')
    if state.start_msp1:
        with st.spinner('Progress ... Take Picture MSP 1'):
            file_name = '1'
            save_msp_now(file_name)
            file_msp_loc = os.path.join('temp_msp','temporary_msp' +file_name +".jpg")
            state.frame_msps[0] = Image.open(file_msp_loc)
    if state.start_msp2:
        with st.spinner('Progress ... Take Picture MSP 2'):
            file_name = '2'
            save_msp_now(file_name)
            file_msp_loc = os.path.join('temp_msp','temporary_msp' +file_name +".jpg")
            state.frame_msps[1] = Image.open(file_msp_loc)
    if state.start_msp3:
        with st.spinner('Progress ... Take Picture MSP 3'):
            file_name = '3'
            save_msp_now(file_name)
            file_msp_loc = os.path.join('temp_msp','temporary_msp' +file_name +".jpg")
            state.frame_msps[2] = Image.open(file_msp_loc)
    if state.start_msp4:
        with st.spinner('Progress ... Take Picture MSP 4'):
            file_name = '4'
            save_msp_now(file_name)
            file_msp_loc = os.path.join('temp_msp','temporary_msp' +file_name +".jpg")
            state.frame_msps[3] = Image.open(file_msp_loc)

    if state.frame_msps[0] is not None:
        frameST_msp_1.image(state.frame_msps[0], caption='MSP 1 (required)') # only single channels (gray)
    if state.frame_msps[1] is not None:
        frameST_msp_2.image(state.frame_msps[1], caption='MSP 2 (optional)') # only single channels (gray)
    if state.frame_msps[2] is not None:
        frameST_msp_3.image(state.frame_msps[2], caption='MSP 3 (optional)') # only single channels (gray)
    if state.frame_msps[3] is not None:
        frameST_msp_4.image(state.frame_msps[3], caption='MSP 4 (optional)') # only single channels (gray)

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
        state.sel_resolution_camera = st.selectbox('Resolution', ls_resolution, 2)
        state.sel_port_camera = st.selectbox('List Devices', ls_camera)


    with sb[1].beta_expander('Settings Camera MSP'):
        st.write('## Camera MSP Settings')

    with st.beta_expander('Camera', False):
        section_image(state)

    section_details(state)

    st.write(state.data_ffbs)

def isThereImage(state):
    valid_img = True
    if len(state.frame_rgbs) == 0:
        valid_img = False
    if state.frame_rgbs[0] is None:
        valid_img = False

    if len(state.frame_msps) == 0:
        valid_img = False
    if state.frame_msps[0] is None:
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

    if state.data_ffbs.get('temp_raw') == 0.0:
        st.sidebar.warning('🌡️ Pls fill the **Temperature** Value!')
        # print('Pls fill the Temperature Value!')
        is_complete=False

    if state.data_ffbs.get('lux_raw') == 0:
        st.sidebar.warning('☀️ Pls fill the **Lux** Value!')
        # print('Please fill the Lux Value!')
        is_complete=False

    if btn_submit and is_complete:
        # print('input data')
        st.write(state.data_ffbs)
        isSuccesInput, resetData = db_csv.submit(
                data_ffbs = state.data_ffbs.copy(),
                frame_rgbs = state.frame_rgbs # is list 4 img
            )
        st.success('Succes!')
        
        if isSuccesInput:
            state.frame_rgbs = None
            state.frame_msps = None
            state.raw_img = None
            grader_name = state.data_ffbs.get('grader_name')
            state.data_ffbs = {}
            time.sleep(0.25)
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
