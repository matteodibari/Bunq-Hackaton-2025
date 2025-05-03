import streamlit as st
import base64
from PIL import Image
import io
import time
from langchain_text_splitters import MarkdownTextSplitter
from utils import InputDocument  # Assuming you have a utils.py with InputDocument class

# Try to import NvidiaRAGPipeline
try:
    from rag import NvidiaRAGPipeline
except ImportError:
    # Add a dummy class if import fails
    class NvidiaRAGPipeline:
        def __init__(self, *args, **kwargs):
            pass
        def generate_response(self, query):
            return f"I can help you with that! Here's information about '{query}' related to bunq API.", ["No sources available"]

# --- Load Data & Initialize Pipeline (Cached) ---
@st.cache_data  # Cache the raw data
def load_documents():
    # Example: Replace with your actual document loading
    try:
        with open("bunq_full_docs.txt", 'r', encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError:
        # Fallback content if file doesn't exist
        content = """
        # bunq API Documentation
        Welcome to the bunq API documentation. The bunq API is RESTful and has predictable resource-oriented URLs.
        ## Authentication
        To use the bunq API, you need to authenticate using OAuth 2.0 or API keys.
        ## Rate Limits
        The bunq API has rate limits to prevent abuse.
        """
    
    text_splitter = MarkdownTextSplitter()
    texts = text_splitter.split_text(content)

    input_documents = []
    for text in texts:
        input_documents.append(InputDocument(content=text, metadata={"source": None}))
    
    return input_documents

# Cache the RAG pipeline resource itself
@st.cache_resource  # Use cache_resource for objects like ML models/pipelines
def initialize_rag_pipeline():
    input_docs = load_documents()
    try:
        rag_pipeline = NvidiaRAGPipeline(input_documents=input_docs, retrieve_k=20, rerank_k=5)
    except Exception as e:
        st.warning(f"Could not initialize NvidiaRAGPipeline: {e}")
        # Create a dummy pipeline for demonstration
        rag_pipeline = NvidiaRAGPipeline()
    return rag_pipeline

# Check if we're in the main documentation page or chatbot page
if 'chatbot' not in st.query_params:
    # MAIN DOCUMENTATION PAGE
    # Set page configuration
    st.set_page_config(
        page_title="bunq API Documentation",
        page_icon=":bank:",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS to style the app like bunq's documentation (with added floating chat button)
    st.markdown("""
    <style>
        /* Global styling */
        body {
            color: white;
            background-color: #1e1e1e;
        }
        /* Header styling */
        .stApp header {
            background-color: #1e1e1e;
            color: white;
        }
        /* Main header/navbar */
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 20px;
            background-color: #1e1e1e;
            border-bottom: 1px solid #333;
            margin-bottom: 20px;
        }
        .logo-text {
            color: white;
            font-size: 20px;
            font-weight: bold;
            display: flex;
            align-items: center;
        }
        .search-container {
            display: flex;
            align-items: center;
            background-color: #333;
            border-radius: 5px;
            padding: 5px 10px;
        }
        .search-input {
            background-color: transparent;
            border: none;
            color: white;
            padding: 5px;
            width: 200px;
        }
        .search-shortcut {
            background-color: #444;
            padding: 2px 4px;
            border-radius: 3px;
            font-size: 12px;
            margin-left: 5px;
        }
        .nav-links {
            display: flex;
            gap: 20px;
        }
        .nav-link {
            color: #ccc;
            text-decoration: none;
        }
        /* Main content */
        .main-content {
            display: flex;
            padding: 0 20px;
        }
        /* Banner styling */
        .banner {
            background: linear-gradient(90deg, #4CAF50, #2196F3, #9C27B0, #F44336, #FF9800);
            padding: 40px;
            border-radius: 5px;
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .banner h1 {
            font-size: 72px;
            margin-bottom: 10px;
        }
        .banner h2 {
            font-size: 28px;
        }
        /* Warning box */
        .warning-box {
            background-color: rgba(244, 67, 54, 0.2);
            border-left: 4px solid #F44336;
            padding: 15px;
            margin-bottom: 30px;
            border-radius: 4px;
        }
        /* Section headers */
        .section-header {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 20px;
            margin-top: 30px;
        }
        /* Sidebar customization */
        .css-1d391kg {
            background-color: #1e1e1e;
        }
        .sidebar-title {
            font-size: 14px;
            text-transform: uppercase;
            color: #999;
            margin-bottom: 15px;
        }
        .sidebar-link {
            padding: 8px 0;
            color: #ccc;
            text-decoration: none;
            display: block;
        }
        .sidebar-link:hover {
            color: white;
        }
        .sidebar-link.active {
            color: #FF9800;
        }
        .sidebar-section {
            margin-bottom: 25px;
        }
        /* Feedback section */
        .feedback-container {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 40px;
        }
        .feedback-text {
            color: #999;
        }
        .feedback-button {
            background-color: transparent;
            border: 1px solid #444;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #333;
            border-radius: 4px 4px 0px 0px;
            padding: 10px 20px;
            color: white;
        }
        .stTabs [aria-selected="true"] {
            background-color: #444;
        }
        /* Markdown styling */
        .markdown-text-container p {
            color: #ddd;
            line-height: 1.6;
            margin-bottom: 20px;
        }
        .markdown-text-container h1, .markdown-text-container h2,
        .markdown-text-container h3, .markdown-text-container h4 {
            color: white;
            margin-top: 30px;
            margin-bottom: 15px;
        }
        .jump-section {
            background-color: #252525;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 40px;
        }
        /* Override Streamlit defaults */
        .stApp, .css-18e3th9, .css-1d391kg, .css-1vq4p4l {
            background-color: #1e1e1e;
        }
        .st-bm, .st-af, .st-ae, .st-ag {
            background-color: #1e1e1e;
        }
        /* Button styling */
        .stButton > button {
            background-color: #333;
            color: white;
            border: 1px solid #444;
        }
        .stButton > button:hover {
            background-color: #444;
        }
        .section-divider {
            border-top: 1px solid #333;
            margin: 30px 0;
        }
        
        /* Floating Chat Button */
        .floating-chat-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            background-color: #4CAF50;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            cursor: pointer;
            z-index: 9999;
            text-decoration: none;
            transition: all 0.3s ease;
        }
        .floating-chat-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 16px rgba(0,0,0,0.5);
        }
    </style>
    """, unsafe_allow_html=True)

    # Create the header with logo, search bar, and links
    st.markdown("""
    <div class="header-container">
        <div class="logo-text">
            <span style="background-color: #4CAF50; width: 24px; height: 24px; display: inline-block; margin-right: 10px; border-radius: 4px;"></span>
            bunq API Documentation
        </div>
        <div class="nav-links">
            <div class="search-container">
                <span>🔍</span>
                <input type="text" placeholder="Search..." class="search-input">
                <span class="search-shortcut">Ctrl K</span>
            </div>
            <span class="nav-link">SDK's ▼</span>
            <span class="nav-link">Postman Collection</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Create sidebar with navigation
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">📑 GETTING STARTED</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-link active">👋 Welcome to the bunq API documentation</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-link">🔧 Tools ></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">📚 BASICS</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-link">📋 bunq API Objects ></div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-link">API Context, Device Installation and Session</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-link">Authentication ></div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-link">Pagination</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-link">Errors</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-link">Rate Limits</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-link">Response body formatting</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-link">Moving to production</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-link">Headers</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">🔄 NOT SO BASICS</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-link">Signing ></div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-link">Callbacks (Webhooks)</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">🔒 PSD2</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div style="padding: 20px; background-color: #252525; border-radius: 5px; margin-top: 30px;">', unsafe_allow_html=True)
        st.markdown('<div style="display: flex; align-items: center; gap: 10px;">', unsafe_allow_html=True)
        st.markdown('<span>📚</span> <span>Powered by GitBook</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Main content area
    col1, col2, col3 = st.columns([1, 10, 1])
    with col2:
        # Create the colorful banner
        st.markdown("""
        <div class="banner">
            <h1>bunq</h1>
            <h2>BANK OF THE FREE</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Getting Started header
        st.markdown("""
        <div>
            <span style="background-color: #FF9800; padding: 5px 10px; border-radius: 3px; color: white; margin-right: 10px;">📑</span>
            <span style="font-size: 24px; font-weight: bold;">GETTING STARTED</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Welcome header
        st.markdown("""
        <div style="margin: 20px 0;">
            <span style="font-size: 32px;">👋 Welcome to the bunq API documentation</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Warning box
        st.markdown("""
        <div class="warning-box">
            <p>⚠️ By integrating with bunq's Public API, you agree to comply with bunq's <a href="#" style="color: #FF9800;">Terms & Conditions ↗</a> and all applicable usage policies. Please <strong>review them carefully</strong> before getting started.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Introduction text
        st.markdown("""
        <div class="markdown-text-container">
            <p>Hi there! Thanks for stopping by. The bunq API is a powerful way to automate your banking and build custom experiences around your finances—with over 300 available operations to play with.
    \n We get it—because it's so flexible, the API can feel a bit overwhelming at first. That's why this guide is here: to help you understand how bunq works behind the scenes, so you can quickly find the right endpoints and build your integration with confidence.
    \n Let's start by exploring the key building blocks of the bunq API and how they relate to each other.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Jump Right In section
        st.markdown("""
        <div class="section-header">Jump right in</div>
        <div class="jump-section">
            <div style="display: flex; justify-content: space-around;">
                <div style="text-align: center; padding: 15px;">
                    <div style="background-color: #FFC107; width: 100px; height: 100px; border-radius: 10px; margin: 0 auto; display: flex; align-items: center; justify-content: center;">
                        <span style="font-size: 40px;">💰</span>
                    </div>
                    <p style="margin-top: 10px; color: white;">Quick Start</p>
                </div>
                <div style="text-align: center; padding: 15px;">
                    <div style="background-color: #2196F3; width: 100px; height: 100px; border-radius: 10px; margin: 0 auto; display: flex; align-items: center; justify-content: center;">
                        <span style="font-size: 40px;">💻</span>
                    </div>
                    <p style="margin-top: 10px; color: white;">API Reference</p>
                </div>
                <div style="text-align: center; padding: 15px;">
                    <div style="background-color: #4CAF50; width: 100px; height: 100px; border-radius: 10px; margin: 0 auto; display: flex; align-items: center; justify-content: center;">
                        <span style="font-size: 40px;">📱</span>
                    </div>
                    <p style="margin-top: 10px; color: white;">Developer Tools</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Feedback section
        st.markdown("""
        <div class="feedback-container">
            <span class="feedback-text">Was this helpful?</span>
            <button class="feedback-button">😞</button>
            <button class="feedback-button">😐</button>
            <button class="feedback-button">😊</button>
        </div>
        """, unsafe_allow_html=True)

    # Add floating chat button that opens in a new tab
    st.markdown(f"""
    <a href="?chatbot=true" target="_blank" class="floating-chat-btn">
        💬
    </a>
    """, unsafe_allow_html=True)

else:
    # CHATBOT PAGE
    # Initialize RAG pipeline for chatbot
    rag_pipeline = initialize_rag_pipeline()
    
    # Set page configuration for chatbot
    st.set_page_config(
        page_title="bunq API Assistant",
        page_icon=":speech_balloon:",
        layout="centered"
    )
    
    # Custom CSS for the chatbot page
    st.markdown("""
    <style>
        /* Global styling */
        body {
            color: white;
            background-color: #1e1e1e;
        }
        
        /* Header styling */
        .header {
            background-color: #4CAF50;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
            color: white;
        }
        
        /* Message styling */
        .chat-message {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        
        .user-message {
            background-color: #4CAF50;
            color: white;
            border-top-right-radius: 0;
        }
        
        .assistant-message {
            background-color: #333;
            color: white;
            border-top-left-radius: 0;
        }
        
        /* Override Streamlit defaults */
        .stApp, .css-18e3th9, .css-1d391kg, .css-1vq4p4l {
            background-color: #1e1e1e;
        }
        
        .st-bm, .st-af, .st-ae, .st-ag {
            background-color: #1e1e1e;
        }
        
        /* Button styling */
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background-color: #45a049;
        }
        
        /* Chat input styling */
        .stTextInput > div > div > input {
            background-color: #333;
            color: white;
            border: 1px solid #444;
            border-radius: 5px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Chatbot header
    st.markdown("""
    <div class="header">
        <h1>💬 bunq API Assistant</h1>
        <p>Ask me anything about the bunq API documentation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize chat history in session state if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm your bunq API assistant. How can I help you today?"}]
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    user_input = st.chat_input("Ask about the bunq API...", key="chatbot_input")
    
    # Handle user input
    if user_input:
        # Add user message to history and display it
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            
            try:
                # Call the RAG pipeline to generate a response
                response, sources = rag_pipeline.generate_response(user_input)
                
                # Update placeholder with the generated response
                message_placeholder.markdown(response)
                
                # Add assistant response to history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Display sources if available
                if sources and sources[0] != "No sources available":
                    with st.expander("Sources"):
                        for source in sources:
                            st.write(source)
                
            except Exception as e:
                error_message = "Sorry, I encountered an error. Please try again."
                message_placeholder.markdown(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})