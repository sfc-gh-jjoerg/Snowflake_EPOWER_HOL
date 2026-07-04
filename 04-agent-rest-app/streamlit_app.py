import streamlit as st
import json
import os
import requests
import pandas as pd

st.set_page_config(page_title="EPOWER Assistant", layout="wide")

# Agent registry — maps display name to Snowflake object name
AGENT_OPTIONS = {
    "EPOWER Intelligence (All Domains)": "EPOWER_AGENT",
    "Operations (VPP & Energy Market)": "EPOWER_OPS_AGENT",
    "Commercial (Sales & Service)": "EPOWER_COMMERCIAL_AGENT",
    "People (HR & Workforce)": "EPOWER_PEOPLE_AGENT",
}

SNOWFLAKE_HOST = os.getenv("SNOWFLAKE_HOST")
THREADS_URL_BASE = f"https://{SNOWFLAKE_HOST}/api/v2/cortex/threads"


def get_agent_url(agent_name: str) -> str:
    path = f"/api/v2/databases/EPOWER_DEMO/schemas/EPOWER_GOLD/agents/{agent_name}:run"
    return f"https://{SNOWFLAKE_HOST}{path}"


def get_token():
    with open("/snowflake/session/token") as f:
        return f.read().strip()


def get_headers():
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_token()}",
        "X-Snowflake-Authorization-Token-Type": "OAUTH",
    }


def get_session():
    return st.connection("snowflake").session()


def run_query(sql):
    return get_session().sql(sql).to_pandas()


def create_thread():
    """Create a new conversation thread and return thread_id."""
    headers = get_headers()
    resp = requests.post(THREADS_URL_BASE, headers=headers, json={"origin_application": "EPOWER_APP"})
    resp.raise_for_status()
    return resp.json()["thread_id"]


# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_dashboard, tab_chat = st.tabs(["Dashboard", "Agent Chat"])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: SALES & ENERGY DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
with tab_dashboard:
    st.title("EPOWER Sales & Energy Dashboard")

    regions = run_query("SELECT REGION_KEY, REGION_NAME FROM EPOWER_DEMO.EPOWER_GOLD.REGION_DIM ORDER BY REGION_NAME")
    categories = run_query("SELECT DISTINCT CATEGORY_NAME FROM EPOWER_DEMO.EPOWER_GOLD.PRODUCT_CATEGORY_DIM ORDER BY 1")

    f1, f2, f3 = st.columns(3)
    with f1:
        selected_regions = st.multiselect("Region", options=regions["REGION_NAME"].tolist(), default=regions["REGION_NAME"].tolist())
    with f2:
        selected_categories = st.multiselect("Product Category", options=categories["CATEGORY_NAME"].tolist(), default=categories["CATEGORY_NAME"].tolist())
    with f3:
        time_period = st.selectbox("Time Period", ["Last 12 Months", "Last 6 Months", "Last 3 Months", "Last 30 Days", "All Time"])

    period_map = {
        "Last 12 Months": "DATEADD('month', -12, CURRENT_DATE())",
        "Last 6 Months": "DATEADD('month', -6, CURRENT_DATE())",
        "Last 3 Months": "DATEADD('month', -3, CURRENT_DATE())",
        "Last 30 Days": "DATEADD('day', -30, CURRENT_DATE())",
        "All Time": "'2020-01-01'",
    }
    date_filter = period_map[time_period]

    region_keys = regions[regions["REGION_NAME"].isin(selected_regions)]["REGION_KEY"].tolist()
    region_in = ",".join(str(k) for k in region_keys) if region_keys else "NULL"
    cat_in = ",".join(f"'{c}'" for c in selected_categories) if selected_categories else "''"

    base_where = f"""
        WHERE s.DATE >= {date_filter}
        AND s.REGION_KEY IN ({region_in})
        AND p.CATEGORY_NAME IN ({cat_in})
    """

    # --- KPIs ---
    kpi_sales = run_query(f"""
        SELECT
            COALESCE(SUM(s.AMOUNT), 0) AS total_revenue,
            COUNT(*) AS total_contracts,
            COUNT(DISTINCT s.CUSTOMER_KEY) AS unique_customers,
            COALESCE(ROUND(AVG(s.AMOUNT), 0), 0) AS avg_deal_size
        FROM EPOWER_DEMO.EPOWER_GOLD.SALES_FACT s
        JOIN EPOWER_DEMO.EPOWER_GOLD.PRODUCT_DIM p ON s.PRODUCT_KEY = p.PRODUCT_KEY
        {base_where}
    """)

    vpp_latest = run_query("""
        SELECT
            SUM(ACTIVE_VPP_DEVICES) AS devices,
            ROUND(AVG(AVG_BATTERY_SOC_PCT), 1) AS battery_soc
        FROM EPOWER_DEMO.EPOWER_GOLD.MART_VPP_CAPACITY_HOURLY
        WHERE HOUR = (SELECT MAX(HOUR) FROM EPOWER_DEMO.EPOWER_GOLD.MART_VPP_CAPACITY_HOURLY)
    """)

    c1, c2, c3, c4 = st.columns(4)
    if not kpi_sales.empty:
        c1.metric("Total Revenue", f"\u20ac{kpi_sales.iloc[0]['TOTAL_REVENUE']:,.0f}")
        c2.metric("Contracts Sold", f"{int(kpi_sales.iloc[0]['TOTAL_CONTRACTS']):,}")
    if not vpp_latest.empty and vpp_latest.iloc[0]['DEVICES'] is not None:
        c3.metric("VPP Devices", f"{int(vpp_latest.iloc[0]['DEVICES']):,}")
        c4.metric("Avg Battery SoC", f"{vpp_latest.iloc[0]['BATTERY_SOC']}%")
    else:
        c3.metric("VPP Devices", "---")
        c4.metric("Avg Battery SoC", "---")

    st.divider()

    # --- Charts Row 1 ---
    left, right = st.columns(2)

    with left:
        st.subheader("Monthly Revenue Trend")
        trend = run_query(f"""
            SELECT
                DATE_TRUNC('month', s.DATE)::DATE AS MONTH,
                ROUND(SUM(s.AMOUNT), 0) AS REVENUE
            FROM EPOWER_DEMO.EPOWER_GOLD.SALES_FACT s
            JOIN EPOWER_DEMO.EPOWER_GOLD.PRODUCT_DIM p ON s.PRODUCT_KEY = p.PRODUCT_KEY
            {base_where}
            GROUP BY 1 ORDER BY 1
        """)
        if not trend.empty:
            st.line_chart(trend, x="MONTH", y="REVENUE")

    with right:
        st.subheader("Revenue by Category")
        by_cat = run_query(f"""
            SELECT
                p.CATEGORY_NAME AS CATEGORY,
                ROUND(SUM(s.AMOUNT), 0) AS REVENUE
            FROM EPOWER_DEMO.EPOWER_GOLD.SALES_FACT s
            JOIN EPOWER_DEMO.EPOWER_GOLD.PRODUCT_DIM p ON s.PRODUCT_KEY = p.PRODUCT_KEY
            {base_where}
            GROUP BY 1 ORDER BY 2 DESC
        """)
        if not by_cat.empty:
            st.bar_chart(by_cat, x="CATEGORY", y="REVENUE")

    # --- Charts Row 2 ---
    left2, right2 = st.columns(2)

    with left2:
        st.subheader("VPP Fleet (Last 7 Days)")
        vpp_trend = run_query("""
            SELECT
                HOUR,
                SUM(TOTAL_SOLAR_YIELD_KW) AS SOLAR_KW,
                AVG(AVG_BATTERY_SOC_PCT) AS BATTERY_SOC,
                SUM(NET_GRID_KW) AS NET_GRID_KW
            FROM EPOWER_DEMO.EPOWER_GOLD.MART_VPP_CAPACITY_HOURLY
            WHERE HOUR >= DATEADD('day', -7, CURRENT_TIMESTAMP())
            GROUP BY HOUR ORDER BY HOUR
        """)
        if not vpp_trend.empty:
            st.line_chart(vpp_trend, x="HOUR", y=["SOLAR_KW", "NET_GRID_KW"])

    with right2:
        st.subheader("Electricity Spot Price (Last 7 Days)")
        prices = run_query("""
            SELECT
                HOUR,
                PRICE_EUR_MWH
            FROM EPOWER_DEMO.EPOWER_GOLD.MART_DAY_AHEAD_PRICES
            WHERE HOUR >= DATEADD('day', -7, CURRENT_TIMESTAMP())
            ORDER BY HOUR
        """)
        if not prices.empty:
            st.line_chart(prices, x="HOUR", y="PRICE_EUR_MWH")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: AGENT CHAT (with Threads API)
# ─────────────────────────────────────────────────────────────────────────────
with tab_chat:
    st.title("EPOWER Agent Chat")

    # Agent selector
    selected_agent_label = st.selectbox(
        "Select Agent",
        options=list(AGENT_OPTIONS.keys()),
        index=0,
        help="Choose a domain-specific agent or the all-in-one agent.",
    )
    selected_agent_name = AGENT_OPTIONS[selected_agent_label]
    st.caption(f"Chatting with **{selected_agent_label}** (`{selected_agent_name}`)")

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
    if "active_agent" not in st.session_state:
        st.session_state.active_agent = selected_agent_name

    # Reset conversation when user switches agents
    if st.session_state.active_agent != selected_agent_name:
        st.session_state.active_agent = selected_agent_name
        st.session_state.chat_messages = []
        st.session_state.thread_id = None
        st.session_state.parent_message_id = 0
        st.session_state.last_request = None
        st.session_state.last_response_raw = None
        st.rerun()

    # Toolbar: New Conversation + REST toggle
    toolbar_left, toolbar_right = st.columns([1, 3])
    with toolbar_left:
        if st.session_state.chat_messages:
            if st.button("New Conversation", type="secondary"):
                st.session_state.chat_messages = []
                st.session_state.thread_id = None
                st.session_state.parent_message_id = 0
                st.session_state.last_request = None
                st.session_state.last_response_raw = None
                st.rerun()
    with toolbar_right:
        show_payload = st.toggle("Show REST API Payloads", value=False)

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

    # Starter prompts (only when no messages yet)
    if not st.session_state.chat_messages:
        st.markdown("**Try one of these:**")
        prompt_cols = st.columns(3)
        starters = [
            "What was last month's revenue by region?",
            "Show VPP battery trend for the last week",
            "Top 5 products by revenue this quarter",
        ]
        for i, starter in enumerate(starters):
            if prompt_cols[i].button(starter, key=f"starter_{i}"):
                st.session_state["_pending_prompt"] = starter
                st.rerun()

    # Phase 2: Process the pending request (user message is now visible)
    if st.session_state._processing:
        with st.chat_message("assistant"):
            try:
                # Create thread on first message
                if st.session_state.thread_id is None:
                    st.session_state.thread_id = create_thread()
                    st.session_state.parent_message_id = 0

                # Build request — only send the latest user message (thread has history)
                latest_user_msg = st.session_state.chat_messages[-1]["content"]
                request_body = {
                    "thread_id": st.session_state.thread_id,
                    "parent_message_id": st.session_state.parent_message_id,
                    "messages": [
                        {"role": "user", "content": [{"type": "text", "text": latest_user_msg}]}
                    ],
                    "stream": True,
                }
                agent_url = get_agent_url(selected_agent_name)
                st.session_state.last_request = {
                    "method": "POST",
                    "url": agent_url,
                    "body": request_body,
                }

                headers = get_headers()
                headers["Accept"] = "text/event-stream"
                response = requests.post(agent_url, headers=headers, json=request_body, stream=True)
                response.raise_for_status()

                # Streaming placeholder for real-time text output
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

                    # Capture metadata for thread continuation
                    if "metadata" in event:
                        meta = event["metadata"]
                        if meta.get("role") == "assistant" and "message_id" in meta:
                            assistant_message_id = meta["message_id"]

                    # Stream incremental text tokens (content_index >= 2 = answer text)
                    if "text" in event and event.get("content_index", 0) >= 2:
                        streamed_text += event["text"]
                        # Fix mojibake on-the-fly
                        try:
                            display_text = streamed_text.encode("latin-1").decode("utf-8")
                        except (UnicodeDecodeError, UnicodeEncodeError):
                            display_text = streamed_text
                        text_placeholder.markdown(display_text + "▌")

                    # Final completed event — extract tables, charts, and final text
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

                # Update parent_message_id for next turn
                if assistant_message_id:
                    st.session_state.parent_message_id = assistant_message_id

                # Final render — remove cursor and show complete text
                final_text = streamed_text or "No response."
                try:
                    final_text = final_text.encode("latin-1").decode("utf-8")
                except (UnicodeDecodeError, UnicodeEncodeError):
                    pass
                text_placeholder.markdown(final_text)

                # Render tables and charts below the text
                for tbl in collected_tables:
                    if tbl["title"]:
                        st.caption(tbl["title"])
                    df = pd.DataFrame(tbl["data"], columns=tbl["columns"])
                    st.dataframe(df, use_container_width=True)
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
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": f"Error: {str(e)}",
                })
                st.session_state.last_response_raw = {"error": str(e)}

        st.session_state._processing = False
        st.rerun()

    # Chat input (only shown when not processing — avoids input appearing above spinner)
    if not st.session_state._processing:
        pending = st.session_state.pop("_pending_prompt", None)
        prompt = st.chat_input("Ask the EPOWER Agent...")
        user_input = pending or prompt

        # Phase 1: User submits a question — store it and rerun to show it
        if user_input:
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            st.session_state._processing = True
            st.rerun()

    # REST Payload Viewer
    if show_payload and st.session_state.last_request:
        st.divider()
        with st.expander("REST API Request", expanded=False):
            st.code(json.dumps(st.session_state.last_request, indent=2, default=str), language="json")
        with st.expander("REST API Response (raw SSE events)", expanded=False):
            resp_json = json.dumps(st.session_state.last_response_raw, indent=2, default=str)
            st.markdown(
                f'<div style="max-height:400px;overflow-y:auto;background:#f8f9fa;padding:12px;border-radius:6px;"><pre><code>{resp_json}</code></pre></div>',
                unsafe_allow_html=True,
            )
