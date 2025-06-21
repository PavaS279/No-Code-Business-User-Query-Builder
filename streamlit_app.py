import json
import streamlit as st
from typing import Union
import pandas as pd
import altair as alt
import uuid
import hashlib

# Ensure page config and session initialization happens before anything else
st.set_page_config(page_title="Cortex Analyst", page_icon="🧠", layout="wide")

cnx = st.connection("snowflake")
session = cnx.session()

# Config
SEMANTIC_MODEL_PATH = "CORTEX_ANALYST.CORTEX_AI.CORTEX_ANALYST_STAGE/nlp.yaml"
CHAT_PROCEDURE = "CORTEX_ANALYST.CORTEX_AI.CORTEX_ANALYST_CHAT_PROCEDURE"
DREMIO_PROCEDURE = "SALESFORCE_DREMIO.SALESFORCE_SCHEMA_DREMIO.DREMIO_DATA_PROCEDURE"

def initialize_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "display_messages" not in st.session_state:
        st.session_state.display_messages = []
    if "processing" not in st.session_state:
        st.session_state.processing = False
    if "dataframes" not in st.session_state:
        st.session_state.dataframes = []
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None
# yy
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

def display_chat_message(role, content, message_index=None):
    with st.chat_message(role):
        if isinstance(content, str):
            st.markdown(content)
        elif isinstance(content, dict):
            if content.get("type") == "text":
                st.markdown(content.get("value"))

            elif content.get("type") == "sql":
                st.code(content.get("value"), language="sql")

            elif content.get("type") == "result":
                df = pd.DataFrame(content.get("data"))
                sql = content.get("sql")

                st.markdown("**Generated SQL:**")
                st.code(sql, language="sql")

                if not df.empty:
                    st.success("✅ Dremio executed successfully")
                    tab1, tab2 = st.tabs(["Data 📄", "Chart 📉"])
                    with tab1:
                        st.dataframe(df, use_container_width=True)
                    with tab2:
                        # Use a stable hash from SQL statement as key
                        sql_hash = hashlib.md5(sql.encode()).hexdigest()[:8]
                        display_charts_tab(df, sql_hash)
                else:
                    st.warning("⚠️ No data returned from Dremio.")

def display_charts_tab(df: pd.DataFrame, key_suffix: str) -> None:
    """
    Display various charts based on the DataFrame using unique keys.

    Args:
        df (pd.DataFrame): The query results from Dremio.
        key_suffix (str): A unique identifier (e.g., UUID or hash) to prevent widget key collisions.
    """
    if len(df.columns) >= 2:
        all_cols = list(df.columns)

        col1, col2 = st.columns(2)
        x_col = col1.selectbox("X axis", all_cols, key=f"x_col_{key_suffix}")
        y_col = col2.selectbox(
            "Y axis", [col for col in all_cols if col != x_col], key=f"y_col_{key_suffix}"
        )

        chart_type = st.selectbox(
            "Select chart type",
            [
                "Line Chart 📈", "Bar Chart 📊", "Pie Chart 🥧", "Scatter Plot 🔵",
                "Histogram 📊", "Box Plot 📦", "Combo Chart 🔀", "Number Chart 🔢"
            ],
            key=f"chart_type_{key_suffix}"
        )

        chart_data = df[[x_col, y_col]].dropna()

        if chart_type == "Line Chart 📈":
            st.line_chart(chart_data.set_index(x_col))

        elif chart_type == "Bar Chart 📊":
            st.bar_chart(chart_data.set_index(x_col))

        elif chart_type == "Pie Chart 🥧":
            pie = alt.Chart(chart_data).mark_arc().encode(
                theta=alt.Theta(field=y_col, type="quantitative"),
                color=alt.Color(field=x_col, type="nominal")
            )
            st.altair_chart(pie, use_container_width=True)

        elif chart_type == "Scatter Plot 🔵":
            scatter = alt.Chart(chart_data).mark_circle(size=60).encode(
                x=x_col,
                y=y_col,
                tooltip=[x_col, y_col]
            ).interactive()
            st.altair_chart(scatter, use_container_width=True)

        elif chart_type == "Histogram 📊":
            hist = alt.Chart(chart_data).mark_bar().encode(
                alt.X(y_col, bin=True),
                y='count()'
            )
            st.altair_chart(hist, use_container_width=True)

        elif chart_type == "Box Plot 📦":
            box = alt.Chart(chart_data).mark_boxplot().encode(
                x=x_col,
                y=y_col
            )
            st.altair_chart(box, use_container_width=True)

        elif chart_type == "Combo Chart 🔀":
            line = alt.Chart(chart_data).mark_line(color='blue').encode(x=x_col, y=y_col)
            bar = alt.Chart(chart_data).mark_bar(opacity=0.3).encode(x=x_col, y=y_col)
            combo = bar + line
            st.altair_chart(combo, use_container_width=True)

        elif chart_type == "Number Chart 🔢":
            st.metric(label=f"{y_col} Total", value=round(chart_data[y_col].sum(), 2))

    else:
        st.warning("⚠️ At least 2 columns are required to render a chart.")

def process_user_question(question):
    try:
        st.session_state.processing = True

        user_msg = {
            "role": "user",
            "content": [{"type": "text", "text": question}]
        }
        st.session_state.messages.append(user_msg)
        st.session_state.display_messages.append({
            "role": "user",
            "content": {"type": "text", "value": question}
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.spinner("Analyzing your question..."):
            response, error = call_cortex_analyst_procedure(st.session_state.messages)

            if error:
                raise Exception(f"Cortex Analyst Error: {error}")
            if not response or not isinstance(response, dict):
                raise Exception("❌ Invalid or empty response from Cortex Analyst")

            analyst_response = response.get("message", {})
            content_block = analyst_response.get("content", [])
            if not isinstance(content_block, list):
                raise Exception("❌ Unexpected format in 'content_block'")

            sql_statement = ""
            explanation = ""
            for block in content_block:
                if block.get("type") == "text":
                    explanation = block.get("text", "")
                elif block.get("type") == "sql" and "statement" in block:
                    sql_statement = block["statement"]

            if not sql_statement:
                raise Exception("❌ SQL statement not generated by analyst")

            dremio_result, dremio_error = call_dremio_data_procedure(sql_statement)
            if dremio_error:
                raise Exception(f"❌ Dremio execution failed: {dremio_error}")

            st.session_state.messages.append({
                "role": "analyst",
                "content": content_block
            })

            st.session_state.display_messages.append({
                "role": "assistant",
                "content": {
                    "type": "result",
                    "sql": sql_statement,
                    "data": dremio_result.to_dict(orient="records")
                }
            })

    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        st.error(error_msg)
        st.session_state.display_messages.append({
            "role": "assistant",
            "content": {"type": "text", "value": error_msg}
        })
    finally:
        st.session_state.processing = False

def render_chat_interface():
    # Handle input first and rerun immediately
    if st.session_state.get("pending_question"):
        question = st.session_state.pending_question
        st.session_state.pending_question = None
        process_user_question(question)
        st.rerun()  # Safe: rerun before rendering

    # UI Rendering starts
    st.title("🧠 NLP-Bashboards with Unified ERP Data")
    st.caption("Ask natural questions. Get Bashboards + Unified ERP Data results.")

    for msg in st.session_state.display_messages:
        display_chat_message(msg["role"], msg["content"])

    question = st.chat_input("Ask something...", disabled=st.session_state.processing)
    if question:
        st.session_state.pending_question = question
        st.rerun()  # Trigger rerun safely before display

# Entry point
initialize_session()
render_chat_interface()
