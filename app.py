import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime
import time
import json
import pandas as pd
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from faker import Faker  # For generating mock data
import plotly.express as px  # For visualizations

# Load environment variables
load_dotenv()
fake = Faker()

# ========== SESSION STATE INITIALIZATION ========== #
def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        'chat_history': [],
        'conversation_start_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'current_domain': "General Knowledge",
        'show_history': False,
        'show_analytics': False,
        'saved_conversations': {},
        'user_profile': {
            "name": fake.name(),
            "expertise": fake.job(),
            "preferred_style": "Professional"
        },
        'ai_persona': "Helpful Expert",
        'active_tools': ["Web Search", "Code Interpreter"],
        'conversation_ratings': []
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ========== UI COMPONENTS ========== #
def display_header():
    """Display the application header with animated typing effect"""
    st.set_page_config(page_title="GENE.ai", layout="wide", page_icon="🚀")
    
    # Animated header
    with st.container():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown("""
            <style>
                .typing {
                    border-right: 3px solid;
                    white-space: nowrap;
                    overflow: hidden;
                    animation: typing 2s steps(20, end), blink-caret .75s step-end infinite;
                }
                @keyframes typing {
                    from { width: 0 }
                    to { width: 100% }
                }
                @keyframes blink-caret {
                    from, to { border-color: transparent }
                    50% { border-color: orange; }
                }
            </style>
            <h1 class="typing">GENE.ai Assistant</h1>
            """, unsafe_allow_html=True)
            st.caption("Your hyper-intelligent, multi-modal AI companion")
        
        with col2:
            st.image("logo.png", width=550)

# ========== SIDEBAR CONFIGURATION ========== #
def setup_sidebar():
    """Configure all sidebar options"""
    with st.sidebar:
        st.title("⚙️ Control Panel")
        st.markdown("---")
        
        # Model Configuration
        st.subheader("AI Configuration")
        model = st.selectbox(
            "Model", 
            ["llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"],
            index=0,
            help="Select the AI engine powering your assistant"
        )
        
        st.session_state.ai_persona = st.selectbox(
            "AI Persona",
            ["Helpful Expert", "Creative Genius", "Technical Specialist", "Friendly Advisor"],
            index=0
        )
        
        # User Profile
        st.subheader("👤 Your Profile")
        st.session_state.user_profile["preferred_style"] = st.selectbox(
            "Response Style",
            ["Professional", "Concise", "Detailed", "Casual"],
            index=0
        )
        
        # Knowledge Domain
        st.session_state.current_domain = st.selectbox(
            "🧠 Knowledge Focus",
            ["General Knowledge", "Technical/IT", "Business", "Scientific", "Creative Arts", "Legal", "Medical"],
            index=0
        )
        
        # Tools
        st.subheader("🛠️ Active Tools")
        tools = st.multiselect(
            "Select tools to enable:",
            options=["Web Search", "Code Interpreter", "Data Analysis", "Document Reader", "Image Generator"],
            default=st.session_state.active_tools
        )
        st.session_state.active_tools = tools
        
        # Navigation
        st.markdown("---")
        st.subheader("📂 Navigation")
        if st.button("📜 Conversation History"):
            st.session_state.show_history = not st.session_state.show_history
        if st.button("📊 Chat Analytics"):
            st.session_state.show_analytics = not st.session_state.show_analytics
        
        # System Info
        st.markdown("---")
        st.markdown(f"**Session Started:** {st.session_state.conversation_start_time}")
        st.markdown(f"**Messages:** {len(st.session_state.chat_history)}")
        
        return model

# ========== SPECIALIZED VIEWS ========== #
def display_full_history():
    """Display the complete conversation history"""
    st.title("📜 Full Conversation History")
    st.write(f"Conversation started at: {st.session_state.conversation_start_time}")
    
    if not st.session_state.chat_history:
        st.info("No conversation history yet.")
    else:
        # Search functionality
        search_term = st.text_input("🔍 Search conversations...")
        
        # Filter and display messages
        filtered_history = [
            msg for msg in st.session_state.chat_history
            if search_term.lower() in msg['content'].lower()
        ] if search_term else st.session_state.chat_history
        
        for msg in filtered_history:
            with st.chat_message(name=msg['role']):
                st.write(msg['content'])
        
        # Export options
        st.download_button(
            "💾 Export as JSON",
            data=json.dumps(st.session_state.chat_history, indent=2),
            file_name=f"conversation_{datetime.now().strftime('%Y%m%d')}.json"
        )
    
    if st.button("⬅️ Back to Chat"):
        st.session_state.show_history = False
        st.rerun()

