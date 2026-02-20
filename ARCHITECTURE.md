# GovChat API Server - Complete Architecture

## System Design

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                        YOUR APPLICATION LAYER                             ║
║                     (CrewAI, LangGraph, Your Code)                        ║
╚════════════════════════════════╦════════════════════════════════════════╝
                                 │
                OpenAI API Format │ (messages, temperature, etc.)
                                 │
                                 ↓
╔═══════════════════════════════════════════════════════════════════════════╗
║                         GOVCHAT API SERVER                                ║
║                      (localhost:8000)                                     ║
║  ┌─────────────────────────────────────────────────────────────────────┐  ║
║  │ FastAPI Application                                                 │  ║
║  │ ────────────────────────────────────────────────────────────────    │  ║
║  │                                                                     │  ║
║  │  /v1/chat/completions     - Main chat endpoint                     │  ║
║  │  /v1/models               - List models                             │  ║
║  │  /conversations/{id}      - Manage conversations                    │  ║
║  │  /health                  - Health checks                           │  ║
║  │  /docs                    - Interactive documentation              │  ║
║  │                                                                     │  ║
║  │  Models:                                                            │  ║
║  │  • ChatCompletionRequest  - Incoming request validation            │  ║
║  │  • ChatCompletionResponse - Outgoing response formatting           │  ║
║  │  • ChatMessage            - Individual messages                    │  ║
║  │                                                                     │  ║
║  └──────────┬────────────────────────────────────────────┬────────────┘  ║
║             │                                            │                ║
║      Mode Selection                          Conversation Management      ║
║             │                                            │                ║
║  ┌──────────↓─────────────┐                   ┌─────────↓──────────────┐ ║
║  │  HTTP or Selenium?     │                   │  Maintain History      │ ║
║  │                        │                   │  Track IDs             │ ║
║  │  USE_SELENIUM env var  │                   │  User/Assistant msgs  │ ║
║  └──────────┬────────────────────────────────┬┘                        │ ║
║             │            │                  │                          │ ║
║    ┌────────↓─┐        ┌─↓──────┐          │                          │ ║
║    │ HTTP     │        │Selenium│          │                          │ ║
║    │ Client   │        │ Client │          │                          │ ║
║    └────────┬──┘       └─┬──────┘          │                          │ ║
║             │            │                  │                          │ ║
╚═════════════┼════════════╪══════════════════╪══════════════════════════╝
              │            │                  │
        HTTP  │            │ Browser          │
       Calls  │            │ Automation       │
              │            │                  │
              │            │     Selenium Chrome Driver
              │            │                  │
              │            ↓                  │
              │     ┌──────────────┐         │
              │     │ Chrome       │         │
              │     │ WebDriver    │         │
              │     │ (headless)   │         │
              │     └──────────────┘         │
              │            │                  │
              │            │ Page Automation  │
              │            │ (click, type)    │
              │            │                  │
              └────────────┼──────────────────┘
                           │
                           ↓
        ╔═══════════════════════════════════════════════════════════════════╗
        ║                   GOVCHAT WEBSITE                                 ║
        ║            https://govchat.ars.usda.gov                          ║
        ║                                                                   ║
        ║  ┌─────────────────────────────────────────────────────────┐   ║
        ║  │ Frontend: React/Next.js Chat Interface                 │   ║
        ║  │                                                         │   ║
        ║  │ Input Box → Send Button → Response Display            │   ║
        ║  └──────────────────┬──────────────────────────────────────┘   ║
        ║                     │                                            ║
        ║                     ↓                                            ║
        ║  ┌─────────────────────────────────────────────────────────┐   ║
        ║  │ API: (reverse-engineered endpoints)                    │   ║
        ║  │                                                         │   ║
        ║  │ POST /api/chat/completions                             │   ║
        ║  │ POST /api/conversation/{id}                            │   ║
        ║  │ POST /api/messages                                     │   ║
        ║  └──────────────────┬──────────────────────────────────────┘   ║
        ║                     │                                            ║
        ║                     ↓                                            ║
        ║  ┌─────────────────────────────────────────────────────────┐   ║
        ║  │ Backend: GPT-4 API Client                              │   ║
        ║  │                                                         │   ║
        ║  │ Processes conversations and generates responses        │   ║
        ║  └─────────────────────────────────────────────────────────┘   ║
        ║                                                                   ║
        ║  ✨ UNLIMITED TOKENS - GPT-4 Responses ✨                       ║
        ╚═══════════════════════════════════════════════════════════════════╝
