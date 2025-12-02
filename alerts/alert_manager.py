"""Alert manager for sending notifications via multiple channels."""

import logging
from typing import Optional, Dict, Any
from config import get_config

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages alerts via Slack, Telegram, and Email."""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.slack_webhook_url = self.config.SLACK_WEBHOOK_URL
        self.telegram_bot_token = self.config.TELEGRAM_BOT_TOKEN
        self.telegram_chat_id = self.config.TELEGRAM_CHAT_ID
        
        # Initialize alert channels
        self.slack_enabled = bool(self.slack_webhook_url)
        self.telegram_enabled = bool(self.telegram_bot_token and self.telegram_chat_id)
        self.email_enabled = False  # Will implement later
        
        logger.info(f"AlertManager initialized - Slack: {self.slack_enabled}, Telegram: {self.telegram_enabled}")
    
    async def send_alert(self, message: str, alert_type: str = 'info', title: Optional[str] = None):
        """Send alert via all enabled channels."""
        results = {}
        
        if self.slack_enabled:
            results['slack'] = await self._send_slack(message, alert_type, title)
        
        if self.telegram_enabled:
            results['telegram'] = await self._send_telegram(message, alert_type, title)
        
        if self.email_enabled:
            results['email'] = await self._send_email(message, alert_type, title)
        
        return results
    
    async def send_trade_alert(self, trade_data: Dict[str, Any]):
        """Send alert for trade execution."""
        side = trade_data.get('side', 'UNKNOWN')
        pair = trade_data.get('pair', 'UNKNOWN')
        entry_price = trade_data.get('entry_price', 0)
        size = trade_data.get('size', 0)
        pnl = trade_data.get('pnl', 0)
        
        emoji = "📈" if side == 'LONG' else "📉"
        pnl_emoji = "✅" if pnl > 0 else "❌"
        
        message = f"{emoji} Trade Executed\n\n"
        message += f"Pair: {pair}\n"
        message += f"Side: {side}\n"
        message += f"Entry: ${entry_price:.2f}\n"
        message += f"Size: {size:.6f}\n"
        if pnl != 0:
            message += f"P&L: {pnl_emoji} ${pnl:.2f}"
        
        return await self.send_alert(message, 'trade', f'Trade Executed - {pair}')
    
    async def send_error_alert(self, error_message: str, error_type: str = 'API'):
        """Send alert for errors."""
        message = f"🚨 Error Alert\n\n"
        message += f"Type: {error_type}\n"
        message += f"Message: {error_message}"
        
        return await self.send_alert(message, 'error', f'{error_type} Error')
    
    async def send_daily_summary(self, summary_data: Dict[str, Any]):
        """Send daily P&L summary."""
        daily_pnl = summary_data.get('daily_pnl', 0)
        total_trades = summary_data.get('total_trades', 0)
        win_rate = summary_data.get('win_rate', 0)
        
        emoji = "📊"
        if daily_pnl > 0:
            emoji = "💰"
        elif daily_pnl < 0:
            emoji = "📉"
        
        message = f"{emoji} Daily Trading Summary\n\n"
        message += f"Daily P&L: ${daily_pnl:.2f}\n"
        message += f"Total Trades: {total_trades}\n"
        message += f"Win Rate: {win_rate:.2f}%"
        
        return await self.send_alert(message, 'summary', 'Daily Trading Summary')
    
    async def send_risk_alert(self, risk_message: str):
        """Send alert for risk threshold breaches."""
        message = f"⚠️ Risk Alert\n\n{risk_message}"
        return await self.send_alert(message, 'warning', 'Risk Threshold Breached')
    
    async def _send_slack(self, message: str, alert_type: str, title: Optional[str] = None):
        """Send alert via Slack webhook."""
        if not self.slack_webhook_url:
            return False
        
        try:
            import aiohttp
            
            color_map = {
                'info': '#36a64f',
                'error': '#ff0000',
                'warning': '#ff9900',
                'trade': '#0099cc',
                'summary': '#36a64f'
            }
            
            payload = {
                'text': title or 'TradingBot Alert',
                'attachments': [{
                    'color': color_map.get(alert_type, '#36a64f'),
                    'text': message,
                    'ts': int(__import__('time').time())
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.slack_webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        logger.debug("Slack alert sent successfully")
                        return True
                    else:
                        logger.warning(f"Slack alert failed with status {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}", exc_info=True)
            return False
    
    async def _send_telegram(self, message: str, alert_type: str, title: Optional[str] = None):
        """Send alert via Telegram bot."""
        if not self.telegram_bot_token or not self.telegram_chat_id:
            return False
        
        try:
            import aiohttp
            
            full_message = f"*{title or 'TradingBot Alert'}*\n\n{message}"
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': full_message,
                'parse_mode': 'Markdown'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        logger.debug("Telegram alert sent successfully")
                        return True
                    else:
                        result = await response.json()
                        logger.warning(f"Telegram alert failed: {result}")
                        return False
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}", exc_info=True)
            return False
    
    async def _send_email(self, message: str, alert_type: str, title: Optional[str] = None):
        """Send alert via email (SMTP)."""
        # TODO: Implement email alerts
        logger.debug("Email alerts not yet implemented")
        return False

