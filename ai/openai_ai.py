"""OpenAI integration for market analysis and user guidance."""

import logging
from typing import Optional, Dict, Any
import aiohttp
import json
import asyncio
from config import get_config

logger = logging.getLogger(__name__)


class OpenAIAnalyst:
    """OpenAI analyst for market analysis and user guidance."""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.api_key = (self.config.OPENAI_API_KEY or '').strip()
        # Remove any quotes that might have been added
        if self.api_key:
            self.api_key = self.api_key.strip('"').strip("'")
        self.model = self.config.OPENAI_MODEL
        self.base_url = "https://api.openai.com/v1"
        self.enabled = bool(self.api_key and len(self.api_key) > 10)  # Basic validation - real keys are longer
        
        if not self.enabled:
            key_status = 'empty or too short' if not self.api_key or len(self.api_key) <= 10 else 'invalid'
            logger.warning(f"OpenAI not configured - OPENAI_API_KEY is {key_status}. Key length: {len(self.api_key) if self.api_key else 0}")
        else:
            logger.info(f"OpenAIAnalyst initialized with model: {self.model} (key length: {len(self.api_key)})")
    
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
            analysis = await self._call_openai(prompt)
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
            explanation = await self._call_openai(prompt)
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
            guidance = await self._call_openai(prompt)
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
            analysis = await self._call_openai(prompt)
            return analysis
        except Exception as e:
            logger.error(f"Failed to get AI backtest analysis: {e}", exc_info=True)
            return None
    
    async def _call_openai(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """Make API call to OpenAI with comprehensive logging and robust parsing."""
        import sys
        from datetime import datetime
        
        # Force immediate console output (Railway should capture this)
        print("=" * 60, file=sys.stderr, flush=True)
        print("[_call_openai] STARTING OPENAI API CALL", file=sys.stderr, flush=True)
        print(f"[_call_openai] Timestamp: {datetime.now().isoformat()}", file=sys.stderr, flush=True)
        print(f"[_call_openai] API Key present: {bool(self.api_key)}", file=sys.stderr, flush=True)
        print(f"[_call_openai] API Key length: {len(self.api_key) if self.api_key else 0}", file=sys.stderr, flush=True)
        print(f"[_call_openai] Model: {self.model}", file=sys.stderr, flush=True)
        print(f"[_call_openai] Base URL: {self.base_url}", file=sys.stderr, flush=True)
        print(f"[_call_openai] Prompt length: {len(prompt)} characters", file=sys.stderr, flush=True)
        print("=" * 60, file=sys.stderr, flush=True)
        
        logger.info("=" * 60)
        logger.info("[_call_openai] STARTING OPENAI API CALL")
        logger.info(f"[_call_openai] Timestamp: {datetime.now().isoformat()}")
        logger.info("=" * 60)
        logger.info(f"API Key present: {bool(self.api_key)}")
        logger.info(f"API Key length: {len(self.api_key) if self.api_key else 0}")
        logger.info(f"Model: {self.model}")
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"Prompt length: {len(prompt)} characters")
        
        if not self.api_key:
            logger.error("[_call_openai] ❌ NO API KEY FOUND")
            print(f"[_call_openai] ❌ NO API KEY FOUND", file=sys.stderr, flush=True)
            return None
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                'model': self.model,
                'messages': messages,
                'max_tokens': 2000,
                'temperature': 0.7
            }
            
            try:
                logger.info(f"[_call_openai] Making HTTP request to {self.base_url}/chat/completions")
                print(f"[_call_openai] POST {self.base_url}/chat/completions", file=sys.stderr, flush=True)
                
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    status = response.status
                    logger.info(f"[_call_openai] Response status: {status}")
                    print(f"[_call_openai] Response status: {status}", file=sys.stderr, flush=True)
                    
                    if status != 200:
                        error_text = await response.text()
                        logger.error(f"[_call_openai] ❌ API error {status}: {error_text}")
                        print(f"[_call_openai] ❌ Error {status}: {error_text[:500]}", file=sys.stderr, flush=True)
                        
                        # Parse error response for more details
                        error_details = None
                        error_message = None
                        try:
                            error_json = json.loads(error_text) if error_text else None
                            if error_json and 'error' in error_json:
                                error_details = error_json['error']
                                if isinstance(error_details, dict) and 'message' in error_details:
                                    error_message = error_details['message']
                                elif isinstance(error_details, str):
                                    error_message = error_details
                        except:
                            pass
                        
                        # Provide more detailed error messages
                        if status == 401:
                            raise Exception("Invalid API key. Please check your OPENAI_API_KEY in Railway environment variables.")
                        elif status == 429:
                            # Check if it's quota exceeded or rate limit
                            error_lower = error_text.lower()
                            if error_message:
                                error_msg_lower = error_message.lower()
                            else:
                                error_msg_lower = error_lower
                            
                            if 'quota' in error_msg_lower or 'billing' in error_msg_lower or 'exceeded your current quota' in error_msg_lower:
                                raise Exception("OpenAI API quota exceeded. Please check your OpenAI billing and add credits to your account. Visit: https://platform.openai.com/account/billing")
                            else:
                                raise Exception("OpenAI API rate limit exceeded. Please try again in a few minutes.")
                        elif status == 500:
                            raise Exception("OpenAI API server error. Please try again later.")
                        else:
                            # Include error details if available
                            if error_message:
                                raise Exception(f"OpenAI API error {status}: {error_message}")
                            elif error_details and isinstance(error_details, dict) and 'message' in error_details:
                                raise Exception(f"OpenAI API error {status}: {error_details['message']}")
                            else:
                                raise Exception(f"OpenAI API error {status}: {error_text[:200]}")
                    
                    # Parse response
                    logger.info("[_call_openai] Parsing OpenAI API response...")
                    print("[_call_openai] Parsing OpenAI API response...", file=sys.stderr, flush=True)
                    response_data = await response.json()
                    
                    logger.info("=" * 60)
                    logger.info("[_call_openai] RESPONSE RECEIVED")
                    logger.info("=" * 60)
                    logger.info(f"[_call_openai] Response type: {type(response_data)}")
                    
                    # Force immediate stderr output
                    print("=" * 60, file=sys.stderr, flush=True)
                    print("[_call_openai] RESPONSE RECEIVED", file=sys.stderr, flush=True)
                    print(f"[_call_openai] Response type: {type(response_data)}", file=sys.stderr, flush=True)
                    
                    # Log the full response structure for debugging
                    if isinstance(response_data, dict):
                        response_keys = list(response_data.keys())
                        logger.info(f"[_call_openai] Response keys: {response_keys}")
                        # Log full response structure (truncated for size)
                        response_json = json.dumps(response_data, indent=2, default=str)
                        logger.info(f"[_call_openai] Full response preview (first 1000 chars):\n{response_json[:1000]}...")
                        print(f"[_call_openai] Response received! Keys: {response_keys}", file=sys.stderr, flush=True)
                        print(f"[_call_openai] Full response preview (first 500 chars):", file=sys.stderr, flush=True)
                        print(response_json[:500], file=sys.stderr, flush=True)
                        print("...", file=sys.stderr, flush=True)
                        
                        # Extract content from OpenAI response
                        # OpenAI format: {"choices": [{"message": {"content": "..."}}]}
                        choices = response_data.get('choices', [])
                        
                        if not choices:
                            logger.error("[_call_openai] ❌ No 'choices' field in response")
                            print(f"[_call_openai] ❌ No 'choices' field. Keys: {response_keys}", file=sys.stderr, flush=True)
                            return None
                        
                        if len(choices) == 0:
                            logger.error("[_call_openai] ❌ Choices list is empty")
                            print(f"[_call_openai] ❌ Choices list is empty", file=sys.stderr, flush=True)
                            return None
                        
                        first_choice = choices[0]
                        logger.info(f"[_call_openai] First choice type: {type(first_choice)}")
                        logger.info(f"[_call_openai] First choice keys: {list(first_choice.keys()) if isinstance(first_choice, dict) else 'Not a dict'}")
                        print(f"[_call_openai] First choice type: {type(first_choice)}", file=sys.stderr, flush=True)
                        print(f"[_call_openai] First choice keys: {list(first_choice.keys()) if isinstance(first_choice, dict) else 'Not a dict'}", file=sys.stderr, flush=True)
                        
                        if not isinstance(first_choice, dict):
                            logger.error(f"[_call_openai] ❌ First choice is not a dict: {type(first_choice)}")
                            print(f"[_call_openai] ❌ First choice is not a dict: {type(first_choice)}", file=sys.stderr, flush=True)
                            return None
                        
                        message = first_choice.get('message', {})
                        logger.info(f"[_call_openai] Message type: {type(message)}")
                        logger.info(f"[_call_openai] Message keys: {list(message.keys()) if isinstance(message, dict) else 'Not a dict'}")
                        print(f"[_call_openai] Message type: {type(message)}", file=sys.stderr, flush=True)
                        print(f"[_call_openai] Message keys: {list(message.keys()) if isinstance(message, dict) else 'Not a dict'}", file=sys.stderr, flush=True)
                        
                        if not isinstance(message, dict):
                            logger.error(f"[_call_openai] ❌ Message is not a dict: {type(message)}")
                            print(f"[_call_openai] ❌ Message is not a dict: {type(message)}", file=sys.stderr, flush=True)
                            return None
                        
                        text = message.get('content', '')
                        logger.info(f"[_call_openai] Extracted text type: {type(text)}")
                        logger.info(f"[_call_openai] Extracted text length: {len(text) if text else 0}")
                        logger.info(f"[_call_openai] Extracted text value: {repr(text)[:100]}")
                        print(f"[_call_openai] Extracted text type: {type(text)}", file=sys.stderr, flush=True)
                        print(f"[_call_openai] Extracted text length: {len(text) if text else 0}", file=sys.stderr, flush=True)
                        print(f"[_call_openai] Extracted text value: {repr(text)[:100]}", file=sys.stderr, flush=True)
                        
                        # Return text if valid
                        if text and isinstance(text, str) and text.strip():
                            final_text = text.strip()
                            logger.info(f"[_call_openai] ✅ SUCCESS - Returning {len(final_text)} chars")
                            logger.info(f"[_call_openai] Preview: {final_text[:200]}...")
                            print(f"[_call_openai] ✅ SUCCESS - Returning {len(final_text)} chars", file=sys.stderr, flush=True)
                            print(f"[_call_openai] Preview: {final_text[:200]}...", file=sys.stderr, flush=True)
                            return final_text
                        elif text == '':
                            logger.warning("[_call_openai] ⚠️ OpenAI returned empty string")
                            print(f"[_call_openai] ⚠️ Empty string returned", file=sys.stderr, flush=True)
                            return None
                        else:
                            logger.error(f"[_call_openai] ❌ Invalid text value: {repr(text)}")
                            logger.error(f"[_call_openai] Full response for debugging:\n{json.dumps(response_data, indent=2, default=str)[:2000]}")
                            print(f"[_call_openai] ❌ Invalid text value: {repr(text)}", file=sys.stderr, flush=True)
                            return None
                    
                    else:
                        logger.error(f"[_call_openai] ❌ Response is not a dict: {type(response_data)}")
                        logger.error(f"[_call_openai] Response value: {str(response_data)[:500]}")
                        print(f"[_call_openai] ❌ Response not a dict: {type(response_data)}", file=sys.stderr, flush=True)
                        return None
                        
            except aiohttp.ClientError as e:
                error_msg = f"HTTP client error: {str(e)}"
                logger.error(f"[_call_openai] ❌ ClientError: {error_msg}", exc_info=True)
                print(f"[_call_openai] ❌ ClientError: {e}", file=sys.stderr, flush=True)
                raise Exception(error_msg)
            except asyncio.TimeoutError as e:
                error_msg = "OpenAI API request timed out after 30 seconds"
                logger.error(f"[_call_openai] ❌ Timeout: {error_msg}")
                print(f"[_call_openai] ❌ Timeout: {error_msg}", file=sys.stderr, flush=True)
                raise Exception(error_msg)
            except Exception as e:
                error_msg = f"Unexpected error calling OpenAI API: {str(e)}"
                logger.error(f"[_call_openai] ❌ Exception: {error_msg}", exc_info=True)
                print(f"[_call_openai] ❌ Exception: {e}", file=sys.stderr, flush=True)
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

