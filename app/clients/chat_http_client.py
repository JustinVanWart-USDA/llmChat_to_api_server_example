"""HTTP-based client for chat websites (reverse-engineered API)"""
import requests
import json
import time
import uuid
import os
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatHTTPClient:
    """
    Generic HTTP client for communicating with chat websites.
    This client reverse-engineers the API calls the website makes.
    """
    
    def __init__(self, conversation_id: Optional[str] = None, base_url: Optional[str] = None, api_endpoint: Optional[str] = None):
        """
        Initialize the chat HTTP client
        
        Args:
            conversation_id: Optional existing conversation ID to continue
            base_url: Base URL of the chat website (from .env if not provided)
            api_endpoint: Specific API endpoint path (from .env if not provided)
        """
        self.base_url = base_url or os.getenv("CHAT_WEBSITE_URL", "https://example-chat.com")
        self.api_endpoint = api_endpoint or os.getenv("CHAT_API_ENDPOINT", "")
        self.session = requests.Session()
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.messages_history: List[Dict[str, str]] = []
        logger.info(f"Initialized HTTP client for: {self.base_url}")
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize session with proper headers"""
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
    
    def send_message(self, user_message: str, timeout: int = 120) -> Dict[str, str]:
        """
        Send a message to the chat website and get a response
        
        Args:
            user_message: The user's message
            timeout: Timeout in seconds
        
        Returns:
            Dictionary with 'role' and 'content' keys
        """
        try:
            logger.info(f"Sending message: {user_message[:100]}...")
            
            # Add message to history
            self.messages_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Prepare the API request payload
            payload = self._prepare_messages_payload()
            
            # Make the request
            response = self._make_api_request(payload, timeout)
            
            if response:
                assistant_message = self._extract_response(response)
                self.messages_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                
                logger.info(f"Received response: {assistant_message[:100]}...")
                return {
                    "role": "assistant",
                    "content": assistant_message
                }
            else:
                raise Exception("No response from chat API")
        
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise
    
    def _prepare_messages_payload(self) -> Dict:
        """Prepare request in the format expected by chat API"""
        # Build messages array - only include user/assistant messages, not system
        messages = [
            {
                "role": msg["role"],
                "content": msg["content"]
            }
            for msg in self.messages_history
        ]
        
        # Extract system prompt if available
        system_prompt = "You are a helpful AI assistant. Follow the user's instructions carefully. Respond using markdown."
        
        # Generic payload format (adjust per target site)
        return {
            "model": {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5",
                "maxLength": 12000,
                "tokenLimit": 4000
            },
            "messages": messages,
            "prompt": system_prompt,
            "temperature": 1,
            "key": ""
        }
    
    def _make_api_request(self, payload: Dict, timeout: int) -> Optional[Dict]:
        """
        Make the actual API request to the chat website
        """
        # If specific endpoint is configured, use it
        if self.api_endpoint:
            endpoints_to_try = [f"{self.base_url}{self.api_endpoint}"]
        else:
            # Common endpoint patterns to try
            endpoints_to_try = [
                f"{self.base_url}/api/chat",
                f"{self.base_url}/api/chat/completions",
                f"{self.base_url}/api/conversation/{self.conversation_id}",
                f"{self.base_url}/api/messages",
                f"{self.base_url}/v1/chat/completions",
            ]
        
        for endpoint in endpoints_to_try:
            try:
                logger.info(f"Trying endpoint: {endpoint}")
                response = self.session.post(
                    endpoint,
                    json=payload,
                    timeout=timeout
                )
                
                logger.info(f"Response status: {response.status_code}")
                logger.debug(f"Response text: {response.text[:500]}")
                
                if response.status_code == 200:
                    logger.info(f"Success with endpoint: {endpoint}")
                    # Try to parse as JSON
                    try:
                        return response.json()
                    except ValueError:
                        # Response is not JSON, return raw text
                        logger.warning("Response is not JSON, returning as text")
                        return {"message": response.text}
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on {endpoint}")
                continue
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed on {endpoint}: {e}")
                continue
        
        return None
    
    def _extract_response(self, response_data: Dict) -> str:
        """
        Extract the response text from chat website's response format
        Tries multiple common formats
        """
        if isinstance(response_data, dict):
            # Common message format
            if "message" in response_data:
                msg = response_data["message"]
                if isinstance(msg, dict) and "content" in msg:
                    return msg["content"]
                if isinstance(msg, str):
                    return msg
            
            # OpenAI format (fallback)
            if "choices" in response_data:
                return response_data["choices"][0]["message"]["content"]
            
            # Direct content field
            if "content" in response_data:
                return response_data["content"]
            
            # Response field
            if "response" in response_data:
                return response_data["response"]
            
            # Text field
            if "text" in response_data:
                return response_data["text"]
        
        # Fallback to string representation
        return str(response_data)
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the full conversation history"""
        return self.messages_history.copy()
    
    def clear_history(self):
        """Clear the conversation history"""
        self.messages_history = []
        self.conversation_id = str(uuid.uuid4())
    
    def close(self):
        """Close the session"""
        self.session.close()
