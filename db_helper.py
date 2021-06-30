import pymongo
import numpy as np
import datetime as dt
from datetime import datetime
from pprint import pprint
from bson.objectid import ObjectId
import shutil
import os
from streamlit.elements import select_slider

class DB_Handler:
    def __init__(self, **conf) -> None:
        self.host = conf['host']
        self.user =  conf['username']
        self.port = conf['port']
        self.passwd = conf['passwd']
        self.name_db = conf['db_name']
        self.name_collections = conf['collection_name']
        self.collection_user = conf['collection_user']
        self.isServer = conf['server']
        self.start_connection()

    def start_connection(self,):
        if self.isServer:
            self.conn = pymongo.MongoClient(
                            host= self.host,
                            port=self.port,
                            username=self.user,
                            password=self.passwd,
                            authSource=self.name_db,
                        )
        else:
            self.conn = pymongo.MongoClient(
                            host= self.host,
                            port= self.port)

        self.db = self.conn[self.name_db]
        self.coll = self.db[self.name_collections]
        self.user_coll = self.db[self.collection_user]

    def info(self):
        return self.conn.server_info()

    def close_connections(self):
        self.conn.close()

    def insert_data(self, data: dict):
        self.docs = self.coll.insert_one(data)
        print('data inserted', self.docs.inserted_id, data)
        return self.docs.inserted_id

    def insert_user(self,user_info: dict):
        self.docs = self.user_coll.insert_one(user_info)
        print('Added User Details: ', self.docs.inserted_id, user_info)
        self.docs.inserted_id

    def update_user(self, default, username, role, status):
        result = self.user_coll.update_one({"username": default}, { "$set": {
         'username': username,
         'role': role,
         'status': status } })

        if result.modified_count > 0:
             isUpdated = True
        else:
             isUpdated = False
        return isUpdated

    def update_user_pwd(self, default, pwd):
        result = self.user_coll.update_one({"username": default}, { "$set": {'pwd':pwd} })
        if result.modified_count > 0:
            isPwdUpdated = True
        else:
            isPwdUpdated = False
        return isPwdUpdated

    def update_user_status(self, default, status):
        result = self.user_coll.update_one({"username": default}, { "$set": {'status':status} })
        if result.modified_count > 0:
             isUpdated = True
        else:
             isUpdated = False
        return isUpdated


    def delete_by_username(self, username):
        result = self.user_coll.delete_one({"username":username})
        if result.deleted_count > 0:
            isDeleted = True
        else:
            isDeleted = False
        return isDeleted


    def get_users(self):
        return self.user_coll.find({})

    def get_usernames(self):
        return self.user_coll.distinct("username")

    def get_pwd(self):
        return self.user_coll.distinct("pwd")

    def get_user_count(self):
        return self.user_coll.find({}).count()

    def get_user_by_name(self, username):
        return self.user_coll.find_one({'username':username})

    def show_collection(self,):
        for data in self.coll.find({}):
            hasil = data.get('img_msp')
            print(hasil)

    def get_length_data(self):
        return self.coll.find({}).count()

    def get_all_data(self):
        return self.coll.find({})

    def get_by_date(self, start_date:datetime, end_date:datetime):
        return self.coll.find({
                    "time_input": {"$gte":start_date,"$lt":end_date},
                    })

    def get_super_filter(self,**params):
        return self.coll.find({
                    "time_input": {"$gte":params['start_date'], "$lt":params['end_date']},
                    "grader_name" : {"$in" : params['grader_name']},
                    "grade_ffb" : {"$in" : params['grade_ffb']},
                    "unfresh" : {"$in" : params['unfresh']},
                    "old" : {"$in" : params['old']},
                    "dura" : {"$in" : params['dura']},
                    "dirty" : {"$in" : params['dirty']},
                    "wet" : {"$in" : params['wet']},
                    "long_stalk" : {"$in" : params['long_stalk']},
                    })

    def get_default_val(self):
        val = {}
        val["start_date"] = self.coll.distinct("time_input")[0]
        val["end_date"] = self.coll.distinct("time_input")[-1] + dt.timedelta(days=1)
        val["grader_name"] = self.coll.distinct("grader_name")
        val["grade_ffb"] = self.coll.distinct("grade_ffb")
        val["unfresh"] = self.coll.distinct("unfresh")
        val["old"] = self.coll.distinct("old")
        val["dura"] = self.coll.distinct("dura")
        val["dirty"] = self.coll.distinct("dirty")
        val["wet"] = self.coll.distinct("wet")
        val["long_stalk"] = self.coll.distinct("long_stalk")
        return val

    def delete_img_id(self, id_):
        result = self.coll.find({ "_id": {"$eq": ObjectId(id_)}})
        isDeleted = True
        try:
            for data in result:
                dict_path_msp = data['path_msp']
                dict_path_rgb = data['path_rgb']
                dirname_item = os.path.dirname(dict_path_rgb['0'])
                shutil.rmtree(dirname_item)
        except OSError as e:
            isDeleted = False
            print(e)
        return isDeleted

    def delete_id(self, id_):
        isDeleted = self.delete_img_id(id_)
        if isDeleted:
            re_all = self.coll.delete_many({ "_id": {"$eq": ObjectId(id_)}})
        else:
            return 0, isDeleted
        return re_all.deleted_count, isDeleted


if __name__ == '__name__':
    from conf import configs

    conf = configs(False)

    db = DB_Handler(**conf['db_setting'])
    user_raw = db.get_usernames()
    print(user_raw)
    db.close_connections()