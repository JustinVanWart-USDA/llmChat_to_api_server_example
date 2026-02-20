# GovChat Network Inspection Guide

## How to Find the Real API Endpoints

If the HTTP mode isn't working, follow this guide to discover the actual API endpoints the website uses.

### Step 1: Open DevTools

1. Go to https://govchat.ars.usda.gov in Chrome
2. Press `F12` to open Developer Tools
3. Go to the **Network** tab
4. Make sure it's recording (red dot on left side)

### Step 2: Send a Message

1. Type a message in the chat box
2. Click Send
3. Watch the Network tab for requests

### Step 3: Identify the API Call

Look for requests that:
- **Method**: POST or GET
- **Type**: `xhr` (XHR/XMLHttpRequest) or `fetch`
- **Status**: 200 or 201
- **NOT**: These are normal page resources
  - `document`
  - `stylesheet`
  - `script`
  - `image`

### Step 4: Examine the Request

Click on the suspicious request and look at:

#### Headers Tab
```
Request URL: https://govchat.ars.usda.gov/api/chat/messages
Request Method: POST
Content-Type: application/json
```

**Copy the Request URL** - this is what we need!

#### Request Tab (or Payload)
This shows what data is being sent:
```json
{
  "message": "Your message here",
  "conversation_id": "abc123",
  "model": "gpt-4"
}
```

**Note the request structure** - this tells us how to format our requests.

#### Response Tab
This shows what comes back:
```json
{
  "response": "The AI response here",
  "id": "msg_123"
}
```

**Note the response format** - this tells us what to expect back.

### Step 5: Update the Code

Once you have the endpoint URL, request format, and response format:

1. Open `app/clients/govchat_http_client.py`
2. Update `endpoints_to_try` list with the real endpoint
3. Update `_prepare_messages_payload()` to match request format
4. Update `_extract_response()` to match response format
5. Restart the server

Example:

```python
# In _make_api_request()
endpoints_to_try = [
    "https://govchat.ars.usda.gov/api/chat/completions",  # Real endpoint
    # Keep other attempts as fallback
]
```

### Step 6: Test Again

```bash
python test_client.py
```

## Common Endpoints Found

### OpenAI-like
```
POST /api/chat/completions
POST /api/messages
```

### Custom
```
POST /api/conversation/{id}
POST /chat/send
```

## Request Format Variations

### OpenAI Format (Most Common)
```json
{
  "model": "gpt-4",
  "messages": [
    {"role": "user", "content": "message"}
  ]
}
```

### Custom Format
```json
{
  "message": "text",
  "conversation_id": "id"
}
```

## Response Format Variations

### OpenAI Format
```json
{
  "choices": [{
    "message": {
      "content": "response text"
    }
  }]
}
```

### Simple Format
```json
{
  "response": "response text"
}
```

## Debugging Steps

1. **Check Status Code**
   - 200: Success ✅
   - 400: Bad request - check format
   - 401: Unauthorized - might need auth
   - 403: Forbidden
   - 404: Endpoint not found
   - 429: Rate limited
   - 500: Server error

2. **Check Response Size**
   - If very small: Might be error response
   - Check Response tab for error message

3. **Check Headers**
   - Look for `Authorization`, `X-API-Key`
   - Check `User-Agent`
   - Check `Referer` and `Origin`

4. **Enable Request/Response Logging**
   - Add to `govchat_http_client.py`:
   ```python
   logger.debug(f"Request: {payload}")
   logger.debug(f"Response: {response.json()}")
   ```

## Using the Network Info

Once you find the endpoint, you have:

```
Endpoint: URL from request
Method: POST/GET
Headers: Any special headers
Request Format: Structure of the data sent
Response Format: Structure of the data returned
Timeout: How long to wait (varies by website)
```

Add all this info to the HTTP client and test!

## Common Issues & Solutions

### 404 Not Found
- Wrong endpoint URL
- Check spelling carefully
- Try without `/api` prefix
- Try `/v1/` prefix

### 400 Bad Request
- Wrong request format
- Missing required fields
- Wrong data types

### Connection Timeout
- Website is slow
- Network issue
- Firewall blocking

### Empty Response
- Server might need authentication
- Response format unknown
- Check Response tab for actual data

## Pro Tips

1. **Network Persistence**: Check "Preserve log" in Network tab
2. **Filter Requests**: Use filter box to show only API calls
3. **Copy as cURL**: Right-click request → Copy → Copy as cURL
   - This shows exact format needed
4. **Check Cookies**: Some sites use session cookies
5. **Check CORS Headers**: Might need specific headers

## Still Stuck?

If you can't find the endpoint:
1. Use Selenium mode: `USE_SELENIUM=true python run.py`
2. Share the Network tab findings in a GitHub issue
3. Check if the site requires authentication

## References

- Chrome DevTools Network Tab: https://developer.chrome.com/docs/devtools/network/
- XHR/Fetch Requests: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
- Common API Patterns: https://restfulapi.net/

Good luck hunting for those endpoints! 🔍
