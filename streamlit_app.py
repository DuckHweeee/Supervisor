import streamlit as st
import os
import json
from pathlib import Path
from typing import Annotated, List, Dict, Any
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent
from autogen.coding import LocalCommandLineCodeExecutor
# Import ChromaDB compatibility wrapper to handle SQLite issues
from chromadb_compat import create_chromadb_instance
import PyPDF2
import docx2txt
import pandas as pd
from datetime import datetime
import hashlib
import re
import threading
import time
import requests
from bs4 import BeautifulSoup
import urllib.parse
from urllib.robotparser import RobotFileParser
import feedparser
import ssl
import certifi
import asyncio
import httpx

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

# Weather API Client
class WeatherAPIClient:
    """Client to communicate with the Weather API Server"""
    
    def __init__(self, server_url="http://localhost:8001"):
        self.server_url = server_url
        self.client = None
    
    async def get_weather_data(self, location: str, include_forecast: bool = False) -> Dict[str, Any]:
        """Get weather data from the API server"""
        try:
            # Create httpx client if not exists
            if self.client is None:
                self.client = httpx.AsyncClient(timeout=30.0)
            
            # Call the weather API
            payload = {
                "location": location,
                "units": "metric",
                "include_forecast": include_forecast
            }
            
            response = await self.client.post(f"{self.server_url}/weather", json=payload)
            
            if response.status_code == 200:
                return response.json()
            else:
                # Fallback to static data if API server is not available
                return self._get_fallback_weather(location)
                
        except Exception as e:
            print(f"Error connecting to weather API server: {e}")
            return self._get_fallback_weather(location)
    
    def _get_fallback_weather(self, location: str) -> Dict[str, Any]:
        """Fallback weather data when API server is unavailable"""
        return {
            "location": location,
            "temperature": 26.0,
            "humidity": 80,
            "condition": "Partly Cloudy",
            "coordinates": "11.052754371982356, 106.666777616965",
            "message": "Using cached weather data (API server unavailable)"
        }
    
    async def close(self):
        """Close the HTTP client"""
        if self.client:
            await self.client.aclose()

# Initialize Weather API Client
weather_api_client = WeatherAPIClient()

# Enhanced weather function
def get_current_weather(location, unit="celsius"):
    """Get the weather for some location using Weather API server"""
    try:
        # Create event loop if none exists
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in a running event loop, so we can't use await
                # Use fallback weather data
                return json.dumps(weather_api_client._get_fallback_weather(location))
        except RuntimeError:
            # No event loop exists, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Get weather data
        try:
            weather_data = loop.run_until_complete(
                weather_api_client.get_weather_data(location, include_forecast=False)
            )
            return json.dumps(weather_data)
        except Exception as e:
            # Use fallback weather data
            return json.dumps(weather_api_client._get_fallback_weather(location))
    except Exception as e:
        # Fallback to static data
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

# Old weather function (remove after update)
def get_current_weather_old(location, unit="fahrenheit"):
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

