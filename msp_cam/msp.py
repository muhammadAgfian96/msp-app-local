"""
 This sample demostrates how to set AWB, AGC, and AE function.
 The following points will be demonstrated in this sample code:
 - Initialize StApi
 - Connect to camera
 - Register and use callback function with StApi
 - Acquire image via callback function
 - Set AWB, AGC, AE
 - Copy image data for OpenCV
 - Convert Bayer image format to RGB using OpenCV
 - Preview image using OpenCV
 Note: opencv-python and numpy packages are required:
    pip install numpy
    pip install opencv-python
"""

import cv2
import threading
import numpy as np
import stapipy as sp
import os
import copy
# Image scale when displaying using OpenCV.
DISPLAY_RESIZE_FACTOR = 0.3

# Feature names
EXPOSURE_AUTO = "ExposureAuto"
GAIN_AUTO = "GainAuto"
BALANCE_WHITE_AUTO = "BalanceWhiteAuto"

AUTO_LIGHT_TARGET = "AutoLightTarget"
GAIN = "Gain"
GAIN_RAW = "GainRaw"

EXPOSURE_MODE = "ExposureMode"
EXPOSURE_TIME = "ExposureTime"
EXPOSURE_TIME_RAW = "ExposureTimeRaw" # Custom

BALANCE_RATIO_SELECTOR = "BalanceRatioSelector"
BALANCE_RATIO = "BalanceRatio"


class CMyCallback:
    """
    Class that contains a callback function.
    """

    def __init__(self):
        self._image = None
        self._raw_msp_img = None
        self._lock = threading.Lock()

    @property
    def image(self):
        """Property: return PyIStImage of the grabbed image."""
        duplicate = None
        self._lock.acquire()
        if self._image is not None:
            duplicate = self._image.copy()
        self._lock.release()
        return duplicate
    
    @property
    def stapiraw_data(self):
        """Property: return PyIStImage of the grabbed image."""
        raw_img_msp = None
        self._lock.acquire()
        if self._raw_msp_img is not None:
            raw_img_msp = copy.deepcopy(self._raw_msp_img)
        self._lock.release()
        return raw_img_msp

    

    def datastream_callback(self, handle=None, context=None):
        """
        Callback to handle events from DataStream.

        :param handle: handle that trigger the callback.
        :param context: user data passed on during callback registration.
        """
        sp_datastream = handle.module
        if sp_datastream:
            with sp_datastream.retrieve_buffer() as sp_buffer:
                # Check if the acquired data contains image data.
                if sp_buffer.info.is_image_present:
                    # Create an image object.
                    sp_image = sp_buffer.get_image()

                    # Check the pixelformat of the input image.
                    pixel_format = sp_image.pixel_format
                    pixel_format_info = sp.get_pixel_format_info(pixel_format)

                    # Only mono or bayer is processed.
                    if not(pixel_format_info.is_mono or pixel_format_info.is_bayer):
                        return

                    # Get raw image data.
                    data = sp_image.get_image_data()

                    # Perform pixel value scaling if each pixel component is
                    # larger than 8bit. Example: 10bit Bayer/Mono, 12bit, etc.
                    if pixel_format_info.each_component_total_bit_count > 8:
                        nparr = np.frombuffer(data, np.uint16)
                        division = pow(2, pixel_format_info
                                       .each_component_valid_bit_count - 8)
                        nparr = (nparr / division).astype('uint8')
                    else:
                        nparr = np.frombuffer(data, np.uint8)

                    # Process image for display.
                    nparr = nparr.reshape(sp_image.height, sp_image.width, 1)

                    # Perform color conversion for Bayer.
                    if pixel_format_info.is_bayer:
                        bayer_type = pixel_format_info.get_pixel_color_filter()
                        if bayer_type == sp.EStPixelColorFilter.BayerRG:
                            nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_RG2RGB)
                        elif bayer_type == sp.EStPixelColorFilter.BayerGR:
                            nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_GR2RGB)
                        elif bayer_type == sp.EStPixelColorFilter.BayerGB:
                            nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_GB2RGB)
                        elif bayer_type == sp.EStPixelColorFilter.BayerBG:
                            nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_BG2RGB)

                    # Resize image and store to self._image.
                    nparr = cv2.resize(nparr, None,
                                       fx=DISPLAY_RESIZE_FACTOR,
                                       fy=DISPLAY_RESIZE_FACTOR)
                    self._lock.acquire()
                    self._image = nparr
                    self._raw_msp_img = sp_image
                    self._lock.release()

# ======= my own function =====
def save_stapiraw(raw_img, file_location):
    try :
        if ".StApiRaw" not in file_location:
            file_location+=".StApiRaw"
        st_stillimage_filer = sp.create_filer(sp.EStFilerType.StillImage)
        # Save the image file as StApiRaw file format.
        print("Saving {0} ... ".format(file_location), end="")
        st_stillimage_filer.save(raw_img, sp.EStStillImageFileFormat.StApiRaw, file_location)
        print("done.")
    except:
        print('error save stapiraw')
        return False, ''
    return True, file_location

