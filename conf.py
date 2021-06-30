import os
from os.path import join as path

def configs():
    with open('.machine_id.txt','r') as f:
        machine_id = f.readline()
    
    if machine_id in 'localdevelopment':
        server = False
    elif machine_id in 'serverbinsho':
        server = True
    
    conf = {
        'server': server,

        # streamlit app
        'page_title' : 'Multispectral Data Entry',
        'page_icon' : None,
        'page_layout': 'wide',
        'initial_sidebar_state': 'auto',
        # graph settings
        'colors_graph_gradient' : ["#125c30", "#3b7640","#5f9152", "#84ac64", "#aac777", "#d2e38c",
                    "#fbffa3", "#faf28a", "#f9e471", "#fad659", "#fbc741", "#fdb727", "#ffa600"],
        'colors_graph_google' : ['#4285F4', '#DB4437', '#e8602c', '#F4B400',
                    '#0F9D58', '#333333', '#d44baa',  '#f4980f'],
    }
    if server:
        conf['db_setting'] = {
                'server': server,
                'host' : '127.0.0.1',
                'username' :  'agfian',
                'passwd' : 'katalaluan123456',
                'port' : 27017,
                'db_name' : 'agfian1',
                'collection_name': 'multispectral',
                'collection_user' : 'users_multispectral',
                'bank_images_msp' : path('/mnt/hdd_1/data/multispectral/'),
            }




    else:
        conf['db_setting'] =  {
                'server': server,
                'host' : 'localhost',
                'username' :  '',
                'passwd' : '',
                'port' : 27017,
                'db_name' : 'latihan',
                'collection_name': 'msp_ffbs',
                'collection_user' : 'users',
                'bank_images_msp' : path('images',),
            }

    return conf


