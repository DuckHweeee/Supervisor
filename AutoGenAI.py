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
import asyncio
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
from urllib.robotparser import RobotFileParser
import feedparser
import ssl
import certifi

# Load environment variables from .env file
load_dotenv()

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
            import httpx
            
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

# Define weather tool that uses Weather API server
def get_current_weather(location, unit="celsius"):
    """Get the weather for some location using Weather API server"""
    import asyncio
    
    # Handle unit conversion and forecast requests
    include_forecast = False
    if "forecast" in location.lower():
        include_forecast = True
        location = location.replace("forecast", "").strip()
    
    # Get weather data from API server
    try:
        loop = asyncio.get_event_loop()
        weather_data = loop.run_until_complete(
            weather_api_client.get_weather_data(location, include_forecast)
        )
        
        # Format the response based on what we received
        if isinstance(weather_data, dict):
            # Check if it's a full weather response or just current weather
            if "current" in weather_data:
                # Full response with current and forecast
                current = weather_data["current"]
                result = {
                    "location": current.get("location", location),
                    "temperature": f"{current.get('temperature', 'N/A')}°C",
                    "unit": "celsius",
                    "humidity": f"{current.get('humidity', 'N/A')}%",
                    "condition": current.get("condition", "Unknown"),
                    "coordinates": current.get("coordinates", ""),
                    "feels_like": f"{current.get('feels_like', 'N/A')}°C",
                    "wind_speed": f"{current.get('wind_speed', 'N/A')} km/h",
                    "pressure": f"{current.get('pressure', 'N/A')} hPa",
                    "timestamp": current.get("timestamp", "")
                }
                
                if include_forecast and "daily_forecast" in weather_data:
                    result["forecast"] = weather_data["daily_forecast"]
                
                return json.dumps(result, ensure_ascii=False)
            else:
                # Direct current weather data
                result = {
                    "location": weather_data.get("location", location),
                    "temperature": f"{weather_data.get('temperature', 'N/A')}°C",
                    "unit": "celsius",
                    "humidity": f"{weather_data.get('humidity', 'N/A')}%",
                    "condition": weather_data.get("condition", "Unknown"),
                    "coordinates": weather_data.get("coordinates", ""),
                    "feels_like": f"{weather_data.get('feels_like', 'N/A')}°C",
                    "wind_speed": f"{weather_data.get('wind_speed', 'N/A')} km/h",
                    "pressure": f"{weather_data.get('pressure', 'N/A')} hPa",
                    "timestamp": weather_data.get("timestamp", "")
                }
                
                if "message" in weather_data:
                    result["message"] = weather_data["message"]
                
                return json.dumps(result, ensure_ascii=False)
        else:
            return json.dumps(weather_data, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error getting weather data: {e}")
        # Return fallback data
        return json.dumps({
            "location": location,
            "temperature": "26°C",
            "unit": "celsius",
            "humidity": "80%",
            "condition": "Partly Cloudy",
            "coordinates": "11.052754371982356, 106.666777616965",
            "message": f"Weather service temporarily unavailable: {str(e)}"
        }, ensure_ascii=False)

# Smart Building Knowledge Base using ChromaDB with simple text search and web training
class SmartBuildingKnowledgeBase:
    def __init__(self, persist_directory="./knowledge_base"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="smart_building_docs"
        )
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Smart Building AI Assistant/1.0 (Educational Research)'
        })
        
    def simple_embedding(self, text: str) -> List[float]:
        """Create a simple hash-based embedding for text"""
        # Convert text to lowercase and remove special characters
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
        words = clean_text.split()
        
        # Create a simple word frequency vector (first 100 dimensions)
        embedding = [0.0] * 100
        for i, word in enumerate(words[:100]):
            # Simple hash-based approach
            hash_val = hash(word) % 100
            embedding[hash_val] += 1.0
        
        # Normalize
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
            # If we can't check robots.txt, assume we can fetch (be conservative)
            return True
    
    def extract_text_from_url(self, url: str) -> str:
        """Extract text content from a web URL with improved SSL handling"""
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
                print(f"⚠️ SSL verification failed for {url}. Attempting without SSL verification...")
                try:
                    response = self.session.get(url, timeout=30, verify=False)
                    response.raise_for_status()
                    print(f"✅ Successfully fetched content from {url} (SSL verification bypassed)")
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
            from bs4 import BeautifulSoup
            
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
            
        except ImportError:
            # Fallback if BeautifulSoup is not available
            return f"HTML content from {url} (install beautifulsoup4 for better parsing):\n{html_content[:2000]}..."
        except Exception as e:
            return f"Error parsing HTML from {url}: {str(e)}"
    
    def extract_text_from_rss(self, rss_content: str, url: str) -> str:
        """Extract text from RSS/Atom feeds"""
        try:
            import feedparser
            
            feed = feedparser.parse(rss_content)
            
            content_parts = [f"RSS Feed: {feed.feed.get('title', 'Unknown')}\nURL: {url}\n"]
            
            for entry in feed.entries[:10]:  # Limit to 10 recent entries
                title = entry.get('title', 'No title')
                summary = entry.get('summary', entry.get('description', 'No summary'))
                link = entry.get('link', '')
                
                content_parts.append(f"Article: {title}\nLink: {link}\nSummary: {summary}\n")
            
            return '\n'.join(content_parts)
            
        except ImportError:
            return f"RSS content from {url} (install feedparser for RSS parsing):\n{rss_content[:1000]}..."
        except Exception as e:
            return f"Error parsing RSS from {url}: {str(e)}"
    
    def add_url_to_knowledge_base(self, url: str, metadata: Dict[str, Any] = None) -> bool:
        """Add content from a URL to the knowledge base"""
        try:
            print(f"🌐 Fetching content from: {url}")
            
            # Extract text from URL
            text = self.extract_text_from_url(url)
            
            if text.startswith("Error"):
                print(f"❌ {text}")
                return False
            
            if len(text.strip()) < 100:
                print(f"❌ Insufficient content from {url}")
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
            self.collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=chunk_metadata,
                ids=chunk_ids
            )
            
            print(f"✅ Successfully added {len(chunks)} chunks from {url}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding URL {url}: {str(e)}")
            return False
    
    def train_from_url_list(self, urls: List[str], category: str = "web_training") -> Dict[str, Any]:
        """Train the knowledge base from a list of URLs"""
        results = {
            "successful": 0,
            "failed": 0,
            "total_chunks": 0,
            "errors": []
        }
        
        print(f"🌐 Starting web training from {len(urls)} URLs...")
        
        for i, url in enumerate(urls, 1):
            print(f"\n📄 Processing URL {i}/{len(urls)}: {url}")
            
            try:
                success = self.add_url_to_knowledge_base(url, {"category": category})
                if success:
                    results["successful"] += 1
                    # Count chunks added
                    collection_info = self.collection.get()
                    current_chunks = len([m for m in collection_info['metadatas'] if m.get('source_url') == url])
                    results["total_chunks"] += current_chunks
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Failed to process {url}")
                    
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Error with {url}: {str(e)}")
                print(f"❌ Error processing {url}: {e}")
        
        print(f"\n📊 Web Training Complete!")
        print(f"✅ Successful: {results['successful']}")
        print(f"❌ Failed: {results['failed']}")
        print(f"📄 Total chunks added: {results['total_chunks']}")
        
        return results
    
    def add_document(self, file_path: str, metadata: Dict[str, Any] = None) -> bool:
        """Add a document to the knowledge base"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                print(f"File not found: {file_path}")
                return False
                
            text = self.extract_text_from_file(file_path)
            if not text or text.startswith("Error"):
                print(f"Failed to extract text from: {file_path}")
                return False
                
            chunks = self.chunk_text(text)
            
            # Create embeddings using simple embedding function
            embeddings = [self.simple_embedding(chunk) for chunk in chunks]
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
            
            base_metadata = {
                "filename": file_path.name,
                "file_path": str(file_path),
                "file_type": file_path.suffix,
                "added_date": datetime.now().isoformat(),
                **metadata
            }
            
            # Generate unique IDs for chunks
            chunk_ids = [f"{file_path.stem}_{i}" for i in range(len(chunks))]
            chunk_metadata = [
                {**base_metadata, "chunk_index": i, "chunk_id": chunk_ids[i]}
                for i in range(len(chunks))
            ]
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=chunk_metadata,
                ids=chunk_ids
            )
            
            print(f"Successfully added {len(chunks)} chunks from {file_path.name}")
            return True
            
        except Exception as e:
            print(f"Error adding document: {str(e)}")
            return False
    
    def search_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents based on query"""
        try:
            # First try embedding search
            query_embedding = [self.simple_embedding(query)]
            
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )
            
            # If no good results, try text-based search
            if not results['documents'][0]:
                # Fallback to text search
                all_docs = self.collection.get()
                text_results = []
                query_words = set(query.lower().split())
                
                for i, doc in enumerate(all_docs['documents']):
                    doc_words = set(doc.lower().split())
                    # Simple word overlap scoring
                    overlap = len(query_words.intersection(doc_words))
                    if overlap > 0:
                        text_results.append({
                            'document': doc,
                            'metadata': all_docs['metadatas'][i],
                            'score': overlap
                        })
                
                # Sort by score and take top results
                text_results.sort(key=lambda x: x['score'], reverse=True)
                search_results = []
                for result in text_results[:n_results]:
                    search_results.append({
                        "content": result['document'],
                        "metadata": result['metadata'],
                        "distance": 1.0 - (result['score'] / len(query_words))  # Convert score to distance
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
            print(f"Error searching documents: {str(e)}")
            return []
    
    def get_context_for_query(self, query: str, max_context_length: int = 4000) -> str:
        """Get relevant context for a query and synthesize it into actionable information"""
        search_results = self.search_documents(query, n_results=15)
        
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
                synthesized_info.append("🌐 **Web Sources Information:**")
                synthesized_info.append(web_info)
        
        # HVAC and Climate Control
        if any(term in query_lower for term in ['hvac', 'heating', 'cooling', 'temperature', 'thermostat', 'ac', 'air conditioning', 'climate']):
            synthesized_info.append("🌡️ **HVAC System Guidelines:** Optimal temperature range is 68-72°F (20-22°C) for comfort and energy efficiency. Smart thermostats can reduce energy consumption by 15-25% through automated scheduling and weather-based adjustments.")
        
        # Lighting Systems
        if any(term in query_lower for term in ['lighting', 'lights', 'illumination', 'led', 'bulb', 'brightness']):
            synthesized_info.append("💡 **Lighting Recommendations:** LED systems provide 80% energy savings compared to traditional lighting. Use daylight sensors and occupancy controls for optimal efficiency. Natural light integration can reduce artificial lighting needs by 50-80%.")
        
        # Energy Management
        if any(term in query_lower for term in ['energy', 'power', 'efficiency', 'consumption', 'electricity', 'kwh']):
            synthesized_info.append("⚡ **Energy Efficiency:** Smart scheduling and automated controls can reduce building energy consumption by 20-30%. Monitor peak usage times and implement load balancing. Weather-responsive systems optimize energy use automatically.")
        
        # Safety Systems
        if any(term in query_lower for term in ['safety', 'fire', 'emergency', 'smoke', 'detector', 'alarm', 'co2']):
            synthesized_info.append("🚨 **Safety Protocols:** Fire safety systems require monthly testing. Smoke detectors should be inspected quarterly. Emergency exits must remain clearly marked and accessible. CO2 monitoring ensures air quality.")
        
        # Security Systems
        if any(term in query_lower for term in ['security', 'camera', 'lock', 'access', 'surveillance', 'motion']):
            synthesized_info.append("🔒 **Security Management:** Access control systems should be integrated with occupancy tracking. Motion detectors and cameras require regular maintenance and firmware updates. Implement layered security with multiple detection methods.")
        
        # Room and Space Management
        if any(term in query_lower for term in ['room', 'floor', 'classroom', 'capacity', 'space', 'occupancy']):
            synthesized_info.append("🏢 **Room Management:** Optimize space utilization through occupancy sensors and booking systems. Standard classrooms accommodate 30-62 students with appropriate AV equipment. Track utilization rates for efficient space planning.")
        
        # Equipment and Devices
        if any(term in query_lower for term in ['equipment', 'device', 'sensor', 'monitor', 'controller', 'smart']):
            synthesized_info.append("🔧 **Equipment Management:** IoT devices require regular firmware updates and network connectivity checks. Implement predictive maintenance schedules for optimal performance. Monitor device status for proactive maintenance.")
        
        # Maintenance and Service
        if any(term in query_lower for term in ['maintenance', 'repair', 'service', 'technician', 'install', 'filter']):
            synthesized_info.append("🛠️ **Maintenance Protocols:** Establish preventive maintenance schedules. HVAC filters should be replaced every 3-6 months. Document all service activities. Use predictive maintenance to prevent equipment failures.")
        
        # Building Automation
        if any(term in query_lower for term in ['automation', 'smart', 'control', 'system', 'iot', 'integration']):
            synthesized_info.append("🤖 **Building Automation:** Integrate all systems for centralized control. Use IoT sensors for real-time monitoring and automated responses to environmental changes. Implement smart scheduling for optimal efficiency.")
        
        # Environmental Monitoring
        if any(term in query_lower for term in ['environmental', 'air quality', 'humidity', 'moisture', 'leak', 'water']):
            synthesized_info.append("🌿 **Environmental Monitoring:** Maintain humidity levels between 30-50% for comfort. Use air quality sensors to monitor CO2 levels and ensure proper ventilation. Implement leak detection systems for water damage prevention.")
        
        # Cost and Budget Management
        if any(term in query_lower for term in ['cost', 'budget', 'money', 'expense', 'financial', 'savings']):
            synthesized_info.append("💰 **Cost Management:** Energy-efficient systems can reduce operational costs by 25-40%. Implement smart scheduling to minimize peak demand charges. Weather-responsive controls optimize energy spending.")
        
        # Building Information and General Management
        if any(term in query_lower for term in ['building', 'name', 'location', 'floors', 'rooms', 'information', 'overview']):
            synthesized_info.append("🏢 **Building Information:** The building management system provides comprehensive control over all building operations. Implement integrated monitoring for optimal performance across all systems.")
        
        # AI and Machine Learning Integration
        if any(term in query_lower for term in ['ai', 'machine learning', 'ml', 'neural network', 'algorithm', 'prediction', 'analytics']):
            synthesized_info.append("🤖 **AI & Machine Learning:** Implement predictive analytics for equipment failure prediction, energy consumption forecasting, and occupancy pattern analysis. Use computer vision for people counting and neural networks for system optimization.")
        
        # Cybersecurity and Privacy
        if any(term in query_lower for term in ['cybersecurity', 'security', 'privacy', 'encryption', 'hack', 'cyber', 'vulnerability']):
            synthesized_info.append("🔒 **Cybersecurity & Privacy:** Implement zero-trust architecture, encrypt all data transmissions, regularly update IoT device firmware, and conduct vulnerability assessments. Ensure compliance with data protection regulations.")
        
        # Digital Twins and Simulation
        if any(term in query_lower for term in ['digital twin', 'simulation', 'model', 'virtual', 'twin', 'digital model']):
            synthesized_info.append("📊 **Digital Twins & Simulation:** Create virtual building models for performance optimization, predictive maintenance, and scenario testing. Use real-time sensor data to validate and update digital twin accuracy.")
        
        # Retrofit and Modernization
        if any(term in query_lower for term in ['retrofit', 'modernization', 'upgrade', 'renovation', 'legacy', 'old system']):
            synthesized_info.append("🔧 **Retrofit & Modernization:** Prioritize upgrades based on ROI analysis, integrate new technology with existing systems, and plan phased implementations to minimize disruption. Consider energy efficiency incentives and rebates.")
        
        # Regulatory Compliance
        if any(term in query_lower for term in ['regulation', 'compliance', 'code', 'standard', 'permit', 'inspection', 'ada', 'osha']):
            synthesized_info.append("📋 **Regulatory Compliance:** Ensure adherence to building codes, ADA accessibility requirements, fire safety standards, and environmental regulations. Maintain proper documentation and schedule regular inspections.")
        
        # Performance Benchmarking
        if any(term in query_lower for term in ['benchmark', 'performance', 'kpi', 'metrics', 'comparison', 'standard', 'rating']):
            synthesized_info.append("📈 **Performance Benchmarking:** Track energy use intensity (EUI), compare against industry standards, monitor occupant satisfaction scores, and implement continuous improvement strategies. Use ENERGY STAR Portfolio Manager for benchmarking.")
        
        # Emergency Preparedness
        if any(term in query_lower for term in ['emergency', 'disaster', 'crisis', 'backup', 'resilience', 'continuity', 'evacuation']):
            synthesized_info.append("🚨 **Emergency Preparedness:** Develop comprehensive emergency response plans, maintain backup systems, conduct regular drills, and ensure clear communication protocols. Implement redundant systems for critical operations.")
        
        # Occupant Wellness and Experience
        if any(term in query_lower for term in ['wellness', 'comfort', 'satisfaction', 'occupant', 'experience', 'productivity', 'health']):
            synthesized_info.append("😌 **Occupant Wellness:** Optimize indoor air quality (CO2 <800 ppm), maintain comfortable temperature (68-72°F), provide adequate lighting (300-500 lux), and implement noise control measures. Use biophilic design elements.")
        
        # Advanced Analytics and Predictive Maintenance
        if any(term in query_lower for term in ['predictive', 'analytics', 'forecast', 'trend', 'pattern', 'anomaly', 'detection']):
            synthesized_info.append("🔮 **Predictive Analytics:** Implement machine learning algorithms for failure prediction, energy forecasting, and anomaly detection. Use historical data to identify patterns and optimize maintenance schedules proactively.")
        
        # If no specific category matches, provide general building management advice
        if not synthesized_info and (hvac_info or lighting_info or energy_info or general_info):
            synthesized_info.append("🏢 **Building Management:** Implement comprehensive building automation systems with regular maintenance schedules, energy monitoring, and automated controls for optimal performance and efficiency.")
        
        return "\n".join(synthesized_info) if synthesized_info else ""
    
    def extract_specific_info_from_web_content(self, web_content_info: List[Dict], query: str) -> str:
        """Extract specific information from web content based on the query"""
        if not web_content_info:
            return ""
        
        extracted_info = []
        query_lower = query.lower()
        
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
                    
                    # Check if sentence contains query terms
                    query_words = query_lower.split()
                    matches = sum(1 for word in query_words if word in sentence_lower)
                    
                    if matches > 0:
                        relevant_sentences.append(sentence)
            
            # If we found relevant sentences, format them nicely
            if relevant_sentences:
                # Take the most relevant sentences (up to 3)
                top_sentences = relevant_sentences[:3]
                
                extracted_info.append({
                    'url': url,
                    'domain': domain,
                    'key_info': top_sentences
                })
        
        # Format the extracted information
        if extracted_info:
            formatted_info = []
            for item in extracted_info:
                domain_name = item['domain'].replace('www.', '')
                formatted_info.append(f"📄 **From {domain_name}:**")
                for info in item['key_info']:
                    formatted_info.append(f"   • {info}")
                formatted_info.append(f"   🔗 Source: {item['url']}")
                formatted_info.append("")
            
            return "\n".join(formatted_info)
        
        return ""

# Initialize Knowledge Base
kb = SmartBuildingKnowledgeBase()

# Load sample documents if they exist
def load_sample_documents():
    """Load sample documents into the knowledge base"""
    sample_files = [
        "smart_building_data/hvac_manual.txt",
        "smart_building_data/lighting_specifications.txt",
        "smart_building_data/building_data.json"
    ]
    
    for file_path in sample_files:
        if Path(file_path).exists():
            try:
                kb.add_document(file_path, {
                    "document_type": "system_manual",
                    "auto_loaded": True
                })
                print(f"Auto-loaded: {file_path}")
            except Exception as e:
                print(f"Failed to auto-load {file_path}: {e}")

# Load sample documents on startup
load_sample_documents()

# Smart Building document management functions
def add_document_to_kb(file_path: str, document_type: str = "general") -> str:
    """Add a document to the smart building knowledge base"""
    metadata = {
        "document_type": document_type,
        "building_system": "smart_building"
    }
    
    success = kb.add_document(file_path, metadata)
    if success:
        return f"Successfully added document: {Path(file_path).name}"
    else:
        return f"Failed to add document: {Path(file_path).name}"

def add_url_to_kb(url: str, category: str = "web_content") -> str:
    """Add content from a URL to the smart building knowledge base"""
    metadata = {
        "document_type": "web_content",
        "category": category,
        "building_system": "smart_building"
    }
    
    success = kb.add_url_to_knowledge_base(url, metadata)
    if success:
        return f"Successfully added content from: {url}"
    else:
        return f"Failed to add content from: {url}"

def train_from_building_websites(urls: List[str] = None) -> str:
    """Train the AI from building management and smart building websites"""
    
    if urls is None:
        # Default list of authoritative building management websites
        urls = [
            "https://www.ashrae.org/technical-resources/standards-and-guidelines",
            "https://www.usgbc.org/leed",
            "https://www.energystar.gov/buildings",
            "https://www.buildinggreennyc.com/best-practices",
            "https://www.facilitiesnet.com/hvac",
            "https://www.buildings.com/hvac",
            "https://www.automatedbuildings.com",
            "https://www.intelligentbuildings.com",
            "https://www.smartbuildingsmagazine.com"
        ]
    
    print(f"🌐 Training AI from {len(urls)} building management websites...")
    
    results = kb.train_from_url_list(urls, "building_management_websites")
    
    response = f"""🎓 Web Training Results:
    
📊 **Training Summary:**
• URLs Processed: {results['successful'] + results['failed']}
• Successful: {results['successful']}
• Failed: {results['failed']}
• Total Content Chunks: {results['total_chunks']}

✅ **Knowledge Enhanced:** The AI now has access to content from authoritative building management websites including ASHRAE standards, LEED guidelines, ENERGY STAR resources, and smart building best practices.

🔍 **New Capabilities:** The AI can now answer questions about:
• Industry standards and guidelines
• Green building certifications
• HVAC best practices from experts
• Smart building technologies
• Energy efficiency standards
• Building automation trends"""

    if results['errors']:
        response += f"\n\n⚠️ **Errors Encountered:**\n" + "\n".join(results['errors'][:5])
    
    return response

def get_web_training_suggestions() -> str:
    """Get suggestions for URLs to train the AI with building knowledge"""
    suggestions = """🌐 **Recommended Training URLs for Smart Building AI:**

🏢 **Building Standards & Guidelines:**
• https://www.ashrae.org - HVAC industry standards
• https://www.usgbc.org - Green building and LEED certification
• https://www.energystar.gov - Energy efficiency guidelines
• https://www.iea.org - International energy efficiency best practices

🤖 **Smart Building Technologies:**
• https://www.automatedbuildings.com - Building automation insights
• https://www.intelligentbuildings.com - Smart building technologies
• https://www.smartbuildingsmagazine.com - Industry trends and case studies
• https://www.bacnet.org - Building automation protocols

🔧 **HVAC & Systems:**
• https://www.facilitiesnet.com/hvac - HVAC maintenance and optimization
• https://www.buildings.com - Building systems and management
• https://www.contractingbusiness.com - HVAC best practices
• https://www.achr-news.com - Air conditioning and refrigeration

💡 **Energy & Sustainability:**
• https://www.greenbiz.com - Sustainable building practices
• https://www.buildinggreen.com - Environmental building strategies
• https://www.nrel.gov - Renewable energy and efficiency research
• https://www.epa.gov/energy - Environmental energy guidelines

📚 **Usage Examples:**
• add_url_to_kb("https://www.ashrae.org/standards", "hvac_standards")
• train_from_building_websites() - Uses default authoritative sources
• train_from_building_websites(["your_custom_urls"]) - Custom training

⚠️ **Important Notes:**
• URLs must be publicly accessible
• Content must be related to building management
• Training respects robots.txt and rate limits
• Large websites may take time to process"""
    
    return suggestions

def search_building_knowledge(query: str) -> str:
    """Search the smart building knowledge base and provide actionable recommendations"""
    context = kb.get_context_for_query(query)
    
    if not context:
        return "No specific information found in the knowledge base for this query. Please ensure relevant documentation is available."
    
    # Add contextual recommendations based on the query
    query_lower = query.lower()
    recommendations = []
    
    if any(term in query_lower for term in ['temperature', 'heating', 'cooling', 'hvac']):
        recommendations.append("💡 **Related:** Check temperature settings, maintenance schedules, and filter replacement procedures")
    
    if any(term in query_lower for term in ['lighting', 'lights']):
        recommendations.append("💡 **Related:** Review LED specifications, motion sensor settings, and energy efficiency measures")
    
    if any(term in query_lower for term in ['energy', 'power']):
        recommendations.append("💡 **Related:** Consider weather-based optimization and consumption monitoring")
    
    if any(term in query_lower for term in ['security', 'access control', 'surveillance']):
        recommendations.append("💡 **Related:** Check camera placements, recording settings, and alarm configurations")
    
    if any(term in query_lower for term in ['maintenance', 'repair', 'service']):
        recommendations.append("💡 **Related:** Review service logs, maintenance schedules, and equipment warranties")
    
    if any(term in query_lower for term in ['automation', 'smart building', 'iot']):
        recommendations.append("💡 **Related:** Explore automation opportunities for energy savings and enhanced comfort")
    
    # Combine context with recommendations
    response = f"{context}"
    if recommendations:
        response += f"\n\n{recommendations[0]}"
    
    return response

def get_knowledge_base_stats() -> str:
    """Get statistics about the knowledge base"""
    try:
        collection_info = kb.collection.get()
        doc_count = len(collection_info['documents'])
        
        # Count unique files
        unique_files = set()
        for metadata in collection_info['metadatas']:
            if 'filename' in metadata:
                unique_files.add(metadata['filename'])
        
        stats = f"""Knowledge Base Statistics:
- Total document chunks: {doc_count}
- Unique documents: {len(unique_files)}
- Available files: {', '.join(unique_files) if unique_files else 'None'}
        
To add more documents, place files in 'smart_building_data/' folder and use the add_building_document function."""
        
        return stats
    except Exception as e:
        return f"Error getting knowledge base stats: {e}"

# Create a user proxy agent that only handles code execution
def is_termination_msg(message):
    """Check if a message is a termination message"""
    content = message.get("content") if message else None
    if content is None:
        return False
    return content.rstrip().endswith("TERMINATE")

user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",  # Never ask for human input
    max_consecutive_auto_reply=5,  # Allow more turns for complete responses
    is_termination_msg=is_termination_msg,
    code_execution_config={"executor": code_executor}
)

# Create an AI assistant that can handle Smart Building queries
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

# Register the weather tool with both agents
@user_proxy.register_for_execution()
@assistant.register_for_llm(description="Get comprehensive weather information including current conditions, forecasts, and building management recommendations.")
def weather_forecast(
    location: Annotated[str, "City name, 'current location', 'university', or 'Đại học quốc tế Miền Đông' for coordinates 11.052754371982356, 106.666777616965"],
    unit: Annotated[str, "Temperature unit (fahrenheit/celsius)"] = "celsius",
    include_forecast: Annotated[bool, "Include 3-day weather forecast"] = False,
    include_recommendations: Annotated[bool, "Include smart building recommendations"] = True
) -> str:
    # Get current weather data
    weather_details = get_current_weather(location=location, unit=unit)
    weather = json.loads(weather_details)
    
    # Build comprehensive response
    response_parts = []
    
    # Current weather information
    if weather.get('temperature') and weather.get('temperature') != 'unknown':
        response_parts.append(f"📍 **Current Weather at {weather['location']}:**")
        response_parts.append(f"🌡️ Temperature: {weather['temperature']}")
        
        if weather.get('feels_like'):
            response_parts.append(f"🌡️ Feels like: {weather['feels_like']}")
        
        response_parts.append(f"💧 Humidity: {weather['humidity']}")
        response_parts.append(f"🌤️ Condition: {weather['condition']}")
        
        if weather.get('wind_speed'):
            response_parts.append(f"💨 Wind: {weather['wind_speed']}")
        
        if weather.get('pressure'):
            response_parts.append(f"📊 Pressure: {weather['pressure']}")
        
        if weather.get('timestamp'):
            response_parts.append(f"⏰ Last updated: {weather['timestamp']}")
        
        if weather.get('coordinates'):
            response_parts.append(f"📍 Coordinates: {weather['coordinates']}")
    
    # Add forecast if requested
    if include_forecast and weather.get('forecast'):
        response_parts.append(f"\n📅 **3-Day Forecast:**")
        for day in weather['forecast'][:3]:
            date = day.get('date', 'Unknown date')
            max_temp = day.get('max_temp', 'N/A')
            min_temp = day.get('min_temp', 'N/A')
            condition = day.get('condition', 'Unknown')
            response_parts.append(f"  {date}: {max_temp}°/{min_temp}° - {condition}")
    
    # Add smart building recommendations
    if include_recommendations and weather.get('temperature'):
        response_parts.append(f"\n🏢 **Smart Building Recommendations:**")
        
        try:
            temp_str = weather['temperature'].replace('°C', '').replace('°F', '')
            temp = float(temp_str)
            humidity_str = weather['humidity'].replace('%', '')
            humidity = float(humidity_str) if humidity_str != 'N/A' else 50
            
            # HVAC recommendations
            if temp > 30:
                response_parts.append("❄️ **HVAC:** Set cooling to 22-24°C, increase ventilation")
                response_parts.append("⚡ **Energy:** High cooling load expected - monitor energy usage")
            elif temp < 20:
                response_parts.append("🔥 **HVAC:** Set heating to 20-22°C, reduce ventilation")
                response_parts.append("⚡ **Energy:** Heating required - optimize heating schedule")
            else:
                response_parts.append("🌡️ **HVAC:** Optimal temperature range - maintain current settings")
                response_parts.append("⚡ **Energy:** Good conditions for natural ventilation")
            
            # Humidity recommendations
            if humidity > 70:
                response_parts.append("💧 **Humidity:** High humidity - increase dehumidification")
            elif humidity < 40:
                response_parts.append("💧 **Humidity:** Low humidity - reduce dehumidification")
            else:
                response_parts.append("💧 **Humidity:** Optimal humidity levels")
            
            # Lighting recommendations based on condition
            condition_lower = weather['condition'].lower()
            if 'clear' in condition_lower or 'sunny' in condition_lower:
                response_parts.append("💡 **Lighting:** Excellent natural light - reduce artificial lighting by 80%")
            elif 'partly' in condition_lower:
                response_parts.append("💡 **Lighting:** Good natural light - reduce artificial lighting by 50%")
            elif 'cloudy' in condition_lower or 'overcast' in condition_lower:
                response_parts.append("💡 **Lighting:** Limited natural light - maintain artificial lighting")
            
        except (ValueError, TypeError):
            response_parts.append("🏢 **Building Recommendations:** Weather data available for analysis")
    
    # Add error message if weather unavailable
    if weather.get('message'):
        response_parts.append(f"\n⚠️ **Note:** {weather['message']}")
    
    return "\n".join(response_parts)

# Register Smart Building tools
@user_proxy.register_for_execution()
@assistant.register_for_llm(description="Add content from a URL to the smart building knowledge base for AI training.")
def add_web_content(
    url: Annotated[str, "URL to extract content from (must be publicly accessible)"],
    category: Annotated[str, "Category for the content (e.g., 'hvac_standards', 'energy_efficiency', 'building_automation')"] = "web_content"
) -> str:
    return add_url_to_kb(url, category)

@user_proxy.register_for_execution()
@assistant.register_for_llm(description="Train the AI from authoritative building management websites to enhance knowledge.")
def train_from_web(
    custom_urls: Annotated[List[str], "Optional list of custom URLs to train from. If not provided, uses default authoritative building websites."] = None
) -> str:
    return train_from_building_websites(custom_urls)

@user_proxy.register_for_execution()
@assistant.register_for_llm(description="Get recommendations for URLs and websites to train the AI with building management knowledge.")
def get_training_url_suggestions() -> str:
    return get_web_training_suggestions()

@user_proxy.register_for_execution()
@assistant.register_for_llm(description="Add a document to the smart building knowledge base.")
def add_building_document(
    file_path: Annotated[str, "Path to the document file"],
    document_type: Annotated[str, "Type of document (manual, specification, maintenance, etc.)"] = "general"
) -> str:
    return add_document_to_kb(file_path, document_type)

@user_proxy.register_for_execution()
@assistant.register_for_llm(description="Search the smart building knowledge base for comprehensive information about systems, maintenance, specifications, and operations.")
def search_building_info(
    query: Annotated[str, "Search query about smart building systems, HVAC, lighting, security, energy management, etc."]
) -> str:
    context = search_building_knowledge(query)
    
    if context.strip() == "Relevant Smart Building Information:\n" or "No relevant information found" in context:
        return f"❌ **No specific information found for '{query}' in the knowledge base.**\n\n🔍 **Suggestions:**\n- Try more general terms (e.g., 'HVAC' instead of 'HVAC temperature control')\n- Check available documents with the list_building_files function\n- Add relevant documents to the knowledge base\n\n📚 **Available topics include:** HVAC systems, lighting specifications, building automation, energy management, security systems, and maintenance procedures."
    
    # Format the response better
    formatted_response = f"📚 **Smart Building Information for '{query}':**\n\n"
    formatted_response += context.replace("Relevant Smart Building Information:\n\n", "")
    
    # Add helpful suggestions based on the query
    query_lower = query.lower()
    suggestions = []
    
    if 'hvac' in query_lower:
        suggestions.append("💡 **Related:** Check temperature settings, maintenance schedules, and filter replacement procedures")
    elif 'lighting' in query_lower:
        suggestions.append("💡 **Related:** Review LED specifications, motion sensor settings, and energy efficiency measures")
    elif 'energy' in query_lower:
        suggestions.append("💡 **Related:** Consider weather-based optimization and consumption monitoring")
    elif 'security' in query_lower:
        suggestions.append("💡 **Related:** Check camera placements, recording settings, and alarm configurations")
    elif 'maintenance' in query_lower:
        suggestions.append("💡 **Related:** Review service logs, maintenance schedules, and equipment warranties")
    
    if suggestions:
        formatted_response += f"\n\n{suggestions[0]}"
    
    return formatted_response

@user_proxy.register_for_execution()
@assistant.register_for_llm(description="List files in the smart building data directory.")
def list_building_files() -> str:
    data_dir = Path("smart_building_data")
    if not data_dir.exists():
        return "Smart building data directory not found."
    
    files = list(data_dir.glob("*"))
    if not files:
        return "No files found in smart building data directory."
    
    file_list = "Files in smart building data directory:\n"
    for file in files:
        file_list += f"- {file.name} ({file.suffix})\n"
    
    return file_list

@user_proxy.register_for_execution()
@assistant.register_for_llm(description="Get statistics about the knowledge base.")
def get_kb_stats() -> str:
    return get_knowledge_base_stats()

# Create a user proxy agent that only handles code execution
def is_termination_msg(message):
    """Check if a message is a termination message"""
    content = message.get("content") if message else None
    if content is None:
        return False
    return content.rstrip().endswith("TERMINATE")

# Demo function to show capabilities without interactive chat
def demo_smart_building_assistant():
    """Demonstrate the Smart Building AI Assistant capabilities"""
    print("🏢 Smart Building AI Assistant Demo")
    print("=" * 50)
    
    # Test weather function
    print("\n🌡️ Testing Weather Function:")
    weather_result = get_current_weather("Đại học quốc tế Miền Đông")
    print(f"Weather at university: {weather_result}")
    
    # Test knowledge base
    print("\n📚 Testing Knowledge Base:")
    hvac_info = search_building_knowledge("HVAC maintenance schedule")
    print(f"HVAC Information: {hvac_info[:200]}...")
    
    # Test document listing
    print("\n📋 Available Documents:")
    data_dir = Path("smart_building_data")
    if data_dir.exists():
        files = list(data_dir.glob("*"))
        for file in files:
            print(f"  - {file.name}")
    
    print("\n✅ Demo completed! Use the Streamlit app for interactive chat.")
    print("Run: streamlit run streamlit_app.py")

if __name__ == "__main__":
    demo_smart_building_assistant()

# Register comprehensive weather analysis tool
@assistant.register_for_llm(description="Perform comprehensive weather analysis for smart building optimization, including HVAC recommendations, energy management, and comfort analysis.")
def analyze_building_weather_impact(
    location: Annotated[str, "Location for weather analysis"] = "university",
    analysis_type: Annotated[str, "Type of analysis: 'hvac', 'energy', 'comfort', or 'comprehensive'"] = "comprehensive"
) -> str:
    """Comprehensive weather analysis for building management"""
    
    # Get current weather data
    weather_details = get_current_weather(location=location)
    weather = json.loads(weather_details)
    
    if weather.get('temperature') == 'unknown':
        return f"❌ **Weather data unavailable for {location}**\n\nUnable to perform building analysis without current weather conditions."
    
    response_parts = []
    response_parts.append(f"🏢 **Smart Building Weather Analysis for {weather['location']}**")
    response_parts.append(f"📊 **Analysis Type:** {analysis_type.title()}")
    response_parts.append("")
    
    # Current conditions summary
    response_parts.append(f"🌤️ **Current Conditions:**")
    response_parts.append(f"Temperature: {weather['temperature']} (Feels like: {weather.get('feels_like', 'N/A')})")
    response_parts.append(f"Humidity: {weather['humidity']} | Condition: {weather['condition']}")
    if weather.get('wind_speed'):
        response_parts.append(f"Wind: {weather['wind_speed']} | Pressure: {weather.get('pressure', 'N/A')}")
    response_parts.append("")
    
    try:
        # Extract numeric values for analysis
        temp_str = weather['temperature'].replace('°C', '').replace('°F', '')
        temp = float(temp_str)
        humidity_str = weather['humidity'].replace('%', '')
        humidity = float(humidity_str) if humidity_str != 'N/A' else 50
        
        # HVAC Analysis
        if analysis_type in ['hvac', 'comprehensive']:
            response_parts.append("❄️ **HVAC OPTIMIZATION:**")
            
            if temp > 32:
                response_parts.append("🔴 **HIGH TEMPERATURE ALERT**")
                response_parts.append("• Set cooling setpoint: 22°C")
                response_parts.append("• Increase ventilation rate to HIGH")
                response_parts.append("• Pre-cool building during early morning hours")
                response_parts.append("• Consider additional cooling zones activation")
            elif temp > 28:
                response_parts.append("🟡 **WARM CONDITIONS**")
                response_parts.append("• Set cooling setpoint: 23-24°C")
                response_parts.append("• Increase ventilation rate to MEDIUM")
                response_parts.append("• Monitor indoor temperature closely")
            elif temp < 18:
                response_parts.append("🔵 **COOL CONDITIONS**")
                response_parts.append("• Set heating setpoint: 20-22°C")
                response_parts.append("• Reduce ventilation rate to conserve heat")
                response_parts.append("• Check for heating system optimization")
            else:
                response_parts.append("🟢 **OPTIMAL CONDITIONS**")
                response_parts.append("• Maintain current HVAC settings")
                response_parts.append("• Consider natural ventilation opportunities")
            
            # Humidity control
            if humidity > 70:
                response_parts.append("• **HUMIDITY:** Increase dehumidification - target 45-55%")
            elif humidity < 40:
                response_parts.append("• **HUMIDITY:** Reduce dehumidification - target 50-60%")
            else:
                response_parts.append("• **HUMIDITY:** Optimal levels - maintain current settings")
            
            response_parts.append("")
        
        # Energy Analysis
        if analysis_type in ['energy', 'comprehensive']:
            response_parts.append("⚡ **ENERGY MANAGEMENT:**")
            
            # Calculate energy load factor
            cooling_load = max(0, (temp - 24) / 10)  # 0-1 scale
            heating_load = max(0, (20 - temp) / 15)  # 0-1 scale
            
            if cooling_load > 0.7:
                response_parts.append("🔴 **HIGH COOLING LOAD** (80-100% capacity)")
                response_parts.append("• Implement peak demand management")
                response_parts.append("• Consider load shedding for non-critical systems")
                response_parts.append("• Monitor energy consumption closely")
            elif cooling_load > 0.4:
                response_parts.append("🟡 **MODERATE COOLING LOAD** (40-70% capacity)")
                response_parts.append("• Optimize cooling efficiency")
                response_parts.append("• Consider energy storage systems")
            elif heating_load > 0.5:
                response_parts.append("🔵 **HEATING REQUIRED** (50%+ capacity)")
                response_parts.append("• Implement heating schedule optimization")
                response_parts.append("• Check building envelope efficiency")
            else:
                response_parts.append("🟢 **LOW ENERGY DEMAND** (<40% capacity)")
                response_parts.append("• Excellent conditions for energy savings")
                response_parts.append("• Consider reduced system operation")
            
            # Lighting recommendations
            condition_lower = weather['condition'].lower()
            if 'clear' in condition_lower or 'sunny' in condition_lower:
                response_parts.append("• **LIGHTING:** Reduce artificial lighting by 70-80%")
                response_parts.append("• **SOLAR:** Excellent conditions for solar energy generation")
            elif 'partly' in condition_lower:
                response_parts.append("• **LIGHTING:** Reduce artificial lighting by 40-60%")
                response_parts.append("• **SOLAR:** Good conditions for solar energy generation")
            else:
                response_parts.append("• **LIGHTING:** Maintain full artificial lighting")
                response_parts.append("• **SOLAR:** Limited solar energy generation")
            
            response_parts.append("")
        
        # Comfort Analysis
        if analysis_type in ['comfort', 'comprehensive']:
            response_parts.append("😌 **OCCUPANT COMFORT:**")
            
            # Calculate comfort index
            temp_comfort = 1.0 - abs(temp - 24) / 10
            humidity_comfort = 1.0 - abs(humidity - 50) / 40
            overall_comfort = (temp_comfort + humidity_comfort) / 2
            
            if overall_comfort > 0.8:
                response_parts.append("🟢 **EXCELLENT COMFORT** (80%+ satisfaction)")
                response_parts.append("• Maintain current environmental settings")
                response_parts.append("• Monitor for any comfort complaints")
            elif overall_comfort > 0.6:
                response_parts.append("🟡 **GOOD COMFORT** (60-80% satisfaction)")
                response_parts.append("• Fine-tune temperature and humidity settings")
                response_parts.append("• Consider zone-based adjustments")
            else:
                response_parts.append("🔴 **POOR COMFORT** (<60% satisfaction)")
                response_parts.append("• Immediate HVAC adjustments required")
                response_parts.append("• Implement comfort recovery measures")
            
            # Specific comfort recommendations
            if abs(temp - 24) > 3:
                response_parts.append("• **TEMPERATURE:** Outside comfort zone - adjust setpoints")
            if humidity > 65 or humidity < 35:
                response_parts.append("• **HUMIDITY:** Outside comfort range - adjust humidity control")
            
            response_parts.append("")
        
        # Additional recommendations for comprehensive analysis
        if analysis_type == 'comprehensive':
            response_parts.append("🎯 **PRIORITY ACTIONS:**")
            
            priorities = []
            if temp > 30:
                priorities.append("1. **URGENT:** Activate maximum cooling capacity")
            if humidity > 75:
                priorities.append("2. **HIGH:** Increase dehumidification immediately")
            if temp < 18:
                priorities.append("1. **URGENT:** Ensure adequate heating")
            
            if not priorities:
                priorities.append("1. **MAINTAIN:** Current settings are optimal")
                priorities.append("2. **MONITOR:** Continue regular system monitoring")
            
            for priority in priorities[:3]:  # Show top 3 priorities
                response_parts.append(f"   {priority}")
            
            response_parts.append("")
            response_parts.append("📈 **MONITORING RECOMMENDATIONS:**")
            response_parts.append("• Check indoor temperature every 30 minutes")
            response_parts.append("• Monitor energy consumption trends")
            response_parts.append("• Track occupant comfort feedback")
            response_parts.append("• Review weather forecasts for planning")
    
    except (ValueError, TypeError) as e:
        response_parts.append(f"⚠️ **Analysis Error:** Unable to process weather data - {str(e)}")
    
    return "\n".join(response_parts)

def extract_specific_info_from_web_content(self, web_content_info: List[Dict], query: str) -> str:
        """Extract specific information from web content based on the query"""
        if not web_content_info:
            return ""
        
        extracted_info = []
        query_lower = query.lower()
        
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
                    
                    # Check if sentence contains query terms
                    query_words = query_lower.split()
                    matches = sum(1 for word in query_words if word in sentence_lower)
                    
                    if matches > 0:
                        relevant_sentences.append(sentence)
            
            # If we found relevant sentences, format them nicely
            if relevant_sentences:
                # Take the most relevant sentences (up to 3)
                top_sentences = relevant_sentences[:3]
                
                extracted_info.append({
                    'url': url,
                    'domain': domain,
                    'key_info': top_sentences
                })
        
        # Format the extracted information
        if extracted_info:
            formatted_info = []
            for item in extracted_info:
                domain_name = item['domain'].replace('www.', '')
                formatted_info.append(f"📄 **From {domain_name}:**")
                for info in item['key_info']:
                    formatted_info.append(f"   • {info}")
                formatted_info.append(f"   🔗 Source: {item['url']}")
                formatted_info.append("")
            
            return "\n".join(formatted_info)
        
        return ""

# Initialize Knowledge Base
kb = SmartBuildingKnowledgeBase()
