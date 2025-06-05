import streamlit as st

# --- Title ---
st.title("NLP-Based Dashboard with Unified ERP Data s")

# --- Connect to Snowflake (Uncomment and configure when ready) ---
cnx = st.connection("snowflake")
session = cnx.session()

# --- Snowflake Call Logic ---
def call_snowflake_procedure(prompt):
    try:
        # Replace with actual Snowflake execution
        cursor = session.cursor()
        cursor.execute(f"CALL CORTEX_ANALYST_COMPLEX.SALESFORCEDB.GET_SQL_FROM_QUESTION_PIN('{prompt}')")
        result = cursor.fetchone()
        return result[0] if result else "No response from procedure."
        # return f"🧠 Simulated SQL from: {prompt}"  # Placeholder
    except Exception as e:
        return f"Error: {e}"
    # finally:
    #     cursor.close()

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

# --- Server-side Toggle Fallback ---
if st.button("Open Chat (Dev fallback)"):
    st.session_state.chat_open = not st.session_state.chat_open

# --- Handle Toggle from JS (if any) ---
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
            response = call_snowflake_procedure(user_input)
            st.session_state.chat_history.append(("Bot", response))

    st.markdown("</div>", unsafe_allow_html=True)
