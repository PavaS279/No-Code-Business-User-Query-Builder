import streamlit as st
import requests
import time

# --- Constants ---
METABASE_PUBLIC_URL = "https://swift-barb.metabaseapp.com/public/dashboard/3684da17-150a-4b59-a8b8-da220729c0fc"
WEBHOOK_URL = "https://manually-cunning-bluejay.ngrok-free.app/webhook-test/2b3514c4-bf88-4f79-83a8-c0d19381cab0"

# --- Page Setup ---
st.set_page_config(page_title="ERP Dashboard", layout="wide")
st.title("📊 Unified ERP Dashboard")

# --- Refresh Dashboard ---
if "reload_ts" not in st.session_state:
    st.session_state.reload_ts = int(time.time())

if st.button("🔄 Refresh Dashboard"):
    st.session_state.reload_ts = int(time.time())

iframe_url = f"{METABASE_PUBLIC_URL}?reload={st.session_state.reload_ts}"
st.markdown(f"""
    <iframe src="{iframe_url}"
            frameborder="0"
            width="100%"
            height="600"
            allowtransparency="true">
    </iframe>
""", unsafe_allow_html=True)

# --- Session State Defaults ---
if "chat_open" not in st.session_state:
    st.session_state.chat_open = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        ("Bot", 'Click on the "Refresh Dashboard" button to update and view the latest data in your dashboard.')
    ]

# --- Chat Icon ---
with st.sidebar:
    if st.button("💬 Open/Close Chat"):
        st.session_state.chat_open = not st.session_state.chat_open

# --- Chat Window ---
if st.session_state.chat_open:
    with st.container():
        st.markdown("""
            <div style="position: fixed; bottom: 20px; right: 20px; width: 350px;
                        max-height: 450px; background-color: white; border: 1px solid #ccc;
                        border-radius: 10px; padding: 15px; overflow-y: auto; z-index: 9999;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        """, unsafe_allow_html=True)

        # Display chat history
        for sender, msg in st.session_state.chat_history:
            label = "🧑 You" if sender == "User" else "🤖 Bot"
            st.markdown(f"**{label}:** {msg}")

        # Input form
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("Type your message...", key="chat_input")
            submitted = st.form_submit_button("Send")
            if submitted and user_input.strip():
                st.session_state.chat_history.append(("User", user_input))
                try:
                    res = requests.post(WEBHOOK_URL, json={"prompt": user_input}, timeout=10)
                    bot_msg = "✅ Message successfully sent to backend." if res.ok else "⚠️ Backend error."
                except Exception as e:
                    bot_msg = f"❌ Failed: {str(e)}"
                st.session_state.chat_history.append(("Bot", bot_msg))

        st.markdown("</div>", unsafe_allow_html=True)
