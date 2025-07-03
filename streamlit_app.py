import streamlit as st
import os
import json
from pathlib import Path
from typing import Annotated, List, Dict, Any
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent
from autogen.coding import LocalCommandLineCodeExecutor
import chromadb
import PyPDF2
import docx2txt
import pandas as pd
from datetime import datetime
import hashlib
import re
import threading
import time

# Load environment variables from .env file
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Smart Building AI Assistant",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .upload-box {
        border: 2px dashed #4c566a;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        background-color: #f0f2f6;
        margin: 10px 0;
    }
    .stAlert {
        padding: 0.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Configure Groq
config_list = [{
    "model": "llama-3.3-70b-versatile",
    "api_key": os.environ.get("GROQ_API_KEY"),
    "api_type": "groq"
}]

# Create a directory to store code files from code executor
work_dir = Path("coding")
work_dir.mkdir(exist_ok=True)
code_executor = LocalCommandLineCodeExecutor(work_dir=work_dir)

# Weather function
def get_current_weather(location, unit="fahrenheit"):
    """Get the weather for some location"""
    weather_data = {
        "berlin": {"temperature": "13", "humidity": "65%", "condition": "Cloudy"},
        "istanbul": {"temperature": "40", "humidity": "45%", "condition": "Sunny"},
        "san francisco": {"temperature": "55", "humidity": "70%", "condition": "Foggy"},
        "ho chi minh city": {"temperature": "86", "humidity": "80%", "condition": "Partly Cloudy"},
        "saigon": {"temperature": "86", "humidity": "80%", "condition": "Partly Cloudy"},
        "đại học quốc tế miền đông": {"temperature": "86", "humidity": "80%", "condition": "Partly Cloudy", "coordinates": "11.052754371982356, 106.666777616965"},
        "current location": {"temperature": "86", "humidity": "80%", "condition": "Partly Cloudy", "coordinates": "11.052754371982356, 106.666777616965"}
    }
    
    location_lower = location.lower()
    if location_lower in weather_data:
        weather_info = weather_data[location_lower]
        result = {
            "location": location.title(),
            "temperature": weather_info["temperature"],
            "unit": unit,
            "humidity": weather_info["humidity"],
            "condition": weather_info["condition"]
        }
        if "coordinates" in weather_info:
            result["coordinates"] = weather_info["coordinates"]
        return json.dumps(result)
    return json.dumps({"location": location, "temperature": "unknown", "message": "Weather data not available for this location"})

# Smart Building Knowledge Base class (simplified for Streamlit)
class SmartBuildingKnowledgeBase:
    def __init__(self, persist_directory="./knowledge_base"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="smart_building_docs"
        )
        
    def simple_embedding(self, text: str) -> List[float]:
        """Create a simple hash-based embedding for text"""
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
        words = clean_text.split()
        
        embedding = [0.0] * 100
        for i, word in enumerate(words[:100]):
            hash_val = hash(word) % 100
            embedding[hash_val] += 1.0
        
        total = sum(embedding) or 1
        return [x / total for x in embedding]
    
    def extract_text_from_file(self, file_path: Path) -> str:
        """Extract text from various file formats"""
        file_extension = file_path.suffix.lower()
        
        try:
            if file_extension == '.pdf':
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                return text
                
            elif file_extension in ['.docx', '.doc']:
                return docx2txt.process(str(file_path))
                
            elif file_extension == '.txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
                    
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
                return df.to_string()
                
            elif file_extension == '.csv':
                df = pd.read_csv(file_path)
                return df.to_string()
                
            elif file_extension == '.json':
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    return json.dumps(data, indent=2)
                    
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"
            
        return "Unsupported file format"
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        return chunks
    
    def add_document(self, file_path: str, metadata: Dict[str, Any] = None) -> bool:
        """Add a document to the knowledge base"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False
                
            text = self.extract_text_from_file(file_path)
            if not text or text.startswith("Error"):
                return False
                
            chunks = self.chunk_text(text)
            embeddings = [self.simple_embedding(chunk) for chunk in chunks]
            
            if metadata is None:
                metadata = {}
            
            base_metadata = {
                "filename": file_path.name,
                "file_path": str(file_path),
                "file_type": file_path.suffix,
                "added_date": datetime.now().isoformat(),
                **metadata
            }
            
            chunk_ids = [f"{file_path.stem}_{i}" for i in range(len(chunks))]
            chunk_metadata = [
                {**base_metadata, "chunk_index": i, "chunk_id": chunk_ids[i]}
                for i in range(len(chunks))
            ]
            
            self.collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=chunk_metadata,
                ids=chunk_ids
            )
            
            return True
            
        except Exception as e:
            st.error(f"Error adding document: {str(e)}")
            return False
    
    def search_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents based on query"""
        try:
            query_embedding = [self.simple_embedding(query)]
            
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )
            
            if not results['documents'][0]:
                all_docs = self.collection.get()
                text_results = []
                query_words = set(query.lower().split())
                
                for i, doc in enumerate(all_docs['documents']):
                    doc_words = set(doc.lower().split())
                    overlap = len(query_words.intersection(doc_words))
                    if overlap > 0:
                        text_results.append({
                            'document': doc,
                            'metadata': all_docs['metadatas'][i],
                            'score': overlap
                        })
                
                text_results.sort(key=lambda x: x['score'], reverse=True)
                search_results = []
                for result in text_results[:n_results]:
                    search_results.append({
                        "content": result['document'],
                        "metadata": result['metadata'],
                        "distance": 1.0 - (result['score'] / len(query_words))
                    })
                return search_results
            
            search_results = []
            for i in range(len(results['documents'][0])):
                search_results.append({
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                })
            
            return search_results
            
        except Exception as e:
            st.error(f"Error searching documents: {str(e)}")
            return []
    
    def get_context_for_query(self, query: str, max_context_length: int = 4000) -> str:
        """Get relevant context for a query"""
        search_results = self.search_documents(query, n_results=10)
        
        context = "Relevant Smart Building Information:\n\n"
        current_length = len(context)
        
        for result in search_results:
            content = result['content']
            filename = result['metadata'].get('filename', 'Unknown')
            
            section = f"From {filename}:\n{content}\n\n"
            
            if current_length + len(section) <= max_context_length:
                context += section
                current_length += len(section)
            else:
                break
                
        return context

