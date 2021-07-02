import cv2
import streamlit as st

def start_capturing(state, frameST):
    cap = cv2.VideoCapture(0)
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
    print(state.frame_msp)


def increase_brightness(state, img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    lim = 255 - state.value_brightness
    v[v > lim] = 255
    v[v <= lim] += state.value_brightness

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img