import os
import sys
sys.path.append('../')


import cv2
from numpy.lib.utils import info
import streamlit as st
from conf import configs
# Import DictWriter class from CSV module
from csv import DictWriter
from uuid import uuid4
from datetime import datetime
import time
from csv_handler import CsvHandler
from camera_handler import  *
from msp_cam.save_msp import save_img as save_msp_now
from PIL import Image
from utils import manage_state, init_state, delete_state, set_state
# from streamlit import session_state as state


conf = configs()
db_csv = CsvHandler()

def section_details(state):
    cat_grade = ['Empty', 'Unripe', 'Underripe', ' Ripe', 'Overripe', 'Rotten']
    cat_val = ['Yes', 'No', 'NA']
    st.write('## Detail Data')
    st.text(state.data_ffbs.get('id'))
    sb = st.columns((2,1,1))
    sb[0].selectbox('Grades', cat_grade, key='grade_ffb')
    state.temp_raw = sb[1].number_input(
        label='Temperature (Celcius)',
        # value=state.data_ffbs.get('temp_raw', 0.0),
        value=state.temp_raw,
        step=0.5,
        format="%.2f",
        # key='temp_raw'
    )
    

    state.lux_raw = sb[2].number_input(
        label='Light Intensity (Lux)',
        value=state.lux_raw,
        step=50.00,
        format="%.2f",
        # key='lux_raw'

    )

    sb = st.columns((1,1,1,1))
    # st.selectbox()
    state.pest_damaged = sb[0].selectbox('Pest Damaged', cat_val, index = cat_val.index(state.pest_damaged))
    state.long_stalk = sb[1].selectbox('Long Stalk', cat_val,  index = cat_val.index(state.long_stalk))
    state.wet = sb[2].selectbox('Wet', cat_val,  index = cat_val.index(state.wet))
    state.dirty = sb[3].selectbox('Dirty', cat_val,  index = cat_val.index(state.dirty))
    state.dura = sb[0].selectbox('Dura', cat_val,  index = cat_val.index(state.dura))
    state.old = sb[1].selectbox('Old', cat_val,  index = cat_val.index(state.old))
    state.unfresh = sb[2].selectbox('Unfresh', cat_val,  index = cat_val.index(state.unfresh))

    sb_1, sb_2 = st.columns((1,1))
    notes = sb_1.text_area('Notes (optional)', key='notes')
    tags = sb_2.text_area('Tags (optional)', key='tags')
    tags = tags.split('\n')
    state.data_ffbs.update({
        'grade_ffb' : state.grade_ffb,
        'temp_raw':state.temp_raw,
        'lux_raw':state.lux_raw,
        'pest_damaged':state.pest_damaged,
        'long_stalk':state.long_stalk,
        'wet':state.wet,
        'dirty':state.dirty,
        'dura':state.dura,
        'old':state.old,
        'unfresh':state.unfresh,
        'notes': '|'.join(state.notes.split('\n')),
        'tags': '|'.join(state.tags.split('\n'))
    })