# Initialize session state
if 'kb' not in st.session_state:
    st.session_state.kb = SmartBuildingKnowledgeBase()

if 'messages' not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """🏢 **Welcome to the Smart Building AI Assistant!** 

I'm here to help you with:
- 🔧 HVAC systems and maintenance
- 💡 Lighting controls and troubleshooting  
- 🌡️ Temperature monitoring and sensors
- ⚡ Energy management and efficiency
- 📋 Building documentation and manuals
- 🚨 Emergency procedures and contacts

**Quick Start:**
- Use the sidebar buttons for common queries
- Upload building documents to expand my knowledge
- Ask me anything about your smart building systems!

How can I help you today?"""
        }
    ]

if 'assistant' not in st.session_state:
    st.session_state.assistant = None

if 'user_proxy' not in st.session_state:
    st.session_state.user_proxy = None

# Initialize AutoGen agents
def initialize_agents():
    if st.session_state.assistant is None:
        assistant = AssistantAgent(
            name="smart_building_assistant",
            system_message="""You are a Smart Building AI Assistant. Provide clear, concise answers about:
            - Smart building systems (HVAC, lighting, security, IoT devices)
            - Building operations and maintenance
            - Energy management and automation
            
            Always search the knowledge base first and cite source documents when available.""",
            llm_config={"config_list": config_list}
        )
        
        user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            code_execution_config={"executor": code_executor}
        )
        
        st.session_state.assistant = assistant
        st.session_state.user_proxy = user_proxy

# Helper functions
def search_building_knowledge(query: str) -> str:
    """Search the smart building knowledge base"""
    context = st.session_state.kb.get_context_for_query(query)
    if context.strip() == "Relevant Smart Building Information:\n":
        return "No relevant information found in the knowledge base."
    return context

def add_document_to_kb(file_path: str, document_type: str = "general") -> str:
    """Add a document to the smart building knowledge base"""
    metadata = {
        "document_type": document_type,
        "building_system": "smart_building"
    }
    
    success = st.session_state.kb.add_document(file_path, metadata)
    if success:
        return f"Successfully added document: {Path(file_path).name}"
    else:
        return f"Failed to add document: {Path(file_path).name}"

def get_response_from_assistant(query: str) -> str:
    """Get response from the assistant based on the query"""
    initialize_agents()
    
    # Check if query is about listing files
    if "list" in query.lower() and "file" in query.lower():
        data_dir = Path("smart_building_data")
        if not data_dir.exists():
            return "📁 Smart building data directory not found."
        
        files = list(data_dir.glob("*"))
        if not files:
            return "📁 No files found in smart building data directory."
        
        file_list = "📋 **Files in smart building data directory:**\n\n"
        for file in files:
            file_list += f"📄 **{file.name}** ({file.suffix})\n"
        
        return file_list
    
    # Check if query is about adding documents
    elif "add document" in query.lower():
        words = query.split()
        for i, word in enumerate(words):
            if word.lower() == "document" and i + 1 < len(words):
                file_path = words[i + 1]
                return add_document_to_kb(file_path)
        return "❌ Please specify a file path to add."
    
    # Weather queries
    elif "weather" in query.lower():
        location_keywords = {
            "berlin": "berlin",
            "istanbul": "istanbul", 
            "san francisco": "san francisco",
            "ho chi minh": "ho chi minh city",
            "saigon": "saigon",
            "university": "đại học quốc tế miền đông",
            "current location": "current location",
            "here": "current location"
        }
        
        detected_location = None
        for keyword, location in location_keywords.items():
            if keyword in query.lower():
                detected_location = location
                break
        
        if detected_location:
            weather_info = get_current_weather(detected_location)
            data = json.loads(weather_info)
            if "coordinates" in data:
                return f"🌡️ **Weather at {data['location']}:**\n📍 Coordinates: {data['coordinates']}\n🌡️ Temperature: {data['temperature']}°{data['unit']}\n💧 Humidity: {data['humidity']}\n☁️ Condition: {data['condition']}"
            else:
                return f"🌡️ **Weather in {data['location']}:** {data['temperature']}°{data['unit']}, {data['condition']}, Humidity: {data['humidity']}"
        else:
            return "🌡️ I can provide weather information for Berlin, Istanbul, San Francisco, Ho Chi Minh City, Saigon, and Đại học quốc tế Miền Đông."
    
    # Search knowledge base for building-related queries
    elif any(keyword in query.lower() for keyword in ["hvac", "lighting", "system", "maintenance", "temperature", "sensor", "emergency", "troubleshoot", "specification"]):
        context = search_building_knowledge(query)
        
        if "No relevant information" not in context:
            return f"🏢 **Based on your smart building documentation:**\n\n{context}"
        else:
            return "❓ I couldn't find specific information about that in the knowledge base. Try uploading relevant documents or asking a more general question."
    
    # General queries
    else:
        context = search_building_knowledge(query)
        
        if "No relevant information" not in context:
            return f"🏢 **Based on your smart building documentation:**\n\n{context}"
        else:
            # Use assistant for general response
            try:
                response = st.session_state.assistant.generate_reply(
                    messages=[{"role": "user", "content": query}]
                )
                return f"🤖 {response}"
            except Exception as e:
                return f"❌ I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question."

# Main App Layout
def main():
    st.title("🏢 Smart Building AI Assistant")
    st.markdown("Your intelligent assistant for smart building management and operations")
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Knowledge Base Management")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload Building Documents",
            type=['pdf', 'txt', 'docx', 'csv', 'xlsx', 'json'],
            help="Upload manuals, specifications, or other building-related documents"
        )
        
        document_type = st.selectbox(
            "Document Type",
            ["general", "manual", "specification", "maintenance", "emergency", "energy", "security"]
        )
        
        if uploaded_file is not None:
            # Save uploaded file
            save_path = Path("smart_building_data") / uploaded_file.name
            save_path.parent.mkdir(exist_ok=True)
            
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            if st.button("Add to Knowledge Base"):
                with st.spinner("Processing document..."):
                    result = add_document_to_kb(str(save_path), document_type)
                    st.success(result)
        
        st.markdown("---")
        
        # Knowledge base stats
        if st.button("📊 View Knowledge Base Stats"):
            try:
                collection_info = st.session_state.kb.collection.get()
                doc_count = len(collection_info['documents'])
                
                unique_files = set()
                for metadata in collection_info['metadatas']:
                    if 'filename' in metadata:
                        unique_files.add(metadata['filename'])
                
                st.metric("Total Chunks", doc_count)
                st.metric("Unique Documents", len(unique_files))
                
                if unique_files:
                    st.write("**Files in Knowledge Base:**")
                    for file in unique_files:
                        st.write(f"📄 {file}")
                        
            except Exception as e:
                st.error(f"Error getting stats: {e}")
        
        st.markdown("---")
        
        # Quick actions
        st.header("🚀 Quick Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🌡️ Weather", use_container_width=True):
                st.session_state.messages.append({
                    "role": "user",
                    "content": "What's the weather at Đại học quốc tế Miền Đông?"
                })
                st.rerun()
            
            if st.button("🔧 HVAC", use_container_width=True):
                st.session_state.messages.append({
                    "role": "user",
                    "content": "What are the HVAC system specifications and maintenance schedule?"
                })
                st.rerun()
                
            if st.button("🚨 Emergency", use_container_width=True):
                st.session_state.messages.append({
                    "role": "user",
                    "content": "What are the emergency contact numbers and procedures?"
                })
                st.rerun()
        
        with col2:
            if st.button("💡 Lighting", use_container_width=True):
                st.session_state.messages.append({
                    "role": "user",
                    "content": "Tell me about the smart lighting system specifications"
                })
                st.rerun()
            
            if st.button("📋 Files", use_container_width=True):
                st.session_state.messages.append({
                    "role": "user",
                    "content": "List all files in the knowledge base"
                })
                st.rerun()
                
            if st.button("🏢 Building Info", use_container_width=True):
                st.session_state.messages.append({
                    "role": "user",
                    "content": "Tell me about the building equipment and room information"
                })
                st.rerun()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    # Main chat interface
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Process the last message if it's a user message without a response
    if (st.session_state.messages and 
        st.session_state.messages[-1]["role"] == "user" and 
        (len(st.session_state.messages) == 1 or st.session_state.messages[-2]["role"] == "user")):
        
        last_user_message = st.session_state.messages[-1]["content"]
        
        # Get assistant response
        with st.spinner("🤖 Thinking..."):
            response = get_response_from_assistant(last_user_message)
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
    
    # React to user input
    if prompt := st.chat_input("Ask me anything about your smart building..."):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get assistant response
        with st.spinner("🤖 Thinking..."):
            response = get_response_from_assistant(prompt)
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
