
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

conf = configs()
db_csv = CsvHandler()

def start_capturing(state, frameST):
    cap = cv2.VideoCapture(state.sel_port_camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(state.sel_resolution_camera[0]))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(state.sel_resolution_camera[1]))
    while state.start_rgb:
        ret, state.frame_rgb = cap.read()
        # Stop the program if reached end of video
        if not ret or state.stop_rgb == True:
            print("Done processing !!!")
            frameST.write('Done Capturing')
            frameST.image(state.frame_rgb, channels="BGR")
            # Release device
            cap.release()
            state.start_rgb = False
            state.stop_rgb = False
            break
        state.frame_rgb = increase_brightness(state, state.frame_rgb)
        frameST.image(state.frame_rgb, channels="BGR")
    cap.release()
    print('cap release')
    return state.frame_rgb

def start_capturing_msp(state, frameST):
    cap = cv2.VideoCapture(0)
    while state.start_msp:
        ret, state.frame_msp = cap.read()
        # Stop the program if reached end of video
        print('asd')
        if not ret:
            print("Done processing !!!")
            frameST.write('Done Capturing')
            frameST.image(state.frame_msp, channels="BGR")
            # Release device
            cap.release()
            state.start_msp = False
            state.stop_msp = False
            break

        frameST.image(state.frame_msp, channels="BGR")
    # state.frame_msp = frame_msp
    print('cap release')
    cap.release()


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
        

    state.start_msp = colss[2].button('Start Capture MSP')
    state.stop_msp = colss[3].button('Capture MSP')
    if state.start_msp:
        state.frame_msp = start_capturing_msp(state, frameST2)
    if state.frame_msp is not None:
        frameST2.image(state.frame_msp, channels="BGR")

def increase_brightness(state, img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    lim = 255 - state.value_brightness
    v[v > lim] = 255
    v[v <= lim] += state.value_brightness

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img

@st.cache()
def list_camera():
    is_working = True
    dev_port = 0
    isLinux = 0
    ls_camera = []
    information = []


    while is_working:

        if os.name =='nt':
            camera_idx = dev_port+cv2.CAP_DSHOW
        else:
            camera_idx = dev_port
        camera = cv2.VideoCapture(camera_idx)
        if not camera.isOpened():
            isLinux += 1
            if isLinux >=2:
                is_working = False
            print("Port %s is not working." %camera_idx)
        else:
            is_reading, img = camera.read()
            w = camera.get(3)
            h = camera.get(4)
            if is_reading:
                print("Port %s is working and reads images (%s x %s)" %(camera_idx,h,w))
                information.append("Port %s is working and reads images (%s x %s)" %(camera_idx,h,w))
                ls_camera.append(camera_idx)
                isLinux = 0
            else:
                print("Port %s for camera ( %s x %s) is present but does not reads." %(camera_idx,h,w))
                # available_ports.append(dev_port)
        
        dev_port +=1
    return ls_camera, information

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
        ls_resolution = [(1280, 720), (1920,1080)]
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
                frame_msp = state.frame_msp, 
                frame_rgb = state.frame_rgb
            )
        st.success('Succes!')
        
        if isSuccesInput:
            # state.frame_rgb = None
            # state.frame_msp = None
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
