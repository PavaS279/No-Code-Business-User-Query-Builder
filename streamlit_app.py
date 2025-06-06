import streamlit as st
import requests

# --- Page Setup ---
st.set_page_config(layout="wide")
st.title("NLP-Based Dashboard with Unified ERP Data")

# --- Layout with Embedded Metabase and Chat ---
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("""
        <iframe 
            src="http://44.197.151.60:3000" 
            width="100%" 
            height="800" 
            frameborder="0"
            allowfullscreen
        ></iframe>
    """, unsafe_allow_html=True)

# --- Chat UI State ---
if "chat_open" not in st.session_state:
    st.session_state.chat_open = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Chat Icon (Floating) ---
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

# --- Dev Fallback Button (optional for local testing) ---
if st.button("Open Chat (Dev fallback)"):
    st.session_state.chat_open = not st.session_state.chat_open

# --- JS Toggle Chat Handler ---
if "toggle_chat" in st.session_state:
    st.session_state.chat_open = not st.session_state.chat_open
    del st.session_state["toggle_chat"]

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

    for sender, msg in st.session_state.chat_history:
        label = "🧑 You" if sender == "User" else "🤖 Bot"
        st.markdown(f"**{label}:** {msg}")

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Type your question", key="chat_input")
        submitted = st.form_submit_button("Send")
        if submitted and user_input.strip():
            st.session_state.chat_history.append(("User", user_input))

            # --- Send message to webhook ---
            try:
                response = requests.post(
                    "https://13.218.21.136:5678/webhook-test/806f1553-6b37-4189-94cb-1c4caa1cdbd8",
                    json={"question": user_input},
                    timeout=5,
                    verify=False  # For self-signed certs; remove in prod
                )
                if response.ok:
                    reply = response.text
                else:
                    reply = f"Webhook error: {response.status_code}"
            except Exception as e:
                reply = f"Error: {e}"

            st.session_state.chat_history.append(("Bot", reply))

    st.markdown("</div>", unsafe_allow_html=True)
