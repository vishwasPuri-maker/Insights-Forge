import streamlit as st
import requests
import os

st.set_page_config(page_title="Apex AI Live Analytics", layout="wide")

st.title("Apex AI Enterprise Analytics Assistant")
st.sidebar.header("System Status")
st.sidebar.text("Model: Gemma 2B")
st.sidebar.text("Engine: Ollama")
st.sidebar.text("Security: Multi-Agent Guardrails")
st.sidebar.text("Memory: SQLite Persistent")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask an analytics question or test a prompt injection..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            api_url = os.environ.get("API_URL", "http://localhost:8000")
            res = requests.post(f"{api_url}/chat", json={"query": prompt, "session_id": "local_live_1"})
            res_data = res.json()
            
            response_text = res_data.get("response", "Error: No response")
            
            # Display special warning block if blocked by Security Guardrail
            if res_data.get("status") == "blocked":
                st.error("🚨 **SECURITY INTERVENTION TRIGGERED**")
                st.warning(response_text)
                st.session_state.messages.append({"role": "assistant", "content": f"🚨 {response_text}"})
            else:
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            
            with st.expander("Enterprise Governance & Orchestration Metadata"):
                st.json({
                    "Active Agent": res_data.get("role"),
                    "Analysis Type": res_data.get("analysis_type"),
                    "Confidence Score": res_data.get("confidence"),
                    "Context Sources": res_data.get("sources"),
                    "Security Warnings": res_data.get("warnings", []),
                    "Schema Status": "Strictly Validated"
                })
                
        except Exception as e:
            st.error(f"Failed to connect to local backend: {e}")
