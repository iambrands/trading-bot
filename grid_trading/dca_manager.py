"""Dollar Cost Averaging (DCA) strategy manager."""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class DCAStrategy:
    """Dollar Cost Averaging strategy configuration."""
    
    def __init__(
        self,
        dca_id: str,
        pair: str,
        side: str,  # 'BUY' or 'SELL'
        amount: float,  # Amount to invest per interval
        interval: str,  # 'hourly', 'daily', 'weekly'
        total_amount: Optional[float] = None,  # Total to invest (optional limit)
        start_price: Optional[float] = None,
        end_price: Optional[float] = None  # Stop DCA at this price
    ):
        self.dca_id = dca_id
        self.pair = pair
        self.side = side
        self.amount = amount
        self.interval = interval
        self.total_amount = total_amount
        self.start_price = start_price
        self.end_price = end_price
        
        self.status = 'active'  # active, paused, stopped, completed
        self.created_at = datetime.utcnow()
        self.next_execution: Optional[datetime] = None
        self.total_invested = 0.0
        self.executions: List[Dict] = []
        
        # Calculate next execution time
        self._calculate_next_execution()
    
    def _calculate_next_execution(self):
        """Calculate next execution time based on interval."""
        now = datetime.utcnow()
        
        if self.interval == 'hourly':
            self.next_execution = now + timedelta(hours=1)
        elif self.interval == 'daily':
            self.next_execution = now + timedelta(days=1)
        elif self.interval == 'weekly':
            self.next_execution = now + timedelta(weeks=1)
        else:
            self.next_execution = now + timedelta(hours=1)  # Default hourly
    
    def should_execute(self) -> bool:
        """Check if it's time to execute the DCA order."""
        if self.status != 'active':
            return False
        
        if self.total_amount and self.total_invested >= self.total_amount:
            self.status = 'completed'
            return False
        
        if self.next_execution and datetime.utcnow() >= self.next_execution:
            return True
        
        return False
    
    def record_execution(self, price: float, size: float):
        """Record a DCA execution."""
        execution = {
            'timestamp': datetime.utcnow(),
            'price': price,
            'size': size,
            'amount': price * size
        }
        self.executions.append(execution)
        self.total_invested += execution['amount']
        self._calculate_next_execution()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DCA strategy to dictionary."""
        return {
            'dca_id': self.dca_id,
            'pair': self.pair,
            'side': self.side,
            'amount': float(self.amount),
            'interval': self.interval,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'start_price': float(self.start_price) if self.start_price else None,
            'end_price': float(self.end_price) if self.end_price else None,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'next_execution': self.next_execution.isoformat() if self.next_execution else None,
            'total_invested': float(self.total_invested),
            'execution_count': len(self.executions),
            'executions': [
                {
                    'timestamp': e['timestamp'].isoformat(),
                    'price': float(e['price']),
                    'size': float(e['size']),
                    'amount': float(e['amount'])
                }
                for e in self.executions[-10:]  # Last 10 executions
            ]
        }


class DCAManager:
    """Manages DCA strategies."""
    
    def __init__(self, exchange, config=None):
        self.exchange = exchange
        self.config = config
        self.strategies: Dict[str, DCAStrategy] = {}
        self.running = False
        self.monitor_task: Optional[asyncio.Task] = None
    
    async def create_dca(
        self,
        pair: str,
        side: str,
        amount: float,
        interval: str,
        total_amount: Optional[float] = None,
        start_price: Optional[float] = None,
        end_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Create a new DCA strategy."""
        dca_id = str(uuid.uuid4())
        
        try:
            strategy = DCAStrategy(
                dca_id=dca_id,
                pair=pair,
                side=side,
                amount=amount,
                interval=interval,
                total_amount=total_amount,
                start_price=start_price,
                end_price=end_price
            )
            
            self.strategies[dca_id] = strategy
            
            logger.info(f"Created DCA strategy {dca_id} for {pair}")
            
            return {
                'success': True,
                'dca_id': dca_id,
                'strategy': strategy.to_dict()
            }
        
        except Exception as e:
            logger.error(f"Failed to create DCA strategy: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    async def stop_dca(self, dca_id: str) -> bool:
        """Stop a DCA strategy."""
        if dca_id not in self.strategies:
            return False
        
        self.strategies[dca_id].status = 'stopped'
        logger.info(f"Stopped DCA strategy {dca_id}")
        return True
    
    async def pause_dca(self, dca_id: str) -> bool:
        """Pause a DCA strategy."""
        if dca_id not in self.strategies:
            return False
        
        self.strategies[dca_id].status = 'paused'
        logger.info(f"Paused DCA strategy {dca_id}")
        return True
    
    async def resume_dca(self, dca_id: str) -> bool:
        """Resume a paused DCA strategy."""
        if dca_id not in self.strategies:
            return False
        
        strategy = self.strategies[dca_id]
        if strategy.status == 'paused':
            strategy.status = 'active'
            logger.info(f"Resumed DCA strategy {dca_id}")
        return True
    
    async def get_dca(self, dca_id: str) -> Optional[Dict[str, Any]]:
        """Get DCA strategy details."""
        if dca_id not in self.strategies:
            return None
        
        return self.strategies[dca_id].to_dict()
    
    async def list_dca_strategies(
        self,
        pair: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List DCA strategies with optional filtering."""
        strategies = []
        
        for strategy in self.strategies.values():
            if pair and strategy.pair != pair:
                continue
            if status and strategy.status != status:
                continue
            
            strategies.append(strategy.to_dict())
        
        return strategies
    
    async def start_monitoring(self):
        """Start monitoring DCA strategies for execution times."""
        if self.running:
            return
        
        self.running = True
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("DCA monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring DCA strategies."""
        self.running = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("DCA monitoring stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop for DCA strategies."""
        while self.running:
            try:
                await self._check_strategies()
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in DCA monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _check_strategies(self):
        """Check all active DCA strategies for execution."""
        active_strategies = [s for s in self.strategies.values() if s.status == 'active']
        
        for strategy in active_strategies:
            try:
                if strategy.should_execute():
                    await self._execute_dca(strategy)
            except Exception as e:
                logger.error(f"Error checking DCA {strategy.dca_id}: {e}", exc_info=True)
    
    async def _execute_dca(self, strategy: DCAStrategy):
        """Execute a DCA order."""
        try:
            # Get current market price
            market_data = await self.exchange.get_market_data([strategy.pair])
            if strategy.pair not in market_data:
                logger.warning(f"Could not get market price for {strategy.pair}")
                return
            
            current_price = market_data[strategy.pair].get('price', 0)
            
            # Check price limits
            if strategy.end_price:
                if strategy.side == 'BUY' and current_price > strategy.end_price:
                    strategy.status = 'stopped'
                    logger.info(f"DCA {strategy.dca_id} stopped - price above end_price")
                    return
                elif strategy.side == 'SELL' and current_price < strategy.end_price:
                    strategy.status = 'stopped'
                    logger.info(f"DCA {strategy.dca_id} stopped - price below end_price")
                    return
            
            # Calculate order size
            if strategy.side == 'BUY':
                # Buying with USD amount
                size = strategy.amount / current_price
                quote_size = strategy.amount
            else:
                # Selling base currency
                size = strategy.amount / current_price
                quote_size = None
            
            logger.info(f"Executing DCA order: {strategy.pair} {strategy.side} {size} at {current_price}")
            
            # Place order
            result = await self.exchange.place_order(
                strategy.pair,
                strategy.side,
                size if strategy.side == 'SELL' else 0,
                quote_size if strategy.side == 'BUY' else None
            )
            
            # Record execution
            strategy.record_execution(current_price, size)
            
            logger.info(f"DCA order executed successfully")
            
        except Exception as e:
            logger.error(f"Failed to execute DCA order: {e}", exc_info=True)




