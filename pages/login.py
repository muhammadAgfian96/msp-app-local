from copy import error
import os

import streamlit as st
import hashlib, binascii, os
import time

from db_helper import DB_Handler
from datetime import datetime
from conf import configs
from easydict import EasyDict as edict


conf = configs()
# ===================== main ==========================================
def login_page(state):

    # st.set_page_config(layout='centered')
    st.write('# Welcome Multispectral App')
    with st.form('login'):
        name = st.text_input('Username')
        pwd = st.text_input('Password', type='password')
        hash_pwd = hash_password(pwd)
        submit = st.form_submit_button('Sign-In')
    if submit:
        try:
            data = get_user_by_name(name)
            password_provided = data.get("pwd")
            isMatchPass = verify_password(password_provided, pwd)
            if not isMatchPass:
                st.error('Incorrect Username/Password')
                time.sleep(1)
            else:
                state.user = edict()
                state.user.name = name
                state.user.role = data.get('role')
                state.user.status = data.get('status')
            return isMatchPass
            # return state.login_status if state.login_status else False

        except TypeError:
            st.error('Incorrect Username/Password')

def register_page(state):
    if state.status_regis:
        status_regis = state.status_regis
        st.warning(status_regis)
    else:
        status_regis = ''

    # Register
    with st.form('register'):
        state.regis = edict()
        state.regis.name = st.text_input('Username')
        state.regis.pwd = st.text_input('Password', type='password')
        state.regis.repwd = st.text_input('Re-type Password', type='password')
        c1, c2 = st.beta_columns(2)
        with c1:
            state.regis.role = st.selectbox('Roles',['grader', 'admin', 'superuser'])
        with c2:
            state.regis.status = st.selectbox('Status',['Active', 'Non-Active'])
        state.regis.date = datetime.today()
        state.regis.hash_pwd = hash_password(state.regis.pwd)
        submit_signup = st.form_submit_button('Register')

        user_info = {
            'username':state.regis.name,
            'pwd':state.regis.hash_pwd,
            'role':state.regis.role,
            'status':state.regis.status,
            'date_created':state.regis.date
        }

    if submit_signup:
        #isLoaded, data = load_user_file(state)
        isLoaded = check_user_count()
        if (state.regis.repwd != state.regis.pwd):
            state.status.regis= 'Not same password, check your password!'
            return False
        if state.regis.name == None or len(state.regis.name) < 4 \
            or state.regis.pwd == None or len(state.regis.pwd) < 4:
            state.status_regis= 'Your username or password is Null or too short (less than 4 character)!'
            return False

        isSaved = check_user_exists(user_info, state)
        #isSaved = save_to_file(data, state)

        if not isLoaded:
            st.warning('Creating New DB')
        if isSaved:
            # loading bar
            prog_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                prog_bar.progress(i)
            st.success('Succes Regis')
            time.sleep(1)
        else:
            st.warning('Ouch ch ch! username has been exist! Try Again!')
            time.sleep(2)
        return False

def user_page(state):
    all_data = get_user_db()
    options = [
        'Register New User',
        'Update User',
        'Delete User',
        ]

    sel_box = st.sidebar.selectbox('Select Option', options, index=state.user_page if state.user_page else 0)
    state.user_page = options.index(sel_box)
    user_pg_default = state.user_page

    if sel_box == options[0]:
        register_page(state)

    if sel_box == options[1]:
        update_user(state, all_data)

    if sel_box == options[2]:
        delete_user(state, all_data)



# ====================== utils =========================================

def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password

def submit_user_db(user_info):
    db = DB_Handler(**conf['db_setting'])
    db.insert_user(user_info)
    db.close_connections()

def get_usernames():
    db = DB_Handler(**conf['db_setting'])
    user_raw = db.get_usernames()
    db.close_connections()

    user_datas = []
    for user in user_raw:
        user_datas.append(user)
    return user_datas

def get_user_by_name(username):
    db = DB_Handler(**conf['db_setting'])
    user = db.get_user_by_name(username)
    db.close_connections()
    return user

def check_user_count():
    db = DB_Handler(**conf['db_setting'])
    user_count = db.get_user_count()
    db.close_connections()

    if user_count >= 1:
        isLoaded = True
    else:
        isLoaded = False
    return isLoaded

def get_user_db():
    db = DB_Handler(**conf['db_setting'])
    user_raw = db.get_users()
    db.close_connections()

    user_datas = []
    for user in user_raw:
        user_datas.append(user)
    return user_datas

def check_user_exists(user_info, state):
    #usernames = get_usernames()
    all_data = get_user_db()
    usernames = []
    for data in all_data:
        usernames.append(data.get('username'))

    if state.regis.name not in usernames:
        submit_user_db(user_info)
        isSaved = True
        state.regis = None
    else:
        isSaved = False
    return isSaved

def update_user_data(default, username, role, status):
    db = DB_Handler(**conf['db_setting'])
    isUpdated = db.update_user(default, username, role, status)
    db.close_connections()
    return isUpdated

def update_user_pwd(default, pwd):
    db = DB_Handler(**conf['db_setting'])
    isPwdUpdated = db.update_user_pwd(default, pwd)
    db.close_connections()
    return isPwdUpdated

def update_user_status(default, status):
    db = DB_Handler(**conf['db_setting'])
    isUpdated = db.update_user_status(default, status)
    db.close_connections()
    return isUpdated

def delete_by_username(username):
    db = DB_Handler(**conf['db_setting'])
    isDeleted = db.delete_by_username(username)
    db.close_connections()
    return isDeleted



