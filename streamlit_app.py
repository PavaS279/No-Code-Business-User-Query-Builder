import streamlit as st

# --- Heading ---
st.title("NLP-Based Dashboard with Unified ERP Data")

# --- Snowflake Procedure Call (Placeholder) ---
def call_snowflake_procedure(prompt):
    # Replace this with actual Snowflake session call
    return f"Echo from Snowflake procedure: '{prompt}'"

# --- Initialize Chatbot State ---
if "chat_open" not in st.session_state:
    st.session_state.chat_open = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Floating Chat Button (bottom-right) ---
chat_button_style = """
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
<button id="chat-fab" onclick="fetch('/_toggle_chat')">💬</button>
"""

st.markdown(chat_button_style, unsafe_allow_html=True)

# --- JavaScript to Send Toggle Event to Streamlit ---
toggle_script = """
<script>
const chatButton = window.parent.document.getElementById('chat-fab');
if (chatButton) {
    chatButton.addEventListener("click", () => {
        fetch(window.location.href, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ "toggle_chat": true })
        }).then(() => {
            window.location.reload();
        });
    });
</script>
"""
st.markdown(toggle_script, unsafe_allow_html=True)

# --- Workaround: Add Manual Toggle in UI for Fallback ---
if st.button("Toggle Chat (for testing without JS)"):
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
            max-height: 500px;
            background-color: #f9f9f9;
            border: 1px solid #ccc;
            border-radius: 10px;
            padding: 15px;
            overflow-y: auto;
            z-index: 9999;
        }
        </style>
        <div class="chat-box">
    """, unsafe_allow_html=True)

    # Display Chat History
    for speaker, message in st.session_state.chat_history:
        label = "🧑 You" if speaker == "User" else "🤖 Bot"
        st.markdown(f"**{label}:** {message}")

    # Input Form
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Your message", key="chat_input")
        submitted = st.form_submit_button("Send")
        if submitted and user_input.strip():
            st.session_state.chat_history.append(("User", user_input))
            response = call_snowflake_procedure(user_input)
            st.session_state.chat_history.append(("Bot", response))

    st.markdown("</div>", unsafe_allow_html=True)
