# Import DictWriter class from CSV module
import csv
from csv import DictWriter
from uuid import uuid4
import pandas as pd
from collections import Counter
from datetime import datetime
import os
import cv2
import pandas as pd
from pandas.core.frame import DataFrame
from datetime import datetime, timedelta
import numpy as np
# from easydict import EasyDict as edict

class CsvHandler:
    def __init__(self, filename='db_ffbs.csv', root_path='db_images'):
        self.filename = filename
        self.root_path_img = root_path
        self.df = None

    def process_image(self, frame_msp, frame_rgb):
        # check forlder,
        if not os.path.exists(self.folder_image):
            # make
            os.makedirs(self.folder_image)

        # write
        msp_path = os.path.join(self.folder_image, 'msp_' + str(self.id_) + '.tif')
        rgb_path = os.path.join(self.folder_image, 'rgb_' + str(self.id_) + '.jpg')
        try:
            cv2.imwrite(msp_path, frame_msp)
            cv2.imwrite(rgb_path, frame_rgb)
        except :
            print('ERROR IMAGE')
            return False

        path_imgs = {
            'msp_path' : msp_path,
            'rgb_path' : rgb_path
        }
        print('succes create image')
        return True, path_imgs

    def submit(self, data_ffbs, frame_msp, frame_rgb):
        self.id_ = data_ffbs.get('id')
        self.folder_image = os.path.join(self.root_path_img, self.id_)
        
        data_ffbs.update({
            'date' : datetime.now()
        })

        # save_image
        isValid, path_imgs = self.process_image(frame_msp= frame_msp, 
                                    frame_rgb=frame_rgb)
        data_ffbs.update(path_imgs)
        field_names = list(data_ffbs.keys())

        if not isValid:
            print('error is valid image')
            return False


        if not os.path.isfile(self.filename):
            titles = ",".join(field_names)
            with open(self.filename, "w") as f:
                f.writelines(titles+"\n")

        with open(self.filename, "r") as f:
            lines = f.readlines()
            len_old_data = len(lines)

        # check titles
        if len_old_data <= 0:
            titles = ",".join(field_names)
            with open(self.filename, "w") as f:
                f.writelines(titles+"\n")

        # append data
        with open(self.filename, 'a+', newline='') as f_object:
            dictwriter_object = DictWriter(f_object, fieldnames=field_names)
            dictwriter_object.writerow(data_ffbs)
            f_object.close()
            
        with open(self.filename, "r") as f:
            lines = f.readlines()
            len_new_data = len(lines)  
            
        if len_old_data < len_new_data:
            print("succes add")
            return True, {}
        else:
            print("not add/ id not found")
            return False, data_ffbs

    def delete_one_file(self, id_):
        exp_id = "04d2d438f41649058e933a6f39451de3"
        
        if len(id_) != len(exp_id):
            print("id is not complete!")
            return

        with open(self.filename, "r") as f:
            lines = f.readlines()
            len_old_data = len(lines)

        with open(self.filename, "w") as f:
            for line in lines:
                if id_ not in line:
                    f.write(line)
                else:
                    print('id_delete', line)
                    id_deleted = line.split(',')[0]

        with open(self.filename, "r") as f:
            lines = f.readlines()
            len_new_data = len(lines)        
                    
        if len_old_data > len_new_data:
            print("succes delete")
            return True, id_deleted
        else:
            print("not delete any items/ id not found")
            return False, 0

    def get_data(self) -> DataFrame:
        df = pd.read_csv(self.filename, index_col='id')
        df.date = pd.to_datetime(df.date)
        cols = ['date',  'grader_name', 'grade_ffb', 'temp_raw', 'lux_raw', 'pest_damaged', 'long_stalk', 'wet', 'dirty', 'dura', 'old', 'unfresh', 'notes', 'tags',  'msp_path', 'rgb_path']
        df.fillna('[NaN]',inplace=True)
        self.df = df[cols]
        return self.df
    
    def get_data_by_filter(self, **params):
        # if not isinstance(self.df, DataFrame):
        self.get_data()
        df=self.df.copy()
        # do a filter task
        start_date = params["start_date"]
        end_date = params["end_date"]
        grader_name = params["grader_name"]
        grade_ffb = params["grade_ffb"]
        unfresh = params["unfresh"]
        old = params["old"]
        dura = params["dura"]
        dirty = params["dirty"]
        wet = params["wet"]
        long_stalk = params["long_stalk"]
        temp_low_high =params["temp_low_high"]
        lux_low_high = params["lux_low_high"]

        df = df[(df['date']>=start_date) & (df['date']<=end_date)]
        df = df[df['grader_name'].isin(grader_name)]
        df = df[df['grade_ffb'].isin(grade_ffb)]
        df = df[df['unfresh'].isin(unfresh)]
        df = df[df['old'].isin(old)]
        df = df[df['dura'].isin(dura)]
        df = df[df['dirty'].isin(dirty)]
        df = df[df['wet'].isin(wet)]
        df = df[df['long_stalk'].isin(long_stalk)]
        df = df[df['temp_raw'].between(temp_low_high[0],temp_low_high[1])]
        df = df[df['lux_raw'].between(lux_low_high[0],lux_low_high[1])]
        return df
    
    def get_length_data(self):
        self.get_data()
        print('make from get_length_data')
        return self.df.shape[0]

    def get_default_value(self):
        self.get_data()
        print('get data')
        
        lux_ls = self.df.lux_raw.sort_values(ascending=True).unique().tolist()
        temp_ls = self.df.temp_raw.sort_values(ascending=True).unique().tolist()
        start_time = self.npdt_dt(list(self.df.date.sort_values(ascending=True))[0])
        end_time = self.npdt_dt(list(self.df.date.sort_values(ascending=True))[-1])

        default = {}
        default['start_time'] = start_time
        default['end_time'] = end_time
        default['grader_name'] = self.df.grader_name.unique().tolist()
        default['grade_ffb'] = self.df.grade_ffb.unique().tolist()
        
        default['unfresh'] = self.df.unfresh.unique().tolist()
        default['old'] = self.df.old.unique().tolist()
        
        default['dura'] = self.df.dura.unique().tolist()
        default['dirty'] = self.df.dirty.unique().tolist()
        
        default['wet'] = self.df.wet.unique().tolist()
        default['pest_damaged'] = self.df.pest_damaged.unique().tolist()
        
        default['long_stalk'] = self.df.long_stalk.unique().tolist()
        
        if temp_ls[0] == temp_ls[-1]:
            temp_ls.append(temp_ls[0]+1)
        if lux_ls[0] == lux_ls[-1]:
            lux_ls.append(lux_ls[0]+1)

        default['temp_low_high'] = [temp_ls[0], temp_ls[-1]] # little to big
        default['lux_low_high'] = [lux_ls[0], lux_ls[-1]]

        return default

    def npdt_dt(self, npdt_time):
        hasil = (npdt_time - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
        return datetime.utcfromtimestamp(hasil)
    
    

if __name__ == '__main__':
    db_csv = CsvHandler()
    db_csv.get_length_data()
    db_csv.get_default_value()