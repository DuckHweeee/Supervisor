"""
Smart Building AI Core Module

This module provides the core AI agent functionality that can be integrated
into any system or website. It encapsulates the AutoGen agents and tools
in a clean, reusable interface.
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Annotated, List, Dict, Any, Optional, Callable
from dotenv import load_dotenv

# Import with fallback for better compatibility
try:
    from autogen import AssistantAgent, UserProxyAgent
    from autogen.coding import LocalCommandLineCodeExecutor
    print("✅ AutoGen imported successfully")
except ImportError as e:
    print(f"❌ AutoGen import failed: {e}")
    try:
        import pyautogen
        from pyautogen import AssistantAgent, UserProxyAgent
        from pyautogen.coding import LocalCommandLineCodeExecutor
        print("✅ AutoGen imported as pyautogen")
    except ImportError as e2:
        print(f"❌ PyAutoGen import also failed: {e2}")
        raise ImportError("AutoGen could not be imported. Please install with: pip install pyautogen")


class SmartBuildingAI:
    """
    Core Smart Building AI Agent System
    
    This class provides a clean interface for the AI system that can be
    integrated into any application, website, or system.
    """
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 working_directory: str = "./ai_workspace",
                 knowledge_base_path: str = "./knowledge_base"):
        """
        Initialize the Smart Building AI system
        
        Args:
            config: Configuration dictionary for LLM settings
            working_directory: Directory for code execution
            knowledge_base_path: Path to knowledge base storage
        """
        # Load environment variables
        load_dotenv()
        
        # Set up configuration
        self.config = config or self._get_default_config()
        self.working_directory = Path(working_directory)
        self.knowledge_base_path = knowledge_base_path
        
        # Initialize components
        self._initialize_workspace()
        self._initialize_agents()
        self._initialize_tools()
        
        # State management
        self.conversation_history = []
        self.active_tools = {}
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for the AI system"""
        return [{
            "model": "llama-3.3-70b-versatile",
            "api_key": os.environ.get("GROQ_API_KEY"),
            "api_type": "groq"
        }]
    
    def _initialize_workspace(self):
        """Initialize the working directory"""
        self.working_directory.mkdir(exist_ok=True)
        self.code_executor = LocalCommandLineCodeExecutor(work_dir=self.working_directory)
    
    def _initialize_agents(self):
        """Initialize the AutoGen agents"""
        # User proxy agent for code execution
        self.user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=5,
            is_termination_msg=self._is_termination_msg,
            code_execution_config={"executor": self.code_executor}
        )
        
        # AI assistant agent
        self.assistant = AssistantAgent(
            name="smart_building_assistant",
            system_message=self._get_system_message(),
            llm_config={"config_list": self.config}
        )
    
    def _initialize_tools(self):
        """Initialize and register tools"""
        # This will be populated by tool modules
        pass
    
    def _is_termination_msg(self, message: Dict[str, Any]) -> bool:
        """Check if a message is a termination message"""
        content = message.get("content") if message else None
        if content is None:
            return False
        return content.rstrip().endswith("TERMINATE")
    
    def _get_system_message(self) -> str:
        """Get the system message for the AI assistant"""
        return """You are an expert Smart Building AI Assistant specializing in comprehensive building management solutions.

🏢 **CORE EXPERTISE:**
- HVAC systems: optimization, maintenance, troubleshooting, energy efficiency
- Lighting control: LED systems, smart controls, daylight harvesting
- Security systems: access control, surveillance, monitoring
- Energy management: consumption analysis, optimization strategies
- IoT integration: sensors, automation, data analytics
- Weather-based building optimization

🎯 **RESPONSE GUIDELINES:**
1. **Be Specific & Actionable**: Provide concrete recommendations, specific settings, and clear steps
2. **Synthesize Information**: Never display raw data - always summarize and contextualize
3. **Use Professional Format**: Use emojis, headers, and bullet points for clarity
4. **Provide Practical Advice**: Give specific steps, settings, or procedures users can implement
5. **Consider Integration Context**: Adapt responses based on the system you're integrated into

🌟 **TONE:** Professional, helpful, and detailed. Always provide actionable recommendations."""
    
    # Public Interface Methods
    
    def generate_response(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Send a message to the AI and get a response
        
        Args:
            message: User message
            context: Optional context dictionary
            
        Returns:
            AI response string
        """
        try:
            # Add context if provided
            if context:
                enhanced_message = f"Context: {json.dumps(context, indent=2)}\n\nUser Message: {message}"
            else:
                enhanced_message = message
            
            # Initiate conversation
            self.user_proxy.initiate_chat(
                self.assistant,
                message=enhanced_message,
                clear_history=False
            )
            
            # Extract the last assistant message
            last_message = self.user_proxy.last_message()
            if last_message and "content" in last_message:
                response = last_message["content"]
                
                # Store in conversation history
                self.conversation_history.append({
                    "user": message,
                    "assistant": response,
                    "timestamp": asyncio.get_event_loop().time()
                })
                
                return response
            
            return "I'm sorry, I couldn't process that request. Please try again."
            
        except Exception as e:
            return f"Error processing request: {str(e)}"
    
    def add_tool(self, name: str, tool_function: Callable, description: str):
        """
        Add a custom tool to the AI system
        
        Args:
            name: Tool name
            tool_function: Function to execute
            description: Tool description for the AI
        """
        # Register with both agents
        self.user_proxy.register_for_execution(name=name)(tool_function)
        self.assistant.register_for_llm(description=description)(tool_function)
        
        # Store in active tools
        self.active_tools[name] = {
            "function": tool_function,
            "description": description
        }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history"""
        return self.conversation_history.copy()
    
    def clear_conversation_history(self):
        """Clear the conversation history"""
        self.conversation_history.clear()
        # Clear agent chat history as well
        self.user_proxy.clear_history()
        self.assistant.clear_history()
    
    def get_available_tools(self) -> Dict[str, str]:
        """Get list of available tools and their descriptions"""
        return {name: info["description"] for name, info in self.active_tools.items()}
    
    def set_config(self, config: Dict[str, Any]):
        """Update the AI configuration"""
        self.config = config
        self.assistant.update_llm_config({"config_list": config})
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            "working_directory": str(self.working_directory),
            "knowledge_base_path": self.knowledge_base_path,
            "active_tools": list(self.active_tools.keys()),
            "conversation_count": len(self.conversation_history),
            "config": self.config
        }