```

## Data Flow Example

### Request Flow
```
1. USER CODE
   ├─ Creates ChatCompletionRequest
   └─ Sends to http://127.0.0.1:8000/v1/chat/completions

2. FASTAPI SERVER
   ├─ Receives request
   ├─ Validates with Pydantic model
   ├─ Extracts user message
   └─ Routes to client (HTTP or Selenium)

3. HTTP CLIENT
   ├─ Prepares payload
   ├─ Tries endpoints in order
   ├─ Sends to GovChat website
   └─ Extracts response

4. GOVCHAT WEBSITE
   ├─ Receives chat message
   ├─ Calls GPT-4 API
   ├─ Generates response
   └─ Returns to client

5. RESPONSE FLOW
   ├─ HTTP Client parses response
   ├─ FastAPI formats as OpenAI response
   ├─ Returns ChatCompletionResponse
   └─ User code gets response

6. CONVERSATION HISTORY
   ├─ Stored in client
   ├─ Available via /conversations/{id}
   └─ Used for multi-turn conversations
```

## File Structure & Responsibilities

```
govchat_api_server/
│
├── run.py                          # Entry point - starts server
├── run.bat / run.sh               # Platform launchers
├── test_client.py                 # Test harness
├── examples.py                    # CrewAI/LangGraph examples
│
├── app/                           # Application code
│   ├── __init__.py
│   │
│   ├── main.py                    # ⭐ FastAPI server
│   │   ├─ Endpoints
│   │   │  ├─ POST /v1/chat/completions
│   │   │  ├─ GET  /v1/models
│   │   │  ├─ GET  /conversations/{id}
│   │   │  └─ DELETE /conversations/{id}
│   │   ├─ Global State (conversation_clients)
│   │   ├─ Client Management
│   │   └─ Error Handling
│   │
│   ├── models.py                  # ⭐ Data Models
│   │   ├─ ChatMessage
│   │   ├─ ChatCompletionRequest
│   │   ├─ ChatCompletionResponse
│   │   └─ Supporting models
│   │
│   └── clients/                   # ⭐ Communication layer
│       ├── __init__.py
│       │
│       ├── govchat_http_client.py # HTTP Mode (Preferred)
│       │   ├─ _make_api_request()
│       │   ├─ _extract_response()
│       │   ├─ send_message()
│       │   └─ Conversation history
│       │
│       └── govchat_selenium_client.py # Selenium Mode (Fallback)
│           ├─ _setup_driver()
│           ├─ _send_input_message()
│           ├─ _wait_for_response()
│           └─ Selenium interactions
│
├── tests/                         # Test suite (expandable)
│
├── requirements.txt               # Python dependencies
├── .env (optional)               # Environment variables
│
└── Documentation/
    ├── README.md                 # Full documentation
    ├── GETTING_STARTED.md        # Quick start (5 min)
    ├── CONFIG.md                 # Configuration guide
    ├── NETWORK_INSPECTION.md     # How to find endpoints
    ├── BUILD_SUMMARY.md          # This summary
    └── ARCHITECTURE.md           # Architecture docs
```

## Class Hierarchy

```
FastAPI Application (main.py)
  ├─ Route Handlers
  │  ├─ root()
  │  ├─ chat_completions()  ← Main endpoint
  │  ├─ list_models()
  │  ├─ get_conversation_history()
  │  └─ delete_conversation()
  │
  ├─ Helper Functions
  │  ├─ _get_or_create_client()
  │  └─ _count_tokens()
  │
  └─ Client Management
     └─ Stores: Dict[conversation_id, client_object]
        └─ Can be GovChatHTTPClient or GovChatSeleniumClient

GovChatHTTPClient (HTTP Mode)
  ├─ Attributes
  │  ├─ session: requests.Session
  │  ├─ conversation_id: str
  │  └─ messages_history: List[Dict]
  │
  ├─ Public Methods
  │  ├─ send_message(message) → Dict
  │  ├─ get_conversation_history() → List
  │  └─ close()
  │
  └─ Private Methods
     ├─ _initialize_session()
     ├─ _prepare_messages_payload()
     ├─ _make_api_request()
     └─ _extract_response()

GovChatSeleniumClient (Selenium Mode)
  ├─ Attributes
  │  ├─ driver: WebDriver
  │  ├─ messages_history: List[Dict]
  │  └─ headless: bool
  │
  ├─ Public Methods
  │  ├─ send_message(message) → Dict
  │  ├─ get_conversation_history() → List
  │  └─ close()
  │
  └─ Private Methods
     ├─ _setup_driver()
     ├─ _send_input_message()
     ├─ _wait_for_response()
     └─ _is_loading_text()
