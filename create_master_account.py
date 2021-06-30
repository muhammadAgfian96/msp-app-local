from db_helper import DB_Handler
from conf import configs
import hashlib, binascii, os
from datetime import datetime

conf = configs(False)

def main():
    # ==================== configure here =====================
    master_account = {
        'username': 'superadmin1',
        'pwd' :  hashing('admin123'),
        'role' : 'superuser',
        'status': 'Active',
        'date_created': datetime.now()
    }

    # =========================================================


    assert master_account['role'] in ['grader', 'admin', 'superuser'], 'ops not in role'
    assert master_account['status'] in ['Active', 'Non-Active'], 'ops not in role'


    isNotExist = check_user_exists(master_account)
    
    if isNotExist:
        submit_user_db(master_account)
        print('succes made it')
        users_data = get_user_db()
        print(users_data)
    else:
        print(get_user_db())
        raw = get_alluser_db()
        for d in raw:
            print(d)
            break



def hashing(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)

    return (salt + pwdhash).decode('ascii')

def get_alluser_db():
    db = DB_Handler(**conf['db_setting'])
    user_raw = db.get_users()
    db.close_connections()
    return user_raw

def get_user_db():
    db = DB_Handler(**conf['db_setting'])
    user_raw = db.get_usernames()
    db.close_connections()

    user_datas = []
    for user in user_raw:
        user_datas.append(user)
    return user_datas

def check_user_exists(user_info):
    #usernames = get_usernames()
    all_data = get_user_db()
    usernames = []
    print(all_data)
    if len(all_data) > 0:
        for data in all_data:
            usernames.append(data)

    if user_info['username'] not in usernames:
        isNotExist = True
    else:
        isNotExist = False
        print('the account is already exists!')
    return isNotExist

def submit_user_db(user_info):
    db = DB_Handler(**conf['db_setting'])
    db.insert_user(user_info)
    db.close_connections()

def get_usernames():
    db = DB_Handler(**conf['db_setting'])
    user_raw = db.get_usernames()
    db.close_connections()


if __name__ == '__main__':
    main()