def save_stapiraw_to_imgs(file_location_stapiraw, base_folder, id_, formats=['']):
    # Load image here the way
    # 1 load stapiraw
    st_stillimage_filer = sp.create_filer(sp.EStFilerType.StillImage)
    print("Loading {0} ... ".format(file_location_stapiraw), end="")
    st_image = st_stillimage_filer.load(file_location_stapiraw)
    print("done.")

    # 2 Convert image to BGR8 format.
    st_converter = sp.create_converter(sp.EStConverterType.PixelFormat)
    st_converter.destination_pixel_format = \
        sp.EStPixelFormatNamingConvention.BGR8
    st_image = st_converter.convert(st_image)

    # 3 Save as bitmap, tiff, png, jpg, csv
    save_list = {sp.EStStillImageFileFormat.Bitmap: '.bmp',
                    sp.EStStillImageFileFormat.TIFF: '.tif',
                    sp.EStStillImageFileFormat.PNG: '.png',
                    sp.EStStillImageFileFormat.JPEG: '.jpg',
                    sp.EStStillImageFileFormat.CSV: '.csv',
    }
    for file_format, file_ext in save_list.items():
        file_location = os.path.join(base_folder,
            'msp_'+ id_ + file_ext)
        print("Saving {0} ... ".format(file_location), end="")
        st_stillimage_filer.save(st_image, file_format, file_location)
        print("done.")

def raw_to_opencv_img(raw_img, DISPLAY_RESIZE_FACTOR=0.5):
    # Check the pixelformat of the input image.
    pixel_format = raw_img.pixel_format
    pixel_format_info = sp.get_pixel_format_info(pixel_format)

    # Only mono or bayer is processed.
    if not(pixel_format_info.is_mono or pixel_format_info.is_bayer):
        return

    data = raw_img.get_image_data()

    # Perform pixel value scaling if each pixel component is
    # larger than 8bit. Example: 10bit Bayer/Mono, 12bit, etc.
    if pixel_format_info.each_component_total_bit_count > 8:
        nparr = np.frombuffer(data, np.uint16)
        division = pow(2, pixel_format_info.each_component_valid_bit_count - 8)
        nparr = (nparr / division).astype('uint8')
    else:
        nparr = np.frombuffer(data, np.uint8)

        # Process image for display.
        nparr = nparr.reshape(raw_img.height, raw_img.width, 1)

        # Perform color conversion for Bayer.
        if pixel_format_info.is_bayer:
            bayer_type = pixel_format_info.get_pixel_color_filter()
            if bayer_type == sp.EStPixelColorFilter.BayerRG:
                nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_RG2RGB)
            elif bayer_type == sp.EStPixelColorFilter.BayerGR:
                nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_GR2RGB)
            elif bayer_type == sp.EStPixelColorFilter.BayerGB:
                nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_GB2RGB)
            elif bayer_type == sp.EStPixelColorFilter.BayerBG:
                nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_BG2RGB)

                # Resize image and store to self._image.
        nparr = cv2.resize(nparr, None, fx=DISPLAY_RESIZE_FACTOR, fy=DISPLAY_RESIZE_FACTOR)
        return nparr



# ========== config function from documentation ======
def edit_enumeration(nodemap, enum_name):
    """
    Display and allow user to modify the enumeration value.

    :param nodemap: node map.
    :param enum_name: name of the enumeration node.
    """
    node = nodemap.get_node(enum_name)
    if not node.is_writable:
        return

    # Cast to PyIEnumeration from PyNode
    enum_node = sp.PyIEnumeration(node)

    while True:
        print(enum_name)
        enum_entries = enum_node.entries
        for index in range(len(enum_entries)):
            enum_entry = enum_entries[index]
            if enum_entry.is_available:
                print("{0} : {1} {2}".format(index,
                      sp.PyIEnumEntry(enum_entry).symbolic_value,
                      "(Current)" if enum_node.value == enum_entry.value
                                             else ""))
        selection = int(input("Select : "))
        if selection < len(enum_entries):
            enum_entry = enum_entries[selection]
            enum_node.set_int_value(enum_entry.value)
            break


def edit_setting(nodemap, node_name):
    """
    Edit setting which has numeric type.

    :param nodemap:  Node map.
    :param node_name: Node name.
    """
    node = nodemap.get_node(node_name)
    if not node.is_writable:
        return
    if node.principal_interface_type == sp.EGCInterfaceType.IFloat:
        node_value = sp.PyIFloat(node)
    elif node.principal_interface_type == sp.EGCInterfaceType.IInteger:
        node_value = sp.PyIInteger(node)
    while True:
        print(node_name)
        print(" Min={0} Max={1} Current={2}{3}".format(
              node_value.min, node_value.max, node_value.value,
              " Inc={0}".format(node_value.inc) if\
                    node_value.inc_mode == sp.EGCIncMode.FixedIncrement\
                    else ""))
        new_value = input("New value : ")
        print()
        if node.principal_interface_type == sp.EGCInterfaceType.IFloat:
            new_numeric_value = float(new_value)
        else:
            new_numeric_value = int(new_value)
        if node_value.min <= new_numeric_value <= node_value.max:
            node_value.value = new_numeric_value
            return


