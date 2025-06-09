import streamlit as st
import jwt
import time
import requests

# --- Configuration ---
METABASE_PUBLIC_DASHBOARD = "https://swift-barb.metabaseapp.com/public/dashboard/3684da17-150a-4b59-a8b8-da220729c0fc"
METABASE_SECRET_KEY = "mb_OkwqioX3KW4CDFaAkLY3r+9iwQQiBhAOY3tYMvagWW4="
CHAT_WEBHOOK_URL = "https://manually-cunning-bluejay.ngrok-free.app/webhook-test/2b3514c4-bf88-4f79-83a8-c0d19381cab0"

# --- JWT Token Generation for Embedded Dashboard ---
def get_signed_metabase_url():
    payload = {
        "resource": {"dashboard": 2},
        "params": {},
        "exp": round(time.time()) + (10 * 60)
    }
    token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")
    iframe_url = f"{METABASE_PUBLIC_DASHBOARD}/embed/dashboard/{token}?bordered=true&titled=true&reload={int(time.time())}"
    return iframe_url

# --- Page Configuration ---
st.set_page_config(page_title="ERP NLP Dashboard", layout="wide")
st.markdown("<style>footer {visibility: hidden;}</style>", unsafe_allow_html=True)

# --- Dashboard Embed with Refresh Button ---
st.title("📊 Unified ERP Dashboard")
if st.button("🔄 Refresh Dashboard"):
    st.session_state["dashboard_reload"] = int(time.time())
iframe_url = get_signed_metabase_url()
st.markdown(f"""
    <iframe src="{iframe_url}"
            frameborder="0"
            width="100%"
            height="600"
            allowtransparency="true">
    </iframe>
""", unsafe_allow_html=True)

# --- Chat State Management ---
if "chat_open" not in st.session_state:
    st.session_state.chat_open = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        ("Bot", 'Click on the "Refresh Dashboard" button to update and view the latest data in your dashboard.')
    ]

# --- Floating Chat Icon ---
chat_toggle_html = """
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
st.markdown(chat_toggle_html, unsafe_allow_html=True)

# --- Dev Toggle ---
if st.button("Toggle Chat (Dev)"):
    st.session_state.chat_open = not st.session_state.chat_open

# --- Render Chat Box ---
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

    # Chat History
    for sender, msg in st.session_state.chat_history:
        prefix = "🧑 You" if sender == "User" else "🤖 Bot"
        st.markdown(f"**{prefix}:** {msg}")

    # Chat Input
    with st.form("chat_form", clear_on_submit=True):
        chat_input = st.text_input("Type your message...", key="chat_input")
        sent = st.form_submit_button("Send")
        if sent and chat_input.strip():
            st.session_state.chat_history.append(("User", chat_input))
            try:
                resp = requests.post(
                    CHAT_WEBHOOK_URL,
                    json={"prompt": chat_input},
                    timeout=10
                )
                if resp.ok:
                    reply = "✅ Message successfully sent to backend."
                else:
                    reply = "⚠️ Backend responded with an error."
            except Exception as e:
                reply = f"❌ Failed to send message: {str(e)}"

            st.session_state.chat_history.append(("Bot", reply))

    st.markdown("</div>", unsafe_allow_html=True)
