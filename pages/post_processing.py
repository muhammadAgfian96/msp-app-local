import streamlit as st
import cv2
import functools
import operator
import numpy as np
from enum import Enum

import os
import matplotlib.pyplot as plt
from skimage import io
import stapipy as sp

def post_processing_page(state):
    with st.beta_expander('Convert StapiRaw to TIF'):
        sb = st.beta_columns((2,1))
        state.pp_dst_folder = sb[1].text_input('Folder Destination', state.pp_dst_folder if state.pp_dst_folder else 'db_tiff')
        state.pp_file_stapiraw = sb[0].text_input('File Stapiraw', state.pp_file_stapiraw if state.pp_file_stapiraw else '')
        state.pp_put_text = sb[0].checkbox('Put Text On Splitting Image', state.pp_put_text if state.pp_put_text else False)
        
        if st.button('Convert and Split 4 band'):
            result = convert_to_tif(state)
            if result:
                st.success('Succes Convert')
            else:
                st.error('Failed Convert')

    with st.beta_expander('Histogram'):
        sb = st.beta_columns((3,1))
        state.pp_folder_stapiraw = sb[0].text_input('Folder 1 StapiRaw', state.pp_folder_stapiraw if state.pp_folder_stapiraw else '.')
        # state.pp_file_stapiraw = sb[1].text_input('File Stapiraw-', state.pp_main_folder if state.pp_main_folder else '.')
        col = st.beta_columns((1,3))
        state.pp_bins = col[0].selectbox('bins', [64, 128, 256, 512,1024], index=2)
        
        if st.button('Generate'):
            histogram(state)
            st.success('Succes Convert')

def convert_to_tif(state):
    # Load image
    file_stapiraw = state.pp_file_stapiraw

    # file destionation
    name_file = file_stapiraw.split('.')[0].split('stapiraw_')[-1]
    folder_dst = os.path.join(state.pp_dst_folder, name_file)
    file_path = os.path.join(state.pp_dst_folder, name_file, name_file+'.tif')
    os.makedirs(folder_dst, exist_ok=True)  # succeeds even if directory exists.

    # result = True
    try:
        # init first
        sp.initialize()
        st_system = sp.create_system()

        # prepare converter
        st_stillimage_filer = sp.create_filer(sp.EStFilerType.StillImage)
        st_image = st_stillimage_filer.load(file_stapiraw)
        print("done.")

        # Convert image to BGR8 format.
        st_converter = sp.create_converter(sp.EStConverterType.PixelFormat)
        st_converter.destination_pixel_format = sp.EStPixelFormatNamingConvention.BGR8
        st_image = st_converter.convert(st_image)


        # saving tif file and convert
        st_stillimage_filer.save(st_image, sp.EStStillImageFileFormat.TIFF, file_path)
        
        splitting(file_path, name_file, folder_dst, state.pp_put_text)
        result = True
        st.info(f'saved on {file_path}')
        state.pp_file_stapiraw = ''
    except :
        result = False
    return result


# ------------------------------ Splitting Function ---------------------

class Band(Enum):
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4

def sel_band(img, band, put_text=True):
    h,w = img.shape
    if band == Band.BLUE:
        raw_row = [(i,i+1) for i in range(0, h, 4)]
        sel_row =  functools.reduce(operator.iconcat, raw_row, [])
        sel_col = sel_row
        text = 'BLUE'
        
    if band == Band.RED:
        raw_row = [(i,i+1) for i in range(2, h, 4)]
        sel_row =  functools.reduce(operator.iconcat, raw_row, [])
        sel_col = sel_row
        text = 'RED'

    if band == Band.GREEN:
        ls = [(i,i+1) for i in range(0, h, 4)]
        sel_row =  functools.reduce(operator.iconcat, ls, [])
        ls = [(i,i+1) for i in range(2, w, 4)]
        sel_col =  functools.reduce(operator.iconcat, ls, [])
        text = 'GREEN'

    if band == Band.YELLOW:
        ls = [(i,i+1) for i in range(2, h, 4)]
        sel_row =  functools.reduce(operator.iconcat, ls, [])
        ls = [(i,i+1) for i in range(0, w, 4)]
        sel_col =  functools.reduce(operator.iconcat, ls, [])
        text = 'YELLOW'

    sel_img = img[sel_row, :][:, sel_col].copy()
    if put_text:
        sel_img = cv2.putText(sel_img, text, (100,100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 3)
    return sel_img

def splitting(path_tif, name_file, model_folder, put_text):
    img = cv2.imread(path_tif, cv2.IMREAD_GRAYSCALE)

    red = sel_band(img, Band.RED, put_text=put_text)
    green = sel_band(img, Band.GREEN, put_text=put_text)
    yellow = sel_band(img, Band.YELLOW, put_text=put_text)
    blue = sel_band(img, Band.BLUE, put_text=put_text)

    red_file = os.path.join(model_folder, f'{name_file}_820nm.tif')
    green_file = os.path.join(model_folder, f'{name_file}_735nm.tif')
    blue_file = os.path.join(model_folder, f'{name_file}_580nm.tif')
    yellow_file = os.path.join(model_folder, f'{name_file}_660nm.tif')
    bgyr_file = os.path.join(model_folder, f'{name_file}_bgyr.tif')

    cv2.imwrite(red_file, red)
    cv2.imwrite(green_file, green)
    cv2.imwrite(blue_file, blue)
    cv2.imwrite(yellow_file, yellow)


    img1=np.hstack([blue, green])
    img2=np.hstack([yellow, red])
    img_all=np.vstack([img1,img2])

    cv2.imwrite(bgyr_file, img_all)


def histogram(state):

    model_folder = state.pp_folder_stapiraw
    name_file = model_folder.split('/')[-1]

    ext_ = ['_820nm.tif', '_735nm.tif', '_580nm.tif', '_660nm.tif']
    files = [os.path.join(model_folder, name_file+ex) for ex in ext_]
    for file in files:
        image = io.imread(file) 
        # plt.hist(image.ravel(), bins=state.pp_bins)
        # plt.title(file.split('/')[-1])
        # x1,x2,y1,y2=plt.axis()
        # plt.axis((x1,x2,0,2000))
        # plt.savefig(file.split('.tif')[0]+'_hist.jpg')
        # plt.close()


        # plt.figure()
        # io.imshow(im)
        # plt.show()
    
        # UNNORMALIZED HISTOGRAM - useful to look at original pattern
        h = [(image==v).sum() for v in range(256)]
        
        plt.figure()
        plt.bar(range(256), h)
        plt.title(file)
        x1,x2,y1,y2=plt.axis()
        plt.axis((x1,x2,0,6000))
        plt.savefig(file.split('.tif')[0]+'_hist_UNnormalized.jpg')
        plt.close()
        
        
        # NORMALISED HISTOGRAM - needed to compare different histograms
        h = np.array(h)
        norm_h = h/h.sum()
        
        plt.figure()
        plt.bar(range(256), norm_h)
        plt.title(file)
        x1,x2,y1,y2=plt.axis()
        plt.axis((x1,x2,0,0.025))
        plt.savefig(file.split('.tif')[0]+'_hist_Normalized.jpg')
        plt.close()
        
        #plt.savefig(file)        
        
        
        
        