# Smart Building Knowledge Base class with web content support
class SmartBuildingKnowledgeBase:
    def __init__(self, persist_directory="./knowledge_base"):
        # Use the compatibility wrapper for ChromaDB
        self.chromadb_wrapper = create_chromadb_instance(persist_directory)
        self.use_fallback = self.chromadb_wrapper.use_fallback
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Smart Building AI Assistant/1.0 (Educational Research)'
        })
        
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
            
            # Use the ChromaDB compatibility wrapper
            self.chromadb_wrapper.add_documents(
                documents=chunks,
                metadatas=chunk_metadata,
                ids=chunk_ids,
                embeddings=embeddings
            )
            
            return True
            
        except Exception as e:
            st.error(f"Error adding document: {str(e)}")
            return False
    
    def search_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents based on query"""
        try:
            query_embedding = [self.simple_embedding(query)]
            
            # Use the ChromaDB compatibility wrapper
            results = self.chromadb_wrapper.query_documents(
                query_embeddings=query_embedding,
                n_results=n_results
            )
            
            # Convert results to our expected format
            search_results = []
            if results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    search_results.append({
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if 'distances' in results else 0.5
                    })
            
            return search_results
            
        except Exception as e:
            st.error(f"Error searching documents: {str(e)}")
            return []
    
    def get_context_for_query(self, query: str, max_context_length: int = 4000) -> str:
        """Get relevant context for a query and synthesize it into precise, actionable information"""
        search_results = self.search_documents(query, n_results=20)
        
        if not search_results:
            return ""
        
        # Categorize and synthesize information based on query type
        query_lower = query.lower()
        
        # Extract and categorize relevant information with expanded categories
        hvac_info = []
        lighting_info = []
        energy_info = []
        safety_info = []
        room_info = []
        equipment_info = []
        maintenance_info = []
        security_info = []
        automation_info = []
        environmental_info = []
        cost_info = []
        web_content_info = []  # Specifically for web-sourced content
        general_info = []
        
        # Analyze search results and extract relevant information
        for result in search_results:
            content = result['content']
            content_lower = content.lower()
            metadata = result.get('metadata', {})
            
            # Check if this is web-sourced content
            is_web_content = metadata.get('source_type') == 'web_content' or metadata.get('source_url')
            
            # If it's web content, prioritize it and extract key information
            if is_web_content:
                web_content_info.append({
                    'content': content,
                    'url': metadata.get('source_url', 'Unknown URL'),
                    'domain': metadata.get('domain', 'Unknown domain'),
                    'category': metadata.get('category', 'web_content')
                })
            
            # Categorize based on content type - expanded categories
            if any(term in content_lower for term in ['hvac', 'heating', 'cooling', 'ventilation', 'temperature', 'thermostat', 'ac', 'air conditioning', 'climate']):
                hvac_info.append({'content': content, 'metadata': metadata})
            elif any(term in content_lower for term in ['lighting', 'led', 'bulb', 'illumination', 'brightness', 'light', 'lamp']):
                lighting_info.append({'content': content, 'metadata': metadata})
            elif any(term in content_lower for term in ['energy', 'power', 'consumption', 'efficiency', 'kwh', 'electricity', 'electrical', 'meter']):
                energy_info.append({'content': content, 'metadata': metadata})
            elif any(term in content_lower for term in ['safety', 'fire', 'emergency', 'alarm', 'smoke', 'detector', 'co2']):
                safety_info.append({'content': content, 'metadata': metadata})
            elif any(term in content_lower for term in ['security', 'camera', 'lock', 'access', 'motion', 'surveillance']):
                security_info.append({'content': content, 'metadata': metadata})
            elif any(term in content_lower for term in ['room', 'floor', 'classroom', 'capacity', 'space']):
                room_info.append({'content': content, 'metadata': metadata})
            elif any(term in content_lower for term in ['equipment', 'device', 'sensor', 'monitor', 'controller']):
                equipment_info.append({'content': content, 'metadata': metadata})
            elif any(term in content_lower for term in ['maintenance', 'repair', 'service', 'technician', 'install']):
                maintenance_info.append({'content': content, 'metadata': metadata})
            elif any(term in content_lower for term in ['automation', 'smart', 'control', 'system', 'iot']):
                automation_info.append({'content': content, 'metadata': metadata})
            elif any(term in content_lower for term in ['environmental', 'air quality', 'humidity', 'moisture', 'leak']):
                environmental_info.append({'content': content, 'metadata': metadata})
            elif any(term in content_lower for term in ['cost', 'budget', 'money', 'expense', 'financial', 'savings']):
                cost_info.append({'content': content, 'metadata': metadata})
            else:
                general_info.append({'content': content, 'metadata': metadata})
        
        # Generate comprehensive synthesized response based on query context
        synthesized_info = []
        
        # If web content is available, prioritize it in the response
        if web_content_info:
            web_info = self.extract_specific_info_from_web_content(web_content_info, query)
            if web_info:
                synthesized_info.append("🌐 **Latest Web Information:**")
                synthesized_info.append(web_info)
        
        # Enhanced contextual responses based on query intent
        query_intent = self.determine_query_intent(query_lower)
        
        # HVAC and Climate Control
        if query_intent == 'hvac' or any(term in query_lower for term in ['hvac', 'heating', 'cooling', 'temperature', 'thermostat', 'ac', 'air conditioning', 'climate']):
            if hvac_info:
                specific_info = self.extract_relevant_content(hvac_info, query)
                if specific_info:
                    synthesized_info.append(f"🌡️ **HVAC System Information:** {specific_info}")
            synthesized_info.append("🎯 **HVAC Best Practices:** Optimal temperature range is 68-72°F (20-22°C) for comfort and energy efficiency. Smart thermostats can reduce energy consumption by 15-25% through automated scheduling and weather-based adjustments.")
        
        # Lighting Systems
        elif query_intent == 'lighting' or any(term in query_lower for term in ['lighting', 'lights', 'illumination', 'led', 'bulb', 'brightness']):
            if lighting_info:
                specific_info = self.extract_relevant_content(lighting_info, query)
                if specific_info:
                    synthesized_info.append(f"💡 **Lighting System Information:** {specific_info}")
            synthesized_info.append("🎯 **Lighting Best Practices:** LED systems provide 80% energy savings compared to traditional lighting. Use daylight sensors and occupancy controls for optimal efficiency. Natural light integration can reduce artificial lighting needs by 50-80%.")
        
        # Energy Management
        elif query_intent == 'energy' or any(term in query_lower for term in ['energy', 'power', 'efficiency', 'consumption', 'electricity', 'kwh']):
            if energy_info:
                specific_info = self.extract_relevant_content(energy_info, query)
                if specific_info:
                    synthesized_info.append(f"⚡ **Energy System Information:** {specific_info}")
            synthesized_info.append("🎯 **Energy Efficiency Strategies:** Smart scheduling and automated controls can reduce building energy consumption by 20-30%. Monitor peak usage times and implement load balancing. Weather-responsive systems optimize energy use automatically.")
        
        # Safety Systems
        elif query_intent == 'safety' or any(term in query_lower for term in ['safety', 'fire', 'emergency', 'smoke', 'detector', 'alarm', 'co2']):
            if safety_info:
                specific_info = self.extract_relevant_content(safety_info, query)
                if specific_info:
                    synthesized_info.append(f"🚨 **Safety System Information:** {specific_info}")
            synthesized_info.append("🎯 **Safety Best Practices:** Fire safety systems require monthly testing. Smoke detectors should be inspected quarterly. Emergency exits must remain clearly marked and accessible. CO2 monitoring ensures air quality.")
        
        # Security Systems
        elif query_intent == 'security' or any(term in query_lower for term in ['security', 'camera', 'lock', 'access', 'surveillance', 'motion']):
            if security_info:
                specific_info = self.extract_relevant_content(security_info, query)
                if specific_info:
                    synthesized_info.append(f"🔒 **Security System Information:** {specific_info}")
            synthesized_info.append("🎯 **Security Best Practices:** Access control systems should be integrated with occupancy tracking. Motion detectors and cameras require regular maintenance and firmware updates. Implement layered security with multiple detection methods.")
        
        # Building Automation
        elif query_intent == 'automation' or any(term in query_lower for term in ['automation', 'smart', 'control', 'system', 'iot', 'integration']):
            if automation_info:
                specific_info = self.extract_relevant_content(automation_info, query)
                if specific_info:
                    synthesized_info.append(f"🤖 **Automation System Information:** {specific_info}")
            synthesized_info.append("🎯 **Automation Best Practices:** Integrate all systems for centralized control. Use IoT sensors for real-time monitoring and automated responses to environmental changes. Implement smart scheduling for optimal efficiency.")
        
        # Room and Space Management
        elif query_intent == 'room' or any(term in query_lower for term in ['room', 'floor', 'classroom', 'capacity', 'space', 'occupancy']):
            if room_info:
                specific_info = self.extract_relevant_content(room_info, query)
                if specific_info:
                    synthesized_info.append(f"🏢 **Room Information:** {specific_info}")
            synthesized_info.append("🎯 **Space Management:** Optimize space utilization through occupancy sensors and booking systems. Standard classrooms accommodate 30-62 students with appropriate AV equipment. Track utilization rates for efficient space planning.")
        
        # Equipment and Devices
        elif query_intent == 'equipment' or any(term in query_lower for term in ['equipment', 'device', 'sensor', 'monitor', 'controller']):
            if equipment_info:
                specific_info = self.extract_relevant_content(equipment_info, query)
                if specific_info:
                    synthesized_info.append(f"🔧 **Equipment Information:** {specific_info}")
            synthesized_info.append("🎯 **Equipment Management:** IoT devices require regular firmware updates and network connectivity checks. Implement predictive maintenance schedules for optimal performance. Monitor device status for proactive maintenance.")
        
        # Maintenance and Service
        elif query_intent == 'maintenance' or any(term in query_lower for term in ['maintenance', 'repair', 'service', 'technician', 'install', 'filter']):
            if maintenance_info:
                specific_info = self.extract_relevant_content(maintenance_info, query)
                if specific_info:
                    synthesized_info.append(f"🛠️ **Maintenance Information:** {specific_info}")
            synthesized_info.append("🎯 **Maintenance Best Practices:** Establish preventive maintenance schedules. HVAC filters should be replaced every 3-6 months. Document all service activities. Use predictive maintenance to prevent equipment failures.")
        
        # Environmental Monitoring
        elif query_intent == 'environmental' or any(term in query_lower for term in ['environmental', 'air quality', 'humidity', 'moisture', 'leak', 'water']):
            if environmental_info:
                specific_info = self.extract_relevant_content(environmental_info, query)
                if specific_info:
                    synthesized_info.append(f"🌿 **Environmental Information:** {specific_info}")
            synthesized_info.append("🎯 **Environmental Monitoring:** Maintain humidity levels between 30-50% for comfort. Use air quality sensors to monitor CO2 levels and ensure proper ventilation. Implement leak detection systems for water damage prevention.")
        
        # Cost and Budget Management
        elif query_intent == 'cost' or any(term in query_lower for term in ['cost', 'budget', 'money', 'expense', 'financial', 'savings']):
            if cost_info:
                specific_info = self.extract_relevant_content(cost_info, query)
                if specific_info:
                    synthesized_info.append(f"💰 **Cost Information:** {specific_info}")
            synthesized_info.append("🎯 **Cost Management:** Energy-efficient systems can reduce operational costs by 25-40%. Implement smart scheduling to minimize peak demand charges. Weather-responsive controls optimize energy spending.")
        
        # General information for other queries
        else:
            if general_info:
                specific_info = self.extract_relevant_content(general_info, query)
                if specific_info:
                    synthesized_info.append(f"📊 **Building Information:** {specific_info}")
            synthesized_info.append("🎯 **General Best Practices:** Implement comprehensive building automation systems with regular maintenance schedules, energy monitoring, and automated controls for optimal performance and efficiency.")
        
        return "\n".join(synthesized_info) if synthesized_info else ""

    def can_fetch_url(self, url: str) -> bool:
        """Check if we can legally fetch from this URL according to robots.txt"""
        try:
            parsed_url = urllib.parse.urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            user_agent = self.session.headers.get('User-Agent', '*')
            return rp.can_fetch(user_agent, url)
        except Exception:
            return True
    
    def extract_text_from_url(self, url: str) -> str:
        """Extract text content from a web URL with SSL error handling"""
        try:
            # Check robots.txt compliance
            if not self.can_fetch_url(url):
                return f"Error: Robots.txt disallows fetching from {url}"
            
            # Add delay to be respectful
            time.sleep(1)
            
            # Try with SSL verification first
            try:
                response = self.session.get(url, timeout=30, verify=True)
                response.raise_for_status()
            except requests.exceptions.SSLError as ssl_error:
                # If SSL verification fails, try without verification but warn user
                st.warning(f"⚠️ SSL verification failed for {url}. Attempting without SSL verification...")
                try:
                    response = self.session.get(url, timeout=30, verify=False)
                    response.raise_for_status()
                    st.success(f"✅ Successfully fetched content from {url} (SSL verification bypassed)")
                except Exception as fallback_error:
                    return f"Error: SSL certificate verification failed and fallback also failed for {url}. " \
                           f"Original SSL error: {str(ssl_error)}. " \
                           f"Fallback error: {str(fallback_error)}. " \
                           f"This website may have SSL configuration issues."
            
            # Handle different content types
            content_type = response.headers.get('content-type', '').lower()
            
            if 'text/html' in content_type:
                return self.extract_text_from_html(response.text, url)
            elif 'application/pdf' in content_type:
                return f"PDF content from {url} (PDF parsing from URL not implemented yet)"
            elif 'text/plain' in content_type:
                return response.text
            elif 'application/rss+xml' in content_type or 'application/atom+xml' in content_type:
                return self.extract_text_from_rss(response.text, url)
            else:
                return f"Content from {url}:\n{response.text[:2000]}..."
                
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if "SSL" in error_msg or "certificate" in error_msg.lower():
                return f"Error: SSL/Certificate issue with {url}. " \
                       f"Details: {error_msg}. " \
                       f"This website may have SSL configuration problems or require specific certificates."
            else:
                return f"Error fetching {url}: {error_msg}"
        except Exception as e:
            return f"Error processing {url}: {str(e)}"
    
    def extract_text_from_html(self, html_content: str, url: str) -> str:
        """Extract meaningful text from HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text() if title else "No title"
            
            # Extract main content
            content_selectors = [
                'main', 'article', '.content', '.main-content', 
                '#content', '#main', '.post-content', '.entry-content'
            ]
            
            main_content = None
            for selector in content_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if not main_content:
                main_content = soup.find('body') or soup
            
            # Extract text
            text = main_content.get_text(separator='\n', strip=True)
            
            # Clean up text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            cleaned_text = '\n'.join(lines)
            
            return f"Title: {title_text}\nURL: {url}\n\nContent:\n{cleaned_text}"
            
        except Exception as e:
            return f"Error parsing HTML from {url}: {str(e)}"
    
    def extract_text_from_rss(self, rss_content: str, url: str) -> str:
        """Extract text from RSS/Atom feeds"""
        try:
            feed = feedparser.parse(rss_content)
            
            content_parts = [f"RSS Feed: {feed.feed.get('title', 'Unknown')}\nURL: {url}\n"]
            
            for entry in feed.entries[:10]:  # Limit to 10 recent entries
                title = entry.get('title', 'No title')
                summary = entry.get('summary', entry.get('description', 'No summary'))
                link = entry.get('link', '')
                
                content_parts.append(f"Article: {title}\nLink: {link}\nSummary: {summary}\n")
            
            return '\n'.join(content_parts)
            
        except Exception as e:
            return f"Error parsing RSS from {url}: {str(e)}"
    
    def add_url_to_knowledge_base(self, url: str, metadata: Dict[str, Any] = None) -> bool:
        """Add content from a URL to the knowledge base"""
        try:
            # Extract text from URL
            text = self.extract_text_from_url(url)
            
            if text.startswith("Error"):
                st.error(f"❌ {text}")
                return False
            
            if len(text.strip()) < 100:
                st.error(f"❌ Insufficient content from {url}")
                return False
            
            # Chunk the text
            chunks = self.chunk_text(text)
            
            # Create embeddings
            embeddings = [self.simple_embedding(chunk) for chunk in chunks]
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
            
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc
            
            base_metadata = {
                "source_url": url,
                "domain": domain,
                "source_type": "web_content",
                "added_date": datetime.now().isoformat(),
                **metadata
            }
            
            # Generate unique IDs for chunks
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            chunk_ids = [f"web_{url_hash}_{i}" for i in range(len(chunks))]
            chunk_metadata = [
                {**base_metadata, "chunk_index": i, "chunk_id": chunk_ids[i]}
                for i in range(len(chunks))
            ]
            
            # Add to collection
            # Use the ChromaDB compatibility wrapper
            self.chromadb_wrapper.add_documents(
                documents=chunks,
                metadatas=chunk_metadata,
                ids=chunk_ids,
                embeddings=embeddings
            )
            
            st.success(f"✅ Successfully added {len(chunks)} chunks from {url}")
            return True
            
        except Exception as e:
            st.error(f"❌ Error adding URL {url}: {str(e)}")
            return False
    
    def train_from_url_list(self, urls: List[str], category: str = "web_training") -> Dict[str, Any]:
        """Train the knowledge base from a list of URLs"""
        results = {
            "successful_urls": [],
            "failed_urls": [],
            "total_chunks": 0,
            "errors": []
        }
        
        for url in urls:
            try:
                st.info(f"📥 Processing: {url}")
                
                if self.add_url_to_knowledge_base(url, {"category": category}):
                    results["successful_urls"].append(url)
                    st.success(f"✅ Successfully added: {url}")
                else:
                    results["failed_urls"].append(url)
                    st.error(f"❌ Failed to add: {url}")
                    
            except Exception as e:
                results["failed_urls"].append(url)
                results["errors"].append(f"Error with {url}: {str(e)}")
                st.error(f"❌ Error processing {url}: {str(e)}")
        
        # Count total chunks
        try:
            results["total_chunks"] = self.chromadb_wrapper.count_documents()
        except Exception as e:
            results["errors"].append(f"Error counting chunks: {str(e)}")
        
        return results
    
    def load_and_process_training_data(self, file_path: str = "ai_training_data.json") -> bool:
        """Load and process training data from JSON file"""
        try:
            if not os.path.exists(file_path):
                st.warning(f"Training data file not found: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                training_data = json.load(f)
            
            # Process each section of training data
            processed_chunks = 0
            for section_name, section_data in training_data.items():
                if isinstance(section_data, dict):
                    # Convert section data to text
                    section_text = f"Section: {section_name}\n\n"
                    section_text += json.dumps(section_data, indent=2, ensure_ascii=False)
                    
                    # Chunk the text
                    chunks = self.chunk_text(section_text)
                    embeddings = [self.simple_embedding(chunk) for chunk in chunks]
                    
                    # Create metadata
                    base_metadata = {
                        "source_type": "training_data",
                        "section": section_name,
                        "filename": file_path,
                        "added_date": datetime.now().isoformat(),
                        "category": "training_data"
                    }
                    
                    # Generate chunk IDs
                    chunk_ids = [f"training_{section_name}_{i}" for i in range(len(chunks))]
                    chunk_metadata = [
                        {**base_metadata, "chunk_index": i, "chunk_id": chunk_ids[i]}
                        for i in range(len(chunks))
                    ]
                    
                    # Add to collection using the compatibility wrapper
                    self.chromadb_wrapper.add_documents(
                        documents=chunks,
                        metadatas=chunk_metadata,
                        ids=chunk_ids,
                        embeddings=embeddings
                    )
                    
                    processed_chunks += len(chunks)
            
            st.success(f"✅ Successfully processed {processed_chunks} chunks from training data")
            return True
            
        except Exception as e:
            st.error(f"❌ Error processing training data: {str(e)}")
            return False
    
    def extract_specific_info_from_web_content(self, web_content_info: List[Dict], query: str) -> str:
        """Extract specific information from web content based on the query with enhanced precision"""
        if not web_content_info:
            return ""
        
        extracted_info = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for web_item in web_content_info:
            content = web_item['content']
            url = web_item['url']
            domain = web_item['domain']
            
            # Extract key sentences that are most relevant to the query
            sentences = content.split('.')
            relevant_sentences = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20:  # Ignore very short sentences
                    sentence_lower = sentence.lower()
                    sentence_words = set(sentence_lower.split())
                    
                    # Calculate relevance score
                    matches = len(query_words.intersection(sentence_words))
                    if matches > 0:
                        # Prefer sentences with higher match ratio
                        score = matches / len(query_words)
                        relevant_sentences.append((score, sentence))
            
            # Sort by relevance and take top sentences
            if relevant_sentences:
                relevant_sentences.sort(key=lambda x: x[0], reverse=True)
                top_sentences = [sentence for score, sentence in relevant_sentences[:2]]  # Take top 2
                
                if top_sentences:
                    extracted_info.append({
                        'url': url,
                        'domain': domain,
                        'key_info': top_sentences,
                        'relevance_score': sum(score for score, _ in relevant_sentences[:2])
                    })
        
        # Sort by relevance score and format the extracted information
        if extracted_info:
            extracted_info.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            formatted_info = []
            for item in extracted_info[:2]:  # Limit to top 2 most relevant sources
                domain_name = item['domain'].replace('www.', '')
                formatted_info.append(f"📄 **{domain_name}:**")
                for info in item['key_info']:
                    # Clean up the information
                    clean_info = info.strip()
                    if not clean_info.endswith('.'):
                        clean_info += '.'
                    formatted_info.append(f"   • {clean_info}")
                formatted_info.append(f"   🔗 Source: {item['url']}")
                formatted_info.append("")
            
            return "\n".join(formatted_info)

        return ""
    
    def determine_query_intent(self, query_lower: str) -> str:
        """Determine the primary intent of a query for more targeted responses"""
        # Define intent categories with their associated keywords
        intent_keywords = {
            'hvac': ['hvac', 'heating', 'cooling', 'temperature', 'thermostat', 'ac', 'air conditioning', 'climate', 'ventilation'],
            'lighting': ['lighting', 'lights', 'illumination', 'led', 'bulb', 'brightness', 'lamp', 'dimmer'],
            'energy': ['energy', 'power', 'efficiency', 'consumption', 'electricity', 'kwh', 'meter', 'electrical'],
            'safety': ['safety', 'fire', 'emergency', 'smoke', 'detector', 'alarm', 'co2', 'carbon monoxide'],
            'security': ['security', 'camera', 'lock', 'access', 'surveillance', 'motion', 'intrusion', 'keycard'],
            'automation': ['automation', 'smart', 'control', 'system', 'iot', 'integration', 'automated'],
            'room': ['room', 'floor', 'classroom', 'capacity', 'space', 'occupancy', 'booking'],
            'equipment': ['equipment', 'device', 'sensor', 'monitor', 'controller', 'hardware'],
            'maintenance': ['maintenance', 'repair', 'service', 'technician', 'install', 'filter', 'replace'],
            'environmental': ['environmental', 'air quality', 'humidity', 'moisture', 'leak', 'water', 'indoor air'],
            'cost': ['cost', 'budget', 'money', 'expense', 'financial', 'savings', 'roi', 'payback']
        }
        
        # Score each intent based on keyword matches
        intent_scores = {}
        for intent, keywords in intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                intent_scores[intent] = score
        
        # Return the intent with the highest score, or 'general' if none found
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        return 'general'
    
    def extract_relevant_content(self, content_list: List[Dict], query: str, max_sentences: int = 3) -> str:
        """Extract the most relevant content from a list of content items based on query"""
        if not content_list:
            return ""
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        relevant_info = []
        
        for item in content_list:
            content = item['content']
            sentences = content.split('.')
            
            # Score sentences based on relevance to query
            scored_sentences = []
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20:  # Ignore very short sentences
                    sentence_lower = sentence.lower()
                    sentence_words = set(sentence_lower.split())
                    
                    # Calculate relevance score
                    matches = len(query_words.intersection(sentence_words))
                    if matches > 0:
                        score = matches / len(query_words)  # Normalize by query length
                        scored_sentences.append((score, sentence))
            
            # Get top sentences for this content item
            if scored_sentences:
                scored_sentences.sort(key=lambda x: x[0], reverse=True)
                top_sentences = [sentence for score, sentence in scored_sentences[:max_sentences]]
                if top_sentences:
                    relevant_info.extend(top_sentences)
        
        # Return the most relevant information, limited to avoid overwhelming
        if relevant_info:
            # Remove duplicates while preserving order
            unique_info = []
            seen = set()
            for info in relevant_info:
                if info not in seen:
                    unique_info.append(info)
                    seen.add(info)
            
            # Limit to top 3 pieces of information
            return " ".join(unique_info[:3])
        
        return ""
    
    def synthesize_blended_response(self, web_info: str, local_info: str, query: str) -> str:
        """Synthesize information from both web and local sources into a cohesive response"""
        if not web_info and not local_info:
            return ""
        
        # Create a blended response that prioritizes the most relevant information
        synthesized = []
        
        if web_info:
            synthesized.append(f"🌐 **Current Industry Information:**\n{web_info}")
        
        if local_info:
            synthesized.append(f"📋 **Building-Specific Information:**\n{local_info}")
        
        # Add contextual recommendations based on query type
        query_lower = query.lower()
        if any(term in query_lower for term in ['how to', 'best practice', 'recommendation', 'should', 'optimize']):
            synthesized.append("💡 **Actionable Recommendations:** Implement a phased approach with pilot testing, monitor performance metrics, and adjust based on real-world feedback.")
        
        return "\n\n".join(synthesized)
    
    def rank_content_by_relevance(self, content_list: List[Dict], query: str) -> List[Dict]:
        """Rank content items by relevance to the query"""
        if not content_list:
            return []
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Score each content item
        scored_content = []
        for item in content_list:
            content = item['content'].lower()
            content_words = set(content.split())
            
            # Calculate relevance score
            matches = len(query_words.intersection(content_words))
            total_words = len(content_words)
            
            # Score based on matches and content length (prefer more specific content)
            if matches > 0 and total_words > 0:
                score = (matches / len(query_words)) * (matches / total_words)
                scored_content.append((score, item))
        
        # Sort by score (descending) and return top items
        scored_content.sort(key=lambda x: x[0], reverse=True)
        return [item for score, item in scored_content[:10]]  # Return top 10 most relevant
    
    def extract_actionable_insights(self, content: str, query: str) -> str:
        """Extract actionable insights from content based on query intent"""
        query_lower = query.lower()
        
        # Look for actionable patterns in the content
        actionable_patterns = [
            r'should\s+([^.]+)',
            r'recommend\s+([^.]+)',
            r'must\s+([^.]+)',
            r'need\s+to\s+([^.]+)',
            r'best\s+practice\s+([^.]+)',
            r'optimal\s+([^.]+)',
            r'implement\s+([^.]+)'
        ]
        
        insights = []
        for pattern in actionable_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            insights.extend(matches[:2])  # Limit to 2 matches per pattern
        
        # Clean up and format insights
        clean_insights = []
        for insight in insights:
            insight = insight.strip()
            if len(insight) > 10 and not insight.endswith('.'):
                insight += '.'
            clean_insights.append(insight)
        
        return " ".join(clean_insights[:3])  # Return top 3 actionable insights
            
# Enhanced helper functions from AutoGenAI.py
def load_sample_documents():
    """Load sample documents into the knowledge base"""
    try:
        # Load training data from JSON file
        if st.session_state.kb.load_and_process_training_data():
            st.success("✅ Training data loaded successfully")
        else:
            st.warning("⚠️ Could not load training data file")
        
        # Load documents from smart_building_data directory
        data_dir = Path("smart_building_data")
        if data_dir.exists():
            documents = list(data_dir.glob("*.pdf")) + list(data_dir.glob("*.txt")) + list(data_dir.glob("*.docx"))
            for doc_path in documents:
                st.session_state.kb.add_document(str(doc_path))
                st.success(f"✅ Added: {doc_path.name}")
    except Exception as e:
        st.error(f"❌ Error loading sample documents: {str(e)}")

def add_document_to_kb(file_path: str, document_type: str = "general") -> str:
    """Add a document to the knowledge base"""
    try:
        if not os.path.exists(file_path):
            return f"❌ File not found: {file_path}"
        
        metadata = {
            "document_type": document_type,
            "category": document_type
        }
        
        success = st.session_state.kb.add_document(file_path, metadata)
        if success:
            return f"✅ Successfully added document: {Path(file_path).name}"
        else:
            return f"❌ Failed to add document: {Path(file_path).name}"
    except Exception as e:
        return f"❌ Error adding document: {str(e)}"

def add_url_to_kb(url: str, category: str = "web_content") -> str:
    """Add content from a URL to the knowledge base"""
    try:
        metadata = {
            "category": category,
            "source_type": "web_content"
        }
        
        success = st.session_state.kb.add_url_to_knowledge_base(url, metadata)
        if success:
            return f"✅ Successfully added web content from: {url}"
        else:
            return f"❌ Failed to add web content from: {url}"
    except Exception as e:
        return f"❌ Error adding URL: {str(e)}"

def train_from_building_websites(urls: List[str] = None) -> str:
    """Train the knowledge base from building management websites"""
    if urls is None:
        urls = [
            "https://www.becamex.com.vn/en/industry-4-0-innovation-center/",
            "https://www.energy.gov/eere/buildings/smart-buildings",
            "https://www.nist.gov/programs-projects/smart-connected-systems",
            "https://www.schneider-electric.com/en/work/solutions/buildings/",
            "https://www.siemens.com/global/en/products/buildings.html"
        ]
    
    try:
        results = st.session_state.kb.train_from_url_list(urls, "building_management")
        
        summary = f"🌐 **Web Training Results:**\n"
        summary += f"✅ Successful URLs: {len(results['successful_urls'])}\n"
        summary += f"❌ Failed URLs: {len(results['failed_urls'])}\n"
        summary += f"📊 Total chunks in KB: {results['total_chunks']}\n"
        
        if results['successful_urls']:
            summary += f"\n**Successfully added:**\n"
            for url in results['successful_urls']:
                summary += f"• {url}\n"
        
        if results['failed_urls']:
            summary += f"\n**Failed to add:**\n"
            for url in results['failed_urls']:
                summary += f"• {url}\n"
        
        if results['errors']:
            summary += f"\n**Errors:**\n"
            for error in results['errors']:
                summary += f"• {error}\n"
        
        return summary
    except Exception as e:
        return f"❌ Error during web training: {str(e)}"

def get_web_training_suggestions() -> str:
    """Get suggestions for web training URLs"""
    suggestions = {
        "Building Management": [
            "https://www.becamex.com.vn/en/industry-4-0-innovation-center/",
            "https://www.energy.gov/eere/buildings/smart-buildings",
            "https://www.nist.gov/programs-projects/smart-connected-systems"
        ],
        "HVAC Systems": [
            "https://www.ashrae.org/",
            "https://www.carrier.com/commercial/en/us/products/hvac/",
            "https://www.trane.com/commercial/north-america/us/en.html"
        ],
        "Smart Building Technology": [
            "https://www.schneider-electric.com/en/work/solutions/buildings/",
            "https://www.siemens.com/global/en/products/buildings.html",
            "https://www.honeywell.com/us/en/products/buildings"
        ],
        "Energy Management": [
            "https://www.energy.gov/eere/buildings/energy-management-systems",
            "https://www.eia.gov/energyexplained/use-of-energy/commercial-buildings.php"
        ]
    }
    
    response = "🌐 **Recommended URLs for Web Training:**\n\n"
    for category, urls in suggestions.items():
        response += f"**{category}:**\n"
        for url in urls:
            response += f"• {url}\n"
        response += "\n"
    
    response += "💡 **To add these URLs, use commands like:**\n"
    response += "• `add url https://example.com category building_management`\n"
    response += "• `train from web` (to add multiple URLs at once)\n"
    
    return response



def get_knowledge_base_stats() -> str:
    """Get statistics about the knowledge base"""
    try:
        collection_info = st.session_state.kb.collection.get()
        
        total_docs = len(collection_info.get('documents', []))
        unique_sources = set()
        web_sources = 0
        local_files = 0
        training_data_chunks = 0
        
        for metadata in collection_info.get('metadatas', []):
            source_type = metadata.get('source_type', 'unknown')
            
            if source_type == 'web_content':
                web_sources += 1
                unique_sources.add(metadata.get('domain', 'Unknown domain'))
            elif source_type == 'training_data':
                training_data_chunks += 1
                unique_sources.add(f"Training: {metadata.get('section', 'Unknown section')}")
            else:
                local_files += 1
                unique_sources.add(metadata.get('filename', 'Unknown file'))
        
        stats = f"📊 **Knowledge Base Statistics:**\n\n"
        stats += f"📚 Total chunks: {total_docs}\n"
        stats += f"🌐 Web content chunks: {web_sources}\n"
        stats += f"📄 Local file chunks: {local_files}\n"
        stats += f"🎓 Training data chunks: {training_data_chunks}\n"
        stats += f"📋 Unique sources: {len(unique_sources)}\n"
        
        return stats
    except Exception as e:
        return f"❌ Error getting knowledge base stats: {str(e)}"
    
# Initialize session state
if 'kb' not in st.session_state:
    st.session_state.kb = SmartBuildingKnowledgeBase()
    # Automatically load training data on first run
    try:
        if os.path.exists("ai_training_data.json"):
            st.session_state.kb.load_and_process_training_data()
    except Exception as e:
        print(f"Note: Could not auto-load training data: {e}")

if 'training_data_loaded' not in st.session_state:
    st.session_state.training_data_loaded = False

if 'messages' not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """🏢 **Welcome to the Smart Building AI Assistant!** 

I'm here to help you with comprehensive building management:

**🔧 Core Systems:**
- HVAC optimization and maintenance schedules
- Smart lighting controls and energy efficiency  
- Temperature monitoring and climate control
- Energy management and consumption analysis
- Security systems and access control
- Building automation and IoT integration

**🌐 Enhanced Capabilities:**
- Web-trained on industry standards and best practices
- Access to Đại học quốc tế Miền Đông building data
- Real-time weather integration for building optimization
- Comprehensive equipment specifications and troubleshooting
- Energy efficiency recommendations and cost analysis

**🚀 Quick Commands:**
- `web training` - Train AI from building management websites
- `stats` - View knowledge base statistics
- `weather` - Get current weather and building recommendations
- Ask about specific systems: HVAC, lighting, energy, safety, security

**📚 Knowledge Sources:**
- Local building documentation and training data
- Industry standards from authoritative websites
- Equipment manuals and maintenance procedures
- Best practices and operational guidelines

How can I help optimize your smart building today?"""
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
            system_message="""You are an expert Smart Building AI Assistant specializing in comprehensive building management solutions. You provide specific, actionable responses without displaying raw data or documentation content.

🏢 **CORE EXPERTISE:**
- HVAC systems: optimization, maintenance, troubleshooting, energy efficiency
- Lighting control: LED systems, smart controls, daylight harvesting
- Security systems: access control, surveillance, monitoring
- Energy management: consumption analysis, optimization strategies
- IoT integration: sensors, automation, data analytics
- Weather-based building optimization

🎯 **RESPONSE GUIDELINES:**
1. **Be Specific & Actionable**: Provide concrete recommendations, specific settings, and clear steps
2. **Synthesize Information**: Never display raw data from knowledge base - always summarize and contextualize
3. **Use Professional Format**: Use emojis, headers, and bullet points for clarity
4. **Include Context**: Search knowledge base and provide synthesized insights
5. **Provide Practical Advice**: Give specific steps, settings, or procedures users can implement
6. **Consider Weather Impact**: Factor in current weather conditions for HVAC/energy recommendations
7. **Offer Multiple Solutions**: Suggest alternatives when applicable

🔧 **WHEN ANSWERING:**
- For weather queries: Include current conditions, forecasts, and specific building impact recommendations
- For HVAC questions: Provide exact temperature settings, maintenance schedules, and energy optimization strategies
- For lighting queries: Include specifications, control strategies, and quantified energy savings
- For general building questions: Search knowledge base and provide synthesized recommendations
- For troubleshooting: Offer step-by-step diagnostic and resolution procedures

❌ **AVOID:**
- Displaying raw content from knowledge base documents
- Showing unprocessed data or technical specifications
- Generic advice without specific recommendations
- Responses that don't provide actionable next steps

🌟 **TONE:** Professional, helpful, and detailed. Always synthesize information into specific, actionable recommendations that demonstrate expertise in smart building management.""",
            llm_config={"config_list": config_list}
        )
        
        user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=5,
            code_execution_config={"executor": code_executor}
        )
        
        st.session_state.assistant = assistant
        st.session_state.user_proxy = user_proxy

