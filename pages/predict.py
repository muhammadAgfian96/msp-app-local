import streamlit as st
import requests
import json
import cv2
import base64

def predict_page(state):
    st.write('Predcition!')
    headers = {
            'Content-type': 'application/json', 
            'Accept': 'text/plain',
            }
    
    data = {
                "class_gt": "string",
                "img64": "string"
            }

    # result = requests.post('http://10.8.0.10:8989/predict_grade', data=json.dumps(data), headers=headers)
    