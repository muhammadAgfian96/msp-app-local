import cv2
import streamlit as st
import os


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