# Helper functions
def search_building_knowledge(query: str) -> str:
    """Search the building knowledge base for information with enhanced context"""
    try:
        context = st.session_state.kb.get_context_for_query(query)
        
        if context:
            # Add a summary of what was found
            search_results = st.session_state.kb.search_documents(query, n_results=10)
            
            sources = []
            for result in search_results:
                metadata = result.get('metadata', {})
                source_type = metadata.get('source_type', 'unknown')
                
                if source_type == 'web_content':
                    sources.append(f"🌐 {metadata.get('domain', 'Web source')}")
                elif source_type == 'training_data':
                    sources.append(f"� Training data: {metadata.get('section', 'Unknown section')}")
                else:
                    sources.append(f"� {metadata.get('filename', 'Document')}")
            
            # Remove duplicates
            unique_sources = list(set(sources))
            
            response = f"{context}\n\n"
            if unique_sources:
                response += f"**Sources consulted:** {', '.join(unique_sources[:5])}"
                if len(unique_sources) > 5:
                    response += f" and {len(unique_sources) - 5} more..."
            
            return response
        else:
            return "❓ No specific information found in the knowledge base. Try uploading more documents or adding web content."
    except Exception as e:
        return f"❌ Error searching knowledge base: {str(e)}"

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
    """Get enhanced response from the assistant based on the query"""
    initialize_agents()
    
    # Check if query is about adding web content
    if "add url" in query.lower() or "add website" in query.lower():
        words = query.split()
        url = None
        category = "web_content"
        
        # Look for URL in the query
        for word in words:
            if word.startswith("http"):
                url = word
                break
        
        # Look for category
        if "category" in query.lower():
            for i, word in enumerate(words):
                if word.lower() == "category" and i + 1 < len(words):
                    category = words[i + 1]
                    break
        
        if url:
            return add_url_to_kb(url, category)
        else:
            return "❌ Please specify a URL to add. Example: 'add url https://example.com'"
    
    # Check if query is about web training
    elif "train from web" in query.lower() or "web training" in query.lower():
        return train_from_building_websites()
    
    # Check if query is about getting web suggestions
    elif "web suggestions" in query.lower() or "training suggestions" in query.lower():
        return get_web_training_suggestions()
    
    # Check if query is about knowledge base statistics
    elif "stats" in query.lower() or "statistics" in query.lower():
        return get_knowledge_base_stats()
    
    # Check if query is about listing files
    elif "list" in query.lower() and "file" in query.lower():
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
    
    # Check if query is about loading sample documents
    elif "load sample" in query.lower() or "initialize" in query.lower():
        load_sample_documents()
        return "✅ Sample documents and training data loaded successfully!"
    
    # Weather queries with enhanced functionality
    elif "weather" in query.lower():
        location_keywords = {
            "ho chi minh": "ho chi minh city",
            "saigon": "saigon",
            "university": "đại học quốc tế miền đông",
            "current location": "current location",
            "here": "current location",
            "berlin": "berlin",
            "istanbul": "istanbul",
            "san francisco": "san francisco"
        }
        
        detected_location = None
        for keyword, location in location_keywords.items():
            if keyword in query.lower():
                detected_location = location
                break
        
        if detected_location:
            weather_info = get_current_weather(detected_location)
            try:
                data = json.loads(weather_info)
                response = f"🌡️ **Weather at {data['location']}:**\n"
                
                if "coordinates" in data:
                    response += f"📍 Coordinates: {data['coordinates']}\n"
                
                response += f"🌡️ Temperature: {data['temperature']}°{data.get('unit', 'C')}\n"
                response += f"💧 Humidity: {data['humidity']}\n"
                response += f"☁️ Condition: {data['condition']}\n"
                
                if "message" in data:
                    response += f"ℹ️ {data['message']}\n"
                
                # Add building management recommendations based on weather
                if "temperature" in data and isinstance(data["temperature"], (int, float)):
                    temp = data["temperature"]
                    if temp > 30:
                        response += f"\n🏢 **Building Management Recommendations:**\n"
                        response += f"• Increase AC cooling to maintain 22-24°C indoor temperature\n"
                        response += f"• Monitor energy consumption as cooling demand increases\n"
                        response += f"• Ensure proper ventilation and air circulation\n"
                    elif temp < 18:
                        response += f"\n🏢 **Building Management Recommendations:**\n"
                        response += f"• Adjust heating system to maintain 20-22°C indoor temperature\n"
                        response += f"• Check for drafts and ensure proper insulation\n"
                        response += f"• Monitor heating system efficiency\n"
                
                return response
            except:
                return f"🌡️ Weather information: {weather_info}"
        else:
            return "🌡️ I can provide weather information for Berlin, Istanbul, San Francisco, Ho Chi Minh City, Saigon, and Đại học quốc tế Miền Đông."
    
    # For all other queries, use the enhanced AI assistant
    else:
        try:
            # Use the enhanced AI assistant for comprehensive responses
            return enhanced_ai_assistant(query, st.session_state.kb)
        except Exception as e:
            # Fallback to knowledge base search
            context = search_building_knowledge(query)
            
            if "No specific information" not in context:
                return f"🏢 **Based on your smart building documentation:**\n\n{context}"
            else:
                return f"❓ I couldn't find specific information about that in the knowledge base. Try uploading relevant documents, adding web content, or asking a more general question.\n\nError details: {str(e)}"

