import streamlit as st
import requests
from typing import Optional

# Configure Streamlit page
st.set_page_config(
    page_title="GenAI RAG Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend API configuration
# BACKEND_URL = "http://backend:8000"  # For Docker
BACKEND_URL = "http://localhost:8000"  # For local development


class ChatInterface:
    def __init__(self):
        self.init_session_state()

    def init_session_state(self):
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "current_document" not in st.session_state:
            st.session_state.current_document = None
        if "document_processed" not in st.session_state:
            st.session_state.document_processed = False

    def upload_and_process_pdf(self, uploaded_file) -> bool:
        try:
            with st.spinner("Processing PDF..."):
                files = {"file": uploaded_file.getvalue()}
                response = requests.post(f"{BACKEND_URL}/process-pdf", files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")})

                if response.status_code == 200:
                    result = response.json()
                    st.session_state.current_document = result.get("filename", uploaded_file.name)
                    st.session_state.document_processed = True
                    st.success(f"✅ Document '{st.session_state.current_document}' processed successfully!")
                    return True
                else:
                    error_msg = response.json().get("detail", "Unknown error")
                    self._handle_api_error(response.status_code, error_msg)
                    return False

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Connection error: {str(e)}")
            return False

    def _handle_api_error(self, status_code: int, error_msg: str):
        """Handle different API error types with user-friendly messages"""
        if status_code == 429:
            st.error(f"⏳ **OpenAI Quota Exceeded**\n\n{error_msg}\n\n💡 **What to do:**\n- Check your OpenAI account billing\n- Wait for quota reset\n- Upgrade your OpenAI plan")
        elif status_code == 401:
            st.error(f"🔐 **Authentication Error**\n\n{error_msg}\n\n💡 **What to do:**\n- Check your OpenAI API key\n- Verify API key permissions\n- Ensure proper environment setup")
        elif status_code == 503:
            st.error(f"🚧 **Service Unavailable**\n\n{error_msg}\n\n💡 **What to do:**\n- Try again in a few minutes\n- Check OpenAI service status\n- Contact support if issue persists")
        else:
            st.error(f"❌ Error processing PDF: {error_msg}")

    def query_document(self, question: str) -> Optional[dict]:
        try:
            payload = {
                "question": question,
                "filename": st.session_state.current_document
            }
            with st.spinner("Generating answer..."):
                response = requests.post(f"{BACKEND_URL}/query", json=payload)

            if response.status_code == 200:
                return response.json()
            else:
                error_msg = response.json().get("detail", "Unknown error")
                self._handle_api_error(response.status_code, error_msg)
                return None

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Connection error: {str(e)}")
            return None

    def check_backend_health(self) -> bool:
        try:
            response = requests.get(f"{BACKEND_URL}/health")
            return response.status_code == 200
        except:
            return False

    def render_sidebar(self):
        st.sidebar.title("📁 GenAI RAG Chatbot")
        st.sidebar.markdown("---")

        if self.check_backend_health():
            st.sidebar.success("🟢 Backend Connected")
        else:
            st.sidebar.error("🔴 Backend Disconnected")

        uploaded_file = st.sidebar.file_uploader("Upload a PDF", type="pdf")
        if uploaded_file:
            if st.sidebar.button("📤 Process PDF"):
                if self.upload_and_process_pdf(uploaded_file):
                    st.rerun()

        if st.session_state.current_document:
            st.sidebar.markdown("---")
            st.sidebar.subheader("📄 Current Document")
            st.sidebar.info(st.session_state.current_document)

            if st.sidebar.button("❌ Clear Document"):
                st.session_state.current_document = None
                st.session_state.document_processed = False
                st.session_state.messages = []
                st.rerun()

        st.sidebar.markdown("---")
        st.sidebar.markdown("""
        ℹ️ **How to Use:**
        1. Upload a PDF
        2. Click "Process PDF"
        3. Ask questions
        """)

        st.sidebar.markdown("---")
        st.sidebar.caption("Powered by RAG, FAISS, GPT & FastAPI")

    def render_chat_interface(self):
        st.title("🧠 Chat with Your Document")

        if not st.session_state.document_processed:
            st.info("📄 Please upload and process a PDF from the sidebar.")
            return

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "assistant" and message.get("sources"):
                    with st.expander("📚 Sources"):
                        for i, src in enumerate(message["sources"]):
                            st.markdown(f"**Source {i+1}**:\n```{src['content']}```")

        if prompt := st.chat_input("Ask something..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                response = self.query_document(prompt)
                if response:
                    answer = response.get("answer", "No response.")
                    sources = response.get("sources", [])
                    st.markdown(answer)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })

                    if sources:
                        with st.expander("📚 Sources"):
                            for i, src in enumerate(sources):
                                st.markdown(f"**Source {i+1}**:\n```{src['content']}```")
                else:
                    st.error("❌ Failed to get a response.")

    def run(self):
        st.markdown("""
        <style>
        .stChatMessage { background-color: #f9f9f9; padding: 1rem; border-radius: 10px; margin-bottom: 1rem; }
        </style>
        """, unsafe_allow_html=True)

        self.render_sidebar()
        self.render_chat_interface()


def main():
    ChatInterface().run()


if __name__ == "__main__":
    main()
