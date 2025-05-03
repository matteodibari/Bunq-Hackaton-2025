import streamlit as st
import time  # Optional: for simulating thinking time
from langchain_text_splitters import MarkdownTextSplitter
from utils import InputDocument  # Assuming you have a utils.py with InputDocument class

# --- 1. Setup & Import ---
# Assuming your NvidiaRAGPipeline class is in a file named 'rag.py'
# Make sure 'rag.py' is in the same directory or your Python path
try:
    from rag import NvidiaRAGPipeline
except ImportError:
    st.error("Could not import NvidiaRAGPipeline. Make sure 'rag.py' is in the correct path.")
    # Add a dummy class if import fails so the rest of the Streamlit app doesn't crash immediately
    class NvidiaRAGPipeline:
        def __init__(self, *args, **kwargs):
            st.warning("Using dummy RAG pipeline because import failed.")
        def generate_response(self, query):
            st.warning("Dummy RAG pipeline cannot generate real responses.")
            return f"Sorry, I couldn't process '{query}' due to an internal error.", ["No sources available"]

# --- 2. Load Data & Initialize Pipeline (Cached) ---

# Replace this with your actual document loading logic
# Example: Load from text files, PDFs, etc.
@st.cache_data  # Cache the raw data if loading is slow
def load_documents():
    print("Loading documents...") # Add print statement to see when this runs
    # Example: Replace with your actual document loading
    
    with open("bunq_full_docs.txt", 'r', encoding="utf-8") as file:
        content = file.read()

    text_splitter = MarkdownTextSplitter()
    texts = text_splitter.split_text(content)

    input_documents = []
    for text in texts:
        input_documents.append(InputDocument(content=text, metadata={"source": None}))

    rag_pipeline = NvidiaRAGPipeline(input_documents=input_documents, retrieve_k=20, rerank_k=5)


    print(f"Loaded {len(input_documents)} documents.")
    
    return input_documents, rag_pipeline

# Cache the RAG pipeline resource itself
@st.cache_resource # Use cache_resource for objects like ML models/pipelines
def initialize_rag_pipeline():
    print("Initializing RAG Pipeline...") # Add print statement to see when this runs
    input_docs, rag_pipeline = load_documents()
    return rag_pipeline



# --- App Title ---
st.title("💬 NVIDIA RAG Chatbot")
st.caption("🚀 A Streamlit chatbot powered by NvidiaRAGPipeline")

# --- Initialize Pipeline ---
rag_pipeline = initialize_rag_pipeline()

# --- 3. Initialize Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! How can I help you today?"}]

# --- 4. Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"]) # Use markdown to render potential formatting

# --- 5. Get User Input ---
if prompt := st.chat_input("Ask me something..."):
    if not rag_pipeline:
        st.error("RAG Pipeline is not available. Please check the logs.")
    else:
        # --- 6. Process User Input ---

        # Add user message to history and display it
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            try:
                # Call your RAG pipeline
                start_time = time.time() # Optional: time the response
                response, sources = rag_pipeline.generate_response(prompt)
                end_time = time.time()   # Optional: time the response

                # Format the response with sources (optional)
                formatted_response = f"{response}"
                # formatted_response = response # Or just the response

                message_placeholder.markdown(formatted_response)
                print(f"Response generated in {end_time - start_time:.2f} seconds.") # Optional

                # Add assistant response to history
                st.session_state.messages.append({"role": "assistant", "content": formatted_response})

            except Exception as e:
                st.error(f"An error occurred while generating the response: {e}")
                error_message = "Sorry, I encountered an error. Please try again."
                message_placeholder.markdown(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})