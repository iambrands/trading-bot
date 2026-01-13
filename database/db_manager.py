"""PostgreSQL database manager for trade and performance storage."""

import json
import logging
import asyncio
from datetime import datetime, date
from typing import Optional, List, Dict, Any
import asyncpg
from config import get_config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.pool: Optional[asyncpg.Pool] = None
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize database connection pool and create tables."""
        try:
            self.pool = await asyncpg.create_pool(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                database=self.config.DB_NAME,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD,
                min_size=2,
                max_size=10
            )
            
            async with self.pool.acquire() as conn:
                await self._create_tables(conn)
            
            self.initialized = True
            logger.info("Database initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}", exc_info=True)
            self.initialized = False
            return False
    
    async def _create_tables(self, conn):
        """Create database tables if they don't exist."""
        # Users table for authentication
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                onboarding_completed BOOLEAN DEFAULT FALSE,
                onboarding_completed_at TIMESTAMP,
                disclaimer_acknowledged_at TIMESTAMP
            )
        """)
        
        # Add onboarding columns if they don't exist (for existing databases)
        try:
            await conn.execute("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN DEFAULT FALSE
            """)
        except Exception as e:
            logger.debug(f"onboarding_completed column may already exist: {e}")
        
        try:
            await conn.execute("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS onboarding_completed_at TIMESTAMP
            """)
        except Exception as e:
            logger.debug(f"onboarding_completed_at column may already exist: {e}")
        
        try:
            await conn.execute("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS disclaimer_acknowledged_at TIMESTAMP
            """)
        except Exception as e:
            logger.debug(f"disclaimer_acknowledged_at column may already exist: {e}")
        
        # Trades table - check if user_id column exists, add if not
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id SERIAL PRIMARY KEY,
                pair VARCHAR(20) NOT NULL,
                side VARCHAR(10) NOT NULL,
                entry_price DECIMAL(20, 8) NOT NULL,
                exit_price DECIMAL(20, 8),
                size DECIMAL(20, 8) NOT NULL,
                entry_time TIMESTAMP NOT NULL,
                exit_time TIMESTAMP,
                stop_loss DECIMAL(20, 8),
                take_profit DECIMAL(20, 8),
                pnl DECIMAL(20, 8),
                pnl_pct DECIMAL(10, 4),
                exit_reason VARCHAR(50),
                order_id VARCHAR(100),
                confidence_score DECIMAL(5, 2),
                notes TEXT,
                tags TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add journaling columns if they don't exist (for existing databases)
        try:
            await conn.execute("""
                ALTER TABLE trades 
                ADD COLUMN IF NOT EXISTS notes TEXT
            """)
        except Exception as e:
            logger.debug(f"notes column may already exist: {e}")
        
        try:
            await conn.execute("""
                ALTER TABLE trades 
                ADD COLUMN IF NOT EXISTS tags TEXT[]
            """)
        except Exception as e:
            logger.debug(f"tags column may already exist: {e}")
        
        # Add user_id column if it doesn't exist (for existing databases)
        try:
            await conn.execute("""
                ALTER TABLE trades 
                ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
            """)
        except Exception as e:
            logger.debug(f"user_id column may already exist or users table not ready: {e}")
            # If users table doesn't exist yet, we'll add it later - no error
            pass
        
        # Performance metrics table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL UNIQUE,
                account_balance DECIMAL(20, 8) NOT NULL,
                daily_pnl DECIMAL(20, 8) NOT NULL,
                total_trades INTEGER NOT NULL,
                winning_trades INTEGER NOT NULL,
                losing_trades INTEGER NOT NULL,
                win_rate DECIMAL(5, 2),
                profit_factor DECIMAL(10, 4),
                sharpe_ratio DECIMAL(10, 4),
                max_drawdown DECIMAL(10, 4),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # System logs table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id SERIAL PRIMARY KEY,
                log_level VARCHAR(20) NOT NULL,
                message TEXT NOT NULL,
                details JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Advanced orders table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS advanced_orders (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                order_id VARCHAR(255) NOT NULL UNIQUE,
                order_type VARCHAR(50) NOT NULL,
                pair VARCHAR(20) NOT NULL,
                side VARCHAR(10) NOT NULL,
                size DECIMAL(20, 8) NOT NULL,
                filled_size DECIMAL(20, 8) DEFAULT 0,
                status VARCHAR(20) NOT NULL,
                order_data JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                filled_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Grid trading strategies table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS grid_strategies (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                grid_id VARCHAR(255) NOT NULL UNIQUE,
                pair VARCHAR(20) NOT NULL,
                lower_price DECIMAL(20, 8) NOT NULL,
                upper_price DECIMAL(20, 8) NOT NULL,
                grid_count INTEGER NOT NULL,
                order_size DECIMAL(20, 8) NOT NULL,
                side VARCHAR(10) NOT NULL,
                status VARCHAR(20) NOT NULL,
                grid_data JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # DCA strategies table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS dca_strategies (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                dca_id VARCHAR(255) NOT NULL UNIQUE,
                pair VARCHAR(20) NOT NULL,
                side VARCHAR(10) NOT NULL,
                amount DECIMAL(20, 8) NOT NULL,
                interval VARCHAR(20) NOT NULL,
                total_amount DECIMAL(20, 8),
                start_price DECIMAL(20, 8),
                end_price DECIMAL(20, 8),
                status VARCHAR(20) NOT NULL,
                total_invested DECIMAL(20, 8) DEFAULT 0,
                execution_count INTEGER DEFAULT 0,
                strategy_data JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                next_execution TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Backtests table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS backtests (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(255),
                pair VARCHAR(20) NOT NULL,
                start_date TIMESTAMP NOT NULL,
                end_date TIMESTAMP NOT NULL,
                initial_balance DECIMAL(20, 8) NOT NULL,
                final_balance DECIMAL(20, 8) NOT NULL,
                total_pnl DECIMAL(20, 8) NOT NULL,
                total_trades INTEGER NOT NULL,
                winning_trades INTEGER NOT NULL,
                losing_trades INTEGER NOT NULL,
                win_rate DECIMAL(5, 2),
                profit_factor DECIMAL(10, 4),
                max_drawdown DECIMAL(10, 4),
                roi_pct DECIMAL(10, 4),
                results JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_trades_user_id ON trades(user_id);
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_trades_pair ON trades(pair);
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_trades_entry_time ON trades(entry_time);
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_performance_date ON performance_metrics(date);
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_logs_level ON system_logs(log_level);
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_backtests_user_id ON backtests(user_id);
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_backtests_created_at ON backtests(created_at);
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_advanced_orders_user_id ON advanced_orders(user_id);
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_advanced_orders_status ON advanced_orders(status);
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_advanced_orders_pair ON advanced_orders(pair);
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_grid_strategies_user_id ON grid_strategies(user_id);
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_grid_strategies_status ON grid_strategies(status);
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_dca_strategies_user_id ON dca_strategies(user_id);
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_dca_strategies_status ON dca_strategies(status);
        """)
        
        logger.info("Database tables created/verified")
    
    async def close(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    async def save_trade(self, trade_data: Dict[str, Any]) -> Optional[int]:
        """Save a new trade to the database."""
        if not self.initialized or not self.pool:
            logger.warning("Database not initialized, skipping trade save")
            return None
        
        try:
            async with self.pool.acquire() as conn:
                trade_id = await conn.fetchval("""
                    INSERT INTO trades (
                        pair, side, entry_price, size, entry_time,
                        stop_loss, take_profit, order_id, confidence_score
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    RETURNING id
                """,
                    trade_data['pair'],
                    trade_data['side'],
                    trade_data['entry_price'],
                    trade_data['size'],
                    trade_data.get('entry_time', datetime.utcnow()),
                    trade_data.get('stop_loss'),
                    trade_data.get('take_profit'),
                    trade_data.get('order_id'),
                    trade_data.get('confidence_score')
                )
                logger.debug(f"Saved trade {trade_id} to database")
                return trade_id
        except Exception as e:
            logger.error(f"Failed to save trade: {e}", exc_info=True)
            return None
    
    async def update_trade(self, trade_id: int, exit_data: Dict[str, Any]) -> bool:
        """Update trade with exit information."""
        if not self.initialized or not self.pool:
            logger.warning("Database not initialized, skipping trade update")
            return False
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE trades SET
                        exit_price = $1,
                        exit_time = $2,
                        pnl = $3,
                        pnl_pct = $4,
                        exit_reason = $5
                    WHERE id = $6
                """,
                    exit_data.get('exit_price'),
                    exit_data.get('exit_time', datetime.utcnow()),
                    exit_data.get('pnl'),
                    exit_data.get('pnl_pct'),
                    exit_data.get('exit_reason'),
                    trade_id
                )
                logger.debug(f"Updated trade {trade_id} with exit data")
                return True
        except Exception as e:
            logger.error(f"Failed to update trade {trade_id}: {e}", exc_info=True)
            return False
    
    async def get_recent_trades(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch recent trades from database."""
        if not self.initialized or not self.pool:
            return []
        
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM trades
                    ORDER BY entry_time DESC
                    LIMIT $1
                """, limit)
                
                trades = []
                from decimal import Decimal
                for row in rows:
                    trade = dict(row)
                    # Convert Decimal to float
                    for key, value in trade.items():
                        if isinstance(value, Decimal):
                            trade[key] = float(value)
                        # Handle tags array
                        if key == 'tags' and value is not None:
                            trade[key] = list(value) if not isinstance(value, list) else value
                        elif key == 'tags' and value is None:
                            trade[key] = []
                    trades.append(trade)
                return trades
        except Exception as e:
            logger.error(f"Failed to fetch recent trades: {e}", exc_info=True)
            return []
    
    async def get_trades_with_date_range(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch trades with optional date range filtering."""
        if not self.initialized or not self.pool:
            return []
        
        try:
            async with self.pool.acquire() as conn:
                query = "SELECT * FROM trades WHERE 1=1"
                params = []
                param_index = 1
                
                if user_id:
                    query += f" AND (user_id = ${param_index} OR user_id IS NULL)"
                    params.append(user_id)
                    param_index += 1
                
                if start_date:
                    query += f" AND entry_time >= ${param_index}"
                    params.append(start_date)
                    param_index += 1
                
                if end_date:
                    query += f" AND entry_time <= ${param_index}"
                    params.append(end_date)
                    param_index += 1
                
                query += " ORDER BY entry_time DESC"
                
                rows = await conn.fetch(query, *params)
                trades = []
                from decimal import Decimal
                for row in rows:
                    trade = dict(row)
                    # Convert Decimal to float
                    for key, value in trade.items():
                        if isinstance(value, Decimal):
                            trade[key] = float(value)
                        # Handle tags array
                        if key == 'tags' and value is not None:
                            trade[key] = list(value) if not isinstance(value, list) else value
                        elif key == 'tags' and value is None:
                            trade[key] = []
                    trades.append(trade)
                return trades
        except Exception as e:
            logger.error(f"Failed to fetch trades with date range: {e}", exc_info=True)
            return []
    
    async def update_trade_journal(self, trade_id: int, notes: Optional[str] = None, tags: Optional[List[str]] = None, user_id: Optional[int] = None) -> bool:
        """Update trade notes and/or tags."""
        if not self.initialized or not self.pool:
            logger.warning("Database not initialized, skipping journal update")
            return False
        
        try:
            async with self.pool.acquire() as conn:
                set_clauses = []
                params = []
                param_index = 1
                
                if notes is not None:
                    set_clauses.append(f"notes = ${param_index}")
                    params.append(notes)
                    param_index += 1
                
                if tags is not None:
                    set_clauses.append(f"tags = ${param_index}")
                    params.append(tags)
                    param_index += 1
                
                if not set_clauses:
                    return False
                
                if user_id:
                    query = f"UPDATE trades SET {', '.join(set_clauses)} WHERE id = ${param_index} AND (user_id = ${param_index + 1} OR user_id IS NULL)"
                    params.append(trade_id)
                    params.append(user_id)
                else:
                    query = f"UPDATE trades SET {', '.join(set_clauses)} WHERE id = ${param_index}"
                    params.append(trade_id)
                
                await conn.execute(query, *params)
                logger.debug(f"Updated journal for trade {trade_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to update trade journal: {e}", exc_info=True)
            return False
    
    async def get_trade_by_id(self, trade_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get a single trade by ID."""
        if not self.initialized or not self.pool:
            return None
        
        try:
            async with self.pool.acquire() as conn:
                if user_id:
                    row = await conn.fetchrow("""
                        SELECT * FROM trades
                        WHERE id = $1 AND (user_id = $2 OR user_id IS NULL)
                    """, trade_id, user_id)
                else:
                    row = await conn.fetchrow("""
                        SELECT * FROM trades
                        WHERE id = $1
                    """, trade_id)
                
                if row:
                    trade = dict(row)
                    # Convert Decimal to float and handle tags array
                    from decimal import Decimal
                    for key, value in trade.items():
                        if isinstance(value, Decimal):
                            trade[key] = float(value)
                        # Tags come as a list from PostgreSQL, ensure it's a proper list
                        if key == 'tags' and value is not None:
                            if isinstance(value, list):
                                trade[key] = value
                            else:
                                trade[key] = list(value) if value else []
                        elif key == 'tags' and value is None:
                            trade[key] = []
                    return trade
                return None
        except Exception as e:
            logger.error(f"Failed to get trade by ID: {e}", exc_info=True)
            return None
    
    async def get_trades_with_tags(self, tags: List[str], user_id: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get trades that have any of the specified tags."""
        if not self.initialized or not self.pool:
            return []
        
        try:
            async with self.pool.acquire() as conn:
                if user_id:
                    rows = await conn.fetch("""
                        SELECT * FROM trades
                        WHERE (user_id = $1 OR user_id IS NULL)
                        AND tags && $2
                        ORDER BY entry_time DESC
                        LIMIT $3
                    """, user_id, tags, limit)
                else:
                    rows = await conn.fetch("""
                        SELECT * FROM trades
                        WHERE tags && $1
                        ORDER BY entry_time DESC
                        LIMIT $2
                    """, tags, limit)
                
                trades = []
                from decimal import Decimal
                for row in rows:
                    trade = dict(row)
                    for key, value in trade.items():
                        if isinstance(value, Decimal):
                            trade[key] = float(value)
                    trades.append(trade)
                return trades
        except Exception as e:
            logger.error(f"Failed to fetch trades with tags: {e}", exc_info=True)
            return []
    
    async def get_journal_analytics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get analytics for trade journal (tag statistics, pattern recognition)."""
        if not self.initialized or not self.pool:
            return {}
        
        try:
            async with self.pool.acquire() as conn:
                # Get all trades with tags
                if user_id:
                    rows = await conn.fetch("""
                        SELECT tags, pnl, pnl_pct, exit_reason
                        FROM trades
                        WHERE (user_id = $1 OR user_id IS NULL)
                        AND tags IS NOT NULL
                        AND array_length(tags, 1) > 0
                    """, user_id)
                else:
                    rows = await conn.fetch("""
                        SELECT tags, pnl, pnl_pct, exit_reason
                        FROM trades
                        WHERE tags IS NOT NULL
                        AND array_length(tags, 1) > 0
                    """)
                
                # Aggregate tag statistics
                tag_stats = {}
                from decimal import Decimal
                
                for row in rows:
                    tags = row['tags'] or []
                    pnl = float(row['pnl']) if row['pnl'] else 0
                    pnl_pct = float(row['pnl_pct']) if row['pnl_pct'] else 0
                    
                    for tag in tags:
                        if tag not in tag_stats:
                            tag_stats[tag] = {
                                'count': 0,
                                'wins': 0,
                                'losses': 0,
                                'total_pnl': 0.0,
                                'total_pnl_pct': 0.0,
                                'avg_pnl_pct': 0.0,
                                'win_rate': 0.0
                            }
                        
                        tag_stats[tag]['count'] += 1
                        tag_stats[tag]['total_pnl'] += pnl
                        tag_stats[tag]['total_pnl_pct'] += pnl_pct
                        
                        if pnl > 0:
                            tag_stats[tag]['wins'] += 1
                        elif pnl < 0:
                            tag_stats[tag]['losses'] += 1
                
                # Calculate win rates and averages
                for tag, stats in tag_stats.items():
                    if stats['count'] > 0:
                        stats['win_rate'] = (stats['wins'] / stats['count']) * 100
                        stats['avg_pnl_pct'] = stats['total_pnl_pct'] / stats['count']
                
                return {
                    'tag_statistics': tag_stats,
                    'total_tagged_trades': len(rows)
                }
        except Exception as e:
            logger.error(f"Failed to get journal analytics: {e}", exc_info=True)
            return {}
    
    async def save_performance_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Save daily performance metrics."""
        if not self.initialized or not self.pool:
            logger.warning("Database not initialized, skipping metrics save")
            return False
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO performance_metrics (
                        date, account_balance, daily_pnl, total_trades,
                        winning_trades, losing_trades, win_rate,
                        profit_factor, sharpe_ratio, max_drawdown
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    ON CONFLICT (date) DO UPDATE SET
                        account_balance = EXCLUDED.account_balance,
                        daily_pnl = EXCLUDED.daily_pnl,
                        total_trades = EXCLUDED.total_trades,
                        winning_trades = EXCLUDED.winning_trades,
                        losing_trades = EXCLUDED.losing_trades,
                        win_rate = EXCLUDED.win_rate,
                        profit_factor = EXCLUDED.profit_factor,
                        sharpe_ratio = EXCLUDED.sharpe_ratio,
                        max_drawdown = EXCLUDED.max_drawdown
                """,
                    metrics.get('date', datetime.utcnow().date()),
                    metrics.get('account_balance'),
                    metrics.get('daily_pnl'),
                    metrics.get('total_trades', 0),
                    metrics.get('winning_trades', 0),
                    metrics.get('losing_trades', 0),
                    metrics.get('win_rate'),
                    metrics.get('profit_factor'),
                    metrics.get('sharpe_ratio'),
                    metrics.get('max_drawdown')
                )
                logger.debug("Saved performance metrics to database")
                return True
        except Exception as e:
            logger.error(f"Failed to save performance metrics: {e}", exc_info=True)
            return False
    
    async def log_event(self, level: str, message: str, details: Optional[Dict] = None) -> bool:
        """Log system event to database."""
        if not self.initialized or not self.pool:
            return False
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO system_logs (log_level, message, details)
                    VALUES ($1, $2, $3)
                """,
                    level,
                    message,
                    json.dumps(details) if details else None
                )
                return True
        except Exception as e:
            logger.error(f"Failed to log event to database: {e}", exc_info=True)
            return False
    
    # User Authentication Methods
    async def create_user(self, email: str, password_hash: str, full_name: Optional[str] = None) -> Optional[int]:
        """Create a new user account."""
        if not self.initialized or not self.pool:
            logger.warning("Database not initialized, cannot create user")
            return None
        
        try:
            async with self.pool.acquire() as conn:
                user_id = await conn.fetchval("""
                    INSERT INTO users (email, password_hash, full_name)
                    VALUES ($1, $2, $3)
                    RETURNING id
                """, email.lower(), password_hash, full_name)
                logger.info(f"Created user {user_id} with email {email}")
                return user_id
        except asyncpg.UniqueViolationError:
            logger.warning(f"User with email {email} already exists")
            return None
        except Exception as e:
            logger.error(f"Failed to create user: {e}", exc_info=True)
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        if not self.initialized or not self.pool:
            return None
        
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT id, email, password_hash, full_name, is_active, created_at, last_login,
                           onboarding_completed, onboarding_completed_at, disclaimer_acknowledged_at
                    FROM users
                    WHERE email = $1
                """, email.lower())
                
                if row:
                    return dict(row)
                return None
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}", exc_info=True)
            return None
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        if not self.initialized or not self.pool:
            return None
        
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT id, email, password_hash, full_name, is_active, created_at, last_login,
                           onboarding_completed, onboarding_completed_at, disclaimer_acknowledged_at
                    FROM users
                    WHERE id = $1
                """, user_id)
                
                if row:
                    return dict(row)
                return None
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}", exc_info=True)
            return None
    
    # Backtest Methods
    async def save_backtest(self, backtest_data: Dict[str, Any], user_id: Optional[int] = None) -> Optional[int]:
        """Save backtest results to database."""
        if not self.initialized or not self.pool:
            logger.error(f"❌ Database not initialized or pool is None. initialized={self.initialized}, pool={self.pool is not None}")
            return None
        
        try:
            logger.info(f"💾💾💾 save_backtest called: name={backtest_data.get('name')}, user_id={user_id}, pair={backtest_data.get('pair')}")
            
            async with self.pool.acquire() as conn:
                logger.info(f"💾💾💾 Database connection acquired. About to INSERT backtest with user_id={user_id} (type: {type(user_id)})")
                
                # Serialize results to JSON, handling any Infinity/NaN that might have slipped through
                results_json = backtest_data.get('results', {})
                try:
                    results_json_str = json.dumps(results_json)
                    logger.info(f"💾💾💾 Successfully serialized results to JSON (length: {len(results_json_str)})")
                except (ValueError, TypeError) as json_error:
                    logger.error(f"❌❌❌ Failed to serialize results to JSON: {json_error}")
                    logger.error(f"   results type: {type(results_json)}, keys: {list(results_json.keys()) if isinstance(results_json, dict) else 'N/A'}")
                    # Try to sanitize and retry
                    def sanitize_for_json(obj):
                        # Handle datetime/date objects
                        if isinstance(obj, (datetime, date)):
                            return obj.isoformat()
                        # Handle floats (Infinity/NaN)
                        elif isinstance(obj, float):
                            if obj == float('inf') or obj == float('-inf'):
                                return None
                            if obj != obj:  # NaN
                                return None
                            return obj
                        elif isinstance(obj, dict):
                            return {k: sanitize_for_json(v) for k, v in obj.items()}
                        elif isinstance(obj, list):
                            return [sanitize_for_json(item) for item in obj]
                        return obj
                    results_json = sanitize_for_json(results_json)
                    results_json_str = json.dumps(results_json)
                    logger.info(f"💾💾💾 Successfully serialized after sanitization (length: {len(results_json_str)})")
                
                # Ensure start_date and end_date are datetime objects, not strings
                start_date = backtest_data.get('start_date')
                end_date = backtest_data.get('end_date')
                
                # Convert string dates back to datetime if needed (shouldn't happen, but safety check)
                if isinstance(start_date, str):
                    logger.warning(f"⚠️ start_date is a string, converting to datetime: {start_date}")
                    from dateutil.parser import parse as parse_date
                    start_date = parse_date(start_date)
                if isinstance(end_date, str):
                    logger.warning(f"⚠️ end_date is a string, converting to datetime: {end_date}")
                    from dateutil.parser import parse as parse_date
                    end_date = parse_date(end_date)
                
                logger.info(f"💾💾💾 Inserting with start_date type: {type(start_date)}, end_date type: {type(end_date)}")
                
                backtest_id = await conn.fetchval("""
                    INSERT INTO backtests (
                        user_id, name, pair, start_date, end_date,
                        initial_balance, final_balance, total_pnl,
                        total_trades, winning_trades, losing_trades,
                        win_rate, profit_factor, max_drawdown, roi_pct, results
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                    RETURNING id
                """,
                    user_id,  # If None, will be NULL in database
                    backtest_data.get('name'),
                    backtest_data.get('pair'),
                    start_date,  # Now guaranteed to be datetime object
                    end_date,  # Now guaranteed to be datetime object
                    backtest_data.get('initial_balance'),
                    backtest_data.get('final_balance'),
                    backtest_data.get('total_pnl'),
                    backtest_data.get('total_trades', 0),
                    backtest_data.get('winning_trades', 0),
                    backtest_data.get('losing_trades', 0),
                    backtest_data.get('win_rate'),
                    backtest_data.get('profit_factor'),
                    backtest_data.get('max_drawdown'),
                    backtest_data.get('roi_pct'),
                    results_json_str  # Use the already-serialized JSON string
                )
                
                if backtest_id:
                    logger.info(f"✅✅✅✅✅✅ BACKTEST SAVED TO DATABASE! ID: {backtest_id}, user_id: {user_id}, name: {backtest_data.get('name')}")
                else:
                    logger.error(f"❌❌❌❌❌❌ INSERT RETURNED NONE - backtest NOT saved (user_id: {user_id}, name: {backtest_data.get('name')})")
                
                return backtest_id
        except Exception as e:
            logger.error(f"❌❌❌❌❌❌ EXCEPTION IN save_backtest: {e}", exc_info=True)
            logger.error(f"   user_id: {user_id}, name: {backtest_data.get('name')}, pair: {backtest_data.get('pair')}")
            import traceback
            logger.error(f"   Full traceback: {traceback.format_exc()}")
            return None
    
    async def get_backtests(self, user_id: Optional[int] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent backtests."""
        if not self.initialized or not self.pool:
            logger.warning(f"🔍 get_backtests: Database not initialized (user_id: {user_id})")
            return []
        
        try:
            async with self.pool.acquire() as conn:
                # IMPORTANT: If user_id is provided, also check for NULL user_id backtests
                # This handles cases where backtests were saved before user_id was properly set
                if user_id:
                    rows = await conn.fetch("""
                        SELECT * FROM backtests
                        WHERE user_id = $1 OR user_id IS NULL
                        ORDER BY created_at DESC
                        LIMIT $2
                    """, user_id, limit)
                    logger.info(f"🔍 get_backtests: Querying with user_id={user_id} (including NULL backtests), found {len(rows)} rows")
                else:
                    rows = await conn.fetch("""
                        SELECT * FROM backtests
                        WHERE user_id IS NULL
                        ORDER BY created_at DESC
                        LIMIT $1
                    """, limit)
                    logger.info(f"🔍 get_backtests: Querying for NULL user_id backtests, found {len(rows)} rows")
                
                results = []
                for row in rows:
                    backtest = dict(row)
                    # Convert Decimal objects to float (PostgreSQL returns Decimal for numeric types)
                    from decimal import Decimal
                    for key, value in backtest.items():
                        if isinstance(value, Decimal):
                            backtest[key] = float(value)
                    # Parse JSON results
                    if backtest.get('results') and isinstance(backtest['results'], str):
                        try:
                            backtest['results'] = json.loads(backtest['results'])
                        except:
                            pass
                    results.append(backtest)
                
                return results
        except Exception as e:
            logger.error(f"Failed to fetch backtests: {e}", exc_info=True)
            return []
    
    async def get_backtest_by_id(self, backtest_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get backtest by ID."""
        if not self.initialized or not self.pool:
            return None
        
        try:
            async with self.pool.acquire() as conn:
                if user_id:
                    row = await conn.fetchrow("""
                        SELECT * FROM backtests
                        WHERE id = $1 AND user_id = $2
                    """, backtest_id, user_id)
                else:
                    row = await conn.fetchrow("""
                        SELECT * FROM backtests
                        WHERE id = $1
                    """, backtest_id)
                
                if row:
                    backtest = dict(row)
                    # Convert Decimal objects to float (PostgreSQL returns Decimal for numeric types)
                    from decimal import Decimal
                    for key, value in backtest.items():
                        if isinstance(value, Decimal):
                            backtest[key] = float(value)
                    # Parse JSON results
                    if backtest.get('results') and isinstance(backtest['results'], str):
                        try:
                            backtest['results'] = json.loads(backtest['results'])
                        except:
                            pass
                    return backtest
                return None
        except Exception as e:
            logger.error(f"Failed to get backtest by ID: {e}", exc_info=True)
            return None
    
    async def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp."""
        if not self.initialized or not self.pool:
            return False
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE users
                    SET last_login = CURRENT_TIMESTAMP
                    WHERE id = $1
                """, user_id)
                return True
        except Exception as e:
            logger.error(f"Failed to update last login: {e}", exc_info=True)
            return False
    
    async def get_onboarding_status(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user's onboarding status."""
        if not self.initialized or not self.pool:
            return None
        
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT onboarding_completed, onboarding_completed_at, disclaimer_acknowledged_at
                    FROM users
                    WHERE id = $1
                """, user_id)
                
                if row:
                    return {
                        'completed': row['onboarding_completed'] or False,
                        'completed_at': row['onboarding_completed_at'].isoformat() if row['onboarding_completed_at'] else None,
                        'disclaimer_acknowledged': row['disclaimer_acknowledged_at'] is not None,
                        'disclaimer_acknowledged_at': row['disclaimer_acknowledged_at'].isoformat() if row['disclaimer_acknowledged_at'] else None
                    }
                return None
        except Exception as e:
            logger.error(f"Failed to get onboarding status: {e}", exc_info=True)
            return None
    
    async def complete_onboarding(self, user_id: int) -> bool:
        """Mark onboarding as completed for a user."""
        if not self.initialized or not self.pool:
            return False
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE users
                    SET onboarding_completed = TRUE,
                        onboarding_completed_at = CURRENT_TIMESTAMP
                    WHERE id = $1
                """, user_id)
                logger.info(f"Onboarding completed for user {user_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to complete onboarding: {e}", exc_info=True)
            return False
    
    async def acknowledge_disclaimer(self, user_id: int) -> bool:
        """Record that user has acknowledged the risk disclaimer."""
        if not self.initialized or not self.pool:
            return False
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE users
                    SET disclaimer_acknowledged_at = CURRENT_TIMESTAMP
                    WHERE id = $1
                """, user_id)
                logger.info(f"Disclaimer acknowledged for user {user_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to acknowledge disclaimer: {e}", exc_info=True)
            return False
    
    async def get_daily_pnl(self, date: Optional[datetime.date] = None) -> float:
        """Get daily P&L for a specific date."""
        if not self.initialized or not self.pool:
            return 0.0
        
        if date is None:
            date = datetime.utcnow().date()
        
        try:
            async with self.pool.acquire() as conn:
                daily_pnl = await conn.fetchval("""
                    SELECT COALESCE(SUM(pnl), 0) FROM trades
                    WHERE DATE(entry_time) = $1
                """, date)
                return float(daily_pnl) if daily_pnl else 0.0
        except Exception as e:
            logger.error(f"Failed to get daily P&L: {e}", exc_info=True)
            return 0.0
    
    async def save_advanced_order(self, order_data: Dict[str, Any], user_id: Optional[int] = None) -> Optional[int]:
        """Save an advanced order to the database."""
        if not self.initialized or not self.pool:
            logger.warning("Database not initialized, skipping order save")
            return None
        
        try:
            async with self.pool.acquire() as conn:
                order_id = await conn.fetchval("""
                    INSERT INTO advanced_orders (
                        user_id, order_id, order_type, pair, side, size,
                        filled_size, status, order_data
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT (order_id) DO UPDATE SET
                        filled_size = EXCLUDED.filled_size,
                        status = EXCLUDED.status,
                        order_data = EXCLUDED.order_data,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING id
                """,
                    user_id,
                    order_data.get('order_id'),
                    order_data.get('order_type'),
                    order_data.get('pair'),
                    order_data.get('side'),
                    order_data.get('size'),
                    order_data.get('filled_size', 0),
                    order_data.get('status'),
                    json.dumps(order_data.get('order_data', {}))
                )
                return order_id
        except Exception as e:
            logger.error(f"Failed to save advanced order: {e}", exc_info=True)
            return None
    
    async def get_advanced_orders(
        self,
        user_id: Optional[int] = None,
        pair: Optional[str] = None,
        status: Optional[str] = None,
        order_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get advanced orders with optional filtering."""
        if not self.initialized or not self.pool:
            return []
        
        try:
            async with self.pool.acquire() as conn:
                query = "SELECT * FROM advanced_orders WHERE 1=1"
                params = []
                param_index = 1
                
                if user_id:
                    query += f" AND (user_id = ${param_index} OR user_id IS NULL)"
                    params.append(user_id)
                    param_index += 1
                
                if pair:
                    query += f" AND pair = ${param_index}"
                    params.append(pair)
                    param_index += 1
                
                if status:
                    query += f" AND status = ${param_index}"
                    params.append(status)
                    param_index += 1
                
                if order_type:
                    query += f" AND order_type = ${param_index}"
                    params.append(order_type)
                    param_index += 1
                
                query += " ORDER BY created_at DESC"
                
                rows = await conn.fetch(query, *params)
                orders = []
                for row in rows:
                    order_dict = dict(row)
                    # Parse JSONB order_data
                    if order_dict.get('order_data'):
                        if isinstance(order_dict['order_data'], str):
                            order_dict['order_data'] = json.loads(order_dict['order_data'])
                    # Convert datetime objects
                    for key in ['created_at', 'filled_at', 'updated_at']:
                        if key in order_dict and order_dict[key]:
                            if hasattr(order_dict[key], 'isoformat'):
                                order_dict[key] = order_dict[key].isoformat()
                    orders.append(order_dict)
                
                return orders
        except Exception as e:
            logger.error(f"Failed to get advanced orders: {e}", exc_info=True)
            return []
    
    async def update_advanced_order(self, order_id: str, updates: Dict[str, Any]) -> bool:
        """Update an advanced order."""
        if not self.initialized or not self.pool:
            return False
        
        try:
            async with self.pool.acquire() as conn:
                # Build update query dynamically
                set_clauses = []
                params = []
                param_index = 1
                
                if 'status' in updates:
                    set_clauses.append(f"status = ${param_index}")
                    params.append(updates['status'])
                    param_index += 1
                
                if 'filled_size' in updates:
                    set_clauses.append(f"filled_size = ${param_index}")
                    params.append(updates['filled_size'])
                    param_index += 1
                
                if 'order_data' in updates:
                    set_clauses.append(f"order_data = ${param_index}")
                    params.append(json.dumps(updates['order_data']))
                    param_index += 1
                
                if 'filled_at' in updates:
                    set_clauses.append(f"filled_at = ${param_index}")
                    params.append(updates['filled_at'])
                    param_index += 1
                
                if not set_clauses:
                    return True  # Nothing to update
                
                set_clauses.append(f"updated_at = CURRENT_TIMESTAMP")
                
                params.append(order_id)
                query = f"UPDATE advanced_orders SET {', '.join(set_clauses)} WHERE order_id = ${param_index}"
                
                await conn.execute(query, *params)
                return True
        except Exception as e:
            logger.error(f"Failed to update advanced order {order_id}: {e}", exc_info=True)
            return False
    
    async def delete_advanced_order(self, order_id: str) -> bool:
        """Delete an advanced order."""
        if not self.initialized or not self.pool:
            return False
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("DELETE FROM advanced_orders WHERE order_id = $1", order_id)
                return True
        except Exception as e:
            logger.error(f"Failed to delete advanced order {order_id}: {e}", exc_info=True)
            return False
