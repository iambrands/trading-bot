"""Claude AI integration for market analysis and user guidance."""

import logging
from typing import Optional, Dict, Any
import aiohttp
import json
import asyncio
from config import get_config

logger = logging.getLogger(__name__)


class ClaudeAIAnalyst:
    """Claude AI analyst for market analysis and user guidance."""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.api_key = (self.config.CLAUDE_API_KEY or '').strip()
        # Remove any quotes that might have been added
        if self.api_key:
            self.api_key = self.api_key.strip('"').strip("'")
        self.model = self.config.CLAUDE_MODEL
        self.base_url = "https://api.anthropic.com/v1"
        self.enabled = bool(self.api_key and len(self.api_key) > 10)  # Basic validation - real keys are longer
        
        if not self.enabled:
            key_status = 'empty or too short' if not self.api_key or len(self.api_key) <= 10 else 'invalid'
            logger.warning(f"Claude AI not configured - CLAUDE_API_KEY is {key_status}. Key length: {len(self.api_key) if self.api_key else 0}")
        else:
            logger.info(f"ClaudeAIAnalyst initialized with model: {self.model} (key length: {len(self.api_key)})")
    
    async def analyze_market_conditions(
        self, 
        market_data: Dict[str, Any],
        trading_signals: Dict[str, Any]
    ) -> Optional[str]:
        """
        Analyze market conditions and provide AI insights.
        
        Args:
            market_data: Current market data (prices, indicators)
            trading_signals: Trading signals and conditions
        
        Returns:
            AI-generated analysis text or None if unavailable
        """
        if not self.enabled:
            return None
        
        try:
            prompt = self._create_market_analysis_prompt(market_data, trading_signals)
            analysis = await self._call_claude(prompt)
            return analysis
        except Exception as e:
            logger.error(f"Failed to get AI market analysis: {e}", exc_info=True)
            return None
    
    async def explain_strategy(
        self,
        strategy_config: Dict[str, Any],
        current_metrics: Dict[str, Any]
    ) -> Optional[str]:
        """
        Explain trading strategy and provide user-friendly guidance.
        
        Args:
            strategy_config: Current strategy configuration
            current_metrics: Current performance metrics
        
        Returns:
            AI-generated explanation text
        """
        if not self.enabled:
            return None
        
        try:
            prompt = self._create_strategy_explanation_prompt(strategy_config, current_metrics)
            explanation = await self._call_claude(prompt)
            return explanation
        except Exception as e:
            logger.error(f"Failed to get AI strategy explanation: {e}", exc_info=True)
            return None
    
    async def get_user_guidance(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Get AI-powered user guidance for any question.
        
        Args:
            question: User's question
            context: Optional context (current bot state, metrics, etc.)
        
        Returns:
            AI-generated guidance text
        """
        if not self.enabled:
            return None
        
        try:
            prompt = self._create_user_guidance_prompt(question, context)
            guidance = await self._call_claude(prompt)
            return guidance
        except Exception as e:
            logger.error(f"Failed to get AI user guidance: {e}", exc_info=True)
            return None
    
    async def analyze_backtest_results(
        self,
        backtest_results: Dict[str, Any],
        strategy_config: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Analyze backtest results and provide insights.
        
        Args:
            backtest_results: Backtest results dictionary
            strategy_config: Optional strategy configuration
        
        Returns:
            AI-generated analysis text or None if unavailable
        """
        if not self.enabled:
            return None
        
        try:
            prompt = self._create_backtest_analysis_prompt(backtest_results, strategy_config)
            analysis = await self._call_claude(prompt)
            return analysis
        except Exception as e:
            logger.error(f"Failed to get AI backtest analysis: {e}", exc_info=True)
            return None
    
    async def _call_claude(self, prompt: str) -> Optional[str]:
        """Make API call to Claude AI with comprehensive logging and robust parsing."""
        import sys
        from datetime import datetime
        
        # Force immediate console output (Railway should capture this)
        print("=" * 60, file=sys.stderr, flush=True)
        print("[_call_claude] STARTING CLAUDE API CALL", file=sys.stderr, flush=True)
        print(f"[_call_claude] Timestamp: {datetime.now().isoformat()}", file=sys.stderr, flush=True)
        print(f"[_call_claude] API Key present: {bool(self.api_key)}", file=sys.stderr, flush=True)
        print(f"[_call_claude] API Key length: {len(self.api_key) if self.api_key else 0}", file=sys.stderr, flush=True)
        print(f"[_call_claude] Model: {self.model}", file=sys.stderr, flush=True)
        print(f"[_call_claude] Base URL: {self.base_url}", file=sys.stderr, flush=True)
        print(f"[_call_claude] Prompt length: {len(prompt)} characters", file=sys.stderr, flush=True)
        print("=" * 60, file=sys.stderr, flush=True)
        
        logger.info("=" * 60)
        logger.info("[_call_claude] STARTING CLAUDE API CALL")
        logger.info(f"[_call_claude] Timestamp: {datetime.now().isoformat()}")
        logger.info("=" * 60)
        logger.info(f"API Key present: {bool(self.api_key)}")
        logger.info(f"API Key length: {len(self.api_key) if self.api_key else 0}")
        logger.info(f"Model: {self.model}")
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"Prompt length: {len(prompt)} characters")
        
        if not self.api_key:
            logger.error("[_call_claude] ❌ NO API KEY FOUND")
            print(f"[_call_claude] ❌ NO API KEY FOUND", file=sys.stderr, flush=True)
            return None
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'x-api-key': self.api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json'
            }
            
            payload = {
                'model': self.model,
                'max_tokens': 2000,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            }
            
            try:
                logger.info(f"[_call_claude] Making HTTP request to {self.base_url}/messages")
                print(f"[_call_claude] POST {self.base_url}/messages", file=sys.stderr, flush=True)
                
                async with session.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    status = response.status
                    logger.info(f"[_call_claude] Response status: {status}")
                    print(f"[_call_claude] Response status: {status}", file=sys.stderr, flush=True)
                    
                    if status != 200:
                        error_text = await response.text()
                        logger.error(f"[_call_claude] ❌ API error {status}: {error_text}")
                        print(f"[_call_claude] ❌ Error {status}: {error_text[:200]}", file=sys.stderr, flush=True)
                        # Provide more detailed error messages
                        if status == 401:
                            raise Exception("Invalid API key. Please check your CLAUDE_API_KEY.")
                        elif status == 429:
                            raise Exception("Rate limit exceeded. Please try again later.")
                        elif status == 500:
                            raise Exception("Claude API server error. Please try again later.")
                        else:
                            raise Exception(f"Claude API error {status}: {error_text[:200]}")
                    
                    # Parse response
                    logger.info("[_call_claude] Parsing Claude API response...")
                    
                    # First, read raw response text for debugging
                    raw_response_text = await response.text()
                    print(f"[_call_claude] RAW RESPONSE TEXT (first 500 chars): {raw_response_text[:500]}", file=sys.stderr, flush=True)
                    logger.info(f"[_call_claude] Raw response text length: {len(raw_response_text)}")
                    
                    try:
                        response_data = json.loads(raw_response_text)
                    except json.JSONDecodeError as json_err:
                        logger.error(f"[_call_claude] ❌ Failed to parse JSON: {json_err}")
                        logger.error(f"[_call_claude] Raw response: {raw_response_text[:500]}")
                        print(f"[_call_claude] ❌ JSON parse error: {json_err}", file=sys.stderr, flush=True)
                        print(f"[_call_claude] Raw response: {raw_response_text[:500]}", file=sys.stderr, flush=True)
                        return None
                    
                    logger.info("=" * 60)
                    logger.info("[_call_claude] RESPONSE RECEIVED")
                    logger.info("=" * 60)
                    logger.info(f"[_call_claude] Response type: {type(response_data)}")
                    
                    # Log the full response structure for debugging
                    if isinstance(response_data, dict):
                        logger.info(f"[_call_claude] Response keys: {list(response_data.keys())}")
                        # Log full response structure (truncated for size)
                        response_json = json.dumps(response_data, indent=2, default=str)
                        logger.info(f"[_call_claude] Full response JSON (first 2000 chars):\n{response_json[:2000]}...")
                        print(f"[_call_claude] Response keys: {list(response_data.keys())}", file=sys.stderr, flush=True)
                        print(f"[_call_claude] Response JSON (first 1000 chars): {response_json[:1000]}", file=sys.stderr, flush=True)
                    else:
                        logger.error(f"[_call_claude] ❌ Response is not a dict! Type: {type(response_data)}")
                        logger.error(f"[_call_claude] Response value: {response_data}")
                        print(f"[_call_claude] ❌ Response is not a dict! Type: {type(response_data)}", file=sys.stderr, flush=True)
                        print(f"[_call_claude] Response value: {str(response_data)[:500]}", file=sys.stderr, flush=True)
                        
                        # Extract content - handle multiple possible structures
                        content = response_data.get('content')
                        
                        if content is None:
                            logger.error("[_call_claude] ❌ No 'content' field in response")
                            logger.error(f"[_call_claude] Available keys: {list(response_data.keys())}")
                            print(f"[_call_claude] ❌ No 'content' field. Keys: {list(response_data.keys())}", file=sys.stderr, flush=True)
                            return None
                        
                        logger.info(f"[_call_claude] Content type: {type(content)}")
                        logger.info(f"[_call_claude] Content value preview: {str(content)[:200]}...")
                        print(f"[_call_claude] Content type: {type(content)}", file=sys.stderr, flush=True)
                        
                        # Handle different content structures
                        text = None
                        
                        # Case 1: content is a list of blocks
                        if isinstance(content, list):
                            logger.info(f"[_call_claude] Content is list with {len(content)} items")
                            print(f"[_call_claude] Content is list with {len(content)} items", file=sys.stderr, flush=True)
                            
                            if len(content) == 0:
                                logger.error("[_call_claude] ❌ Content list is empty")
                                print(f"[_call_claude] ❌ Content list is empty", file=sys.stderr, flush=True)
                                return None
                            
                            first_item = content[0]
                            logger.info(f"[_call_claude] First item type: {type(first_item)}")
                            logger.info(f"[_call_claude] First item: {first_item}")
                            print(f"[_call_claude] First item type: {type(first_item)}", file=sys.stderr, flush=True)
                            
                            # Standard format: [{"type": "text", "text": "..."}]
                            if isinstance(first_item, dict):
                                first_item_keys = list(first_item.keys())
                                logger.info(f"[_call_claude] First item keys: {first_item_keys}")
                                print(f"[_call_claude] First item keys: {first_item_keys}", file=sys.stderr, flush=True)
                                
                                text = first_item.get('text', '')
                                logger.info(f"[_call_claude] Extracted from dict.text: '{text[:100] if text else 'EMPTY'}'")
                                print(f"[_call_claude] Extracted from dict.text: length={len(text) if text else 0}", file=sys.stderr, flush=True)
                                
                                # If text key didn't work, try other possible keys
                                if not text or text == '':
                                    # Try 'content' key
                                    nested_content = first_item.get('content', '')
                                    if nested_content:
                                        text = nested_content
                                        logger.info(f"[_call_claude] Found text in 'content' key: {len(text)} chars")
                                        print(f"[_call_claude] Found text in 'content' key: {len(text)} chars", file=sys.stderr, flush=True)
                                    else:
                                        # Try 'value' key
                                        value = first_item.get('value', '')
                                        if value:
                                            text = value
                                            logger.info(f"[_call_claude] Found text in 'value' key: {len(text)} chars")
                                            print(f"[_call_claude] Found text in 'value' key: {len(text)} chars", file=sys.stderr, flush=True)
                            
                            # Edge case: list of strings
                            elif isinstance(first_item, str):
                                text = first_item
                                logger.info(f"[_call_claude] Content is list of strings, using first: {len(text)} chars")
                                print(f"[_call_claude] Content is list of strings: {len(text)} chars", file=sys.stderr, flush=True)
                            
                            else:
                                logger.error(f"[_call_claude] ❌ Unexpected first item type: {type(first_item)}")
                                logger.error(f"[_call_claude] First item value: {first_item}")
                                print(f"[_call_claude] ❌ Unexpected first item type: {type(first_item)}", file=sys.stderr, flush=True)
                        
                        # Case 2: content is a dict
                        elif isinstance(content, dict):
                            logger.info("[_call_claude] Content is dict")
                            print(f"[_call_claude] Content is dict", file=sys.stderr, flush=True)
                            text = content.get('text', '') or content.get('content', '') or content.get('value', '')
                            logger.info(f"[_call_claude] Extracted from dict: '{text[:100] if text else 'EMPTY'}'")
                            print(f"[_call_claude] Extracted from dict: length={len(text) if text else 0}", file=sys.stderr, flush=True)
                        
                        # Case 3: content is a string
                        elif isinstance(content, str):
                            logger.info("[_call_claude] Content is string")
                            print(f"[_call_claude] Content is string: {len(content)} chars", file=sys.stderr, flush=True)
                            text = content
                        
                        else:
                            logger.error(f"[_call_claude] ❌ Unexpected content type: {type(content)}")
                            logger.error(f"[_call_claude] Content value: {str(content)[:500]}")
                            print(f"[_call_claude] ❌ Unexpected content type: {type(content)}", file=sys.stderr, flush=True)
                            return None
                        
                        # Validate extracted text
                        logger.info(f"[_call_claude] Extracted text type: {type(text)}")
                        logger.info(f"[_call_claude] Extracted text length: {len(text) if text else 0}")
                        logger.info(f"[_call_claude] Text is None: {text is None}")
                        logger.info(f"[_call_claude] Text is empty string: {text == ''}")
                        print(f"[_call_claude] Text type: {type(text)}, length: {len(text) if text else 0}", file=sys.stderr, flush=True)
                        
                        # Return text if valid
                        if text and isinstance(text, str) and text.strip():
                            final_text = text.strip()
                            logger.info(f"[_call_claude] ✅ SUCCESS - Returning {len(final_text)} chars")
                            logger.info(f"[_call_claude] Preview: {final_text[:200]}...")
                            print(f"[_call_claude] ✅ SUCCESS - Returning {len(final_text)} chars", file=sys.stderr, flush=True)
                            print(f"[_call_claude] Preview: {final_text[:200]}...", file=sys.stderr, flush=True)
                            return final_text
                        
                        elif text == '':
                            logger.warning("[_call_claude] ⚠️ Claude returned empty string")
                            print(f"[_call_claude] ⚠️ Empty string returned", file=sys.stderr, flush=True)
                            return None
                        
                        else:
                            logger.error(f"[_call_claude] ❌ Invalid text value: {repr(text)}")
                            logger.error(f"[_call_claude] Full response for debugging:\n{json.dumps(response_data, indent=2, default=str)[:2000]}")
                            print(f"[_call_claude] ❌ Invalid text value: {repr(text)}", file=sys.stderr, flush=True)
                            return None
                    
                    else:
                        logger.error(f"[_call_claude] ❌ Response is not a dict: {type(response_data)}")
                        logger.error(f"[_call_claude] Response value: {str(response_data)[:500]}")
                        print(f"[_call_claude] ❌ Response not a dict: {type(response_data)}", file=sys.stderr, flush=True)
                        return None
                        
            except aiohttp.ClientError as e:
                error_msg = f"HTTP client error: {str(e)}"
                logger.error(f"[_call_claude] ❌ ClientError: {error_msg}", exc_info=True)
                print(f"[_call_claude] ❌ ClientError: {e}", file=sys.stderr, flush=True)
                raise Exception(error_msg)
            except asyncio.TimeoutError as e:
                error_msg = "Claude API request timed out after 30 seconds"
                logger.error(f"[_call_claude] ❌ Timeout: {error_msg}")
                print(f"[_call_claude] ❌ Timeout: {error_msg}", file=sys.stderr, flush=True)
                raise Exception(error_msg)
            except Exception as e:
                error_msg = f"Unexpected error calling Claude API: {str(e)}"
                logger.error(f"[_call_claude] ❌ Exception: {error_msg}", exc_info=True)
                print(f"[_call_claude] ❌ Exception: {e}", file=sys.stderr, flush=True)
                raise
    
    def _create_market_analysis_prompt(self, market_data: Dict, trading_signals: Dict) -> str:
        """Create prompt for market condition analysis."""
        return f"""You are an expert cryptocurrency trading analyst. Analyze the following market conditions and trading signals.

Provide your analysis using this exact format:

## Market Overview
Brief summary of current market conditions here.

## Trading Opportunities  
Identify if there are good trading opportunities and why.

## Risk Assessment
Any risks or concerns with current market conditions.

## Recommendations
Actionable advice for the trader.

Market Data:
{json.dumps(market_data, indent=2)}

Trading Signals:
{json.dumps(trading_signals, indent=2)}

Use markdown headers (##) for each section. Keep each section concise and actionable. Use bullet points (-) for lists."""
    
    def _create_strategy_explanation_prompt(self, strategy_config: Dict, metrics: Dict) -> str:
        """Create prompt for strategy explanation."""
        return f"""You are a friendly TradePilot assistant. Explain the current trading strategy configuration and performance in simple, easy-to-understand terms.

Strategy Configuration:
{json.dumps(strategy_config, indent=2)}

Current Performance Metrics:
{json.dumps(metrics, indent=2)}

Explain:
1. How the strategy works in simple terms
2. What the current performance means
3. What the user should know or consider
4. Any suggestions for improvement

Write in a conversational, helpful tone."""
    
    def _create_user_guidance_prompt(self, question: str, context: Optional[Dict] = None) -> str:
        """Create prompt for user guidance."""
        context_str = ""
        if context:
            context_str = f"\n\nCurrent Bot Context:\n{json.dumps(context, indent=2)}"
        
        return f"""You are a helpful assistant for TradePilot. Answer the user's question clearly and provide useful guidance.

User Question: {question}
{context_str}

Provide a clear, helpful answer that helps the user understand and use TradePilot effectively."""
    
    def _create_backtest_analysis_prompt(self, backtest_results: Dict, strategy_config: Optional[Dict] = None) -> str:
        """Create prompt for backtest results analysis."""
        strategy_str = ""
        if strategy_config:
            strategy_str = f"\n\nStrategy Configuration:\n{json.dumps(strategy_config, indent=2)}"
        
        return f"""You are an expert cryptocurrency trading analyst. Analyze the following backtest results and provide insights.

Backtest Results:
{json.dumps(backtest_results, indent=2, default=str)}
{strategy_str}

Provide your analysis using this exact format with markdown headers:

## Performance Summary
Brief overview of the backtest performance. Was it profitable? What's the overall assessment?

## Key Strengths
What worked well in this backtest? Highlight positive aspects.

## Areas of Concern
What potential issues or weaknesses does the backtest reveal?

## Recommendations
Actionable advice for improving the strategy or understanding the results.

Use ## for section headers and - for bullet points. Keep it concise and actionable."""

