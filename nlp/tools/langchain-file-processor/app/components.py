"""
Contains reusable Streamlit UI components for the application.
"""
import os
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from .langchain_logic import get_indexed_files
from .state import handle_file_deletion_request

def display_deletable_file_list(vectorstore):
    """Gets and displays the list of indexed files with delete buttons."""
    files = get_indexed_files(vectorstore)
    if files:
        st.markdown("I have the following files in my knowledge base:")
        for file_path in files:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"- `{os.path.basename(file_path)}`")
            with col2:
                st.button(
                    "Delete",
                    key=f"delete_{file_path}",
                    on_click=handle_file_deletion_request,
                    args=(file_path,),
                )
    else:
        st.markdown("I do not have any files in my knowledge base yet. Please upload a PDF in the sidebar.")

def display_chat_history(vectorstore):
    """Displays the chat history and the file list UI when appropriate."""
    for message in st.session_state.messages:
        # Determine the role and content based on the message type
        if isinstance(message, HumanMessage):
            role = "user"
            content = message.content
        elif isinstance(message, AIMessage):
            role = "assistant"
            content = message.content
        elif isinstance(message, dict): # For backward compatibility
            role = message.get("role")
            content = message.get("content")
        else:
            continue # Skip unknown message types

        with st.chat_message(role):
            # Handle special message types like the file list
            if isinstance(message, dict) and message.get("type") == "file_list":
                display_deletable_file_list(vectorstore)
            else:
                st.markdown(content)
