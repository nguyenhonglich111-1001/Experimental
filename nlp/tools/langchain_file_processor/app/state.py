"""
Manages the Streamlit session state for the application.

This module provides functions for initializing and manipulating the session state,
ensuring a centralized and consistent approach to state management across the app.
"""
import streamlit as st
from .langchain_logic import delete_file

def initialize_session_state():
    """Initializes all necessary session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "file_to_delete" not in st.session_state:
        st.session_state.file_to_delete = None

def handle_file_deletion_request(file_path: str):
    """Sets the file_to_delete state variable, to be handled by the UI."""
    st.session_state.file_to_delete = file_path

def confirm_file_deletion(vectorstore):
    """
    Performs the file deletion and resets the state.
    This is intended to be used as a callback for the 'Yes, Delete' button.
    """
    if st.session_state.file_to_delete:
        file_path = st.session_state.file_to_delete
        if delete_file(vectorstore, file_path):
            # On successful deletion, reset the state and let the app rerun
            st.session_state.file_to_delete = None
        else:
            # If deletion fails, just reset the state. Error is shown in delete_file.
            st.session_state.file_to_delete = None

def cancel_file_deletion():
    """
    Cancels the file deletion process and resets the state.
    This is intended to be used as a callback for the 'Cancel' button.
    """
    st.session_state.file_to_delete = None
