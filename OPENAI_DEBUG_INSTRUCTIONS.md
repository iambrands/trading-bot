# OpenAI Debugging Instructions

## Issue
The AI analysis is returning empty/None even though the API call succeeds. This suggests a response parsing issue.

## What to Check

### 1. Check Railway Logs
After the deployment completes, check Railway logs for `[_call_openai]` messages:

**Look for these log entries:**
```
[_call_openai] STARTING OPENAI API CALL
[_call_openai] Response status: 200
[_call_openai] Response keys: ['id', 'object', 'created', 'model', 'choices', ...]
[_call_openai] Full response preview: {...}
[_call_openai] First choice type: <class 'dict'>
[_call_openai] First choice keys: ['index', 'message', 'finish_reason', 'logprobs']
[_call_openai] Message type: <class 'dict'>
[_call_openai] Message keys: ['role', 'content']
[_call_openai] Extracted text type: <class 'str'>
[_call_openai] Extracted text length: XXX
```

### 2. Common Issues

#### Issue A: Empty 'content' field
**Symptom:** `Extracted text length: 0` or `Extracted text value: ''`
**Cause:** OpenAI might be returning empty content
**Fix:** Check if there's a `finish_reason` issue (e.g., "length" means truncated)

#### Issue B: Wrong structure
**Symptom:** Missing keys in logs (e.g., no 'message' key, no 'content' key)
**Cause:** Response structure is different than expected
**Fix:** Update parsing logic based on actual structure

#### Issue C: Content is None
**Symptom:** `Extracted text type: <class 'NoneType'>`
**Cause:** Content field exists but is None
**Fix:** Add None check before validation

### 3. Test Script
Run the test script to see the actual response:
```bash
export OPENAI_API_KEY="your_key_here"
python3 test_openai_response_structure.py
```

This will show the exact response structure OpenAI returns.

### 4. Next Steps
Once you see the logs:
1. Share the `[_call_openai]` log entries
2. We'll fix the parsing logic based on what's actually returned
3. Redeploy and test

## Expected Response Structure

OpenAI Chat Completions API should return:
```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "gpt-4o-mini",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The actual text response here..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

The parsing should extract: `response['choices'][0]['message']['content']`

## If Still Not Working

If logs show the structure is correct but text is still None/empty:
1. Check `finish_reason` - if it's "length", the response was truncated
2. Check if `content` is actually a string or might be `null`
3. Check if there are multiple choices and we need to concatenate them

