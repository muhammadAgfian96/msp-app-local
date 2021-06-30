# Import DictWriter class from CSV module
from csv import DictWriter
from uuid import uuid4
import pandas as pd
from collections import Counter
from datetime import datetime
import os
import cv2
import pandas as pd
from pandas.core.frame import DataFrame
from datetime import datetime

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
        with open(self.filename, 'a') as f_object:
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
                    print(line)
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
    
    def get_data_by_date(self, start_date:datetime, end_date:datetime) -> DataFrame:
        if not isinstance(self.df, DataFrame):
            self.get_data()
        self.df[self.df['date']>=start_date and self.df['date']<=end_date]
        return self.df
    
    def get_data_by_filter(self):
        if not isinstance(self.df, DataFrame):
            self.get_data()
        # do a filter task

        return self.df
    
    def get_length_data(self):
        if not isinstance(self.df, DataFrame):
            self.get_data()
        return self.df.shape[0]

    def get_default_value(self):
        if not isinstance(self.df, DataFrame):
            self.get_data()
            print('get data')
        print(self.df)
        default_val = {}
        default_val["start_date"] = self.coll.distinct("time_input")[0]
        default_val["end_date"] = self.coll.distinct("time_input")[-1] + datetime.timedelta(days=1)
        default_val["grader_name"] = self.coll.distinct("grader_name")
        default_val["grade_ffb"] = self.coll.distinct("grade_ffb")
        default_val["unfresh"] = self.coll.distinct("unfresh")
        default_val["old"] = self.coll.distinct("old")
        default_val["dura"] = self.coll.distinct("dura")
        default_val["dirty"] = self.coll.distinct("dirty")
        default_val["wet"] = self.coll.distinct("wet")
        default_val["long_stalk"] = self.coll.distinct("long_stalk")
        return default_val

if __name__ == '__main__':
    db_csv = CsvHandler()
    db_csv.get_default_value()