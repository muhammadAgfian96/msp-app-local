import cv2
import stapipy as sp
import numpy as np
import streamlit as st
import os
from msp_cam.msp import CMyCallback as MSP_Callback



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
    my_callback = MSP_Callback()
    cb_func = my_callback.datastream_callback
    try:
        # Initialize StApi before using.
        sp.initialize()
        print('init cam msp')
        # Create a system object for device scan and connection.
        sp_system = sp.create_system()
        print('create system')
        # Connect to first detected device.
        sp_device = sp_system.create_first_device()

        # Display DisplayName of the device.
        print('Device=', sp_device.info.display_name)

        # Create a datastream object for handling image stream data.
        sp_datastream = sp_device.create_datastream()
        print('create_datastream')
        # Register callback for datastream
        callback = sp_datastream.register_callback(cb_func)
        print('register_callback')

        # Start the image acquisition of the host (local machine) side.
        sp_datastream.start_acquisition()
        print('start_acquisition')

        # Start the image acquisition of the camera side.
        sp_device.acquisition_start()
        print('sp_device start_acquisition')

        # Get device nodemap to access the device settings.
        # remote_nodemap = sp_device.remote_port.nodemap

        # # Create and start a thread for auto function configuration.
        # autofunc_thread = threading.Thread(target=do_auto_functions,
        #                                    args=(remote_nodemap,))
        # autofunc_thread.start()

        # Display image using OpenCV.
        while state.start_msp:
            print('go')
            state.frame_msp = my_callback.image
            # state.raw_img = my_callback.stapiraw_data
            if state.frame_msp is not None:
                frameST.image(state.frame_msp)
                print('frame')
                # cv2.imshow('image', state.frame_msp)
            key_input = cv2.waitKey(1)
            if key_input != -1:
                break

        # autofunc_thread.join()

        # Stop the image acquisition of the camera side
        sp_device.acquisition_stop()

        # Stop the image acquisition of the host side
        sp_datastream.stop_acquisition()

    except Exception as exception:
        print(exception)

# =================== list devices ==============================

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


# =================== setting camera rgb ========================
def increase_brightness(state, img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    lim = 255 - state.value_brightness
    v[v > lim] = 255
    v[v <= lim] += state.value_brightness

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img