import streamlit as st
import requests

# --- Title ---
st.title("NLP-Based Dashboard with Unified ERP Data")

# --- Chat UI State ---
if "chat_open" not in st.session_state:
    st.session_state.chat_open = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Metabase Embed ---
st.markdown("""
    <style>
    .metabase-container {
        width: 70%;
        height: 600px;
        display: inline-block;
    }
    </style>
    <div class="metabase-container">
        <iframe src="http://44.197.151.60:3000/embed/dashboard/your_dashboard_id#bordered=false&theme=night"
                frameborder="0" width="100%" height="100%">
        </iframe>
    </div>
""", unsafe_allow_html=True)

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

# --- Server-side Toggle Fallback ---
if st.button("Open Chat (Dev fallback)"):
    st.session_state.chat_open = not st.session_state.chat_open

# --- Handle Toggle from JS (if any) ---
if "toggle_chat" in st.session_state:
    st.session_state.chat_open = not st.session_state.chat_open
    del st.session_state["toggle_chat"]

# --- Function to Send Data to Webhook ---
def send_to_webhook(question):
    webhook_url = "https://13.218.21.136:5678/webhook-test/806f1553-6b37-4189-94cb-1c4caa1cdbd8"
    payload = {"question": question}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("response", "No response from Webhook.")
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error sending to Webhook: {e}"

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

    # Display History
    for sender, msg in st.session_state.chat_history:
        label = "🧑 You" if sender == "User" else "🤖 Bot"
        st.markdown(f"**{label}:** {msg}")

    # Input Form
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Type your question", key="chat_input")
        submitted = st.form_submit_button("Send")
        if submitted and user_input.strip():
            st.session_state.chat_history.append(("User", user_input))
            
            # Send question to Webhook
            response = send_to_webhook(user_input)
            st.session_state.chat_history.append(("Bot", response))

    st.markdown("</div>", unsafe_allow_html=True)
