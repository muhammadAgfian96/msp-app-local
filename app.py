import streamlit as st
import  os

from conf import configs
from easydict import EasyDict as edict

from streamlit.hashing import _CodeHasher


# After Streamlit 0.65
from streamlit.report_thread import get_report_ctx
from streamlit.server.server import Server


from pages.excel import excel_page
from pages.form import form_page
from pages.summary import summarize_page, sidebar
from pages.delete_item import delete_page


conf = configs()



def main():
    # configs
    st.set_page_config(page_title=conf['page_title'],
                page_icon=conf['page_icon'],
                layout=conf['page_layout'],
                initial_sidebar_state=conf['initial_sidebar_state'])
    state = _get_state()
    state.data_ffbs = state.data_ffbs if state.data_ffbs else {}

    cols_login = st.beta_columns((4,4,4))
    cols_login[1].write('# Data Entry Multispectral')

    pages = {
        'Excel Page' : excel_page,
        'Form Submit': form_page,
        'Show Datas': summarize_page,
        'Delete Item': delete_page
    }

    pages[sidebar(pages)](state)

    st.write('End Page')
    state.sync()


# -------------- FOR STATE MANAGEMENT -----------------

class _SessionState:
    def __init__(self, session, hash_funcs):
        """Initialize SessionState instance."""
        self.__dict__["_state"] = {
            "data": {},
            "hash": None,
            "hasher": _CodeHasher(hash_funcs),
            "is_rerun": False,
            "session": session,
        }

    def __call__(self, **kwargs):
        """Initialize state data once."""
        for item, value in kwargs.items():
            if item not in self._state["data"]:
                self._state["data"][item] = value

    def __getitem__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)
    def __getattr__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __setitem__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def __setattr__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value
    def clear(self):
        """Clear session state and request a rerun."""
        self._state["data"].clear()
        self._state["session"].request_rerun()
    def sync(self):
        """Rerun the app with all state values up to date from the beginning to fix rollbacks."""

        # Ensure to rerun only once to avoid infinite loops
        # caused by a constantly changing state value at each run.
        #
        # Example: state.value += 1
        if self._state["is_rerun"]:
            self._state["is_rerun"] = False
        elif self._state["hash"] is not None:
            if self._state["hash"] != self._state["hasher"].to_bytes(self._state["data"], None):
                self._state["is_rerun"] = True
                self._state["session"].request_rerun()

        self._state["hash"] = self._state["hasher"].to_bytes(self._state["data"], None)


def _get_session():
    session_id = get_report_ctx().session_id
    session_info = Server.get_current()._get_session_info(session_id)

    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")
    return session_info.session


def _get_state(hash_funcs=None):
    session = _get_session()

    if not hasattr(session, "_custom_session_state"):
        session._custom_session_state = _SessionState(session, hash_funcs)

    return session._custom_session_state


if __name__ == '__main__':
    main()