def display_analytics():
    """Display conversation analytics and insights"""
    st.title("📊 Conversation Analytics")
    
    if not st.session_state.chat_history:
        st.warning("No data to analyze yet")
        return
    
    # Create dataframe from history
    df = pd.DataFrame(st.session_state.chat_history)
    df['length'] = df['content'].apply(len)
    df['time'] = pd.to_datetime(df.get('timestamp', datetime.now()))
    
    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Messages", len(df))
    with col2:
        st.metric("Your Messages", sum(df['role'] == 'human'))
    with col3:
        st.metric("AI Messages", sum(df['role'] == 'AI'))
    
    # Visualizations
    tab1, tab2 = st.tabs(["Message Length", "Activity Over Time"])
    
    with tab1:
        fig = px.histogram(df, x='length', color='role', 
                          title="Distribution of Message Lengths")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        time_df = df.groupby([df['time'].dt.hour, 'role']).size().unstack()
        fig = px.line(time_df, title="Message Activity by Hour")
        st.plotly_chart(fig, use_container_width=True)
    
    if st.button("⬅️ Back to Chat"):
        st.session_state.show_analytics = False
        st.rerun()

# ========== CORE CHAT FUNCTIONALITY ========== #
def generate_response(user_input, groq_chat, memory):
    """Generate AI response with enhanced processing"""
    # Enhanced system prompt with context
    system_prompt = f"""
    You are GENE.ai - a highly advanced AI assistant. 
    Current Mode: {st.session_state.current_domain}
    User Profile: {st.session_state.user_profile}
    Active Tools: {st.session_state.active_tools}
    
    Respond as a {st.session_state.ai_persona} with a {st.session_state.user_profile['preferred_style']} style.
    """
    
    # Special processing for different domains
    if "Technical" in st.session_state.current_domain:
        system_prompt += "\nProvide detailed, accurate technical information with examples when possible."
    elif "Creative" in st.session_state.current_domain:
        system_prompt += "\nBe imaginative and original in your responses."
    
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{human_input}")
    ])
    
    conversation = LLMChain(
        llm=groq_chat,
        prompt=prompt,
        memory=memory,
        verbose=True,
        output_key="response"
    )
    
    # Simulate "typing" effect
    with st.spinner("GENE.ai is thinking..."):
        start_time = time.time()
        response = conversation({"human_input": user_input})['response']
        processing_time = time.time() - start_time
    
    # Add metadata to response
    response += f"\n\n*[Generated in {processing_time:.2f}s | {st.session_state.current_domain} Mode]*"
    return response

def main_chat_interface(groq_chat, memory):
    """Main chat interface with enhanced features"""
    st.markdown(f"### 💬 Chat - **{st.session_state.current_domain}** Mode")
    st.caption(f"Persona: {st.session_state.ai_persona} | Style: {st.session_state.user_profile['preferred_style']}")
    
    # Display recent messages
    for msg in st.session_state.chat_history[-4:]:
        with st.chat_message(name=msg['role']):
            st.write(msg['content'])
    
    # User input with enhanced options
    with st.form("chat_input_form"):
        user_input = st.text_area("Your message:", height=100, 
                                placeholder="Type your message or upload a file...")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            submitted = st.form_submit_button("🚀 Send")
        with col2:
            if st.form_submit_button("✨ Enhance"):
                user_input = f"[ENHANCED QUERY]: {user_input}\n\nPlease expand on this with additional details and examples."
        
        # File uploader would go here in a real implementation
    
    if submitted and user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            'role': 'human',
            'content': user_input,
            'timestamp': datetime.now().isoformat()
        })
        
        # Generate and display response
        response = generate_response(user_input, groq_chat, memory)
        
        st.session_state.chat_history.append({
            'role': 'AI',
            'content': response,
            'timestamp': datetime.now().isoformat()
        })
        
        st.rerun()

# ========== MAIN APPLICATION ========== #
def main():
    initialize_session_state()
    display_header()
    
    # Handle special views
    if st.session_state.show_history:
        display_full_history()
        return
    if st.session_state.show_analytics:
        display_analytics()
        return
    
    # Main chat interface
    model = setup_sidebar()
    
    try:
        groq_api_key = os.getenv('GROQ_API_KEY')
        if not groq_api_key:
            st.error("API key not found. Please configure your .env file.")
            return
        
        # Initialize AI with enhanced memory
        groq_chat = ChatGroq(
            groq_api_key=groq_api_key,
            model_name=model,
            temperature=0.7 if "Creative" in st.session_state.current_domain else 0.3
        )
        
        memory = ConversationBufferWindowMemory(
            k=5,  # Fixed memory window size
            memory_key="chat_history",
            input_key="human_input",
            output_key="response",
            return_messages=True
        )
        
        main_chat_interface(groq_chat, memory)
        
    except Exception as e:
        st.error(f"System error: {str(e)}")

if __name__ == "__main__":
    main()
