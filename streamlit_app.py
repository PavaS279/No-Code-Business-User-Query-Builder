import json
import streamlit as st
from typing import Union
import pandas as pd

# from snowflake.snowpark.context import get_active_session
# from snowflake.snowpark.exceptions import SnowparkSQLException

cnx = st.connection("snowflake")
session = cnx.session()

# Config
SEMANTIC_MODEL_PATH = "CORTEX_ANALYST.CORTEX_AI.CORTEX_ANALYST_STAGE/nlp.yaml"
CHAT_PROCEDURE = "CORTEX_ANALYST.CORTEX_AI.CORTEX_ANALYST_CHAT_PROCEDURE"
DREMIO_PROCEDURE = "SALESFORCE_DREMIO.SALESFORCE_SCHEMA_DREMIO.DREMIO_DATA_PROCEDURE"

def initialize_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.active_suggestion = None
        st.session_state.warnings = []
        st.session_state.form_submitted = {}
        st.session_state.pending_clarification = None
    if "display_messages" not in st.session_state:
        st.session_state.display_messages = []
    if "processing" not in st.session_state:
        st.session_state.processing = False
    if "dataframes" not in st.session_state:
        st.session_state.dataframes = []

def call_cortex_analyst_procedure(messages):
    try:
        messages_json = json.dumps(messages)
        result = session.call(CHAT_PROCEDURE, messages_json, SEMANTIC_MODEL_PATH)
        if not result:
            return None, "No response from procedure"
        procedure_response = json.loads(result)
        if procedure_response.get("success", False):
            return procedure_response.get("content", {}), None
        else:
            return None, procedure_response.get("error_message", "Unknown procedure error")
    except Exception as e:
        return None, f"Error: {str(e)}"

def call_dremio_data_procedure(sql_statement):
    try:
        df_result = session.call(DREMIO_PROCEDURE, sql_statement)
        if hasattr(df_result, "to_pandas"):
            return df_result.to_pandas(), None
        return None, "Unexpected result format from Dremio procedure"
    except Exception as e:
        return None, f"Dremio Error: {str(e)}"

def display_chat_message(role, content):
    with st.chat_message(role):
        if isinstance(content, str):
            st.markdown(content)
        elif isinstance(content, dict):
            if "message" in content:
                st.markdown(content["message"])
            if "query" in content:
                st.code(content["query"], language="sql")

def display_charts_tab(df: pd.DataFrame, message_index: int) -> None:
    if len(df.columns) >= 2:
        all_cols = list(df.columns)
        col1, col2 = st.columns(2)
        x_col = col1.selectbox("X axis", all_cols, key=f"x_col_{message_index}")
        y_col = col2.selectbox("Y axis", [col for col in all_cols if col != x_col], key=f"y_col_{message_index}")
        chart_type = st.selectbox("Select chart type", ["Line Chart 📈", "Bar Chart 📊"], key=f"chart_type_{message_index}")

        chart_data = df[[x_col, y_col]].dropna()
        chart_data.set_index(x_col, inplace=True)

        if chart_type == "Line Chart 📈":
            st.line_chart(chart_data)
        elif chart_type == "Bar Chart 📊":
            st.bar_chart(chart_data)
    else:
        st.write("⚠️ At least 2 columns required to display chart")

def process_user_question(question):
    try:
        st.session_state.processing = True

        user_msg = {"role": "user", "content": [{"type": "text", "text": question}]}
        st.session_state.messages.append(user_msg)
        st.session_state.display_messages.append({"role": "user", "content": question})
        display_chat_message("user", question)

        with st.spinner("Analyzing your question..."):
            response, error = call_cortex_analyst_procedure(st.session_state.messages)
            if error:
                raise Exception(error)

            analyst_response = response.get("message", {})
            content_block = analyst_response.get("content", [])

            sql_statement = ""
            explanation = ""
            for block in content_block:
                if block.get("type") == "text":
                    explanation = block.get("text", "")
                elif block.get("type") == "sql" and "statement" in block:
                    sql_statement = block["statement"]

            if not sql_statement:
                raise Exception("No SQL found in response.")

            dremio_result, dremio_error = call_dremio_data_procedure(sql_statement)
            if dremio_error:
                raise Exception(dremio_error)

            display_chat_message("assistant", explanation)
            display_chat_message("assistant", {"message": "Generated SQL:", "query": sql_statement})

            if dremio_result is not None and not dremio_result.empty:
                with st.chat_message("assistant"):
                    st.success("✅ Dremio executed successfully")
                    tab1, tab2 = st.tabs(["Data 📄", "Chart 📉"])
                    with tab1:
                        st.dataframe(dremio_result, use_container_width=True)
                    with tab2:
                        display_charts_tab(dremio_result, len(st.session_state.dataframes))
                    st.session_state.dataframes.append(dremio_result)
            else:
                display_chat_message("assistant", "⚠️ No data returned from Dremio.")

            analyst_msg = {"role": "analyst", "content": content_block}
            st.session_state.messages.append(analyst_msg)

            assistant_display = f"{explanation}\n\n**Generated SQL:**\n```sql\n{sql_statement}\n```\n\n✅ Executed in Dremio."
            st.session_state.display_messages.append({"role": "assistant", "content": assistant_display})

    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        st.error(error_msg)
        st.session_state.display_messages.append({"role": "assistant", "content": error_msg})
    finally:
        st.session_state.processing = False

def render_chat_interface():
    st.title("🧠 NLP-Bashboards with Unified ERP Data")
    st.caption("Ask natural questions. Get Bashboards + Unified ERP Data results.")
    for msg in st.session_state.display_messages:
        display_chat_message(msg["role"], msg["content"])
    if prompt := st.chat_input("Ask something...", disabled=st.session_state.processing):
        process_user_question(prompt)

def main():
    st.set_page_config(page_title="Cortex Analyst", page_icon="🧠", layout="wide")
    initialize_session()
    render_chat_interface()

if __name__ == "__main__":
    main()
