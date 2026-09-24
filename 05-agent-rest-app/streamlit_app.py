import streamlit as st
import json
import os
import requests
import pandas as pd

st.set_page_config(page_title="EPOWER VPP Assistant", layout="wide")

AGENT_NAME = "EPOWER_OPS_AGENT"
SNOWFLAKE_HOST = os.getenv("SNOWFLAKE_HOST")
AGENT_URL = f"https://{SNOWFLAKE_HOST}/api/v2/databases/EPOWER_DEMO/schemas/EPOWER_GOLD/agents/{AGENT_NAME}:run"
THREADS_URL = f"https://{SNOWFLAKE_HOST}/api/v2/cortex/threads"


def get_token():
    with open("/snowflake/session/token") as f:
        return f.read().strip()


def get_headers():
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_token()}",
        "X-Snowflake-Authorization-Token-Type": "OAUTH",
    }


def create_thread():
    resp = requests.post(THREADS_URL, headers=get_headers(), json={"origin_application": "EPOWER_VPP_APP"})
    resp.raise_for_status()
    return resp.json()["thread_id"]


# --- Sidebar: Agent info + API documentation ---
with st.sidebar:
    st.title("EPOWER VPP Assistant")
    st.caption("Powered by Cortex Agent REST API")

    st.markdown("### Agent")
    st.code(AGENT_NAME, language="text")
    st.markdown("""
    **Tools available:**
    - **vpp_analyst** — Fleet telemetry, battery dispatch actions, price zones, arbitrage margins
    - **market_prices_analyst** — Day-ahead electricity prices (EPEX DE-LU)
    - **energy_docs_search** — Energy policies, regulations, subsidies
    - **data_to_chart** — Automatic chart generation
    """)

    st.divider()
    st.markdown("### REST API Pattern")
    st.markdown("""
    This app demonstrates the **Cortex Agent REST API**:

    1. **Create a thread** for stateful conversations
    2. **POST to the agent endpoint** with the user message
    3. **Stream SSE events** for real-time token rendering
    4. **Track `message_id`** for multi-turn conversation context
    """)
    endpoint = AGENT_URL.replace(f"https://{SNOWFLAKE_HOST}", "")
    st.code(f"POST {endpoint}", language="text")
    st.markdown("""
    **Authentication:** OAuth bearer token from the container session
    (`/snowflake/session/token`). No API keys needed when running inside Snowflake.
    """)

    st.divider()
    show_payload = st.toggle("Show REST Payloads", value=False, help="View the raw API request and response")


# --- Session state ---
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "last_request" not in st.session_state:
    st.session_state.last_request = None
if "last_response_raw" not in st.session_state:
    st.session_state.last_response_raw = None
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "parent_message_id" not in st.session_state:
    st.session_state.parent_message_id = 0
if "_processing" not in st.session_state:
    st.session_state._processing = False


# --- Main area ---
st.title("VPP Fleet Intelligence")
st.caption("Ask the Operations Agent about VPP telemetry, battery dispatch, energy prices, and arbitrage margins.")

# New conversation button
if st.session_state.chat_messages:
    if st.button("New Conversation", type="secondary"):
        st.session_state.chat_messages = []
        st.session_state.thread_id = None
        st.session_state.parent_message_id = 0
        st.session_state.last_request = None
        st.session_state.last_response_raw = None
        st.rerun()

# Starter prompts (shown when no messages)
if not st.session_state.chat_messages:
    cols = st.columns(2)
    starters = [
        "What was the total VPP margin last week?",
        "Show battery dispatch actions by price zone",
        "Which clusters export the most during high prices?",
        "What are the current day-ahead electricity prices?",
    ]
    for i, s in enumerate(starters):
        if cols[i % 2].button(s, key=f"starter_{i}", use_container_width=True):
            st.session_state["_pending_prompt"] = s
            st.rerun()

# Display chat history
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("tables"):
            for t in msg["tables"]:
                if t.get("title"):
                    st.caption(t["title"])
                st.dataframe(pd.DataFrame(t["data"], columns=t["columns"]), use_container_width=True)
        if msg.get("charts"):
            for c in msg["charts"]:
                st.vega_lite_chart(c, use_container_width=True)

