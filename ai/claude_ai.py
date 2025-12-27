"""Claude AI integration for market analysis and user guidance."""

import logging
from typing import Optional, Dict, Any
import aiohttp
import json
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
            
            async with session.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Claude API error {response.status}: {error_text}")
                    # Provide more detailed error messages
                    if response.status == 401:
                        raise Exception("Invalid API key. Please check your CLAUDE_API_KEY.")
                    elif response.status == 429:
                        raise Exception("Rate limit exceeded. Please try again later.")
                    elif response.status == 500:
                        raise Exception("Claude API server error. Please try again later.")
                    else:
                        raise Exception(f"Claude API error {response.status}: {error_text[:200]}")
                
                result = await response.json()
                
                # Extract text from response
                content = result.get('content', [])
                if content and len(content) > 0:
                    return content[0].get('text', '')
                
                return "No response from AI"
    
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

