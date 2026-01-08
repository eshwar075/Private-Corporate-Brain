import streamlit as st
import tempfile
import os
from rag_engine import RAGEngine

st.set_page_config(page_title="Private Brain")
st.title("🧠 Private Corporate Brain")

if 'rag_engine' not in st.session_state:
    st.session_state.rag_engine = None

# --- SIDEBAR ---
st.sidebar.header("⚙️ Configuration")
api_key = st.sidebar.text_input("Groq API Key", type="password")
uploaded_file = st.sidebar.file_uploader("Upload PDF", type="pdf")
analyze_btn = st.sidebar.button("Analyze PDF")

# --- LOGIC ---
if analyze_btn:
    if not api_key:
        st.sidebar.error("⚠️ Missing API Key")
    elif not uploaded_file:
        st.sidebar.error("⚠️ Missing File")
    else:
        st.session_state.rag_engine = RAGEngine(api_key)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            path = tmp.name
        
        with st.spinner("Processing..."):
            status = st.session_state.rag_engine.process_document(path)
            st.sidebar.success(status)
            os.remove(path)

# --- CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ready. Upload PDF to start."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

prompt = st.chat_input("Ask a question...")

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    response = "⚠️ Please Analyze PDF first."
    if st.session_state.rag_engine:
        with st.spinner("Thinking..."):
            response = st.session_state.rag_engine.ask(prompt)
    
    st.chat_message("assistant").write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
