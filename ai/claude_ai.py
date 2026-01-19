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
    
    async def _call_claude(self, prompt: str) -> str:
        """Make API call to Claude AI."""
        import sys
        
        logger.info("=== CLAUDE AI REQUEST ===")
        logger.info(f"API Key present: {bool(self.api_key)}")
        logger.info(f"API Key length: {len(self.api_key) if self.api_key else 0}")
        logger.info(f"Model: {self.model}")
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"Prompt length: {len(prompt)} characters")
        print(f"[_call_claude] Starting Claude API call...", file=sys.stderr, flush=True)
        
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
                logger.info(f"Sending request to {self.base_url}/messages")
                print(f"[_call_claude] POST {self.base_url}/messages", file=sys.stderr, flush=True)
                
                async with session.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    logger.info(f"Claude API response status: {response.status}")
                    print(f"[_call_claude] Response status: {response.status}", file=sys.stderr, flush=True)
                    
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Claude API error {response.status}: {error_text}")
                        print(f"[_call_claude] ❌ Error {response.status}: {error_text[:200]}", file=sys.stderr, flush=True)
                        # Provide more detailed error messages
                        if response.status == 401:
                            raise Exception("Invalid API key. Please check your CLAUDE_API_KEY.")
                        elif response.status == 429:
                            raise Exception("Rate limit exceeded. Please try again later.")
                        elif response.status == 500:
                            raise Exception("Claude API server error. Please try again later.")
                        else:
                            raise Exception(f"Claude API error {response.status}: {error_text[:200]}")
                    
                    # Parse response
                    logger.info("Parsing Claude API response...")
                    result = await response.json()
                    
                    logger.info("=== CLAUDE AI RESPONSE ===")
                    logger.info(f"Response type: {type(result)}")
                    logger.info(f"Response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                    
                    # Log full response structure for debugging (without exposing sensitive data)
                    if isinstance(result, dict):
                        logger.info(f"Response has 'content' key: {'content' in result}")
                        logger.info(f"Response has 'id' key: {'id' in result}")
                        logger.info(f"Response has 'model' key: {'model' in result}")
                        
                        # Check content structure
                        content = result.get('content', [])
                        logger.info(f"Content type: {type(content)}")
                        logger.info(f"Content length: {len(content) if isinstance(content, (list, str)) else 'N/A'}")
                        
                        print(f"[_call_claude] Response structure: keys={list(result.keys())}", file=sys.stderr, flush=True)
                        print(f"[_call_claude] Content type: {type(content)}, length: {len(content) if isinstance(content, list) else 'N/A'}", file=sys.stderr, flush=True)
                        
                        # Extract text from response - handle different response formats
                        if isinstance(content, list) and len(content) > 0:
                            first_item = content[0]
                            logger.info(f"First content item type: {type(first_item)}")
                            logger.info(f"First content item keys: {list(first_item.keys()) if isinstance(first_item, dict) else 'Not a dict'}")
                            
                            # Handle both old and new API response formats
                            if isinstance(first_item, dict):
                                # Try 'text' key first (newer format)
                                text = first_item.get('text', '')
                                if text:
                                    logger.info(f"Extracted text from 'text' key: {len(text)} characters")
                                    print(f"[_call_claude] ✅ Extracted text: {len(text)} chars", file=sys.stderr, flush=True)
                                    return text
                                
                                # Try 'content' key (alternative format)
                                nested_content = first_item.get('content', '')
                                if nested_content:
                                    logger.info(f"Extracted text from nested 'content' key: {len(nested_content)} characters")
                                    print(f"[_call_claude] ✅ Extracted text from nested content: {len(nested_content)} chars", file=sys.stderr, flush=True)
                                    return nested_content
                                
                                # Log what keys we have
                                logger.warning(f"No 'text' or 'content' key found in first item. Available keys: {list(first_item.keys())}")
                                print(f"[_call_claude] ⚠️ No text found in first item. Keys: {list(first_item.keys())}", file=sys.stderr, flush=True)
                            elif isinstance(first_item, str):
                                # Content might be a string directly
                                logger.info(f"Content is a string: {len(first_item)} characters")
                                print(f"[_call_claude] ✅ Content is string: {len(first_item)} chars", file=sys.stderr, flush=True)
                                return first_item
                        elif isinstance(content, str):
                            # Content might be a string directly (some API versions)
                            logger.info(f"Content is a string (not array): {len(content)} characters")
                            print(f"[_call_claude] ✅ Content is string: {len(content)} chars", file=sys.stderr, flush=True)
                            return content
                        else:
                            logger.error(f"Unexpected content format: {type(content)}")
                            logger.error(f"Content value: {str(content)[:500]}")
                            print(f"[_call_claude] ❌ Unexpected content format: {type(content)}", file=sys.stderr, flush=True)
                            print(f"[_call_claude] ❌ Content: {str(content)[:200]}", file=sys.stderr, flush=True)
                        
                        # If we get here, we couldn't extract text
                        logger.error("Failed to extract text from Claude API response")
                        logger.error(f"Full response structure: {json.dumps(result, indent=2)[:1000]}")
                        print(f"[_call_claude] ❌ Failed to extract text from response", file=sys.stderr, flush=True)
                        return None  # Return None so the endpoint can handle it properly
                    else:
                        logger.error(f"Response is not a dict: {type(result)}")
                        print(f"[_call_claude] ❌ Response not a dict: {type(result)}", file=sys.stderr, flush=True)
                        return None
                        
            except aiohttp.ClientError as e:
                error_msg = f"HTTP client error: {str(e)}"
                logger.error(error_msg, exc_info=True)
                print(f"[_call_claude] ❌ ClientError: {e}", file=sys.stderr, flush=True)
                raise Exception(error_msg)
            except asyncio.TimeoutError as e:
                error_msg = "Claude API request timed out after 30 seconds"
                logger.error(error_msg)
                print(f"[_call_claude] ❌ Timeout: {error_msg}", file=sys.stderr, flush=True)
                raise Exception(error_msg)
            except Exception as e:
                error_msg = f"Unexpected error calling Claude API: {str(e)}"
                logger.error(error_msg, exc_info=True)
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