def delete_user(state, all_data):
    #Delete page
    c = st.beta_columns((1,1,1,1,1,1))
    c[0].write('### **No.**')
    c[1].write('### **Username**')
    c[2].write('### **Role**')
    c[3].write('### **Status**')
    c[4].write('### **Date Created**')
    c[5].write('### **Update/Delete**')

    btn_delete_list = {}
    btn_update_list = {}
    rad_update_list = {}
    #state.btn_update_list = {}

    st.markdown('<hr>', unsafe_allow_html=True)

    all_data.reverse()
    for i, data in enumerate(all_data):
        if data.get('status') == 'Active':
            stat_default = 0
        else:
            stat_default = 1
        c = st.beta_columns((1,1,1,1,1,1))
        c[0].write(f'{i}')
        c[1].write(data.get('username'))
        c[2].write(data.get('role'))
        c[3].write(data.get('status'))
        stat_radio = c[3].radio('', ['Active', 'Non-Active'], key=data.get('username'), index=stat_default)
        rad_update_list[data.get('username')] = stat_radio
        date = data.get("date_created").strftime("%a, %d-%b-%Y, %I:%M %p")
        c[4].write(date)
        btn_update = c[5].button(f'Update {data.get("username")}')
        btn_update_list[data.get('username')]= btn_update
        #state.btn_update_list[data.get('username')]= btn_update
        btn_delete = c[5].button(f'Delete {data.get("username")}')
        btn_delete_list[data.get('username')]= btn_delete
        st.markdown('<hr>', unsafe_allow_html=True)

    for user in list(rad_update_list.keys()):
        if rad_update_list[user]:
            isUpdated = update_user_status(user, rad_update_list[user])
            if isUpdated:
                st.sidebar.success(f"Status Updated For User: {user}, Press \'R\' if the result did not update")
                return False
            else:
                pass

    for user in list(btn_delete_list.keys()):
        if btn_delete_list[user]:
            isDeleted = delete_by_username(user)
            if isDeleted:
                st.sidebar.success(f'User: {user} has been deleted')
                st.sidebar.warning(f'Please Refresh or Press \'R\'')
            else:
                st.sidebar.warning('Failed to delete user')

    for user in list(btn_update_list.keys()):
        if btn_update_list[user]:
            update_user(state, all_data, user) #Takes user to the update page. The specific user is taken from the list
            time.sleep(2)

    #Solution attempt for the state function bug
    # for user in list(state.btn_update_list.keys()):
    #     if state.btn_update_list[user]:
    #         state.user_btn = state.btn_update_list[user]
    #         while not update_user(state, all_data, user):
    #             state.user_btn = True
    #         else:
    #             state.user_btn = False
    #         st.write(state.user_btn)
            #time.sleep(3)

def update_user(state, all_data, from_list='NA'): #The from_list variable is to update the specific user from the delete list
    #Update Page
    st.write('# **UPDATE USER PAGE**')
    if from_list == 'NA':
        users = []
        for data in all_data:
            users.append(data.get('username'))
    else:
        users = [from_list]

    user_sel = st.selectbox('Choose User', users)
    user_details = get_user_by_name(user_sel)

    if user_details.get('role') == 'grader':
        role_default = 0
    elif user_details.get('role') == 'admin':
        role_default = 1
    elif user_details.get('role') == 'superuser':
        role_default = 2

    if user_details.get('status') == 'Active':
        status_default = 0
    elif user_details.get('status') == 'Non-Active':
        status_default = 1

    cc1, cc2 = st.beta_columns([1,3])
    with st.form('register'):
        with cc1:
            st.write('# Current User Details')

            st.write('## Username: ')
            st.write('### ',user_details.get('username'))

            st.write('## Role: ')
            st.write('### ',user_details.get('role'))

            st.write('## Status: ')
            st.write(user_details['status'])

        with cc2:
            st.write('# New User Details')
            state.regis = edict()
            state.regis.name = st.text_input('username', value= user_details.get('username'))
            state.regis.pwd = st.text_input('password', type='password')
            state.regis.repwd = st.text_input('re-type Password', type='password')
            state.regis.role = st.selectbox('Role',['grader', 'admin', 'superuser'], index=role_default)
            state.regis.status = st.selectbox('Status: ',['Active', 'Non-Active'], index=status_default)
            state.regis.hash_pwd = hash_password(state.regis.pwd)
        submit_update = st.form_submit_button('Update This User')

        if submit_update:
            if (state.regis.repwd != state.regis.pwd):
                st.error('Not same password, check your password!')
                time.sleep(1)
                return False

            if state.regis.name == None or len(state.regis.name) < 4:
                st.error('Your username is Null or too short (less than 4 character)!')
                time.sleep(2)
                return False

            if not state.regis.pwd and not state.regis.repwd:
                isUpdated = update_user_data(user_sel, state.regis.name, state.regis.role, state.regis.status)
                if isUpdated:
                    st.success('User Updated')
                    time.sleep(1)
                    return False
                else:
                    st.warning('User was not updated because the user details are the same')
                    print(isUpdated)
                    time.sleep(3)
                    return False

            else:
                isPwdUpdated = update_user_pwd(user_sel, state.regis.hash_pwd)
                isUpdated = update_user_data(user_sel, state.regis.name, state.regis.role, state.regis.status)
                if isPwdUpdated or isUpdated:
                    st.success('User updated')
                    # st.warning(isPwdUpdated)
                    # st.warning(isUpdated)
                    time.sleep(2)
                    return False
                else:
                    st.warning('User was not updated because the user details are the same')
                    time.sleep(3)
                    return False
        return submit_update

