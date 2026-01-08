# --- CLOUD FIX FOR CHROMADB ---
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# ------------------------------

import os
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader

# --- THE FIX IS HERE ---
from langchain_text_splitters import RecursiveCharacterTextSplitter
# -----------------------

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

class RAGEngine:
    def __init__(self, api_key):
        self.llm = ChatGroq(groq_api_key=api_key, model_name="llama3-8b-8192")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = None
        self.chain = None

    def process_document(self, pdf_path):
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        self.vector_store = Chroma.from_documents(documents=splits, embedding=self.embeddings)
        self._create_chain()
        return "✅ Document Processed Successfully!"

    def _create_chain(self):
        retriever = self.vector_store.as_retriever()
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Answer strictly based on the context. If unknown, say 'I do not know'. Context: {context}"),
            ("human", "{input}"),
        ])
        chain = create_stuff_documents_chain(self.llm, prompt)
        self.chain = create_retrieval_chain(retriever, chain)

    def ask(self, query):
        if not self.chain: return "⚠️ Please upload a file first."
        return self.chain.invoke({"input": query})["answer"]