def edit_enum_setting(nodemap, enum_name, numeric_name):
    """
    Display the contents of the current enumeration node and edit settings.

    :param nodemap: Node map.
    :param enum_name: Enumeration name.
    :param numeric_name: Numeric name.
    """
    node = nodemap.get_node(enum_name)
    if not node.is_writable:
        return

    enum_node = sp.PyIEnumeration(node)
    enum_entries = enum_node.entries
    for index in range(len(enum_entries)):
        enum_entry = enum_entries[index]
        if enum_entry.is_available:
            enum_node.value = enum_entry.value
            print("{0} = {1}".format(enum_name,
                  sp.PyIEnumEntry(enum_entry).symbolic_value))
            edit_setting(nodemap, numeric_name)


def exposure_auto(nodemap):
    """Configure exposure using the given nodemap."""
    # Configure the ExposureMode
    edit_enumeration(nodemap, EXPOSURE_MODE)

    # Configure the ExposureAuto
    edit_enumeration(nodemap, EXPOSURE_AUTO)

    # Configure the AutoLightTarget
    edit_setting(nodemap, AUTO_LIGHT_TARGET)

    if nodemap.get_node(EXPOSURE_TIME):
        edit_setting(nodemap, EXPOSURE_TIME)
    else:
        edit_setting(nodemap, EXPOSURE_TIME_RAW)


def gain_auto(nodemap):
    """Configure gain using the given nodemap."""
    # Configure the GainAuto
    edit_enumeration(nodemap, GAIN_AUTO)

    # Configure the AutoLightTarget
    edit_setting(nodemap, AUTO_LIGHT_TARGET)

    if nodemap.get_node(GAIN):
        edit_setting(nodemap, GAIN)
    else:
        edit_setting(nodemap, GAIN_RAW)


def balance_white_auto(nodemap):
    """Configure balance ratio/white using the given nodemap."""
    # Configure the BalanceWhiteAuto
    edit_enumeration(nodemap, BALANCE_WHITE_AUTO)

    # While switching the BalanceRatioSelector, configure the BalanceRatio
    edit_enum_setting(nodemap, BALANCE_RATIO_SELECTOR, BALANCE_RATIO)


def do_auto_functions(nodemap):
    """Function running in a separate thread for auto function configuration."""
    # Check if features available.
    feature_list = [EXPOSURE_AUTO, GAIN_AUTO, BALANCE_WHITE_AUTO]
    is_writable_list = [False, False, False]
    for index, feature in enumerate(feature_list):
        with nodemap.get_node(feature) as node:
            is_writable_list[index]=True if node.is_writable else False

    while True:
        print()
        print("Auto Functions")
        for index, feature in enumerate(feature_list):
            if is_writable_list[index]:
                print("{0} : {1}".format(index, feature))
        print("Else : Exit")
        selection = int(input("Select : "))
        if selection == 0 and is_writable_list[selection] == True:
            exposure_auto(nodemap)
        elif selection == 1 and is_writable_list[selection] == True:
            gain_auto(nodemap)
        elif selection == 2 and is_writable_list[selection] == True:
            balance_white_auto(nodemap)
        else:
            print("Focus on the OpenCV window and press any key to terminate.")
            break


if __name__ == "__main__":
    my_callback = CMyCallback()
    cb_func = my_callback.datastream_callback
    try:
        # Initialize StApi before using.
        sp.initialize()

        # Create a system object for device scan and connection.
        sp_system = sp.create_system()

        # Connect to first detected device.
        sp_device = sp_system.create_first_device()

        # Display DisplayName of the device.
        print('Device=', sp_device.info.display_name)

        # Create a datastream object for handling image stream data.
        sp_datastream = sp_device.create_datastream()

        # Register callback for datastream
        callback = sp_datastream.register_callback(cb_func)

        # Start the image acquisition of the host (local machine) side.
        sp_datastream.start_acquisition()

        # Start the image acquisition of the camera side.
        sp_device.acquisition_start()

        # Get device nodemap to access the device settings.
        remote_nodemap = sp_device.remote_port.nodemap

        # Create and start a thread for auto function configuration.
        autofunc_thread = threading.Thread(target=do_auto_functions,
                                           args=(remote_nodemap,))
        autofunc_thread.start()

        # Display image using OpenCV.
        while True:
            output_image = my_callback.image
            if output_image is not None:
                cv2.imshow('image', output_image)
            key_input = cv2.waitKey(1)
            if key_input != -1:
                break

        autofunc_thread.join()

        # Stop the image acquisition of the camera side
        sp_device.acquisition_stop()

        # Stop the image acquisition of the host side
        sp_datastream.stop_acquisition()

    except Exception as exception:
        print(exception)
