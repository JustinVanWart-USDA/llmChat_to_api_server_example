"""Data models for OpenAI-compatible API"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ChatRole(str, Enum):
    """Chat message roles"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    """Single chat message"""
    role: ChatRole
    content: str


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request"""
    model: Any = Field(default="gpt-4", description="Model identifier (string or object)")
    messages: List[ChatMessage] = Field(..., description="List of messages")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None)
    top_p: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
    stream: Optional[bool] = Field(default=False)
    prompt: Optional[str] = Field(default=None, description="System prompt")
    key: Optional[str] = Field(default="", description="API key")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model": "gpt-4",
                "messages": [
                    {"role": "user", "content": "Hello, how are you?"}
                ],
                "temperature": 0.7
            }
        }


class ChatCompletionChoice(BaseModel):
    """Single completion choice"""
    index: int
    message: ChatMessage
    finish_reason: str = "stop"


class UsageInfo(BaseModel):
    """Token usage information"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    """OpenAI-compatible chat completion response"""
    id: str
    object: str = "chat.completion"
    created: int
    model: Any  # Accept both string (OpenAI format) and object format
    choices: List[ChatCompletionChoice]
    usage: UsageInfo
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "chatcmpl-123",
                "object": "chat.completion",
                "created": 1677649420,
                "model": "gpt-4",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello! I'm doing well, thank you for asking."
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 10,
                    "total_tokens": 20
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response"""
    error: Dict[str, Any]
