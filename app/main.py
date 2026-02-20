"""Main FastAPI server - OpenAI-compatible interface for chat websites"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uuid
import time
import logging
from typing import Dict
import os
from dotenv import load_dotenv

load_dotenv()

from app.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChoice,
    ChatMessage,
    ChatRole,
    UsageInfo,
    ErrorResponse
)
from app.clients.chat_http_client import ChatHTTPClient
from app.clients.chat_selenium_client import ChatSeleniumClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state
conversation_clients: Dict[str, object] = {}
USE_SELENIUM = os.getenv("USE_SELENIUM", "false").lower() == "true"
CHAT_WEBSITE_URL = os.getenv("CHAT_WEBSITE_URL", "https://example-chat.com")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Chat Website API Server starting...")
    logger.info(f"Target: {CHAT_WEBSITE_URL}")
    logger.info(f"Mode: {'Selenium (browser automation)' if USE_SELENIUM else 'HTTP (reverse-engineered API)'}")
    yield
    logger.info("🛑 Shutting down server...")
    # Close all clients
    for client in conversation_clients.values():
        try:
            if hasattr(client, 'close'):
                client.close()
        except Exception as e:
            logger.error(f"Error closing client: {e}")


app = FastAPI(
    title="Chat Website API Wrapper",
    description="OpenAI-compatible wrapper for chat websites",
    version="1.0.0",
    lifespan=lifespan
)


def _get_or_create_client(conversation_id: str = None):
    """Get existing client or create new one"""
    if conversation_id and conversation_id in conversation_clients:
        return conversation_clients[conversation_id]
    
    if USE_SELENIUM:
        client = ChatSeleniumClient(headless=True)
    else:
        client = ChatHTTPClient(conversation_id=conversation_id)
    
    if conversation_id:
        conversation_clients[conversation_id] = client
    
    return client


def _count_tokens(text: str) -> int:
    """Rough token count estimation (4 chars ≈ 1 token)"""
    return len(text) // 4


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Chat Website API Wrapper is running",
        "target": CHAT_WEBSITE_URL,
        "mode": "selenium" if USE_SELENIUM else "http",
        "active_conversations": len(conversation_clients)
    }


@app.get("/v1/models", tags=["Models"])
async def list_models():
    """List available models (OpenAI compatibility)"""
    return {
        "object": "list",
        "data": [
            {
                "id": "gpt-4",
                "object": "model",
                "created": 1687882411,
                "owned_by": "chat-wrapper",
                "permission": [
                    {
                        "id": "modelperm-123",
                        "object": "model_permission",
                        "created": 1687882411,
                        "allow_create_engine": False,
                        "allow_sampling": True,
                        "allow_logprobs": False,
                        "allow_search_indices": False,
                        "allow_view": True,
                        "allow_fine_tuning": False,
                        "organization": "*",
                        "group_id": None,
                        "is_blocking": False
                    }
                ],
                "root": "gpt-4",
                "parent": None
            }
        ]
    }


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse, tags=["Chat"])
async def chat_completions(request: ChatCompletionRequest):
    """
    Create a chat completion (OpenAI-compatible endpoint)
    
    This endpoint mimics the OpenAI API but routes requests to GovChat.
    """
    try:
        # Generate or extract conversation ID from system prompt if present
        conversation_id = str(uuid.uuid4())
        for msg in request.messages:
            if msg.role == ChatRole.SYSTEM and "conversation_id:" in msg.content:
                # Allow specifying conversation_id in system prompt
                try:
                    conversation_id = msg.content.split("conversation_id:")[-1].strip().split()[0]
                except:
                    pass
        
        logger.info(f"📨 Chat request - Conversation: {conversation_id}, Model: {request.model}")
        
        # Get or create client
        client = _get_or_create_client(conversation_id)
        
        # Extract user message (last user message in the request)
        user_message = None
        for msg in reversed(request.messages):
            if msg.role == ChatRole.USER:
                user_message = msg.content
                break
        
        if not user_message:
            raise HTTPException(
                status_code=400,
                detail="No user message found in request"
            )
        
        # Send message to chat website
        logger.info(f"📤 Sending message: {user_message[:100]}...")
        start_time = time.time()
        
        response = client.send_message(user_message)
        
        elapsed = time.time() - start_time
        logger.info(f"✅ Received response in {elapsed:.2f}s")
        
        # Create OpenAI-compatible response
        prompt_tokens = _count_tokens(user_message)
        completion_tokens = _count_tokens(response["content"])
        
        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:12]}",
            created=int(time.time()),
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(
                        role=ChatRole.ASSISTANT,
                        content=response["content"]
                    ),
                    finish_reason="stop"
                )
            ],
            usage=UsageInfo(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens
            )
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


@app.get("/conversations/{conversation_id}", tags=["Conversations"])
async def get_conversation_history(conversation_id: str):
    """Get the conversation history"""
    if conversation_id not in conversation_clients:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation {conversation_id} not found"
        )
    
    client = conversation_clients[conversation_id]
    history = client.get_conversation_history()
    
    return {
        "conversation_id": conversation_id,
        "messages": history
    }


@app.delete("/conversations/{conversation_id}", tags=["Conversations"])
async def delete_conversation(conversation_id: str):
    """Delete a conversation and close its client"""
    if conversation_id not in conversation_clients:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation {conversation_id} not found"
        )
    
    client = conversation_clients[conversation_id]
    try:
        client.close()
    except Exception as e:
        logger.warning(f"Error closing client: {e}")
    
    del conversation_clients[conversation_id]
    
    return {
        "status": "deleted",
        "conversation_id": conversation_id
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "active_conversations": len(conversation_clients),
        "mode": "selenium" if USE_SELENIUM else "http"
    }


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": str(exc),
                "type": "internal_server_error",
                "code": "internal_error"
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