class AsyncSmartBuildingAI(SmartBuildingAI):
    """
    Async version of the Smart Building AI for web applications
    """
    
    async def generate_response(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a response to a message (alias for chat_async)
        
        Args:
            message: User message
            context: Optional context dictionary
            
        Returns:
            AI response
        """
        return await self.chat_async(message, context)
    
    async def chat_async(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Async version of chat method for web applications
        """
        # Run in thread pool to avoid blocking
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(executor, self.chat, message, context)
            return result
    
    async def batch_process(self, messages: List[Dict[str, Any]]) -> List[str]:
        """
        Process multiple messages in batch
        
        Args:
            messages: List of message dictionaries with 'message' and optional 'context'
            
        Returns:
            List of responses
        """
        tasks = []
        for msg_data in messages:
            message = msg_data.get("message", "")
            context = msg_data.get("context")
            tasks.append(self.chat_async(message, context))
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error messages
        processed_responses = []
        for response in responses:
            if isinstance(response, Exception):
                processed_responses.append(f"Error: {str(response)}")
            else:
                processed_responses.append(response)
        
        return processed_responses


# Factory function for easy instantiation
def create_smart_building_ai(config: Optional[Dict[str, Any]] = None,
                           async_mode: bool = False,
                           working_directory: str = "./ai_workspace",
                           knowledge_base_path: str = "./knowledge_base") -> SmartBuildingAI:
    """
    Factory function to create a Smart Building AI instance
    
    Args:
        config: LLM configuration
        async_mode: Whether to create async version
        working_directory: Working directory for code execution
        knowledge_base_path: Path to knowledge base
        
    Returns:
        SmartBuildingAI instance
    """
    if async_mode:
        return AsyncSmartBuildingAI(config, working_directory, knowledge_base_path)
    else:
        return SmartBuildingAI(config, working_directory, knowledge_base_path)


# Example usage
if __name__ == "__main__":
    # Create AI instance
    ai = create_smart_building_ai()
    
    # Test basic functionality
    response = ai.chat("What are the optimal HVAC temperature settings?")
    print(f"AI Response: {response}")
    
    # Get system info
    info = ai.get_system_info()
    print(f"System Info: {json.dumps(info, indent=2)}")