def enhanced_ai_assistant(query: str, kb: SmartBuildingKnowledgeBase) -> str:
    """Enhanced AI assistant with precise, contextual responses combining web and local sources"""
    
    # Get comprehensive context
    context = kb.get_context_for_query(query)
    
    # Determine query complexity and intent
    query_lower = query.lower()
    
    # Enhanced prompt for more precise responses
    system_prompt = """You are an expert Smart Building AI Assistant with access to comprehensive building management knowledge from both local documents and current web sources. 

Your role is to provide:
1. PRECISE, actionable answers that directly address the user's question
2. CONTEXTUAL information that blends web sources with building-specific data
3. PRACTICAL recommendations with specific steps or metrics
4. CURRENT best practices from industry sources

Guidelines:
- Be concise but comprehensive
- Prioritize actionable information
- Cite sources when using web information
- Provide specific numbers, ranges, or guidelines when available
- Focus on practical implementation
- Blend theoretical knowledge with real-world applications

Answer the user's question using the provided context, ensuring your response is directly relevant and actionable."""
    
    # Enhanced query with context
    enhanced_query = f"""
Context from Knowledge Base:
{context}

User Question: {query}

Please provide a precise, actionable response that addresses the user's specific question using the available context. Focus on practical recommendations and specific guidance.
"""
    
    # Configure the AI assistant
    assistant = AssistantAgent(
        name="SmartBuildingExpert",
        llm_config={"config_list": config_list},
        system_message=system_prompt,
        human_input_mode="NEVER"
    )
    
    # Create user proxy
    user_proxy = UserProxyAgent(
        name="user_proxy",
        code_execution_config=False,
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1
    )
    
    # Get response
    try:
        response = user_proxy.initiate_chat(assistant, message=enhanced_query, silent=True)
        
        # Extract the assistant's response
        if hasattr(response, 'summary'):
            ai_response = response.summary
        else:
            # Extract from chat history
            messages = response.chat_history if hasattr(response, 'chat_history') else []
            ai_response = ""
            for msg in messages:
                if msg.get('name') == 'SmartBuildingExpert':
                    ai_response = msg.get('content', '')
                    break
        
        # If no response found, use a fallback
        if not ai_response:
            ai_response = "I apologize, but I'm having trouble generating a response right now. Please try rephrasing your question or contact support."
        
        # Enhanced response formatting
        if context:
            ai_response = f"{ai_response}\n\n---\n\n**📚 Knowledge Base Context:**\n{context}"
        
        return ai_response
        
    except Exception as e:
        # Fallback response with context
        fallback_response = f"I understand you're asking about: {query}\n\n"
        if context:
            fallback_response += f"Based on the available information:\n\n{context}\n\n"
        fallback_response += "For more specific guidance, please try rephrasing your question or contact a building management professional."
        return fallback_response

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
        
        # Web Content Training
        st.header("🌐 Web Content Training")
        
        # URL input
        url_input = st.text_input(
            "Add URL to Knowledge Base",
            placeholder="https://example.com",
            help="Add content from a website to the knowledge base"
        )
        
        url_category = st.selectbox(
            "URL Category",
            ["web_content", "building_management", "hvac", "lighting", "energy", "safety", "security", "automation"]
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Add URL") and url_input:
                with st.spinner(f"Fetching content from {url_input}..."):
                    result = add_url_to_kb(url_input, url_category)
                    if "Successfully" in result:
                        st.success(result)
                    else:
                        st.error(result)
        
        with col2:
            if st.button("Train from Web"):
                with st.spinner("Training from authoritative websites..."):
                    result = train_from_building_websites()
                    st.success("Training completed!")
                    with st.expander("View Training Results"):
                        st.text(result)
        
        # Training suggestions
        with st.expander("� Web Training Suggestions"):
            suggestions = get_web_training_suggestions()
            st.markdown(suggestions)
        
        st.markdown("---")
        
        # Knowledge Base Actions
        st.header("📚 Knowledge Base Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 View Statistics"):
                with st.spinner("Getting statistics..."):
                    stats = get_knowledge_base_stats()
                    st.info(stats)
        
        with col2:
            if st.button("🔄 Load Training Data"):
                with st.spinner("Loading training data..."):
                    try:
                        if st.session_state.kb.load_and_process_training_data():
                            st.success("✅ Training data loaded successfully!")
                        else:
                            st.warning("⚠️ Could not load training data")
                    except Exception as e:
                        st.error(f"❌ Error loading training data: {str(e)}")
        
        # Auto-training section
        st.subheader("🤖 Auto-Training System")
        st.markdown("**Automatic AI training when content is updated**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎯 Train on IIC_EIU_Overview", use_container_width=True):
                with st.spinner("Training AI on IIC_EIU_Overview.docx..."):
                    try:
                        doc_path = Path("smart_building_data/IIC_EIU_Overview.docx")
                        if doc_path.exists():
                            metadata = {
                                "document_type": "university_overview",
                                "source": "IIC EIU Overview",
                                "category": "institutional",
                                "training_date": datetime.now().isoformat(),
                                "manually_added": True
                            }
                            
                            success = st.session_state.kb.add_document(str(doc_path), metadata)
                            
                            if success:
                                st.success("✅ Successfully trained AI on IIC_EIU_Overview.docx!")
                                
                                # Show updated stats
                                collection_info = st.session_state.kb.collection.get()
                                total_docs = len(collection_info.get('documents', []))
                                st.info(f"📊 Knowledge base now contains {total_docs} document chunks")
                            else:
                                st.error("❌ Failed to train on IIC_EIU_Overview.docx")
                        else:
                            st.error("❌ IIC_EIU_Overview.docx not found in smart_building_data folder")
                    except Exception as e:
                        st.error(f"❌ Error training: {str(e)}")
        
        with col2:
            if st.button("📚 Train on All Documents", use_container_width=True):
                with st.spinner("Training AI on all documents..."):
                    try:
                        data_dir = Path("smart_building_data")
                        if data_dir.exists():
                            # Get all supported files
                            supported_extensions = ['.pdf', '.docx', '.doc', '.txt', '.json', '.md', '.csv', '.xlsx']
                            files_to_train = []
                            
                            for ext in supported_extensions:
                                files_to_train.extend(data_dir.glob(f"*{ext}"))
                            
                            if files_to_train:
                                trained_count = 0
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                for i, file_path in enumerate(files_to_train):
                                    status_text.text(f"Training on: {file_path.name}")
                                    
                                    # Determine document type
                                    file_name = file_path.name.lower()
                                    if 'iic' in file_name or 'eiu' in file_name:
                                        document_type = "university_overview"
                                    elif 'hvac' in file_name:
                                        document_type = "hvac_manual"
                                    elif 'lighting' in file_name:
                                        document_type = "lighting_specifications"
                                    elif 'security' in file_name:
                                        document_type = "security_manual"
                                    elif 'energy' in file_name:
                                        document_type = "energy_management"
                                    else:
                                        document_type = "general_documentation"
                                    
                                    metadata = {
                                        "document_type": document_type,
                                        "training_date": datetime.now().isoformat(),
                                        "batch_trained": True,
                                        "source_file": file_path.name
                                    }
                                    
                                    success = st.session_state.kb.add_document(str(file_path), metadata)
                                    if success:
                                        trained_count += 1
                                    
                                    progress_bar.progress((i + 1) / len(files_to_train))
                                
                                status_text.text("")
                                progress_bar.empty()
                                
                                if trained_count > 0:
                                    st.success(f"✅ Successfully trained on {trained_count}/{len(files_to_train)} documents!")
                                    
                                    # Show updated stats
                                    collection_info = st.session_state.kb.collection.get()
                                    total_docs = len(collection_info.get('documents', []))
                                    st.info(f"📊 Knowledge base now contains {total_docs} document chunks")
                                else:
                                    st.error("❌ No documents could be processed")
                            else:
                                st.warning("⚠️ No supported documents found in smart_building_data folder")
                        else:
                            st.error("❌ smart_building_data folder not found")
                    except Exception as e:
                        st.error(f"❌ Error during batch training: {str(e)}")
        
        # Auto-training status
        st.markdown("**📊 Training Status:**")
        try:
            # Check for training log
            log_file = Path("training_log.json")
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
                    recent_sessions = log_data.get("training_sessions", [])[-5:]  # Last 5 sessions
                    
                    if recent_sessions:
                        st.markdown("**Recent Training Sessions:**")
                        for session in reversed(recent_sessions):  # Most recent first
                            timestamp = session.get('timestamp', 'Unknown')
                            file_name = session.get('file_name', 'Unknown')
                            success = session.get('success', False)
                            status_icon = "✅" if success else "❌"
                            
                            # Format timestamp
                            try:
                                from datetime import datetime
                                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                time_str = dt.strftime("%Y-%m-%d %H:%M")
                            except:
                                time_str = timestamp
                            
                            st.text(f"{status_icon} {time_str} - {file_name}")
            else:
                st.info("💡 No training history found. Train some documents to see status.")
        except Exception as e:
            st.warning(f"⚠️ Could not load training status: {str(e)}")
        
        # Auto-monitoring instructions
        st.markdown("**🔍 Auto-Training Setup:**")
        st.code("""
# To enable automatic training when files are updated:
cd "d:\\Supervisor"
python auto_training.py --watch

# This will monitor file changes and automatically train the AI
        """)
        
        st.info("💡 **Tip**: The AI will automatically train on new or updated documents when you run the auto-training watcher script.")
        
        # Quick action buttons for testing trained content
        st.markdown("---")
        st.header("⚙️ Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🌐 Industry 4.0", use_container_width=True):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "Tell me about Industry 4.0 and the IIC EIU Innovation Center"
                })
                st.rerun()
            
            if st.button("🎓 IIC EIU Overview", use_container_width=True):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "What is the IIC EIU Overview and what does Eastern International University offer?"
                })
                st.rerun()
        
        # Clear chat section
        st.markdown("### 🗑️ Chat Management")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = [st.session_state.messages[0]]  # Keep only welcome message
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
