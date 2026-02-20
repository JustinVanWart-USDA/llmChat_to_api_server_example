"""
Test client for GovChat API Server
Run this to test the server locally
"""
import requests
import json
import time
from typing import List, Dict


class GovChatAPIClient:
    """Client to test the GovChat API Server"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.conversation_id = None
    
    def health_check(self) -> Dict:
        """Check if server is running"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def list_models(self) -> Dict:
        """List available models"""
        response = requests.get(f"{self.base_url}/v1/models")
        response.raise_for_status()
        return response.json()
    
    def chat(self, message: str, system_prompt: str = None) -> str:
        """
        Send a chat message and get a response
        
        Args:
            message: User message
            system_prompt: Optional system prompt
        
        Returns:
            Assistant response text
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": message
        })
        
        payload = {
            "model": "gpt-4",
            "messages": messages,
            "temperature": 0.7
        }
        
        print(f"\n📤 Sending request to {self.base_url}/v1/chat/completions")
        print(f"Message: {message}")
        
        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload,
            timeout=300  # 5 minute timeout
        )
        
        response.raise_for_status()
        data = response.json()
        
        # Extract response
        assistant_message = data["choices"][0]["message"]["content"]
        
        # Store conversation ID for later use
        if not self.conversation_id:
            self.conversation_id = data.get("id")
        
        return assistant_message
    
    def get_conversation_history(self, conversation_id: str = None) -> List[Dict]:
        """Get conversation history"""
        conv_id = conversation_id or self.conversation_id
        if not conv_id:
            raise ValueError("No conversation ID available")
        
        response = requests.get(
            f"{self.base_url}/conversations/{conv_id}"
        )
        response.raise_for_status()
        return response.json()


def main():
    """Test the server"""
    client = GovChatAPIClient()
    
    print("=" * 60)
    print("🚀 GovChat API Server Test")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n[1/4] Testing health check...")
    try:
        health = client.health_check()
        print(f"✅ Server is running!")
        print(f"   Status: {health['status']}")
        print(f"   Mode: {health['mode']}")
        print(f"   Active conversations: {health['active_conversations']}")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running! Start it with: python run.py")
        return
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test 2: List models
    print("\n[2/4] Listing available models...")
    try:
        models = client.list_models()
        print(f"✅ Available models:")
        for model in models["data"]:
            print(f"   - {model['id']}")
    except Exception as e:
        print(f"❌ Failed to list models: {e}")
        return
    
    # Test 3: Send a simple message
    print("\n[3/4] Sending a test message...")
    try:
        print("⏳ Waiting for response (this may take a minute)...")
        response = client.chat("Hello! How are you today?")
        print(f"✅ Response received:")
        print(f"   {response}")
    except requests.exceptions.Timeout:
        print("⏱️  Request timed out - the GovChat website may be slow")
    except Exception as e:
        print(f"❌ Request failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 4: Multi-turn conversation
    print("\n[4/4] Testing multi-turn conversation...")
    try:
        print("⏳ Sending follow-up message...")
        response2 = client.chat("Can you tell me a joke?")
        print(f"✅ Follow-up response received:")
        print(f"   {response2}")
    except Exception as e:
        print(f"⚠️  Follow-up failed (might be normal): {e}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
