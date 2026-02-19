import os, json
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Writesonic GEO Chat", layout="wide")
st.title("Writesonic GEO Chat Prototype")
st.caption("Chat with your GEO analytics via Writesonic API")

WRITESONIC_API_KEY = os.getenv("WRITESONIC_API_KEY", "")

st.sidebar.header("Settings")
geo_url = st.sidebar.text_input("Paste GEO Analytics Endpoint URL")

def fetch_geo(url):
    headers = {"Authorization": f"Bearer {WRITESONIC_API_KEY}"}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        st.error(f"Error {r.status_code}: {r.text}")
        return None
    return r.json()

if st.sidebar.button("Fetch GEO Data"):
    data = fetch_geo(geo_url)
    if data:
        st.session_state["geo_data"] = data

if "geo_data" not in st.session_state:
    st.info("Paste your GEO endpoint and click Fetch GEO Data")
    st.stop()

data = st.session_state["geo_data"]

st.subheader("Raw GEO Data")
st.json(data)

st.subheader("Chat with your analytics")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_q = st.chat_input("Ask a question about your GEO analytics")
if user_q:
    st.session_state.messages.append({"role": "user", "content": user_q})

    prompt = f"""
You are a GEO strategist. Analyze the following analytics data and answer the question.

Question: {user_q}

Data:
{json.dumps(data)[:12000]}
"""

    url = "https://api.writesonic.com/v2/business/content/chatsonic?engine=premium"
    headers = {
        "Authorization": f"Bearer {WRITESONIC_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "input_text": prompt,
        "enable_google_results": False,
        "enable_memory": False
    }

    r = requests.post(url, headers=headers, json=payload)

    if r.status_code != 200:
        answer = f"Error {r.status_code}: {r.text}"
    else:
        answer = r.text

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()