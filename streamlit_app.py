import streamlit as st
import jwt
import time
import requests

# --- Title ---
st.title("NLP-Based Dashboard with Unified ERP Data")

# --- JWT Metabase Embed Generation ---
def get_signed_metabase_url():
    METABASE_SITE_URL = "http://34.207.232.170:3000"
    METABASE_SECRET_KEY = "0187202d69e5a05cc28bd8639f73d6482678b737fe4b5e10a28622d94de1f4"  # Replace with your actual secret

    payload = {
        "resource": {"dashboard": 2},  # Replace with your actual dashboard ID
        "params": {},
        "exp": round(time.time()) + (10 * 60)  # 10 minutes expiry
    }

    token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")
    iframe_url = f"{METABASE_SITE_URL}/embed/dashboard/{token}?bordered=true&titled=true"
    return iframe_url

# --- Render Metabase Iframe ---
iframe_url = get_signed_metabase_url()
st.markdown(f"""
    <iframe src="{iframe_url}"
            frameborder="0"
            width="100%"
            height="600"
            allowtransparency="true">
    </iframe>
""", unsafe_allow_html=True)


# --- Chat UI State ---
if "chat_open" not in st.session_state:
    st.session_state.chat_open = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Floating Chat Icon ---
chat_icon_html = """
<style>
#chat-toggle-btn {
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
<div id="chat-toggle-btn">💬</div>
<script>
document.getElementById("chat-toggle-btn").onclick = function() {
    fetch("/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ "toggle_chat": true })
    }).then(() => {
        window.location.reload();
    });
};
</script>
"""
st.markdown(chat_icon_html, unsafe_allow_html=True)

# --- Fallback Toggle Button (for development use only) ---
if st.button("Open Chat (Dev fallback)"):
    st.session_state.chat_open = not st.session_state.chat_open

# --- Render Chat Box ---
if st.session_state.chat_open:
    st.markdown("""
        <style>
        .chat-box {
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 350px;
            max-height: 400px;
            background-color: #ffffff;
            border: 1px solid #ccc;
            border-radius: 10px;
            padding: 15px;
            overflow-y: auto;
            z-index: 9999;
            box-shadow: 0 2px 12px rgba(0,0,0,0.2);
        }
        </style>
        <div class="chat-box">
    """, unsafe_allow_html=True)

    # Chat History
    for sender, msg in st.session_state.chat_history:
        label = "🧑 You" if sender == "User" else "🤖 Bot"
        st.markdown(f"**{label}:** {msg}")

    # Chat Input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Type your question", key="chat_input")
        submitted = st.form_submit_button("Send")
        if submitted and user_input.strip():
            st.session_state.chat_history.append(("User", user_input))

            # Send to Webhook
            webhook_url = "https://manually-cunning-bluejay.ngrok-free.app/webhook-test/806f1553-6b37-4189-94cb-1c4caa1cdbd8"
            try:
                response = requests.post(webhook_url, json={"message": user_input}, timeout=10, verify=False)
                bot_response = response.text if response.ok else f"Webhook error: {response.status_code}"
            except Exception as e:
                bot_response = f"Exception: {str(e)}"

            st.session_state.chat_history.append(("Bot", bot_response))

    st.markdown("</div>", unsafe_allow_html=True)