def section_image(state):  # sourcery no-metrics
    st.write('## Images Data')
    colss = st.columns((1,1,1,1))
    sb_1, sb_2 = st.columns((1,1))
    sb11, sb12, sb21, sb22 = st.columns((1,1,1,1))

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

    def close_cam():
        cap = cv2.VideoCapture(state.sel_port_camera)
        st.write('running close cam', cap.isOpened() )
        if cap.isOpened() == True:
            cap.release()

    # close_cam()

    # init_state('frame_rgbs', [None, None, None, None])
    # init_state('frame_msps', [None, None, None, None])

    if state.start_rgb1:
        print('capture 1')
        # state.frame_rgbs[0]= start_capturing(state, state.start_rgb1, 0, frameST_rgb_3)
        start_capturing(state, state.start_rgb1, 0, frameST_rgb_3)

    if state.start_rgb2:
        print('capture 2')
        start_capturing(state, state.start_rgb2, 1, frameST_rgb_2)

    if state.start_rgb3:
        print('capture 3')
        start_capturing(state, state.start_rgb3, 2, frameST_rgb_3)

    if state.start_rgb4:
        print('capture 3')
        start_capturing(state, state.start_rgb4, 3, frameST_rgb_4)

    # display
    # print('print',state.frame_rgbs[0] is not None, state.frame_rgbs[0], state.frame_rgbs)
    if state.frame_rgbs is not None:
        if state.frame_rgbs[0] is not None:
            frameST_rgb_1.image(state.frame_rgbs[0], channels="BGR", caption='RGB 1 (required)')
        if state.frame_rgbs[1] is not None:
            frameST_rgb_2.image(state.frame_rgbs[1], channels="BGR", caption='RGB 2 (optional)')
        if state.frame_rgbs[2] is not None:
            frameST_rgb_3.image(state.frame_rgbs[2], channels="BGR", caption='RGB 3 (optional)')
        if state.frame_rgbs[3] is not None:
            frameST_rgb_4.image(state.frame_rgbs[3], channels="BGR", caption='RGB 4 (optional)')
    else:
        st.error('Failed len frame_rgbs')

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
    # st.write('frame_rgbs:', state.frame_rgbs)
    
    uni_id = uuid4().hex
    state.data_ffbs.update({'id':str(uni_id)})
    with st.expander('Settings Once'):
        st.write('## Grader Info')
        sb_1, sb_2 = st.columns((1,1))
        date_start = sb_1.date_input('Date Input')
        grader = sb_2.text_input(
            'Grader Name', state.data_ffbs.get('grader_name', "")
        )

        state.root_path_img = sb_1.text_input('img folder','db_image')
        state.data_ffbs.update({'grader_name' : grader})

    sb = st.columns((1,1))
    with sb[0].expander('Settings Camera RGB'):
        st.write('## Camera RGB Settings')
        ls_resolution = [(640, 480), (1280, 720), (1920,1080)]
        ls_camera, info_cam = list_camera()
        st.write(info_cam)
        state.value_brightness = st.number_input('brightness', 0, 100)
        state.sel_resolution_camera = st.selectbox('Resolution', ls_resolution, 2)
        state.sel_port_camera = st.selectbox('List Devices', ls_camera)


    with sb[1].expander('Settings Camera MSP'):
        st.write('## Camera MSP Settings')

    with st.expander('Camera', False):
        section_image(state)

    section_details(state)

    st.write(state.data_ffbs)

def isThereImage(state):
    valid_img = True
    if len(state.frame_rgbs) == 0:
        valid_img = False
    if state.frame_rgbs[0] is None:
        valid_img = False

    # if len(state.frame_msps) == 0:
    #     valid_img = False
    # if state.frame_msps[0] is None:
    #     valid_img = False

    return valid_img

def form_page(state):
    # state.isSuccesInput = None
    # st.write(state.frame_rgbs)
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

    if state.temp_raw == 0.0:
        st.sidebar.warning('🌡️ Pls fill the **Temperature** Value!')
        # print('Pls fill the Temperature Value!')
        is_complete=False

    if state.lux_raw == 0:
        st.sidebar.warning('☀️ Pls fill the **Lux** Value!')
        # print('Please fill the Lux Value!')
        is_complete=False

    if btn_submit and is_complete:
        # print('input data')
        isSuccesInput, resetData = db_csv.submit(
                data_ffbs = dict(state.data_ffbs),
                frame_rgbs = list(state.frame_rgbs) # is list 4 img
            )

        if isSuccesInput:
            st.sidebar.success('Succes submit!')
            st.sidebar.success('**Press `R`**')
            st.sidebar.write('Data we submit')
            st.sidebar.write(state.data_ffbs)

            # state.frame_rgbs = None
            # state.frame_msps = None
            state.raw_img = None
            set_state('temp_raw', 0.0)
            set_state('lux_raw', 0.0)
            set_state('frame_rgbs', [None, None, None, None])
            set_state('frame_msps', [None, None, None, None])
            
            grader_name = state.data_ffbs.get('grader_name')
            # state.data_ffbs = {}
            time.sleep(0.1)
            state.data_ffbs.update({'id':'here_id', 'grader_name' : grader_name})
            state.isSuccesInput = None
        else:
            state.isSuccesInput = False
    elif btn_submit and is_complete== False:
        state.isSuccesInput = False
        st.sidebar.error('Failed To Submit!')
    else:
        if state.isSuccesInput is None and is_complete:
            st.sidebar.info('Please submit!')
        elif state.isSuccesInput is None:
            st.sidebar.warning('Please complete form!')
        elif state.isSuccesInput == False:
            st.sidebar.error('Failed To Submit!')
            set_state('isSuccesInput', None)
        elif state.isSuccesInput:
            st.sidebar.success('Succes Submit')
            set_state('isSuccesInput', None)
            set_state('temp_raw', 0.0)
            set_state('lux_raw', 0.0)
            set_state('frame_rgbs', [None, None, None, None])
            set_state('frame_msps', [None, None, None, None])
