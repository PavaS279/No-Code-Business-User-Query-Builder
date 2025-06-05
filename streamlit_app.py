import streamlit as st
import numpy as np
import pandas as pd
from math import pi

# --- Snowflake Connection Configuration ---
# cnx = st.connection("snowflake")
# session = cnx.session()

def call_snowflake_procedure(prompt):
    conn = session
    try:
        cursor = conn.cursor()
        cursor.execute(f"CALL CALL_CHATBOT_PROC('{prompt}')")
        result = cursor.fetchone()
        return result[0] if result else "No response from procedure."
    except Exception as e:
        return f"Error: {e}"
    finally:
        cursor.close()

# --- Chat State ---
if "chat_open" not in st.session_state:
    st.session_state.chat_open = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Floating Chat Icon ---
chat_icon_html = """
<style>
#chat-fab {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: #0e76a8;
    color: white;
    border-radius: 50%;
    width: 60px;
    height: 60px;
    font-size: 30px;
    text-align: center;
    line-height: 60px;
    cursor: pointer;
    z-index: 9999;
}
</style>
<div id="chat-fab" onclick="fetch('/?chat_toggle=true')">💬</div>
<script>
const fab = window.parent.document.getElementById('chat-fab');
if (fab) {
    fab.onclick = function() {
        window.location.href = window.location.href + "&chat_toggle=true";
    };
}
</script>
"""
st.markdown(chat_icon_html, unsafe_allow_html=True)

# --- Toggle Chat Box on Click ---
if st.query_params().get("chat_toggle"):
    st.session_state.chat_open = not st.session_state.chat_open
    st.query_params()  # Clear toggle

# --- Render Chat Box if Open ---
if st.session_state.chat_open:
    st.markdown("""
        <style>
        .chat-box {
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 350px;
            max-height: 500px;
            background-color: #f9f9f9;
            border: 1px solid #ccc;
            border-radius: 10px;
            padding: 15px;
            overflow-y: auto;
            z-index: 9999;
        }
        .chat-input {
            width: calc(100% - 10px);
            padding: 5px;
            margin-top: 10px;
        }
        </style>
        <div class="chat-box">
    """, unsafe_allow_html=True)

    # Display chat history
    for speaker, message in st.session_state.chat_history:
        label = "🧑 You" if speaker == "User" else "🤖 Bot"
        st.markdown(f"**{label}:** {message}")

    # Input and send
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Your message", key="chat_input")
        submitted = st.form_submit_button("Send")
        if submitted and user_input.strip():
            st.session_state.chat_history.append(("User", user_input))
            response = call_snowflake_procedure(user_input)
            st.session_state.chat_history.append(("Bot", response))

    st.markdown("</div>", unsafe_allow_html=True)
