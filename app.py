import streamlit as st
from streamlit import session_state as state
import  os

from conf import configs
from easydict import EasyDict as edict



# After Streamlit 0.65
from streamlit.report_thread import get_report_ctx
from streamlit.server.server import Server


from pages.excel import excel_page
from pages.form import form_page
from pages.summary import summarize_page, sidebar
from pages.delete_item import delete_page
from pages.post_processing import post_processing_page
from utils import manage_state, init_state, delete_state, set_state

conf = configs()



def main():
    # configs
    st.set_page_config(page_title=conf['page_title'],
                page_icon=conf['page_icon'],
                layout=conf['page_layout'],
                initial_sidebar_state=conf['initial_sidebar_state'])
    manage_state()
    # init_state('frame_rgbs', [None, 'None', 'None', 'None'])

    cols_login = st.columns((4,4,4))
    cols_login[1].write('# Data Entry Multispectral')

    pages = {
        'Excel Page' : excel_page,
        'Form Submit': form_page,
        'Show Datas': summarize_page,
        'Delete Item': delete_page,
        'Post Processing': post_processing_page
    }
    st.write(state.frame_rgbs)

    pages[sidebar(pages)](state)

    st.write('End Page')


# -------------- FOR STATE MANAGEMENT -----------------

if __name__ == '__main__':
    main()