# Process pending request (user message already visible)
if st.session_state._processing:
    with st.chat_message("assistant"):
        try:
            if st.session_state.thread_id is None:
                st.session_state.thread_id = create_thread()
                st.session_state.parent_message_id = 0

            latest_user_msg = st.session_state.chat_messages[-1]["content"]
            request_body = {
                "thread_id": st.session_state.thread_id,
                "parent_message_id": st.session_state.parent_message_id,
                "messages": [{"role": "user", "content": [{"type": "text", "text": latest_user_msg}]}],
                "stream": True,
            }
            st.session_state.last_request = {"method": "POST", "url": AGENT_URL, "body": request_body}

            headers = get_headers()
            headers["Accept"] = "text/event-stream"
            response = requests.post(AGENT_URL, headers=headers, json=request_body, stream=True)
            response.raise_for_status()

            text_placeholder = st.empty()
            text_placeholder.markdown("*Thinking...*")
            streamed_text = ""
            collected_tables = []
            collected_charts = []
            raw_events = []
            assistant_message_id = None

            for line in response.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data: "):
                    continue
                payload = line[6:]
                if payload.strip() == "[DONE]":
                    break
                try:
                    event = json.loads(payload)
                    raw_events.append(event)
                except json.JSONDecodeError:
                    continue

                if "metadata" in event:
                    meta = event["metadata"]
                    if meta.get("role") == "assistant" and "message_id" in meta:
                        assistant_message_id = meta["message_id"]

                if "text" in event and event.get("content_index", 0) >= 2:
                    streamed_text += event["text"]
                    try:
                        display_text = streamed_text.encode("latin-1").decode("utf-8")
                    except (UnicodeDecodeError, UnicodeEncodeError):
                        display_text = streamed_text
                    text_placeholder.markdown(display_text + "\u258c")

                if event.get("status") == "completed" and "content" in event:
                    evt_meta = event.get("metadata", {})
                    if evt_meta.get("assistant_message_id"):
                        assistant_message_id = evt_meta["assistant_message_id"]

                    for content_item in event["content"]:
                        ctype = content_item.get("type", "")
                        if ctype == "text":
                            text_val = content_item.get("text", "").strip()
                            if text_val:
                                streamed_text = text_val
                        elif ctype == "table":
                            table = content_item.get("table", {})
                            rs = table.get("result_set", {})
                            meta_rs = rs.get("resultSetMetaData", {})
                            cols = [r["name"] for r in meta_rs.get("rowType", [])]
                            data = rs.get("data", [])
                            if cols and data:
                                collected_tables.append({"title": table.get("title", ""), "columns": cols, "data": data})
                        elif ctype == "chart":
                            spec = content_item.get("chart", {}).get("chart_spec", "")
                            if spec:
                                try:
                                    collected_charts.append(json.loads(spec))
                                except json.JSONDecodeError:
                                    pass

            if assistant_message_id:
                st.session_state.parent_message_id = assistant_message_id

            final_text = streamed_text or "No response."
            try:
                final_text = final_text.encode("latin-1").decode("utf-8")
            except (UnicodeDecodeError, UnicodeEncodeError):
                pass
            text_placeholder.markdown(final_text)

            for tbl in collected_tables:
                if tbl["title"]:
                    st.caption(tbl["title"])
                st.dataframe(pd.DataFrame(tbl["data"], columns=tbl["columns"]), use_container_width=True)
            for chart_spec in collected_charts:
                st.vega_lite_chart(chart_spec, use_container_width=True)

            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": final_text,
                "tables": collected_tables,
                "charts": collected_charts,
            })
            st.session_state.last_response_raw = raw_events

        except Exception as e:
            st.session_state.chat_messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
            st.session_state.last_response_raw = {"error": str(e)}

    st.session_state._processing = False
    st.rerun()

# Chat input
if not st.session_state._processing:
    pending = st.session_state.pop("_pending_prompt", None)
    prompt = st.chat_input("Ask the VPP Operations Agent...")
    user_input = pending or prompt

    if user_input:
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        st.session_state._processing = True
        st.rerun()

# REST payload viewer
if show_payload and st.session_state.last_request:
    st.divider()
    col_req, col_resp = st.columns(2)
    with col_req:
        st.markdown("**Request**")
        st.code(json.dumps(st.session_state.last_request, indent=2, default=str), language="json")
    with col_resp:
        st.markdown("**Response (SSE events)**")
        st.code(json.dumps(st.session_state.last_response_raw, indent=2, default=str), language="json")
