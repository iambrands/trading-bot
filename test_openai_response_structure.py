#!/usr/bin/env python3
"""Test script to check OpenAI API response structure"""

import asyncio
import aiohttp
import json
import os

async def test_openai_api():
    """Test OpenAI API directly to see response structure"""
    api_key = os.getenv('OPENAI_API_KEY', '')
    
    if not api_key:
        print("❌ OPENAI_API_KEY not set in environment")
        return
    
    print(f"✅ API Key found (length: {len(api_key)})")
    print(f"Key prefix: {api_key[:10]}...")
    print()
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'gpt-4o-mini',
        'messages': [
            {'role': 'user', 'content': 'Say "Hello, OpenAI!" and nothing else.'}
        ],
        'max_tokens': 100
    }
    
    print("Making test API call to OpenAI...")
    print(f"URL: {url}")
    print(f"Model: {payload['model']}")
    print()
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            status = response.status
            print(f"Response Status: {status}")
            
            if status != 200:
                error_text = await response.text()
                print(f"❌ Error: {error_text}")
                return
            
            response_data = await response.json()
            
            print("=" * 60)
            print("FULL RESPONSE STRUCTURE:")
            print("=" * 60)
            print(json.dumps(response_data, indent=2))
            print("=" * 60)
            print()
            
            # Try to extract content
            print("Extracting content...")
            if 'choices' in response_data:
                choices = response_data['choices']
                print(f"Choices count: {len(choices)}")
                
                if len(choices) > 0:
                    first_choice = choices[0]
                    print(f"First choice keys: {list(first_choice.keys())}")
                    
                    if 'message' in first_choice:
                        message = first_choice['message']
                        print(f"Message keys: {list(message.keys())}")
                        
                        if 'content' in message:
                            content = message['content']
                            print(f"Content type: {type(content)}")
                            print(f"Content length: {len(content) if content else 0}")
                            print(f"Content value: {repr(content)}")
                            print()
                            print("✅ SUCCESS - Extracted content:")
                            print(content)
                        else:
                            print("❌ No 'content' key in message")
                            print(f"Available keys: {list(message.keys())}")
                    else:
                        print("❌ No 'message' key in choice")
                else:
                    print("❌ Choices array is empty")
            else:
                print("❌ No 'choices' key in response")
                print(f"Available keys: {list(response_data.keys())}")

if __name__ == '__main__':
    asyncio.run(test_openai_api())