```

## Request/Response Flow Detailed

### OpenAI Format → GovChat

```
From Client:
{
  "model": "gpt-4",
  "messages": [
    {"role": "user", "content": "Hello"}
  ],
  "temperature": 0.7
}
         ↓
  Validated by Pydantic
         ↓
  FastAPI server extracts:
  - User message: "Hello"
  - Model: "gpt-4"
  - Parameters: temperature, etc.
         ↓
  HTTP Client converts to GovChat format:
  {
    "messages": [
      {
        "id": "uuid",
        "role": "user",
        "content": "Hello",
        "timestamp": "iso-datetime"
      }
    ],
    "conversationId": "uuid",
    "model": "gpt-4"
  }
         ↓
  Sends to GovChat API
         ↓
GovChat Response:
{
  "choices": [{
    "message": {
      "content": "Hello! How can I help?"
    }
  }]
}
         ↓
  Parsed by _extract_response()
         ↓
  Stored in conversation history
         ↓
  Returned as OpenAI format:
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677649420,
  "model": "gpt-4",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Hello! How can I help?"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 1,
    "completion_tokens": 4,
    "total_tokens": 5
  }
}
         ↓
  Returned to client
```

## Conversation State Management

```
Server Startup (global state)
  └─ conversation_clients: Dict[str, client_object]
     └─ Empty initially

First Request with new conversation_id
  ├─ Generate UUID: "conv-abc123"
  ├─ Create GovChatHTTPClient("conv-abc123")
  ├─ Store in conversation_clients["conv-abc123"]
  └─ messages_history: []

Request 1
  ├─ User: "Hello"
  ├─ messages_history.append({"role": "user", "content": "Hello"})
  ├─ Get response: "Hi there!"
  ├─ messages_history.append({"role": "assistant", "content": "Hi there!"})
  └─ messages_history: [user msg, assistant msg]

Request 2 (same conversation)
  ├─ User: "How are you?"
  ├─ Client already exists, reuse it
  ├─ It has full conversation history
  ├─ Send with full history context
  └─ Response includes knowledge of first message

Future Requests
  ├─ GET /conversations/conv-abc123
  │  └─ Returns all messages in history
  │
  └─ DELETE /conversations/conv-abc123
     ├─ Close client
     ├─ Delete from conversation_clients
     └─ conversation_id is now unavailable
```

## Environment Configuration

```
Environment Variables:
├─ USE_SELENIUM (boolean, default: false)
│  └─ true: Use Selenium; false: Use HTTP
│
├─ HOST (string, default: "127.0.0.1")
│  └─ Server listening address
│
├─ PORT (int, default: 8000)
│  └─ Server listening port
│
└─ (CHAT_TIMEOUT - future addition)
   └─ Timeout for GovChat responses

Example:
  USE_SELENIUM=true PORT=8001 python run.py
```

## Failure Modes & Recovery

```
Scenario 1: HTTP Endpoint Wrong
  ├─ Server tries each endpoint in list
  ├─ All fail with 404
  └─ Resolution:
     ├─ Run NETWORK_INSPECTION.md steps
     ├─ Add real endpoint to code
     └─ Restart server

Scenario 2: Network Issue
  ├─ GovChat website unreachable
  ├─ Timeout error
  └─ Resolution:
     ├─ Check internet connection
     ├─ Verify GovChat is online
     ├─ Increase CHAT_TIMEOUT
     └─ Check firewall/VPN

Scenario 3: HTTP Mode Consistently Fails
  ├─ Try multiple endpoints, all fail
  ├─ Response format unexpected
  └─ Resolution:
     ├─ Enable Selenium: USE_SELENIUM=true
     ├─ More reliable but slower
     └─ Great fallback option

Scenario 4: Server Crashes
  ├─ Unhandled exception
  ├─ Check logs
  └─ Resolution:
     ├─ Review error message
     ├─ Check CONFIG.md troubleshooting
     └─ Restart: python run.py
```

---

**This architecture is designed to be:**
- 🎯 **Simple** - Easy to understand and modify
- 🔄 **Flexible** - HTTP or Selenium, easily switchable
- 📚 **Extensible** - Add new endpoints/clients easily
- 🛡️ **Robust** - Error handling and fallbacks
- 📊 **Observable** - Logging at every level

Enjoy your multi-agent system! 🚀
