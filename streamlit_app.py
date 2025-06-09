import streamlit as st
import requests
import time

# --- Constants ---
PUBLIC_METABASE_URL = "https://swift-barb.metabaseapp.com/public/dashboard/3684da17-150a-4b59-a8b8-da220729c0fc"
CHAT_WEBHOOK_URL = "https://manually-cunning-bluejay.ngrok-free.app/webhook-test/2b3514c4-bf88-4f79-83a8-c0d19381cab0"

# --- UI Setup ---
st.set_page_config(page_title="ERP Dashboard", layout="wide")
st.title("📊 Unified ERP Dashboard")

# --- Refresh Button with Cache Buster ---
if st.button("🔄 Refresh Dashboard"):
    st.session_state["reload_ts"] = int(time.time())

reload_ts = st.session_state.get("reload_ts", int(time.time()))
iframe_url = f"{PUBLIC_METABASE_URL}?reload={reload_ts}"
st.markdown(f"""
    <iframe src="{iframe_url}"
            frameborder="0"
            width="100%"
            height="600"
            allowtransparency="true">
    </iframe>
""", unsafe_allow_html=True)

# --- Chat Session State ---
if "chat_open" not in st.session_state:
    st.session_state.chat_open = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        ("Bot", 'Click on the "Refresh Dashboard" button to update and view the latest data in your dashboard.')
    ]

# --- Floating Chat Button ---
chat_button_html = """
<style>
#chat-toggle-btn {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: #0084ff;
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
<div id="chat-toggle-btn">💬</div>
<script>
document.getElementById("chat-toggle-btn").onclick = function() {
    fetch(window.location.href, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ "toggle_chat": true })
    }).then(() => window.location.reload());
};
</script>
"""
st.markdown(chat_button_html, unsafe_allow_html=True)

# --- Optional Dev Fallback ---
if st.button("Toggle Chat (Dev)"):
    st.session_state.chat_open = not st.session_state.chat_open

# --- Chat UI ---
if st.session_state.chat_open:
    st.markdown("""
        <style>
        .chat-box {
            position: fixed;
            bottom: 100px;
            right: 20px;
            width: 350px;
            max-height: 450px;
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 10px;
            padding: 15px;
            overflow-y: auto;
            z-index: 9999;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        </style>
        <div class="chat-box">
    """, unsafe_allow_html=True)

    for sender, msg in st.session_state.chat_history:
        label = "🧑 You" if sender == "User" else "🤖 Bot"
        st.markdown(f"**{label}:** {msg}")

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Type your message...", key="chat_input")
        sent = st.form_submit_button("Send")
        if sent and user_input.strip():
            st.session_state.chat_history.append(("User", user_input))
            try:
                res = requests.post(CHAT_WEBHOOK_URL, json={"prompt": user_input}, timeout=10)
                bot_reply = "✅ Message successfully sent to backend." if res.ok else "⚠️ Backend responded with an error."
            except Exception as e:
                bot_reply = f"❌ Failed to send message: {str(e)}"
            st.session_state.chat_history.append(("Bot", bot_reply))

    st.markdown("</div>", unsafe_allow_html=True)
