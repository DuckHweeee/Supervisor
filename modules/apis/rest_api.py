"""
API Module for Smart Building AI Integration

This module provides REST API endpoints and utilities for integrating
the Smart Building AI into external systems, websites, and applications.
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
import asyncio
import json
import traceback
from datetime import datetime

# Import core modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.ai_agent import AsyncSmartBuildingAI
    from core.knowledge_base import KnowledgeBaseManager
    from integrations.weather import WeatherIntegration
except ImportError:
    # Fallback for direct execution
    from modules.core.ai_agent import AsyncSmartBuildingAI
    from modules.core.knowledge_base import KnowledgeBaseManager
    from modules.integrations.weather import WeatherIntegration


# Pydantic models for API requests/responses
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message to send to the AI")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation tracking")


class ChatResponse(BaseModel):
    response: str = Field(..., description="AI response")
    session_id: str = Field(..., description="Session ID")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Response metadata")


class DocumentUploadRequest(BaseModel):
    content: str = Field(..., description="Document content as text")
    filename: str = Field(..., description="Document filename")
    document_type: Optional[str] = Field(default="text", description="Document type")


class DocumentUploadResponse(BaseModel):
    success: bool = Field(..., description="Upload success status")
    message: str = Field(..., description="Success or error message")
    document_id: Optional[str] = Field(default=None, description="Document ID if successful")


class WeatherRequest(BaseModel):
    location: str = Field(..., description="Location for weather data")
    include_forecast: bool = Field(default=False, description="Include weather forecast")
    include_recommendations: bool = Field(default=True, description="Include building recommendations")


class WeatherResponse(BaseModel):
    weather_data: Dict[str, Any] = Field(..., description="Raw weather data")
    formatted_response: str = Field(..., description="Formatted weather response")


class HealthResponse(BaseModel):
    status: str = Field(..., description="API status")
    version: str = Field(..., description="API version")
    modules: Dict[str, bool] = Field(..., description="Module availability status")
    timestamp: str = Field(..., description="Current timestamp")


class SmartBuildingAPI:
    """
    FastAPI application for Smart Building AI integration
    """
    
    def __init__(self, 
                 knowledge_base_path: str = "knowledge_base",
                 weather_server_url: str = "http://localhost:8001"):
        """
        Initialize the API application
        
        Args:
            knowledge_base_path: Path to the knowledge base directory
            weather_server_url: URL of the weather API server
        """
        self.app = FastAPI(
            title="Smart Building AI API",
            description="REST API for Smart Building AI integration",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize components
        self.ai_agent = None
        self.knowledge_base = None
        self.weather_integration = None
        self.sessions = {}  # Store conversation sessions
        
        # Store configuration
        self.knowledge_base_path = knowledge_base_path
        self.weather_server_url = weather_server_url
        
        # Setup routes
        self._setup_routes()
    
    async def get_ai_agent(self) -> AsyncSmartBuildingAI:
        """Get or create AI agent instance"""
        if self.ai_agent is None:
            try:
                self.ai_agent = AsyncSmartBuildingAI()
                await self.ai_agent.initialize()
            except Exception as e:
                print(f"Error initializing AI agent: {e}")
                raise HTTPException(status_code=500, detail="AI agent initialization failed")
        return self.ai_agent
    
    async def get_knowledge_base(self) -> KnowledgeBaseManager:
        """Get or create knowledge base instance"""
        if self.knowledge_base is None:
            try:
                self.knowledge_base = KnowledgeBaseManager(self.knowledge_base_path)
            except Exception as e:
                print(f"Error initializing knowledge base: {e}")
                raise HTTPException(status_code=500, detail="Knowledge base initialization failed")
        return self.knowledge_base
    
    async def get_weather_integration(self) -> WeatherIntegration:
        """Get or create weather integration instance"""
        if self.weather_integration is None:
            try:
                self.weather_integration = WeatherIntegration(self.weather_server_url)
            except Exception as e:
                print(f"Error initializing weather integration: {e}")
                # Continue without weather integration
                self.weather_integration = WeatherIntegration()
        return self.weather_integration
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def root():
            """Root endpoint with API information"""
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Smart Building AI API</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 800px; }
                    .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
                    .method { color: #2e7d32; font-weight: bold; }
                    code { background: #e8e8e8; padding: 2px 5px; border-radius: 3px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🏢 Smart Building AI API</h1>
                    <p>REST API for integrating Smart Building AI into your applications.</p>
                    
                    <h2>📋 Available Endpoints:</h2>
                    
                    <div class="endpoint">
                        <span class="method">GET</span> <code>/health</code>
                        <p>Check API health and module status</p>
                    </div>
                    
                    <div class="endpoint">
                        <span class="method">POST</span> <code>/chat</code>
                        <p>Send messages to the AI agent</p>
                    </div>
                    
                    <div class="endpoint">
                        <span class="method">POST</span> <code>/upload-document</code>
                        <p>Upload documents to the knowledge base</p>
                    </div>
                    
                    <div class="endpoint">
                        <span class="method">POST</span> <code>/weather</code>
                        <p>Get weather data and building recommendations</p>
                    </div>
                    
                    <div class="endpoint">
                        <span class="method">GET</span> <code>/sessions</code>
                        <p>List active conversation sessions</p>
                    </div>
                    
                    <h2>📖 Documentation:</h2>
                    <p>
                        • <a href="/docs">Interactive API Documentation (Swagger)</a><br>
                        • <a href="/redoc">Alternative Documentation (ReDoc)</a>
                    </p>
                    
                    <h2>🔗 Integration Examples:</h2>
                    <pre><code>// JavaScript Example
fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: 'What is the optimal temperature for energy efficiency?',
        session_id: 'my-session'
    })
})
.then(response => response.json())
.then(data => console.log(data.response));</code></pre>
                </div>
            </body>
            </html>
            """
        
        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint"""
            try:
                # Check module availability
                modules = {
                    "ai_agent": self.ai_agent is not None,
                    "knowledge_base": self.knowledge_base is not None,
                    "weather_integration": self.weather_integration is not None
                }
                
                return HealthResponse(
                    status="healthy",
                    version="1.0.0",
                    modules=modules,
                    timestamp=datetime.now().isoformat()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/chat", response_model=ChatResponse)
        async def chat_endpoint(request: ChatRequest):
            """Chat with the AI agent"""
            try:
                # Get AI agent
                ai_agent = await self.get_ai_agent()
                
                # Generate session ID if not provided
                session_id = request.session_id or f"session_{datetime.now().timestamp()}"
                
                # Get or create session history
                if session_id not in self.sessions:
                    self.sessions[session_id] = []
                
                # Add user message to history
                self.sessions[session_id].append({
                    "role": "user",
                    "content": request.message,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Get AI response
                response = await ai_agent.generate_response(
                    request.message,
                    context=request.context
                )
                
                # Add AI response to history
                self.sessions[session_id].append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Limit session history to last 20 messages
                if len(self.sessions[session_id]) > 20:
                    self.sessions[session_id] = self.sessions[session_id][-20:]
                
                return ChatResponse(
                    response=response,
                    session_id=session_id,
                    metadata={
                        "message_count": len(self.sessions[session_id]),
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
        
        @self.app.post("/upload-document", response_model=DocumentUploadResponse)
        async def upload_document(request: DocumentUploadRequest):
            """Upload a document to the knowledge base"""
            try:
                # Get knowledge base
                kb = await self.get_knowledge_base()
                
                # Add document
                success = kb.add_document(
                    content=request.content,
                    metadata={
                        "filename": request.filename,
                        "document_type": request.document_type,
                        "upload_timestamp": datetime.now().isoformat()
                    }
                )
                
                if success:
                    return DocumentUploadResponse(
                        success=True,
                        message=f"Document '{request.filename}' uploaded successfully",
                        document_id=request.filename
                    )
                else:
                    return DocumentUploadResponse(
                        success=False,
                        message="Failed to upload document"
                    )
                    
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")
        
        @self.app.post("/weather", response_model=WeatherResponse)
        async def weather_endpoint(request: WeatherRequest):
            """Get weather data and building recommendations"""
            try:
                # Get weather integration
                weather = await self.get_weather_integration()
                
                # Get weather data
                weather_data = await weather.get_weather_data(
                    request.location,
                    request.include_forecast
                )
                
                # Format response
                formatted_response = weather.format_weather_response(
                    weather_data,
                    request.include_recommendations
                )
                
                return WeatherResponse(
                    weather_data=weather_data,
                    formatted_response=formatted_response
                )
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Weather error: {str(e)}")
        
        @self.app.get("/sessions")
        async def get_sessions():
            """Get active conversation sessions"""
            try:
                session_info = {}
                for session_id, messages in self.sessions.items():
                    if messages:
                        session_info[session_id] = {
                            "message_count": len(messages),
                            "last_activity": messages[-1]["timestamp"],
                            "created": messages[0]["timestamp"]
                        }
                
                return {
                    "active_sessions": len(session_info),
                    "sessions": session_info
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Sessions error: {str(e)}")
        
        @self.app.delete("/sessions/{session_id}")
        async def delete_session(session_id: str):
            """Delete a conversation session"""
            try:
                if session_id in self.sessions:
                    del self.sessions[session_id]
                    return {"message": f"Session {session_id} deleted successfully"}
                else:
                    raise HTTPException(status_code=404, detail="Session not found")
                    
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Delete error: {str(e)}")
        
        @self.app.get("/knowledge-base/stats")
        async def knowledge_base_stats():
            """Get knowledge base statistics"""
            try:
                kb = await self.get_knowledge_base()
                stats = kb.get_stats()
                return stats
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Knowledge base error: {str(e)}")


def create_api(knowledge_base_path: str = "knowledge_base",
               weather_server_url: str = "http://localhost:8001") -> FastAPI:
    """
    Factory function to create the API application
    
    Args:
        knowledge_base_path: Path to the knowledge base directory
        weather_server_url: URL of the weather API server
        
    Returns:
        FastAPI application instance
    """
    api = SmartBuildingAPI(knowledge_base_path, weather_server_url)
    return api.app


# For direct execution
if __name__ == "__main__":
    import uvicorn
    
    # Create the API
    app = create_api()
    
    # Run the server
    print("🚀 Starting Smart Building AI API server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔗 API Root: http://localhost:8000/")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )
