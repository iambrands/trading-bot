"""REST API server for trading bot control and monitoring."""

import logging
import csv
import io
import json
from datetime import datetime
from typing import Optional, Dict
from collections import defaultdict
from aiohttp import web
# CORS is handled manually via middleware to avoid route wrapping conflicts
# from aiohttp_cors import setup as cors_setup, ResourceOptions
from config import get_config
from auth.auth_manager import AuthManager
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class TradingBotAPI:
    """REST API server for trading bot."""
    
    def __init__(self, bot_instance=None, db_manager=None):
        self.config = get_config()
        self.bot = bot_instance
        self.db_manager = db_manager
        self.auth_manager = AuthManager(self.config)
        self.app = web.Application()
        self._setup_middleware()  # Setup middleware first
        self._setup_routes()  # Setup all routes
        self._setup_cors()  # Setup CORS middleware (doesn't wrap routes)
        self._setup_static_blocker()  # Static blocker last
    
    def _setup_middleware(self):
        """Setup authentication middleware."""
        @web.middleware
        async def auth_middleware(request, handler):
            # LOG ALL REQUESTS - especially POST to /api/backtest/run
            if request.method == 'POST' and '/api/backtest/run' in request.path:
                import sys
                print(f"🔵🔵🔵 MIDDLEWARE: POST to /api/backtest/run detected!", file=sys.stderr)
                print(f"   Path: {request.path}, Method: {request.method}", file=sys.stderr)
                sys.stderr.flush()
                logger.info(f"🔵🔵🔵 MIDDLEWARE: POST to /api/backtest/run - Path: {request.path}")
            
            # Public routes that don't require authentication
            public_routes = [
                '/api/auth/signup',
                '/api/auth/signin',
                '/landing',
                '/signup',
                '/signin',
                '/test-runner',
                '/favicon.ico'
            ]
            
            # Allow static files and favicon (must be before other checks)
            if request.path.startswith('/static') or request.path == '/favicon.ico':
                is_public = True
                return await handler(request)
            
            # Check if route is public
            is_public = any(request.path.startswith(route) for route in public_routes)
            
            # Root path - check if authenticated
            if request.path == '/':
                # Try to get token
                auth_header = request.headers.get('Authorization', '')
                token = self.auth_manager.extract_token_from_header(auth_header)
                if not token:
                    token = request.cookies.get('auth_token') or request.query.get('token')
                
                if token:
                    payload = self.auth_manager.verify_token(token)
                    if payload:
                        # User is authenticated, allow access to dashboard
                        request['user_id'] = payload['user_id']
                        request['user_email'] = payload['email']
                        is_public = True  # Don't block, but we have user info
                    else:
                        # Invalid token, redirect to landing
                        return web.Response(status=302, headers={'Location': '/landing'})
                else:
                    # No token, redirect to landing
                    return web.Response(status=302, headers={'Location': '/landing'})
                is_public = True
            
            if not is_public:
                # Check for authentication token
                auth_header = request.headers.get('Authorization', '')
                token = self.auth_manager.extract_token_from_header(auth_header)
                
                # Try to get token from cookie or query param (for browser requests)
                if not token:
                    token = request.cookies.get('auth_token') or request.query.get('token')
                
                if not token:
                    # Check if it's a dashboard route - redirect to landing
                    if request.path.startswith('/') and not request.path.startswith('/api'):
                        return web.Response(status=302, headers={'Location': '/landing'})
                    return web.json_response({'error': 'Authentication required'}, status=401)
                
                # Verify token
                payload = self.auth_manager.verify_token(token)
                if not payload:
                    if request.path.startswith('/') and not request.path.startswith('/api'):
                        return web.Response(status=302, headers={'Location': '/landing'})
                    return web.json_response({'error': 'Invalid or expired token'}, status=401)
                
                # Store user info in request
                request['user_id'] = payload['user_id']
                request['user_email'] = payload['email']
            
            return await handler(request)
        
        self.app.middlewares.append(auth_middleware)
    
    def _setup_static_blocker(self):
        """Block requests for non-existent hashed CSS/JS files."""
        @web.middleware
        async def static_blocker(request, handler):
            # Block requests for hashed main.css/main.js files that don't exist
            path = request.path
            if (path.startswith('/static/css/main.') or 
                path.startswith('/static/js/main.')):
                # Check if it's a hashed filename (contains a dot and hash pattern)
                if '.' in path.split('/')[-1] and len(path.split('/')[-1].split('.')[1]) > 8:
                    logger.warning(f"Blocked request for non-existent hashed file: {path}")
                    return web.Response(
                        text='File not found - this appears to be from a cached old version. Please clear your browser cache.',
                        status=404,
                        headers={
                            'Cache-Control': 'no-cache, no-store, must-revalidate',
                            'Content-Type': 'text/plain'
                        }
                    )
            return await handler(request)
        
        self.app.middlewares.append(static_blocker)
    
    def _setup_cors(self):
        """CORS disabled to avoid route conflicts - can be added via middleware later if needed."""
        # CORS disabled temporarily to avoid HEAD method conflicts with static routes
        # Static routes handle HEAD automatically and don't need CORS
        # For same-origin requests, CORS is not needed
        # Can add CORS headers manually via middleware later if cross-origin is required
        pass
    
    def _setup_routes(self):
        """Setup API routes."""
        # Public landing and auth pages
        self.app.router.add_get('/landing', self.serve_landing)
        self.app.router.add_get('/signup', self.serve_signup)
        self.app.router.add_get('/signin', self.serve_signin)
        self.app.router.add_get('/test-runner', self.serve_test_runner)
        
        # Authentication API endpoints (public)
        self.app.router.add_post('/api/auth/signup', self.signup)
        self.app.router.add_post('/api/auth/signin', self.signin)
        self.app.router.add_get('/api/auth/verify', self.verify_token)
        self.app.router.add_post('/api/auth/logout', self.logout)
        
        # Dashboard routes (protected)
        self.app.router.add_get('/', self.serve_dashboard)
        self.app.router.add_get('/market-conditions', self.serve_market_conditions)
        self.app.router.add_get('/positions', self.serve_positions)
        self.app.router.add_get('/trades', self.serve_trades)
        self.app.router.add_get('/performance', self.serve_performance)
        self.app.router.add_get('/portfolio', self.serve_portfolio)
        self.app.router.add_get('/charts', self.serve_charts)
        self.app.router.add_get('/orders', self.serve_orders)
        self.app.router.add_get('/grid', self.serve_grid)
        self.app.router.add_get('/logs', self.serve_logs)
        self.app.router.add_get('/settings', self.serve_settings)
        self.app.router.add_get('/help', self.serve_help)
        self.app.router.add_get('/backtest', self.serve_backtest)
        
        # Static files (if needed for additional assets)
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        static_path = os.path.join(project_root, 'static')
        if os.path.exists(static_path):
            self.app.router.add_static('/static', path=static_path, name='static')
        
        # PWA routes
        self.app.router.add_get('/manifest.json', self.serve_manifest)
        self.app.router.add_get('/service-worker.js', self.serve_service_worker)
        self.app.router.add_get('/favicon.ico', self.serve_favicon)
        
        # Status endpoints
        self.app.router.add_get('/api/status', self.get_status)
        self.app.router.add_get('/api/positions', self.get_positions)
        self.app.router.add_get('/api/trades', self.get_trades)
        self.app.router.add_get('/api/performance', self.get_performance)
        self.app.router.add_get('/api/risk', self.get_risk)
        self.app.router.add_get('/api/market-conditions', self.get_market_conditions)
        self.app.router.add_get('/api/prices', self.get_current_prices)
        
        # Settings endpoints
        self.app.router.add_get('/api/settings', self.get_settings)
        self.app.router.add_post('/api/settings', self.save_settings)
        self.app.router.add_get('/api/settings/templates', self.get_templates)
        self.app.router.add_post('/api/settings/templates', self.save_template)
        self.app.router.add_get('/api/settings/templates/list', self.list_templates)
        self.app.router.add_delete('/api/settings/templates/{name}', self.delete_template)
        
        # Chart data endpoints
        self.app.router.add_get('/api/equity-curve', self.get_equity_curve)
        self.app.router.add_get('/api/daily-pnl', self.get_daily_pnl)
        
        # Advanced charting endpoints
        self.app.router.add_get('/api/charts/candles', self.get_chart_candles)
        self.app.router.add_get('/api/charts/indicators', self.get_chart_indicators)
        
        # Portfolio analytics endpoints
        self.app.router.add_get('/api/portfolio/analytics', self.get_portfolio_analytics)
        self.app.router.add_get('/api/portfolio/tax-report', self.get_tax_report)
        
        # Advanced orders endpoints
        self.app.router.add_post('/api/orders/create', self.create_advanced_order)
        self.app.router.add_get('/api/orders', self.list_advanced_orders)
        self.app.router.add_get('/api/orders/{order_id}', self.get_advanced_order)
        self.app.router.add_delete('/api/orders/{order_id}', self.cancel_advanced_order)
        
        # Grid trading endpoints
        self.app.router.add_post('/api/grid/create', self.create_grid)
        self.app.router.add_get('/api/grid', self.list_grids)
        self.app.router.add_get('/api/grid/{grid_id}', self.get_grid)
        self.app.router.add_post('/api/grid/{grid_id}/stop', self.stop_grid)
        self.app.router.add_post('/api/grid/{grid_id}/pause', self.pause_grid)
        self.app.router.add_post('/api/grid/{grid_id}/resume', self.resume_grid)
        
        # DCA endpoints
        self.app.router.add_post('/api/dca/create', self.create_dca)
        self.app.router.add_get('/api/dca', self.list_dca)
        self.app.router.add_get('/api/dca/{dca_id}', self.get_dca)
        self.app.router.add_post('/api/dca/{dca_id}/stop', self.stop_dca)
        self.app.router.add_post('/api/dca/{dca_id}/pause', self.pause_dca)
        self.app.router.add_post('/api/dca/{dca_id}/resume', self.resume_dca)
        
        # Logs endpoints
        self.app.router.add_get('/api/logs', self.get_logs)
        self.app.router.add_get('/api/logs/download', self.download_logs)
        
        # Trade export endpoints
        self.app.router.add_get('/api/trades/export', self.export_trades)
        
        # Backtesting endpoints
        self.app.router.add_post('/api/backtest/run', self.run_backtest)
        self.app.router.add_get('/api/backtest/list', self.list_backtests)
        self.app.router.add_get('/api/backtest/results/{id}', self.get_backtest_results)
        self.app.router.add_get('/api/backtest/debug-count', self.debug_backtest_count)  # Diagnostic endpoint
        self.app.router.add_get('/api/backtest/test-route', self.test_backtest_route)  # Simple test endpoint
        self.app.router.add_post('/api/backtest/test-post', self.test_backtest_post)  # Test POST endpoint
        
        # AI endpoints
        self.app.router.add_post('/api/ai/analyze-market', self.ai_analyze_market)
        self.app.router.add_post('/api/ai/explain-strategy', self.ai_explain_strategy)
        self.app.router.add_post('/api/ai/guidance', self.ai_get_guidance)
        self.app.router.add_post('/api/ai/analyze-backtest', self.ai_analyze_backtest)
        
        # Available coins endpoint
        self.app.router.add_get('/api/available-coins', self.get_available_coins)

        # Diagnostics (helps confirm whether deployment is API-only or full-bot)
        self.app.router.add_get('/api/runtime', self.get_runtime_info)
        self.app.router.add_get('/api/ai/status', self.ai_status)
        
        # Control endpoints
        self.app.router.add_post('/api/start', self.start_bot)
        self.app.router.add_post('/api/pause', self.pause_bot)
        self.app.router.add_post('/api/resume', self.resume_bot)
        self.app.router.add_post('/api/stop', self.stop_bot)
        self.app.router.add_post('/api/close-all', self.close_all_positions)
        self.app.router.add_post('/api/kill-switch', self.kill_switch)
    
    async def serve_dashboard(self, request):
        """Serve the dashboard HTML page."""
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dashboard_path = os.path.join(project_root, 'static', 'dashboard.html')
        
        # Fallback to index.html if dashboard.html doesn't exist
        if not os.path.exists(dashboard_path):
            dashboard_path = os.path.join(project_root, 'static', 'index.html')
        
        try:
            if os.path.exists(dashboard_path):
                # Read file content and serve as text to avoid FileResponse issues
                with open(dashboard_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return web.Response(
                    text=content,
                    content_type='text/html',
                    headers={
                        'Cache-Control': 'no-cache, no-store, must-revalidate',
                        'Pragma': 'no-cache',
                        'Expires': '0'
                    }
                )
            else:
                logger.error(f"Dashboard not found at: {dashboard_path} or {os.path.join(project_root, 'static', 'index.html')}")
                return web.Response(
                    text=f'Dashboard not found. Please ensure static/dashboard.html or static/index.html exists.',
                    status=404
                )
        except Exception as e:
            logger.error(f"Error serving dashboard: {e}", exc_info=True)
            return web.Response(text=f'Error loading dashboard: {str(e)}', status=500)
    
    async def serve_market_conditions(self, request):
        """Serve market conditions page (same as dashboard with routing)."""
        return await self.serve_dashboard(request)
    
    async def serve_positions(self, request):
        """Serve positions page."""
        return await self.serve_dashboard(request)
    
    async def serve_trades(self, request):
        """Serve trades page."""
        return await self.serve_dashboard(request)
    
    async def serve_performance(self, request):
        """Serve performance page."""
        return await self.serve_dashboard(request)
    
    async def serve_portfolio(self, request):
        """Serve portfolio page."""
        return await self.serve_dashboard(request)
    
    async def serve_charts(self, request):
        """Serve charts page."""
        return await self.serve_dashboard(request)
    
    async def serve_orders(self, request):
        """Serve orders page."""
        return await self.serve_dashboard(request)
    
    async def serve_grid(self, request):
        """Serve grid trading page."""
        return await self.serve_dashboard(request)
    
    async def serve_backtest(self, request):
        """Serve backtesting page."""
        return await self.serve_dashboard(request)
    
    async def get_status(self, request):
        """Get bot status and account information."""
        if not self.bot:
            # Return default status when bot is not running
            config = self.config
            return web.json_response({
                'status': 'stopped',
                'balance': config.ACCOUNT_SIZE,
                'positions_count': 0,
                'paper_trading': config.PAPER_TRADING,
                'environment': config.ENVIRONMENT,
                'mode': 'api-only',
                'use_real_market_data': bool(getattr(config, 'USE_REAL_MARKET_DATA', False))
            })
        
        try:
            balance = await self.bot.exchange.get_account_balance()
            positions = self.bot.positions
            
            return web.json_response({
                'status': self.bot.status,
                'balance': balance,
                'positions_count': len(positions),
                'paper_trading': self.bot.config.PAPER_TRADING,
                'environment': self.bot.config.ENVIRONMENT,
                'mode': 'full-bot',
                'use_real_market_data': bool(getattr(self.bot.config, 'USE_REAL_MARKET_DATA', False))
            })
        except Exception as e:
            logger.error(f"Error getting status: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)

    async def get_runtime_info(self, request):
        """Return lightweight runtime diagnostics (safe to expose)."""
        try:
            cfg = self.config
            return web.json_response({
                'mode': 'full-bot' if self.bot else 'api-only',
                'bot_attached': bool(self.bot),
                'paper_trading': bool(getattr(cfg, 'PAPER_TRADING', False)),
                'use_real_market_data': bool(getattr(cfg, 'USE_REAL_MARKET_DATA', False)),
                'has_coinbase_api_key': bool(getattr(cfg, 'COINBASE_API_KEY', '')),
                'api_host': getattr(cfg, 'API_HOST', None),
                'api_port': getattr(cfg, 'API_PORT', None),
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Error getting runtime info: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def ai_status(self, request):
        """Get AI configuration status for diagnostics."""
        try:
            from ai import ClaudeAIAnalyst
            
            api_key = self.config.CLAUDE_API_KEY or ''
            api_key_trimmed = api_key.strip().strip('"').strip("'") if api_key else ''
            has_key = bool(api_key_trimmed)
            key_length = len(api_key_trimmed) if api_key_trimmed else 0
            
            # Try to initialize to check if it's enabled
            ai_analyst = ClaudeAIAnalyst(self.config)
            
            return web.json_response({
                'configured': has_key,
                'enabled': ai_analyst.enabled,
                'key_length': key_length,
                'model': self.config.CLAUDE_MODEL,
                'diagnostic': {
                    'key_exists': has_key,
                    'key_valid_format': key_length > 10 if has_key else False,
                    'analyst_enabled': ai_analyst.enabled,
                    'note': 'If configured=true but enabled=false, the key may be invalid or incorrectly formatted'
                }
            })
        except Exception as e:
            logger.error(f"Error getting AI status: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_positions(self, request):
        """Get active positions with current P&L."""
        if not self.bot:
            # Return empty positions when bot is not running
            return web.json_response([])
        
        try:
            positions = []
            market_data = await self.bot.exchange.get_market_data(self.bot.config.TRADING_PAIRS)
            
            for position in self.bot.positions:
                pair = position['pair']
                current_price = market_data.get(pair, {}).get('price', position['entry_price'])
                
                # Calculate current P&L
                if position['side'] == 'LONG':
                    pnl = (current_price - position['entry_price']) * position['size']
                else:
                    pnl = (position['entry_price'] - current_price) * position['size']
                
                pnl_pct = (pnl / (position['entry_price'] * position['size'])) * 100.0
                
                positions.append({
                    'id': position.get('id'),
                    'pair': pair,
                    'side': position['side'],
                    'size': position['size'],
                    'entry_price': position['entry_price'],
                    'current_price': current_price,
                    'stop_loss': position.get('stop_loss'),
                    'take_profit': position.get('take_profit'),
                    'current_pnl': pnl,
                    'current_pnl_pct': pnl_pct,
                    'entry_time': position.get('entry_time').isoformat() if position.get('entry_time') else None,
                    'confidence_score': position.get('confidence_score')
                })
            
            return web.json_response({'positions': positions})
        except Exception as e:
            logger.error(f"Error getting positions: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_trades(self, request):
        """Get recent trade history."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            limit = int(request.query.get('limit', 50))
            trades = await self.bot.db.get_recent_trades(limit)
            
            # Format trades for JSON response
            formatted_trades = []
            for trade in trades:
                formatted_trade = dict(trade)
                # Convert datetime objects to ISO format strings
                for key in ['entry_time', 'exit_time', 'created_at']:
                    if key in formatted_trade and formatted_trade[key]:
                        if hasattr(formatted_trade[key], 'isoformat'):
                            formatted_trade[key] = formatted_trade[key].isoformat()
                formatted_trades.append(formatted_trade)
            
            return web.json_response({'trades': formatted_trades})
        except Exception as e:
            logger.error(f"Error getting trades: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def export_trades(self, request):
        """Export trades to CSV or JSON format."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            # Get format (csv or json)
            export_format = request.query.get('format', 'csv').lower()
            if export_format not in ['csv', 'json']:
                return web.json_response({'error': 'Invalid format. Use csv or json'}, status=400)
            
            # Parse date range if provided
            start_date = None
            end_date = None
            user_id = request.get('user_id')  # From auth middleware
            
            if request.query.get('start_date'):
                try:
                    start_date = datetime.fromisoformat(request.query.get('start_date'))
                except ValueError:
                    return web.json_response({'error': 'Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}, status=400)
            
            if request.query.get('end_date'):
                try:
                    end_date = datetime.fromisoformat(request.query.get('end_date'))
                except ValueError:
                    return web.json_response({'error': 'Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}, status=400)
            
            # Fetch trades with date range
            trades = await self.bot.db.get_trades_with_date_range(start_date, end_date, user_id)
            
            if not trades:
                return web.json_response({'error': 'No trades found for the specified criteria'}, status=404)
            
            # Format trades (convert datetime objects)
            formatted_trades = []
            for trade in trades:
                formatted_trade = dict(trade)
                for key in ['entry_time', 'exit_time', 'created_at']:
                    if key in formatted_trade and formatted_trade[key]:
                        if hasattr(formatted_trade[key], 'isoformat'):
                            formatted_trade[key] = formatted_trade[key].isoformat()
                formatted_trades.append(formatted_trade)
            
            # Generate export file
            if export_format == 'csv':
                # Create CSV
                output = io.StringIO()
                if formatted_trades:
                    writer = csv.DictWriter(output, fieldnames=formatted_trades[0].keys())
                    writer.writeheader()
                    for trade in formatted_trades:
                        writer.writerow(trade)
                
                csv_content = output.getvalue()
                output.close()
                
                # Create filename with date range
                filename = 'trades_export.csv'
                if start_date or end_date:
                    date_str = ''
                    if start_date:
                        date_str += start_date.strftime('%Y%m%d')
                    date_str += '_to_'
                    if end_date:
                        date_str += end_date.strftime('%Y%m%d')
                    else:
                        date_str += 'now'
                    filename = f'trades_export_{date_str}.csv'
                
                return web.Response(
                    text=csv_content,
                    headers={
                        'Content-Type': 'text/csv',
                        'Content-Disposition': f'attachment; filename="{filename}"'
                    }
                )
            
            else:  # JSON
                json_content = json.dumps(formatted_trades, indent=2)
                
                # Create filename with date range
                filename = 'trades_export.json'
                if start_date or end_date:
                    date_str = ''
                    if start_date:
                        date_str += start_date.strftime('%Y%m%d')
                    date_str += '_to_'
                    if end_date:
                        date_str += end_date.strftime('%Y%m%d')
                    else:
                        date_str += 'now'
                    filename = f'trades_export_{date_str}.json'
                
                return web.Response(
                    text=json_content,
                    headers={
                        'Content-Type': 'application/json',
                        'Content-Disposition': f'attachment; filename="{filename}"'
                    }
                )
                
        except Exception as e:
            logger.error(f"Error exporting trades: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_performance(self, request):
        """Get performance metrics."""
        if not self.bot:
            # Return default performance metrics when bot is not running
            config = self.config
            return web.json_response({
                'total_pnl': 0.0,
                'daily_pnl': 0.0,
                'roi_pct': 0.0,
                'total_roi': 0.0,  # Also include for backward compatibility
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'average_win': 0.0,
                'average_loss': 0.0,
                'account_balance': config.ACCOUNT_SIZE,
                'current_balance': config.ACCOUNT_SIZE,
                'initial_balance': config.ACCOUNT_SIZE
            })
        
        try:
            balance = await self.bot.exchange.get_account_balance()
            summary = self.bot.performance_tracker.get_performance_summary(
                balance, self.bot.initial_balance
            )
            return web.json_response(summary)
        except Exception as e:
            logger.error(f"Error getting performance: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_risk(self, request):
        """Get risk exposure metrics."""
        if not self.bot:
            # Return default risk metrics when bot is not running
            config = self.config
            return web.json_response({
                'total_exposure': 0.0,
                'exposure_pct': 0.0,
                'positions_count': 0,
                'max_positions': config.MAX_POSITIONS,
                'daily_pnl': 0.0,
                'daily_loss_limit': config.DAILY_LOSS_LIMIT,
                'daily_loss_pct': 0.0,
                'risk_per_trade_pct': config.RISK_PER_TRADE_PCT,
                'max_position_size_pct': config.MAX_POSITION_SIZE_PCT
            })
        
        try:
            balance = await self.bot.exchange.get_account_balance()
            risk_metrics = self.bot.risk_manager.get_risk_metrics(balance, self.bot.positions)
            return web.json_response(risk_metrics)
        except Exception as e:
            logger.error(f"Error getting risk metrics: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_portfolio_analytics(self, request):
        """Get comprehensive portfolio analytics."""
        if not self.bot or not self.db_manager:
            return web.json_response({'error': 'Bot or database not initialized'}, status=500)
        
        try:
            user_id = request.get('user_id')
            balance = await self.bot.exchange.get_account_balance()
            
            # Get all trades
            all_trades = await self.db_manager.get_trades_with_date_range(user_id=user_id)
            
            # Filter closed trades only
            closed_trades = [t for t in all_trades if t.get('exit_price') is not None and t.get('pnl') is not None]
            
            # Calculate portfolio analytics
            analytics = {
                'portfolio_value': float(balance),
                'initial_balance': float(self.bot.initial_balance),
                'total_pnl': float(balance - self.bot.initial_balance),
                'roi_pct': float(((balance - self.bot.initial_balance) / self.bot.initial_balance) * 100) if self.bot.initial_balance > 0 else 0.0,
                
                # Asset allocation (by trading pair)
                'asset_allocation': {},
                
                # P&L by trading pair
                'pnl_by_pair': {},
                
                # Win/loss streaks
                'win_streak': 0,
                'loss_streak': 0,
                'current_streak': 0,
                'current_streak_type': None,
                
                # Trade statistics by pair
                'trades_by_pair': {},
                
                # Portfolio value over time (from equity curve)
                'portfolio_history': []
            }
            
            # Group trades by pair
            trades_by_pair = defaultdict(list)
            for trade in closed_trades:
                pair = trade.get('pair', 'UNKNOWN')
                trades_by_pair[pair].append(trade)
            
            # Calculate P&L and statistics by pair
            total_volume_by_pair = defaultdict(float)
            for pair, trades in trades_by_pair.items():
                pair_pnl = sum(float(t.get('pnl', 0)) for t in trades)
                pair_trades = len(trades)
                winning = sum(1 for t in trades if float(t.get('pnl', 0)) > 0)
                losing = pair_trades - winning
                win_rate = (winning / pair_trades * 100) if pair_trades > 0 else 0.0
                total_volume = sum(float(t.get('size', 0)) * float(t.get('entry_price', 0)) for t in trades)
                
                analytics['pnl_by_pair'][pair] = {
                    'total_pnl': float(pair_pnl),
                    'total_trades': pair_trades,
                    'winning_trades': winning,
                    'losing_trades': losing,
                    'win_rate': float(win_rate),
                    'total_volume': float(total_volume)
                }
                
                total_volume_by_pair[pair] = float(total_volume)
                analytics['trades_by_pair'][pair] = pair_trades
            
            # Calculate asset allocation (based on trading volume)
            total_volume_all = sum(total_volume_by_pair.values())
            if total_volume_all > 0:
                for pair, volume in total_volume_by_pair.items():
                    analytics['asset_allocation'][pair] = {
                        'percentage': float((volume / total_volume_all) * 100),
                        'volume': float(volume)
                    }
            
            # Calculate win/loss streaks
            if closed_trades:
                # Sort by entry time
                sorted_trades = sorted(closed_trades, key=lambda x: x.get('entry_time', datetime.min))
                
                current_streak = 0
                current_streak_type = None
                max_win_streak = 0
                max_loss_streak = 0
                
                for trade in sorted_trades:
                    pnl = float(trade.get('pnl', 0))
                    is_win = pnl > 0
                    
                    if current_streak_type is None:
                        current_streak_type = 'win' if is_win else 'loss'
                        current_streak = 1
                    elif (current_streak_type == 'win' and is_win) or (current_streak_type == 'loss' and not is_win):
                        current_streak += 1
                    else:
                        # Streak broken
                        if current_streak_type == 'win':
                            max_win_streak = max(max_win_streak, current_streak)
                        else:
                            max_loss_streak = max(max_loss_streak, current_streak)
                        current_streak_type = 'win' if is_win else 'loss'
                        current_streak = 1
                
                # Check final streak
                if current_streak_type == 'win':
                    max_win_streak = max(max_win_streak, current_streak)
                else:
                    max_loss_streak = max(max_loss_streak, current_streak)
                
                analytics['win_streak'] = max_win_streak
                analytics['loss_streak'] = max_loss_streak
                analytics['current_streak'] = current_streak
                analytics['current_streak_type'] = current_streak_type
            
            # Get portfolio history from equity curve
            equity_curve = self.bot.performance_tracker.get_equity_curve(limit=100)
            analytics['portfolio_history'] = [
                {
                    'timestamp': str(point.get('timestamp', '')),
                    'balance': float(point.get('balance', self.bot.initial_balance))
                }
                for point in equity_curve
            ]
            
            return web.json_response(analytics)
        except Exception as e:
            logger.error(f"Error getting portfolio analytics: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_tax_report(self, request):
        """Generate tax report with FIFO/LIFO calculations."""
        if not self.bot or not self.db_manager:
            return web.json_response({'error': 'Bot or database not initialized'}, status=500)
        
        try:
            from datetime import datetime, timedelta
            user_id = request.get('user_id')
            method = request.query.get('method', 'FIFO')  # FIFO or LIFO
            year = request.query.get('year', str(datetime.utcnow().year))
            
            # Get all closed trades for the year
            start_date = datetime(int(year), 1, 1)
            end_date = datetime(int(year), 12, 31, 23, 59, 59)
            trades = await self.db_manager.get_trades_with_date_range(
                start_date=start_date,
                end_date=end_date,
                user_id=user_id
            )
            
            # Filter closed trades only
            closed_trades = [t for t in trades if t.get('exit_price') is not None and t.get('exit_time') is not None]
            
            # Calculate realized gains/losses
            realized_gains = []
            realized_losses = []
            
            for trade in closed_trades:
                pnl = float(trade.get('pnl', 0))
                entry_time = trade.get('entry_time')
                exit_time = trade.get('exit_time')
                pair = trade.get('pair', '')
                size = float(trade.get('size', 0))
                entry_price = float(trade.get('entry_price', 0))
                exit_price = float(trade.get('exit_price', 0))
                
                if pnl > 0:
                    realized_gains.append({
                        'pair': pair,
                        'entry_time': str(entry_time) if entry_time else '',
                        'exit_time': str(exit_time) if exit_time else '',
                        'size': float(size),
                        'entry_price': float(entry_price),
                        'exit_price': float(exit_price),
                        'gain': float(pnl),
                        'cost_basis': float(size * entry_price),
                        'proceeds': float(size * exit_price)
                    })
                else:
                    realized_losses.append({
                        'pair': pair,
                        'entry_time': str(entry_time) if entry_time else '',
                        'exit_time': str(exit_time) if exit_time else '',
                        'size': float(size),
                        'entry_price': float(entry_price),
                        'exit_price': float(exit_price),
                        'loss': float(abs(pnl)),
                        'cost_basis': float(size * entry_price),
                        'proceeds': float(size * exit_price)
                    })
            
            total_realized_gains = sum(g['gain'] for g in realized_gains)
            total_realized_losses = sum(l['loss'] for l in realized_losses)
            net_realized = total_realized_gains - total_realized_losses
            
            tax_report = {
                'year': year,
                'method': method,
                'total_trades': len(closed_trades),
                'realized_gains': {
                    'count': len(realized_gains),
                    'total': float(total_realized_gains),
                    'trades': realized_gains
                },
                'realized_losses': {
                    'count': len(realized_losses),
                    'total': float(total_realized_losses),
                    'trades': realized_losses
                },
                'net_realized': float(net_realized),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return web.json_response(tax_report)
        except Exception as e:
            logger.error(f"Error generating tax report: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def start_bot(self, request):
        """Start trading bot."""
        if not self.bot:
            return web.json_response({
                'error': 'Trading bot is not running. Please start the bot using: python main.py',
                'message': 'The API server is running, but the trading bot instance is not available. Use main.py to run the full trading bot.'
            }, status=503)
        
        try:
            if self.bot.status == 'running':
                return web.json_response({'message': 'Bot is already running', 'status': self.bot.status})
            
            await self.bot.start()
            return web.json_response({'message': 'Bot started', 'status': self.bot.status})
        except Exception as e:
            logger.error(f"Error starting bot: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def pause_bot(self, request):
        """Pause bot (stop opening new positions)."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            self.bot.status = 'paused'
            logger.info("Bot paused via API")
            return web.json_response({'message': 'Bot paused', 'status': self.bot.status})
        except Exception as e:
            logger.error(f"Error pausing bot: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def resume_bot(self, request):
        """Resume bot (allow opening new positions)."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            if self.bot.status == 'stopped':
                return web.json_response({'error': 'Bot is stopped. Use /api/start to start it.'}, status=400)
            
            self.bot.status = 'running'
            logger.info("Bot resumed via API")
            return web.json_response({'message': 'Bot resumed', 'status': self.bot.status})
        except Exception as e:
            logger.error(f"Error resuming bot: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def stop_bot(self, request):
        """Stop trading bot."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            await self.bot.stop()
            return web.json_response({'message': 'Bot stopped', 'status': self.bot.status})
        except Exception as e:
            logger.error(f"Error stopping bot: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def close_all_positions(self, request):
        """Close all open positions."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            closed_count = await self.bot.close_all_positions()
            return web.json_response({
                'message': f'Closed {closed_count} positions',
                'closed_count': closed_count
            })
        except Exception as e:
            logger.error(f"Error closing positions: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def kill_switch(self, request):
        """Emergency kill switch - stop bot and close all positions."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            logger.warning("KILL SWITCH ACTIVATED")
            await self.bot.kill_switch()
            return web.json_response({
                'message': 'Kill switch activated - bot stopped and all positions closed',
                'status': self.bot.status
            })
        except Exception as e:
            logger.error(f"Error activating kill switch: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_market_conditions(self, request):
        """Get current market conditions and why trades aren't triggering."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            conditions = {}
            
            for pair in self.bot.config.TRADING_PAIRS:
                candles = self.bot.candle_cache.get(pair, [])
                
                if len(candles) < max(self.bot.config.EMA_PERIOD, self.bot.config.RSI_PERIOD, self.bot.config.VOLUME_PERIOD) + 1:
                    conditions[pair] = {
                        'status': 'insufficient_data',
                        'message': f'Need at least {max(self.bot.config.EMA_PERIOD, self.bot.config.RSI_PERIOD, self.bot.config.VOLUME_PERIOD) + 1} candles, have {len(candles)}',
                        'candles_count': len(candles),
                        'required_candles': max(self.bot.config.EMA_PERIOD, self.bot.config.RSI_PERIOD, self.bot.config.VOLUME_PERIOD) + 1
                    }
                    continue
                
                # Get real-time price
                market_data = await self.bot.exchange.get_market_data([pair])
                real_time_price = market_data.get(pair, {}).get('price', 0) if market_data.get(pair) else 0
                
                # Update last candle with real-time price BEFORE calculating indicators
                # This ensures EMA/RSI use the latest price data
                if candles and real_time_price > 0:
                    # Work with a copy to avoid modifying the cache directly
                    candles = list(candles)  # Create a copy
                    candles[-1] = candles[-1].copy()
                    old_close = candles[-1].get('close', 0)
                    candles[-1]['close'] = real_time_price
                    # Update high/low if needed
                    if real_time_price > candles[-1].get('high', 0):
                        candles[-1]['high'] = real_time_price
                    if real_time_price < candles[-1].get('low', float('inf')):
                        candles[-1]['low'] = real_time_price
                    
                    # Log if there's a significant price difference (potential data issue)
                    if abs(real_time_price - old_close) / old_close > 0.5:  # >50% difference
                        logger.warning(f"⚠️ {pair}: Large price difference in cached candle - old_close=${old_close:.2f}, real_time=${real_time_price:.2f}. Candle cache may be stale.")
                
                # Calculate indicators with updated candle data
                indicators = self.bot.strategy.calculate_indicators(candles)
                if not indicators:
                    conditions[pair] = {
                        'status': 'error',
                        'message': 'Failed to calculate indicators'
                    }
                    continue
                
                # Use real-time price if available, otherwise use last candle close
                price = real_time_price if real_time_price > 0 else indicators['price']
                ema = indicators['ema']
                rsi = indicators['rsi']
                volume_ratio = indicators['volume_ratio']
                
                # Validate EMA: if EMA is more than 30% away from current price, cache may be stale
                # If stale, force refresh candle cache for this pair
                if price > 0 and ema > 0:
                    price_ema_ratio = abs(price - ema) / price
                    if price_ema_ratio > 0.30:  # More than 30% difference suggests stale data
                        logger.warning(f"⚠️ {pair}: EMA appears incorrect - Price=${price:.2f}, EMA=${ema:.2f} ({price_ema_ratio*100:.1f}% difference). Refreshing candle cache...")
                        # Force refresh candle cache for this pair
                        try:
                            import asyncio
                            from datetime import datetime, timedelta
                            fresh_candles = await self.bot.exchange.get_candles(
                                pair,
                                granularity='ONE_MINUTE',
                                start=datetime.utcnow() - timedelta(hours=24),
                                end=datetime.utcnow()
                            )
                            if fresh_candles:
                                self.bot.candle_cache[pair] = fresh_candles
                                logger.info(f"✅ {pair}: Candle cache refreshed with {len(fresh_candles)} candles")
                                # Recalculate indicators with fresh data
                                indicators = self.bot.strategy.calculate_indicators(fresh_candles)
                                if indicators:
                                    old_ema = ema  # Save old EMA for logging
                                    ema = indicators['ema']
                                    rsi = indicators['rsi']
                                    volume_ratio = indicators['volume_ratio']
                                    logger.info(f"✅ {pair}: Recalculated EMA=${ema:.2f} (was ${old_ema:.2f}), should be closer to price=${price:.2f}")
                        except Exception as refresh_error:
                            logger.error(f"Failed to refresh candle cache for {pair}: {refresh_error}", exc_info=True)
                
                # Update indicators with real-time price
                indicators['price'] = price
                
                # Check LONG conditions
                long_price_ok = price > ema
                long_rsi_ok = self.bot.config.RSI_LONG_MIN <= rsi <= self.bot.config.RSI_LONG_MAX
                long_volume_ok = volume_ratio >= self.bot.config.VOLUME_MULTIPLIER
                
                if long_price_ok and long_rsi_ok and long_volume_ok:
                    long_confidence = self.bot.strategy.calculate_confidence_score(indicators, 'LONG')
                    long_confident = long_confidence >= self.bot.config.MIN_CONFIDENCE_SCORE
                else:
                    long_confidence = self.bot.strategy.calculate_confidence_score(indicators, 'LONG')
                    long_confident = False
                
                # Check SHORT conditions
                short_price_ok = price < ema
                short_rsi_ok = self.bot.config.RSI_SHORT_MIN <= rsi <= self.bot.config.RSI_SHORT_MAX
                short_volume_ok = volume_ratio >= self.bot.config.VOLUME_MULTIPLIER
                
                if short_price_ok and short_rsi_ok and short_volume_ok:
                    short_confidence = self.bot.strategy.calculate_confidence_score(indicators, 'SHORT')
                    short_confident = short_confidence >= self.bot.config.MIN_CONFIDENCE_SCORE
                else:
                    short_confidence = self.bot.strategy.calculate_confidence_score(indicators, 'SHORT')
                    short_confident = False
                
                # Check if already has position
                has_position = any(p['pair'] == pair for p in self.bot.positions)
                
                conditions[pair] = {
                    'status': 'analyzing',
                    'indicators': {
                        'price': price,
                        'ema': ema,
                        'rsi': rsi,
                        'volume_ratio': volume_ratio,
                        'volume_avg': indicators.get('volume_avg', 0),
                        'current_volume': indicators.get('volume', 0)
                    },
                    'long_signal': {
                        'conditions_met': long_price_ok and long_rsi_ok and long_volume_ok,
                        'confidence': long_confidence,
                        'meets_threshold': long_confident,
                        'checks': {
                            'price_above_ema': long_price_ok,
                            'rsi_in_range': long_rsi_ok,
                            'volume_sufficient': long_volume_ok
                        },
                        'rsi_range': f'{self.bot.config.RSI_LONG_MIN}-{self.bot.config.RSI_LONG_MAX}',
                        'volume_required': f'{self.bot.config.VOLUME_MULTIPLIER}x average'
                    },
                    'short_signal': {
                        'conditions_met': short_price_ok and short_rsi_ok and short_volume_ok,
                        'confidence': short_confidence,
                        'meets_threshold': short_confident,
                        'checks': {
                            'price_below_ema': short_price_ok,
                            'rsi_in_range': short_rsi_ok,
                            'volume_sufficient': short_volume_ok
                        },
                        'rsi_range': f'{self.bot.config.RSI_SHORT_MIN}-{self.bot.config.RSI_SHORT_MAX}',
                        'volume_required': f'{self.bot.config.VOLUME_MULTIPLIER}x average'
                    },
                    'requirements': {
                        'min_confidence': self.bot.config.MIN_CONFIDENCE_SCORE,
                        'volume_multiplier': self.bot.config.VOLUME_MULTIPLIER
                    },
                    'blockers': [],
                    'has_position': has_position
                }
                
                # Identify blockers
                blockers = []
                if has_position:
                    blockers.append(f'Already has position in {pair}')
                if not long_confident and not short_confident:
                    blockers.append('No valid signal meets confidence threshold')
                if long_price_ok and long_rsi_ok and not long_volume_ok:
                    blockers.append(f'Volume too low: {volume_ratio:.2f}x (need {self.bot.config.VOLUME_MULTIPLIER}x)')
                if short_price_ok and short_rsi_ok and not short_volume_ok:
                    blockers.append(f'Volume too low: {volume_ratio:.2f}x (need {self.bot.config.VOLUME_MULTIPLIER}x)')
                
                conditions[pair]['blockers'] = blockers
                conditions[pair]['ready_to_trade'] = (long_confident or short_confident) and not has_position
            
            return web.json_response({
                'bot_status': self.bot.status,
                'bot_running': self.bot.status == 'running',
                'conditions': conditions,
                'summary': {
                    'total_pairs': len(self.bot.config.TRADING_PAIRS),
                    'pairs_with_data': sum(1 for c in conditions.values() if c.get('status') == 'analyzing'),
                    'ready_to_trade': any(c.get('ready_to_trade', False) for c in conditions.values()),
                    'max_positions': self.bot.config.MAX_POSITIONS,
                    'current_positions': len(self.bot.positions)
                }
            })
        except Exception as e:
            logger.error(f"Error getting market conditions: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_current_prices(self, request):
        """Get current real-time prices from exchange."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            # Force fetch real-time prices
            import asyncio
            market_data = await self.bot.exchange.get_market_data(self.bot.config.TRADING_PAIRS)
            
            prices = {}
            for pair, data in market_data.items():
                if not data:
                    continue
                    
                timestamp = data.get('timestamp')
                # Convert datetime to string if needed
                if isinstance(timestamp, datetime):
                    timestamp = timestamp.isoformat()
                elif not timestamp:
                    timestamp = datetime.utcnow().isoformat()
                elif not isinstance(timestamp, str):
                    timestamp = str(timestamp)
                
                prices[pair] = {
                    'price': float(data.get('price', 0)),
                    'volume_24h': float(data.get('volume_24h', 0)),
                    'timestamp': timestamp
                }
            
            return web.json_response({
                'prices': prices,
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'coinbase'
            })
        except Exception as e:
            logger.error(f"Error getting current prices: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_settings(self, request):
        """Get current bot settings."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            config = self.bot.config
            settings = {
                'ema_period': config.EMA_PERIOD,
                'rsi_period': config.RSI_PERIOD,
                'volume_period': config.VOLUME_PERIOD,
                'volume_multiplier': config.VOLUME_MULTIPLIER,
                'min_confidence': config.MIN_CONFIDENCE_SCORE,
                'loop_interval': config.LOOP_INTERVAL_SECONDS,
                'rsi_long_min': config.RSI_LONG_MIN,
                'rsi_long_max': config.RSI_LONG_MAX,
                'rsi_short_min': config.RSI_SHORT_MIN,
                'rsi_short_max': config.RSI_SHORT_MAX,
                'risk_per_trade': config.RISK_PER_TRADE_PCT,
                'max_positions': config.MAX_POSITIONS,
                'daily_loss_limit': config.DAILY_LOSS_LIMIT,
                'max_position_size': config.MAX_POSITION_SIZE_PCT,
                'position_timeout': config.POSITION_TIMEOUT_MINUTES,
                'take_profit_min': config.TAKE_PROFIT_MIN,
                'take_profit_max': config.TAKE_PROFIT_MAX,
                'stop_loss_min': config.STOP_LOSS_MIN,
                'stop_loss_max': config.STOP_LOSS_MAX,
                'trading_pairs': config.TRADING_PAIRS,
                'paper_trading': config.PAPER_TRADING,
                'use_real_market_data': config.USE_REAL_MARKET_DATA
            }
            return web.json_response(settings)
        except Exception as e:
            logger.error(f"Error getting settings: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def save_settings(self, request):
        """Save bot settings (requires restart to apply)."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            settings = await request.json()
            
            # Validate settings
            errors = []
            
            # Validate ranges
            if settings.get('rsi_long_min', 55) >= settings.get('rsi_long_max', 70):
                errors.append('RSI Long Min must be less than RSI Long Max')
            if settings.get('rsi_short_min', 30) >= settings.get('rsi_short_max', 45):
                errors.append('RSI Short Min must be less than RSI Short Max')
            if settings.get('take_profit_min', 0.15) >= settings.get('take_profit_max', 0.40):
                errors.append('Take Profit Min must be less than Take Profit Max')
            if settings.get('stop_loss_min', 0.10) >= settings.get('stop_loss_max', 0.50):
                errors.append('Stop Loss Min must be less than Stop Loss Max')
            
            if errors:
                return web.json_response({'error': '; '.join(errors)}, status=400)
            
            # Update config object (runtime changes)
            config = self.bot.config
            
            if 'ema_period' in settings:
                config.EMA_PERIOD = int(settings['ema_period'])
                self.bot.strategy.ema_period = config.EMA_PERIOD
            
            if 'rsi_period' in settings:
                config.RSI_PERIOD = int(settings['rsi_period'])
                self.bot.strategy.rsi_period = config.RSI_PERIOD
            
            if 'volume_period' in settings:
                config.VOLUME_PERIOD = int(settings['volume_period'])
                self.bot.strategy.volume_period = config.VOLUME_PERIOD
            
            if 'volume_multiplier' in settings:
                config.VOLUME_MULTIPLIER = float(settings['volume_multiplier'])
                self.bot.strategy.volume_multiplier = config.VOLUME_MULTIPLIER
            
            if 'min_confidence' in settings:
                config.MIN_CONFIDENCE_SCORE = float(settings['min_confidence'])
                self.bot.strategy.min_confidence = config.MIN_CONFIDENCE_SCORE
            
            if 'loop_interval' in settings:
                config.LOOP_INTERVAL_SECONDS = int(settings['loop_interval'])
            
            if 'rsi_long_min' in settings:
                config.RSI_LONG_MIN = float(settings['rsi_long_min'])
                self.bot.strategy.rsi_long_min = config.RSI_LONG_MIN
            
            if 'rsi_long_max' in settings:
                config.RSI_LONG_MAX = float(settings['rsi_long_max'])
                self.bot.strategy.rsi_long_max = config.RSI_LONG_MAX
            
            if 'rsi_short_min' in settings:
                config.RSI_SHORT_MIN = float(settings['rsi_short_min'])
                self.bot.strategy.rsi_short_min = config.RSI_SHORT_MIN
            
            if 'rsi_short_max' in settings:
                config.RSI_SHORT_MAX = float(settings['rsi_short_max'])
                self.bot.strategy.rsi_short_max = config.RSI_SHORT_MAX
            
            if 'risk_per_trade' in settings:
                config.RISK_PER_TRADE_PCT = float(settings['risk_per_trade'])
                self.bot.risk_manager.risk_per_trade_pct = config.RISK_PER_TRADE_PCT
            
            if 'max_positions' in settings:
                config.MAX_POSITIONS = int(settings['max_positions'])
                self.bot.risk_manager.max_positions = config.MAX_POSITIONS
            
            if 'daily_loss_limit' in settings:
                config.DAILY_LOSS_LIMIT = float(settings['daily_loss_limit'])
                self.bot.risk_manager.daily_loss_limit = config.DAILY_LOSS_LIMIT
            
            if 'max_position_size' in settings:
                config.MAX_POSITION_SIZE_PCT = float(settings['max_position_size'])
                self.bot.risk_manager.max_position_size_pct = config.MAX_POSITION_SIZE_PCT
            
            if 'position_timeout' in settings:
                config.POSITION_TIMEOUT_MINUTES = int(settings['position_timeout'])
                self.bot.risk_manager.position_timeout_minutes = config.POSITION_TIMEOUT_MINUTES
            
            if 'take_profit_min' in settings:
                config.TAKE_PROFIT_MIN = float(settings['take_profit_min'])
            
            if 'take_profit_max' in settings:
                config.TAKE_PROFIT_MAX = float(settings['take_profit_max'])
            
            if 'stop_loss_min' in settings:
                config.STOP_LOSS_MIN = float(settings['stop_loss_min'])
            
            if 'stop_loss_max' in settings:
                config.STOP_LOSS_MAX = float(settings['stop_loss_max'])
            
            if 'trading_pairs' in settings:
                config.TRADING_PAIRS = settings['trading_pairs']
            
            if 'paper_trading' in settings:
                config.PAPER_TRADING = bool(settings['paper_trading'])
                self.bot.exchange.paper_trading = config.PAPER_TRADING
            
            if 'use_real_market_data' in settings:
                config.USE_REAL_MARKET_DATA = bool(settings['use_real_market_data'])
            
            logger.info("Settings updated via API")
            
            return web.json_response({
                'message': 'Settings saved successfully. Some changes require bot restart.',
                'restart_required': True
            })
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_equity_curve(self, request):
        """Get equity curve data for charts."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        # Get current balance (with fallback)
        current_balance = 100000.0
        try:
            current_balance = await self.bot.exchange.get_account_balance()
        except:
            try:
                if hasattr(self.bot, 'initial_balance'):
                    current_balance = self.bot.initial_balance
                else:
                    current_balance = self.bot.config.ACCOUNT_SIZE
            except:
                current_balance = 100000.0
        
        try:
            limit = int(request.query.get('limit', 100))
            
            # Get equity curve from performance tracker
            equity_data = list(self.bot.performance_tracker.equity_curve)
            
            # If empty, create initial point
            if not equity_data:
                equity_data = [{
                    'timestamp': datetime.utcnow(),
                    'balance': current_balance
                }]
            
            # Limit and format
            equity_data = equity_data[-limit:]
            
            # Format the data
            formatted_data = []
            for point in equity_data:
                if not point:
                    continue
                    
                timestamp = point.get('timestamp')
                balance = point.get('balance', current_balance)
                
                # Format timestamp
                if timestamp:
                    if hasattr(timestamp, 'isoformat'):
                        timestamp_str = timestamp.isoformat()
                    else:
                        timestamp_str = str(timestamp)
                else:
                    timestamp_str = datetime.utcnow().isoformat()
                
                formatted_data.append({
                    'timestamp': timestamp_str,
                    'balance': float(balance)
                })
            
            return web.json_response({
                'equity_curve': formatted_data
            })
        except Exception as e:
            logger.error(f"Error getting equity curve: {e}", exc_info=True)
            # Return simple fallback
            return web.json_response({
                'equity_curve': [{
                    'timestamp': datetime.utcnow().isoformat(),
                    'balance': current_balance
                }]
            })
    
    async def get_daily_pnl(self, request):
        """Get daily P&L history for charts."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            limit = int(request.query.get('limit', 30))
            history = list(self.bot.performance_tracker.daily_pnl_history)
            
            return web.json_response({
                'daily_pnl': [
                    {
                        'date': str(d.get('date', '')),
                        'daily_pnl': d.get('daily_pnl', 0),
                        'total_trades': d.get('total_trades', 0)
                    }
                    for d in history[-limit:]
                ]
            })
        except Exception as e:
            logger.error(f"Error getting daily P&L: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_logs(self, request):
        """Get system logs."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            limit = int(request.query.get('limit', 500))
            level_filter = request.query.get('level', 'ALL')
            
            # Read log file
            import os
            log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tradingbot.log')
            
            logs = []
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()[-limit:]
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Parse log line format: "2025-11-25 22:01:23,330 - module - LEVEL - message"
                        # or aiohttp format: "2025-11-25 22:01:23,330 - aiohttp.access - INFO - 127.0.0.1 [28/Nov/2025:13:26:53 -0600] ..."
                        parts = line.split(' - ', 3)
                        
                        if len(parts) >= 4:
                            timestamp_str = parts[0]
                            module = parts[1]
                            level = parts[2]
                            message = parts[3]
                            
                            # Convert timestamp to ISO format for better JavaScript parsing
                            # Format: "2025-11-25 22:01:23,330" -> "2025-11-25T22:01:23.330Z"
                            timestamp_iso = timestamp_str
                            try:
                                # Parse Python log format: "2025-11-25 22:01:23,330"
                                if ',' in timestamp_str:
                                    # Has milliseconds with comma
                                    dt_str, ms_str = timestamp_str.split(',', 1)
                                    dt_obj = datetime.strptime(dt_str.strip(), '%Y-%m-%d %H:%M:%S')
                                    ms = ms_str.strip()[:3].ljust(3, '0')  # Ensure 3 digits
                                    timestamp_iso = dt_obj.isoformat() + '.' + ms + 'Z'
                                else:
                                    # No milliseconds
                                    dt_obj = datetime.strptime(timestamp_str.strip(), '%Y-%m-%d %H:%M:%S')
                                    timestamp_iso = dt_obj.isoformat() + '.000Z'
                            except Exception as e:
                                # If conversion fails, try simple replacement
                                try:
                                    timestamp_iso = timestamp_str.replace(' ', 'T').replace(',', '.')
                                    if '.' not in timestamp_iso:
                                        timestamp_iso += '.000'
                                    if not timestamp_iso.endswith('Z'):
                                        timestamp_iso += 'Z'
                                except Exception:
                                    # Last resort: use original as-is
                                    timestamp_iso = timestamp_str
                            
                            if level_filter == 'ALL' or level == level_filter:
                                logs.append({
                                    'timestamp': timestamp_iso,
                                    'timestamp_raw': timestamp_str,  # Keep original for display
                                    'module': module,
                                    'level': level,
                                    'message': message
                                })
            
            return web.json_response({'logs': logs})
        except Exception as e:
            logger.error(f"Error getting logs: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def download_logs(self, request):
        """Download log file."""
        import os
        log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tradingbot.log')
        
        if os.path.exists(log_file):
            return web.FileResponse(log_file, headers={
                'Content-Disposition': 'attachment; filename="tradingbot.log"'
            })
        else:
            return web.Response(text='Log file not found', status=404)
    
    async def get_available_coins(self, request):
        """Get list of available trading pairs from Coinbase."""
        try:
            # Fetch available products from Coinbase
            if not self.bot:
                return web.json_response({'error': 'Bot not initialized'}, status=500)
            
            # Use Coinbase public API to get available products
            import aiohttp
            async with aiohttp.ClientSession() as session:
                url = "https://api.exchange.coinbase.com/products"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        products = await response.json()
                        # Filter for USD pairs and extract symbols
                        usd_pairs = [p['id'] for p in products if p.get('id', '').endswith('-USD') and p.get('status') == 'online']
                        return web.json_response({
                            'available_pairs': sorted(usd_pairs),
                            'count': len(usd_pairs)
                        })
            
            # Fallback to common pairs
            return web.json_response({
                'available_pairs': [
                    'BTC-USD', 'ETH-USD', 'LTC-USD', 'BCH-USD', 'LINK-USD',
                    'SOL-USD', 'ADA-USD', 'DOT-USD', 'MATIC-USD', 'AVAX-USD',
                    'UNI-USD', 'AAVE-USD', 'ALGO-USD', 'ATOM-USD', 'FIL-USD'
                ],
                'count': 15
            })
        except Exception as e:
            logger.error(f"Error getting available coins: {e}", exc_info=True)
            # Return common pairs as fallback
            return web.json_response({
                'available_pairs': ['BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD'],
                'count': 4
            })
    
    async def get_templates(self, request):
        """Get saved configuration templates."""
        import os
        import json
        
        template_name = request.query.get('name', '')
        
        templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
        
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
        
        if template_name:
            # Return specific template
            template_file = os.path.join(templates_dir, f'{template_name}.json')
            if os.path.exists(template_file):
                try:
                    with open(template_file, 'r') as f:
                        template_data = json.load(f)
                        return web.json_response({
                            'templates': [{
                                'name': template_name,
                                'data': template_data
                            }]
                        })
                except Exception as e:
                    logger.error(f"Error loading template: {e}", exc_info=True)
                    return web.json_response({'error': str(e)}, status=500)
            else:
                return web.json_response({'error': 'Template not found'}, status=404)
        
        # Return all templates
        templates = []
        if os.path.exists(templates_dir):
            for filename in os.listdir(templates_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(templates_dir, filename), 'r') as f:
                            template_data = json.load(f)
                            templates.append({
                                'name': filename.replace('.json', ''),
                                'data': template_data,
                                'created': os.path.getctime(os.path.join(templates_dir, filename))
                            })
                    except:
                        continue
        
        return web.json_response({'templates': sorted(templates, key=lambda x: x.get('created', 0), reverse=True)})
    
    async def save_template(self, request):
        """Save current settings as a template."""
        import os
        import json
        data = await request.json()
        
        template_name = data.get('name', 'template')
        settings = data.get('settings', {})
        
        # Sanitize filename
        template_name = ''.join(c for c in template_name if c.isalnum() or c in ('-', '_'))[:50]
        
        templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
        
        template_file = os.path.join(templates_dir, f'{template_name}.json')
        
        try:
            with open(template_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            return web.json_response({'message': f'Template "{template_name}" saved successfully'})
        except Exception as e:
            logger.error(f"Error saving template: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def list_templates(self, request):
        """List all saved templates."""
        import os
        templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
        
        if not os.path.exists(templates_dir):
            return web.json_response({'templates': []})
        
        templates = [f.replace('.json', '') for f in os.listdir(templates_dir) if f.endswith('.json')]
        return web.json_response({'templates': sorted(templates)})
    
    async def delete_template(self, request):
        """Delete a saved template."""
        import os
        template_name = request.match_info.get('name', '')
        template_name = ''.join(c for c in template_name if c.isalnum() or c in ('-', '_'))[:50]
        
        templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
        template_file = os.path.join(templates_dir, f'{template_name}.json')
        
        try:
            if os.path.exists(template_file):
                os.remove(template_file)
                return web.json_response({'message': f'Template "{template_name}" deleted'})
            else:
                return web.json_response({'error': 'Template not found'}, status=404)
        except Exception as e:
            logger.error(f"Error deleting template: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)

    async def serve_landing(self, request):
        """Serve landing page."""
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        landing_path = os.path.join(project_root, 'static', 'landing.html')
        
        try:
            if os.path.exists(landing_path):
                # Read file content and serve as text to avoid FileResponse issues
                with open(landing_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return web.Response(
                    text=content,
                    content_type='text/html',
                    headers={
                        'Cache-Control': 'no-cache, no-store, must-revalidate',
                        'Pragma': 'no-cache',
                        'Expires': '0'
                    }
                )
            else:
                logger.error(f"Landing page not found at: {landing_path}")
                return web.Response(text='Landing page not found', status=404)
        except Exception as e:
            logger.error(f"Error serving landing page: {e}", exc_info=True)
            return web.Response(text=f'Error loading landing page: {str(e)}', status=500)
    
    async def serve_signup(self, request):
        """Serve signup page."""
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        signup_path = os.path.join(project_root, 'static', 'signup.html')
        
        try:
            if os.path.exists(signup_path):
                # Read file content and serve as text to avoid FileResponse issues
                with open(signup_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return web.Response(
                    text=content,
                    content_type='text/html',
                    headers={
                        'Cache-Control': 'no-cache, no-store, must-revalidate',
                        'Pragma': 'no-cache',
                        'Expires': '0'
                    }
                )
            else:
                logger.error(f"Signup page not found at: {signup_path}")
                return web.Response(text='Signup page not found', status=404)
        except Exception as e:
            logger.error(f"Error serving signup page: {e}", exc_info=True)
            return web.Response(text=f'Error loading signup page: {str(e)}', status=500)
    
    async def serve_signin(self, request):
        """Serve signin page."""
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        signin_path = os.path.join(project_root, 'static', 'signin.html')
        
        try:
            if os.path.exists(signin_path):
                # Read file content and serve as text to avoid FileResponse issues
                with open(signin_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return web.Response(
                    text=content,
                    content_type='text/html',
                    headers={
                        'Cache-Control': 'no-cache, no-store, must-revalidate',
                        'Pragma': 'no-cache',
                        'Expires': '0'
                    }
                )
            else:
                logger.error(f"Signin page not found at: {signin_path}")
                return web.Response(text='Signin page not found', status=404)
        except Exception as e:
            logger.error(f"Error serving signin page: {e}", exc_info=True)
            return web.Response(text=f'Error loading signin page: {str(e)}', status=500)
    
    async def serve_test_runner(self, request):
        """Serve test runner page."""
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_runner_path = os.path.join(project_root, 'test-dashboard-simple.html')
        
        if os.path.exists(test_runner_path):
            return web.FileResponse(test_runner_path)
        else:
            return web.Response(text='Test runner page not found', status=404)
    
    async def serve_settings(self, request):
        """Serve settings page."""
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        settings_path = os.path.join(project_root, 'static', 'settings.html')
        
        try:
            if os.path.exists(settings_path):
                # Read file content and serve as text to avoid FileResponse issues
                with open(settings_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return web.Response(
                    text=content,
                    content_type='text/html',
                    headers={
                        'Cache-Control': 'no-cache, no-store, must-revalidate',
                        'Pragma': 'no-cache',
                        'Expires': '0'
                    }
                )
            else:
                logger.warning(f"Settings page not found at: {settings_path}, falling back to dashboard")
                return await self.serve_dashboard(request)  # Fallback
        except Exception as e:
            logger.error(f"Error serving settings page: {e}", exc_info=True)
            return await self.serve_dashboard(request)  # Fallback on error
    
    async def serve_help(self, request):
        """Serve help page."""
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        help_path = os.path.join(project_root, 'static', 'help.html')
        
        try:
            if os.path.exists(help_path):
                # Read file content and serve as text to avoid FileResponse issues
                with open(help_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return web.Response(
                    text=content,
                    content_type='text/html',
                    headers={
                        'Cache-Control': 'no-cache, no-store, must-revalidate',
                        'Pragma': 'no-cache',
                        'Expires': '0'
                    }
                )
            else:
                logger.error(f"Help page not found at: {help_path}")
                return web.Response(text='Help page not found', status=404)
        except Exception as e:
            logger.error(f"Error serving help page: {e}", exc_info=True)
            return web.Response(text=f'Error loading help page: {str(e)}', status=500)
    
    # Authentication endpoints
    async def signup(self, request):
        """Handle user signup."""
        if not self.db_manager:
            return web.json_response({'error': 'Database not initialized'}, status=500)
        
        # Ensure database is initialized
        if not self.db_manager.initialized:
            await self.db_manager.initialize()
        
        try:
            data = await request.json()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            full_name = data.get('full_name', '').strip()
            
            # Validation
            if not email or not password:
                return web.json_response({'error': 'Email and password are required'}, status=400)
            
            if len(password) < 8:
                return web.json_response({'error': 'Password must be at least 8 characters'}, status=400)
            
            # Check if user already exists
            existing_user = await self.db_manager.get_user_by_email(email)
            if existing_user:
                return web.json_response({'error': 'User with this email already exists'}, status=400)
            
            # Hash password
            password_hash = self.auth_manager.hash_password(password)
            
            # Create user
            user_id = await self.db_manager.create_user(email, password_hash, full_name)
            
            if not user_id:
                return web.json_response({'error': 'Failed to create user'}, status=500)
            
            # Generate token
            token = self.auth_manager.generate_token(user_id, email)
            
            response = web.json_response({
                'message': 'User created successfully',
                'token': token,
                'user': {
                    'id': user_id,
                    'email': email,
                    'full_name': full_name
                }
            })
            
            # Set token as HTTP-only cookie
            response.set_cookie('auth_token', token, httponly=True, max_age=86400, samesite='Lax')
            
            return response
            
        except Exception as e:
            logger.error(f"Signup error: {e}", exc_info=True)
            return web.json_response({'error': 'Internal server error'}, status=500)
    
    async def signin(self, request):
        """Handle user signin."""
        if not self.db_manager:
            return web.json_response({'error': 'Database not initialized'}, status=500)
        
        # Ensure database is initialized
        if not self.db_manager.initialized:
            await self.db_manager.initialize()
        
        try:
            data = await request.json()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            if not email or not password:
                return web.json_response({'error': 'Email and password are required'}, status=400)
            
            # Get user
            user = await self.db_manager.get_user_by_email(email)
            
            if not user:
                return web.json_response({'error': 'Invalid email or password'}, status=401)
            
            if not user.get('is_active', True):
                return web.json_response({'error': 'Account is inactive'}, status=403)
            
            # Verify password
            if not self.auth_manager.verify_password(password, user['password_hash']):
                return web.json_response({'error': 'Invalid email or password'}, status=401)
            
            # Update last login
            await self.db_manager.update_last_login(user['id'])
            
            # Generate token
            token = self.auth_manager.generate_token(user['id'], user['email'])
            
            response = web.json_response({
                'message': 'Signed in successfully',
                'token': token,
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'full_name': user.get('full_name')
                }
            })
            
            # Set token as HTTP-only cookie
            response.set_cookie('auth_token', token, httponly=True, max_age=86400, samesite='Lax')
            
            return response
            
        except Exception as e:
            logger.error(f"Signin error: {e}", exc_info=True)
            return web.json_response({'error': 'Internal server error'}, status=500)
    
    async def verify_token(self, request):
        """Verify authentication token."""
        auth_header = request.headers.get('Authorization', '')
        token = self.auth_manager.extract_token_from_header(auth_header)
        
        if not token:
            token = request.cookies.get('auth_token')
        
        if not token:
            return web.json_response({'error': 'No token provided'}, status=401)
        
        payload = self.auth_manager.verify_token(token)
        
        if not payload:
            return web.json_response({'error': 'Invalid or expired token'}, status=401)
        
        return web.json_response({
            'valid': True,
            'user_id': payload['user_id'],
            'email': payload['email']
        })
    
    async def logout(self, request):
        """Handle user logout."""
        response = web.json_response({'message': 'Logged out successfully'})
        response.del_cookie('auth_token')
        return response
    
    async def serve_logs(self, request):
        """Serve logs page."""
        return await self.serve_dashboard(request)
    
    # Backtesting endpoints
    async def run_backtest(self, request):
        """Run a backtest with specified parameters."""
        # CRITICAL: Log to BOTH stdout AND stderr to ensure it appears
        import sys
        print("=" * 80, file=sys.stderr)
        print("🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥", file=sys.stderr)
        print("🔥 BACKTEST RUN REQUEST RECEIVED 🔥", file=sys.stderr)
        print(f"Request method: {request.method}, path: {request.path}", file=sys.stderr)
        print("=" * 80, file=sys.stderr)
        sys.stderr.flush()
        
        logger.info("=" * 80)
        logger.info("🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥")
        logger.info("🔥 BACKTEST RUN REQUEST RECEIVED 🔥")
        logger.info(f"Request method: {request.method}, path: {request.path}")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request content_type: {request.content_type}")
        logger.info(f"User ID from request: {request.get('user_id')} (type: {type(request.get('user_id'))})")
        logger.info("🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥")
        logger.info("=" * 80)
        
        try:
            data = await request.json()
            logger.info(f"Backtest request data: {data}")
            
            from backtesting import BacktestEngine, HistoricalDataFetcher
            from datetime import datetime, timedelta
            import asyncio
            import concurrent.futures
            
            # Get parameters
            pair = data.get('pair', 'BTC-USD')
            days = int(data.get('days', 30))
            initial_balance = float(data.get('initial_balance', 100000.0))
            name = data.get('name', f'Backtest {pair} {days}d')
            user_id = request.get('user_id')
            
            # Log user_id for debugging
            logger.info(f"🔵 Starting backtest: user_id={user_id}, pair={pair}, days={days}, name={name}, balance=${initial_balance}")
            
            # Determine granularity based on days (optimize for performance)
            # For longer backtests, use larger candles to reduce processing time
            # This is CRITICAL to avoid timeouts and container kills
            # NOTE: For scalping strategies, 1-7 day backtests are most relevant
            # Use larger granularity for longer periods to reduce candle count and processing time
            if days >= 60:
                granularity = 'ONE_HOUR'  # 1-hour candles for 60+ days (very long backtests)
                logger.info(f"⚡ Using 1-hour candles for {days}-day backtest to optimize performance (~{days * 24} candles)")
                logger.warning(f"⚠️ For scalping strategies, backtests longer than 30 days may not be representative. Consider 1-7 days for best results.")
            elif days >= 14:
                granularity = 'FIFTEEN_MINUTE'  # 15-minute candles for 14-59 days (reduced from 30 to handle 21-day tests better)
                logger.info(f"⚡ Using 15-minute candles for {days}-day backtest to optimize performance (~{days * 24 * 4} candles)")
                logger.warning(f"⚠️ For scalping strategies, backtests longer than 7 days may not be representative. Consider 1-7 days for best results.")
            elif days >= 7:
                granularity = 'FIVE_MINUTE'  # 5-minute candles for 7-13 days
                logger.info(f"⚡ Using 5-minute candles for {days}-day backtest to optimize performance (~{days * 24 * 12} candles)")
            else:
                granularity = 'ONE_MINUTE'  # 1-minute candles for short backtests (1-6 days) - BEST for scalping
                logger.info(f"✅ Using 1-minute candles for {days}-day backtest (~{days * 24 * 60} candles) - Optimal for scalping strategies")
            
            # Fetch historical data
            fetcher = HistoricalDataFetcher(self.config)
            start_date = datetime.utcnow() - timedelta(days=days)
            end_date = datetime.utcnow()
            
            logger.info(f"📊 Fetching historical data for {pair} from {start_date} to {end_date} ({days} days, {granularity})")
            logger.info(f"📊 About to call fetcher.fetch_candles() with timeout=120s")
            fetch_start_time = datetime.utcnow()
            try:
                candles = await asyncio.wait_for(
                    fetcher.fetch_candles(pair, start_date, end_date, granularity=granularity),
                    timeout=120  # 2 minute timeout for data fetch
                )
                fetch_duration = (datetime.utcnow() - fetch_start_time).total_seconds()
                logger.info(f"✅ Successfully fetched {len(candles)} candles in {fetch_duration:.2f} seconds")
            except asyncio.TimeoutError:
                fetch_duration = (datetime.utcnow() - fetch_start_time).total_seconds()
                logger.error(f"❌❌❌ Historical data fetch timed out after 120 seconds (actual wait: {fetch_duration:.2f}s)")
                return web.json_response({
                    'error': 'Historical data fetch timed out. Please try a shorter time period or larger granularity.'
                }, status=504)
            except Exception as fetch_error:
                fetch_duration = (datetime.utcnow() - fetch_start_time).total_seconds()
                logger.error(f"❌❌❌ Error fetching historical data after {fetch_duration:.2f}s: {fetch_error}", exc_info=True)
                import traceback
                logger.error(f"   Full traceback: {traceback.format_exc()}")
                return web.json_response({
                    'error': f'Failed to fetch historical data: {str(fetch_error)}'
                }, status=500)
            
            if not candles or len(candles) < 100:
                logger.warning(f"⚠️ Insufficient historical data: got {len(candles) if candles else 0} candles, need at least 100")
                return web.json_response({
                    'error': f'Insufficient historical data. Got {len(candles) if candles else 0} candles. Need at least 100.'
                }, status=400)
            
            logger.info(f"🔄 Fetched {len(candles)} candles. Starting backtest processing...")
            
            # Run backtest in executor to avoid blocking the event loop
            # This is critical for long backtests that process thousands of candles
            def run_backtest_sync():
                """Run backtest synchronously in thread pool."""
                try:
                    engine = BacktestEngine(self.config, initial_balance=initial_balance)
                    results = engine.run_backtest(candles, pair=pair)
                    return results
                except Exception as e:
                    logger.error(f"Error in backtest execution: {e}", exc_info=True)
                    raise
            
            # Use thread pool executor to run blocking backtest
            # CRITICAL: Railway HTTP timeout is ~30-60 seconds, so we need to complete faster
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                # Calculate timeout: cap at 50 seconds to stay under Railway's HTTP timeout (60s)
                # Estimate ~0.004 seconds per candle (4ms) - realistic for scalping with indicators
                # Scalping strategies process each candle with multiple indicators (RSI, EMA, volume), so it's slower
                # For 1-minute candles, each candle requires full indicator recalculation
                # Real-world testing shows 3-5ms per candle is more accurate
                candle_processing_time = len(candles) * 0.004  # 4ms per candle (realistic estimate)
                estimated_timeout = min(50, max(20, candle_processing_time + 15))  # 20-50 seconds max (larger buffer)
                logger.info(f"⏱️ Running backtest with timeout of {estimated_timeout:.1f} seconds (Railway HTTP timeout protection)")
                logger.info(f"   Processing {len(candles)} candles at ~4ms per candle (estimated {candle_processing_time:.1f}s)")
                logger.info(f"   Timeout buffer: +15s safety margin (total: {estimated_timeout:.1f}s)")
                
                try:
                    results = await asyncio.wait_for(
                        loop.run_in_executor(executor, run_backtest_sync),
                        timeout=estimated_timeout
                    )
                except asyncio.TimeoutError:
                    logger.error(f"❌ Backtest timed out after {estimated_timeout:.1f} seconds (Railway HTTP timeout)")
                    # Provide specific guidance based on backtest length
                    if days >= 30:
                        recommendation = "For scalping strategies, use 1-7 day backtests for best results. Longer periods (30+ days) are less relevant for scalping."
                    elif days >= 7:
                        recommendation = "Try a 1-7 day backtest for scalping strategies. This provides better accuracy and faster results."
                    else:
                        recommendation = "The backtest may be too intensive. Try reducing the time period slightly."
                    
                    return web.json_response({
                        'error': f'Backtest timed out after {estimated_timeout:.1f} seconds. Railway has a 30-60 second HTTP timeout.',
                        'recommendation': recommendation,
                        'optimal_periods': 'For crypto scalping: 1-3 days (best), 3-7 days (good), 7-30 days (acceptable but less representative)'
                    }, status=504)
            
            logger.info(f"✅ Backtest processing completed: {results['total_trades']} trades, P&L: ${results['total_pnl']:.2f}")
            
            # Save to database
            logger.info(f"💾 Preparing to save backtest to database: name={name}, pair={pair}, user_id={user_id}")
            backtest_data = {
                'name': name,
                'pair': pair,
                'start_date': start_date,
                'end_date': end_date,
                'initial_balance': initial_balance,
                'final_balance': results['final_balance'],
                'total_pnl': results['total_pnl'],
                'total_trades': results['total_trades'],
                'winning_trades': results['winning_trades'],
                'losing_trades': results['losing_trades'],
                'win_rate': results['win_rate'],
                'profit_factor': results['profit_factor'],
                'max_drawdown': results['max_drawdown'],
                'roi_pct': results['roi_pct'],
                'results': results  # Store full results for detailed view
            }
            
            # Extract additional fields from results for display
            backtest_data['avg_win'] = results.get('avg_win', 0)
            backtest_data['avg_loss'] = results.get('avg_loss', 0)
            backtest_data['sharpe_ratio'] = results.get('performance', {}).get('sharpe_ratio', 0) if isinstance(results.get('performance'), dict) else 0
            backtest_data['gross_profit'] = sum(t.get('pnl', 0) for t in results.get('trades', []) if t.get('pnl', 0) > 0)
            
            # CRITICAL: Sanitize Infinity/NaN values in results dict ONLY (for JSON serialization)
            # DO NOT sanitize start_date/end_date - they must remain datetime objects for database
            logger.info(f"🧹 Sanitizing backtest results (converting Infinity/NaN to None, preserving datetime objects)")
            # Only sanitize the 'results' dict, not the top-level datetime fields
            if 'results' in backtest_data:
                backtest_data['results'] = self._sanitize_dict(backtest_data['results'])
            # Sanitize numeric fields but preserve datetime objects
            for key in ['win_rate', 'profit_factor', 'max_drawdown', 'roi_pct', 'total_pnl', 'initial_balance', 'final_balance']:
                if key in backtest_data and isinstance(backtest_data[key], float):
                    if backtest_data[key] != backtest_data[key] or backtest_data[key] in (float('inf'), float('-inf')):
                        backtest_data[key] = None
            
            logger.info(f"💾 Backtest data prepared and sanitized. db_manager={self.db_manager is not None}, initialized={self.db_manager.initialized if self.db_manager else False}, user_id={user_id}")
            
            # CRITICAL: Verify start_date and end_date are datetime objects (not strings) before save
            start_date_obj = backtest_data.get('start_date')
            end_date_obj = backtest_data.get('end_date')
            
            if not isinstance(start_date_obj, datetime):
                logger.error(f"❌❌❌ start_date is NOT a datetime object! Type: {type(start_date_obj)}, Value: {start_date_obj}")
                if isinstance(start_date_obj, str):
                    try:
                        start_date_obj = datetime.fromisoformat(start_date_obj.replace('Z', '+00:00'))
                        backtest_data['start_date'] = start_date_obj
                        logger.warning(f"⚠️ Converted start_date string to datetime: {start_date_obj}")
                    except Exception as e:
                        logger.error(f"❌ Failed to convert start_date string to datetime: {e}")
            else:
                logger.info(f"✅ start_date is datetime object: {start_date_obj}")
                
            if not isinstance(end_date_obj, datetime):
                logger.error(f"❌❌❌ end_date is NOT a datetime object! Type: {type(end_date_obj)}, Value: {end_date_obj}")
                if isinstance(end_date_obj, str):
                    try:
                        end_date_obj = datetime.fromisoformat(end_date_obj.replace('Z', '+00:00'))
                        backtest_data['end_date'] = end_date_obj
                        logger.warning(f"⚠️ Converted end_date string to datetime: {end_date_obj}")
                    except Exception as e:
                        logger.error(f"❌ Failed to convert end_date string to datetime: {e}")
            else:
                logger.info(f"✅ end_date is datetime object: {end_date_obj}")
            
            # Save to database - CRITICAL: Log user_id at every step for debugging
            logger.info(f"🔍🔍🔍 PRE-SAVE CHECK: user_id={user_id} (type: {type(user_id)}), db_manager={self.db_manager is not None}, initialized={self.db_manager.initialized if self.db_manager else False}")
            
            backtest_id = None
            if self.db_manager:
                if self.db_manager.initialized:
                    try:
                        logger.info(f"💾💾💾 Calling save_backtest with user_id={user_id}, name={name}, pair={pair}")
                        
                        # Get count BEFORE save
                        async with self.db_manager.pool.acquire() as conn:
                            count_before = await conn.fetchval("SELECT COUNT(*) FROM backtests")
                            logger.info(f"🔍 Database has {count_before} backtests BEFORE save")
                        
                        backtest_id = await self.db_manager.save_backtest(backtest_data, user_id)
                        logger.info(f"💾💾💾 save_backtest returned: {backtest_id} (type: {type(backtest_id)})")
                        
                        # Verify save by querying database
                        if backtest_id:
                            async with self.db_manager.pool.acquire() as conn:
                                count_after = await conn.fetchval("SELECT COUNT(*) FROM backtests")
                                saved_record = await conn.fetchrow("SELECT id, user_id, name FROM backtests WHERE id = $1", backtest_id)
                                logger.info(f"🔍 Database has {count_after} backtests AFTER save (was {count_before})")
                                if saved_record:
                                    logger.info(f"✅✅✅✅✅✅✅✅✅✅✅✅ BACKTEST VERIFIED IN DATABASE! ID: {backtest_id}, user_id: {saved_record['user_id']}, name: {saved_record['name']}")
                                else:
                                    logger.error(f"❌❌❌ BACKTEST ID RETURNED BUT NOT FOUND IN DATABASE! ID: {backtest_id}")
                            
                            backtest_data['id'] = backtest_id
                            logger.info(f"✅✅✅✅✅✅✅✅✅✅✅✅ BACKTEST SAVED SUCCESSFULLY! ID: {backtest_id}, user_id: {user_id}, name: {name}, pair: {pair}")
                        else:
                            async with self.db_manager.pool.acquire() as conn:
                                count_after = await conn.fetchval("SELECT COUNT(*) FROM backtests")
                                logger.info(f"🔍 Database still has {count_after} backtests AFTER failed save (was {count_before})")
                            logger.error(f"❌❌❌❌❌❌ FAILED TO SAVE BACKTEST: save_backtest returned None (user_id: {user_id}, name: {name}, pair: {pair})")
                    except Exception as save_error:
                        logger.error(f"❌❌❌❌❌❌ EXCEPTION SAVING BACKTEST: {save_error}", exc_info=True)
                        import traceback
                        logger.error(f"Full traceback: {traceback.format_exc()}")
                else:
                    logger.error(f"❌❌❌ Database manager exists but NOT INITIALIZED (user_id: {user_id})")
            else:
                logger.error(f"❌❌❌ Database manager is NONE - backtest NOT saved (user_id: {user_id})")
            
            # If save failed, still return results but log warning
            if not backtest_id:
                logger.warning(f"⚠️⚠️⚠️ BACKTEST COMPLETED BUT NOT SAVED TO DATABASE (user_id: {user_id}, db_manager exists: {self.db_manager is not None})")
                # Try to query database to see if ANY backtests exist (diagnostic)
                if self.db_manager and self.db_manager.initialized:
                    try:
                        async with self.db_manager.pool.acquire() as conn:
                            total_count = await conn.fetchval("SELECT COUNT(*) FROM backtests")
                            logger.info(f"🔍 DIAGNOSTIC: Total backtests in database: {total_count}")
                    except Exception as diag_error:
                        logger.error(f"🔍 Diagnostic query failed: {diag_error}")
            
            # Format results for JSON (convert datetime objects)
            formatted_results = self._format_backtest_results(backtest_data)
            
            # Final log before returning response - CRITICAL: This confirms handler completed
            logger.info(f"📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤")
            logger.info(f"📤 RETURNING BACKTEST RESPONSE: success=True, backtest_id={backtest_data.get('id')}, user_id={user_id}, saved={backtest_id is not None}")
            logger.info(f"📤 Results summary: {formatted_results.get('total_trades', 0)} trades, P&L: ${formatted_results.get('total_pnl', 0):.2f}")
            logger.info(f"📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤📤")
            
            return web.json_response({
                'success': True,
                'backtest_id': backtest_data.get('id'),
                'results': formatted_results
            })
            
        except Exception as e:
            logger.error(f"Error running backtest: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def list_backtests(self, request):
        """List all backtests for the current user."""
        try:
            user_id = request.get('user_id')
            logger.info(f"🔍🔍🔍 LIST BACKTESTS: user_id={user_id} (type: {type(user_id)}), db_manager={self.db_manager is not None}, initialized={self.db_manager.initialized if self.db_manager else False}")
            
            if not self.db_manager:
                logger.error("Database manager not available for list_backtests")
                return web.json_response({'error': 'Database not initialized'}, status=500)
            
            if not self.db_manager.initialized:
                logger.error("Database manager not initialized for list_backtests")
                return web.json_response({'error': 'Database not initialized'}, status=500)
            
            limit = int(request.query.get('limit', 20))
            
            # Log before and after query
            logger.info(f"🔍 Querying database for backtests: user_id={user_id}, limit={limit}")
            backtests = await self.db_manager.get_backtests(user_id, limit)
            logger.info(f"🔍🔍🔍 Retrieved {len(backtests)} backtests from database for user_id: {user_id}")
            if len(backtests) == 0:
                logger.warning(f"⚠️⚠️⚠️ NO BACKTESTS FOUND for user_id: {user_id} - This might mean backtests were saved with a different user_id or NULL")
            
            # Format for JSON
            formatted_backtests = []
            for bt in backtests:
                formatted = self._format_backtest_results(bt)
                formatted_backtests.append(formatted)
            
            logger.info(f"Returning {len(formatted_backtests)} formatted backtests")
            return web.json_response({'backtests': formatted_backtests})
            
        except Exception as e:
            logger.error(f"Error listing backtests: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def test_backtest_route(self, request):
        """Simple test endpoint to verify routing is working."""
        import sys
        print("TEST ROUTE CALLED", file=sys.stderr)
        sys.stderr.flush()
        logger.info("TEST BACKTEST ROUTE CALLED - Routing is working!")
        return web.json_response({
            'status': 'success',
            'message': 'Backtest route is accessible',
            'user_id': request.get('user_id'),
            'db_manager_exists': self.db_manager is not None,
            'db_manager_initialized': self.db_manager.initialized if self.db_manager else False
        })
    
    async def test_backtest_post(self, request):
        """Test POST endpoint to verify POST requests are working."""
        import sys
        print("=" * 80, file=sys.stderr)
        print("🧪🧪🧪 TEST POST ENDPOINT CALLED 🧪🧪🧪", file=sys.stderr)
        print(f"Method: {request.method}, Path: {request.path}", file=sys.stderr)
        sys.stderr.flush()
        logger.info("🧪 TEST POST ENDPOINT CALLED")
        
        try:
            data = await request.json()
            logger.info(f"🧪 POST data received: {data}")
        except:
            logger.info("🧪 No JSON data in POST request")
        
        return web.json_response({
            'status': 'success',
            'message': 'POST request received successfully!',
            'method': request.method,
            'path': request.path,
            'user_id': request.get('user_id'),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def debug_backtest_count(self, request):
        """Diagnostic endpoint to check total backtests in database."""
        try:
            if not self.db_manager or not self.db_manager.initialized:
                return web.json_response({'error': 'Database not initialized'}, status=500)
            
            async with self.db_manager.pool.acquire() as conn:
                total_count = await conn.fetchval("SELECT COUNT(*) FROM backtests")
                user_id_count = await conn.fetchval("SELECT COUNT(*) FROM backtests WHERE user_id = $1", request.get('user_id'))
                null_user_count = await conn.fetchval("SELECT COUNT(*) FROM backtests WHERE user_id IS NULL")
                
                # Get most recent backtest
                recent = await conn.fetchrow("""
                    SELECT id, name, user_id, created_at FROM backtests 
                    ORDER BY created_at DESC LIMIT 1
                """)
                
                result = {
                    'total_backtests': total_count,
                    'user_id_backtests': user_id_count,
                    'null_user_id_backtests': null_user_count,
                    'current_user_id': request.get('user_id'),
                    'most_recent': dict(recent) if recent else None
                }
                
                logger.info(f"🔍 DEBUG BACKTEST COUNT: {result}")
                return web.json_response(result)
        except Exception as e:
            logger.error(f"Error in debug_backtest_count: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_backtest_results(self, request):
        """Get detailed results for a specific backtest."""
        if not self.db_manager:
            return web.json_response({'error': 'Database not initialized'}, status=500)
        
        try:
            backtest_id = int(request.match_info['id'])
            user_id = request.get('user_id')
            
            backtest = await self.db_manager.get_backtest_by_id(backtest_id, user_id)
            
            if not backtest:
                return web.json_response({'error': 'Backtest not found'}, status=404)
            
            formatted = self._format_backtest_results(backtest)
            
            return web.json_response({'backtest': formatted})
            
        except Exception as e:
            logger.error(f"Error getting backtest results: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    def _format_backtest_results(self, backtest_data: Dict) -> Dict:
        """Format backtest results for JSON response (handle datetime objects, Infinity, NaN, Decimal)."""
        from decimal import Decimal
        formatted = dict(backtest_data)
        
        # Convert datetime objects to ISO strings
        for key in ['start_date', 'end_date', 'created_at']:
            if key in formatted and formatted[key]:
                if hasattr(formatted[key], 'isoformat'):
                    formatted[key] = formatted[key].isoformat()
        
        # Convert Infinity and NaN to JSON-safe values
        def sanitize_value(value):
            """Convert Infinity/NaN to JSON-safe values."""
            if isinstance(value, float):
                if value == float('inf') or value == float('-inf'):
                    return None  # or 999999.0 if you prefer a large number
                if value != value:  # NaN check
                    return None
            return value
        
        # Sanitize all numeric values in the top-level dict (including Decimal)
        for key, value in formatted.items():
            if isinstance(value, Decimal):
                formatted[key] = float(value)
            elif isinstance(value, (int, float)):
                formatted[key] = sanitize_value(value)
            elif isinstance(value, dict):
                # Recursively sanitize dict values
                formatted[key] = self._sanitize_dict(value)
            elif isinstance(value, list):
                # Sanitize list items (handle Decimal, int, float)
                def sanitize_list_item(item):
                    if isinstance(item, Decimal):
                        return float(item)
                    elif isinstance(item, dict):
                        return self._sanitize_dict(item)
                    elif isinstance(item, (int, float)):
                        return sanitize_value(item)
                    return item
                formatted[key] = [sanitize_list_item(item) for item in value]
        
        # Format results dictionary if it exists
        if 'results' in formatted and isinstance(formatted['results'], dict):
            results = formatted['results']
            # Recursively sanitize the entire results dictionary (handles datetime, Infinity, NaN)
            formatted['results'] = self._sanitize_dict(results)
            results = formatted['results']  # Use sanitized version
            
            # Format equity curve timestamps (now redundant but safe)
            if 'equity_curve' in results:
                for point in results['equity_curve']:
                    if 'timestamp' in point and hasattr(point['timestamp'], 'isoformat'):
                        point['timestamp'] = point['timestamp'].isoformat()
                    # Sanitize numeric values (including Decimal from PostgreSQL)
                    for k, v in point.items():
                        if isinstance(v, Decimal):
                            point[k] = float(v)
                        elif isinstance(v, (int, float)):
                            point[k] = sanitize_value(v)
            
            # Format trade timestamps and sanitize values
            if 'trades' in results:
                for trade in results['trades']:
                    for time_key in ['entry_time', 'exit_time']:
                        if time_key in trade and trade[time_key]:
                            if hasattr(trade[time_key], 'isoformat'):
                                trade[time_key] = trade[time_key].isoformat()
                    # Sanitize all numeric values in trades (including Decimal from PostgreSQL)
                    for k, v in trade.items():
                        if isinstance(v, Decimal):
                            trade[k] = float(v)
                        elif isinstance(v, (int, float)):
                            trade[k] = sanitize_value(v)
        
        return formatted
    
    def _sanitize_dict(self, d: Dict) -> Dict:
        """Recursively sanitize a dictionary, converting Infinity/NaN to None, datetime to ISO strings, and Decimal to float."""
        from datetime import datetime, date
        from decimal import Decimal
        result = {}
        for key, value in d.items():
            # Handle datetime/date objects
            if isinstance(value, (datetime, date)):
                result[key] = value.isoformat()
            # Handle Decimal objects (from PostgreSQL asyncpg)
            elif isinstance(value, Decimal):
                result[key] = float(value)
            elif isinstance(value, float):
                if value == float('inf') or value == float('-inf'):
                    result[key] = None
                elif value != value:  # NaN
                    result[key] = None
                else:
                    result[key] = value
            elif isinstance(value, dict):
                result[key] = self._sanitize_dict(value)
            elif isinstance(value, list):
                def sanitize_item(item):
                    if isinstance(item, (datetime, date)):
                        return item.isoformat()
                    elif isinstance(item, float):
                        if item == float('inf') or item == float('-inf') or item != item:  # NaN
                            return None
                    elif isinstance(item, dict):
                        return self._sanitize_dict(item)
                    return item
                result[key] = [sanitize_item(item) for item in value]
            else:
                result[key] = value
        return result
    
    # AI Endpoints
    async def ai_analyze_market(self, request):
        """Get AI analysis of market conditions."""
        try:
            from ai import ClaudeAIAnalyst
            
            # Check if AI is enabled - with better diagnostics
            api_key = self.config.CLAUDE_API_KEY or ''
            api_key_trimmed = api_key.strip() if api_key else ''
            
            if not api_key_trimmed:
                logger.warning("CLAUDE_API_KEY is not set or is empty")
                # Log first few chars for debugging (without exposing full key)
                has_key = 'Yes' if api_key else 'No'
                key_length = len(api_key) if api_key else 0
                logger.info(f"CLAUDE_API_KEY status: exists={has_key}, length={key_length}")
                return web.json_response({
                    'error': 'AI analysis not available. CLAUDE_API_KEY is not configured or is empty. Please check your Railway environment variables.',
                    'diagnostic': {
                        'key_exists': has_key,
                        'key_length': key_length,
                        'note': 'Make sure CLAUDE_API_KEY is set in Railway without quotes around the value'
                    }
                }, status=503)
            
            data = await request.json()
            market_data = data.get('market_data', {})
            trading_signals = data.get('trading_signals', {})
            
            ai_analyst = ClaudeAIAnalyst(self.config)
            
            if not ai_analyst.enabled:
                logger.warning(f"ClaudeAIAnalyst reports disabled despite key being present (length: {len(api_key_trimmed)})")
                return web.json_response({
                    'error': 'AI analysis not available. CLAUDE_API_KEY appears to be invalid. Please verify the key is correct in Railway environment variables.',
                    'diagnostic': {
                        'key_length': len(api_key_trimmed),
                        'note': 'The key exists but ClaudeAIAnalyst reports it as disabled. Check for typos or invalid key format.'
                    }
                }, status=503)
            
            analysis = await ai_analyst.analyze_market_conditions(market_data, trading_signals)
            
            if not analysis:
                return web.json_response({
                    'error': 'AI analysis failed. Please check your CLAUDE_API_KEY configuration.'
                }, status=503)
            
            return web.json_response({
                'success': True,
                'analysis': analysis
            })
            
        except Exception as e:
            logger.error(f"Error getting AI market analysis: {e}", exc_info=True)
            error_msg = str(e)
            if 'api key' in error_msg.lower() or 'authentication' in error_msg.lower():
                return web.json_response({
                    'error': 'AI analysis failed. Please verify your CLAUDE_API_KEY is correct.'
                }, status=503)
            return web.json_response({
                'error': f'AI analysis error: {error_msg}'
            }, status=500)
    
    async def ai_explain_strategy(self, request):
        """Get AI explanation of trading strategy."""
        try:
            from ai import ClaudeAIAnalyst
            
            data = await request.json()
            strategy_config = data.get('strategy_config', {})
            metrics = data.get('metrics', {})
            
            ai_analyst = ClaudeAIAnalyst(self.config)
            
            explanation = await ai_analyst.explain_strategy(strategy_config, metrics)
            
            if not explanation:
                return web.json_response({
                    'error': 'AI explanation not available. Please configure CLAUDE_API_KEY in .env'
                }, status=503)
            
            return web.json_response({
                'success': True,
                'explanation': explanation
            })
            
        except Exception as e:
            logger.error(f"Error getting AI strategy explanation: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def ai_get_guidance(self, request):
        """Get AI-powered user guidance."""
        try:
            from ai import ClaudeAIAnalyst
            
            data = await request.json()
            question = data.get('question', '')
            context = data.get('context', {})
            
            if not question:
                return web.json_response({'error': 'Question is required'}, status=400)
            
            ai_analyst = ClaudeAIAnalyst(self.config)
            
            guidance = await ai_analyst.get_user_guidance(question, context)
            
            if not guidance:
                return web.json_response({
                    'error': 'AI guidance not available. Please configure CLAUDE_API_KEY in .env'
                }, status=503)
            
            return web.json_response({
                'success': True,
                'guidance': guidance
            })
            
        except Exception as e:
            logger.error(f"Error getting AI guidance: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def ai_analyze_backtest(self, request):
        """Analyze backtest results using AI."""
        try:
            from ai.claude_ai import ClaudeAIAnalyst
            
            data = await request.json()
            backtest_results = data.get('results', {})
            strategy_config = data.get('strategy_config')
            
            ai_analyst = ClaudeAIAnalyst(self.config)
            
            if not ai_analyst.enabled:
                return web.json_response({
                    'error': 'AI analysis not available. Please configure CLAUDE_API_KEY in .env'
                }, status=503)
            
            analysis = await ai_analyst.analyze_backtest_results(backtest_results, strategy_config)
            
            if analysis:
                return web.json_response({
                    'success': True,
                    'analysis': analysis
                })
            else:
                return web.json_response({
                    'error': 'AI analysis failed. Please check your CLAUDE_API_KEY configuration.'
                }, status=503)
                
        except Exception as e:
            logger.error(f"AI backtest analysis error: {e}", exc_info=True)
            return web.json_response({
                'error': f'AI analysis failed: {str(e)}'
            }, status=500)


    async def serve_manifest(self, request):
        """Serve PWA manifest.json."""
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        manifest_path = os.path.join(project_root, 'static', 'manifest.json')
        
        if os.path.exists(manifest_path):
            return web.FileResponse(manifest_path, headers={'Content-Type': 'application/manifest+json'})
        else:
            return web.Response(status=404, text='Manifest not found')
    
    async def serve_service_worker(self, request):
        """Serve service worker JavaScript."""
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sw_path = os.path.join(project_root, 'static', 'service-worker.js')
        
        if os.path.exists(sw_path):
            return web.FileResponse(sw_path, headers={'Content-Type': 'application/javascript'})
        else:
            return web.Response(status=404, text='Service worker not found')
    
    async def serve_favicon(self, request):
        """Serve favicon.ico."""
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        favicon_path = os.path.join(project_root, 'static', 'icon-192.png')
        
        # Use icon-192.png as favicon, or return 204 No Content if not found
        if os.path.exists(favicon_path):
            return web.FileResponse(
                favicon_path,
                headers={'Content-Type': 'image/png', 'Cache-Control': 'public, max-age=31536000'}
            )
        else:
            # Return 204 No Content instead of 404/503 for favicon
            return web.Response(status=204)
    
    async def get_chart_candles(self, request):
        """Get candle data for advanced charting."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            pair = request.query.get('pair', 'BTC-USD')
            timeframe = request.query.get('timeframe', '1h')
            limit = int(request.query.get('limit', '100'))
            
            # Map timeframe to granularity
            timeframe_map = {
                '1m': 'ONE_MINUTE',
                '5m': 'FIVE_MINUTE',
                '15m': 'FIFTEEN_MINUTE',
                '1h': 'ONE_HOUR',
                # Coinbase public candles API doesn't support 4h directly; use 6h as the closest
                '4h': 'SIX_HOUR',
                '1d': 'ONE_DAY'
            }
            granularity = timeframe_map.get(timeframe, 'ONE_HOUR')
            
            # Calculate time range
            from datetime import timedelta
            end_time = datetime.utcnow()
            if timeframe == '1m':
                start_time = end_time - timedelta(minutes=limit)
            elif timeframe == '5m':
                start_time = end_time - timedelta(minutes=limit * 5)
            elif timeframe == '15m':
                start_time = end_time - timedelta(minutes=limit * 15)
            elif timeframe == '1h':
                start_time = end_time - timedelta(hours=limit)
            elif timeframe == '4h':
                start_time = end_time - timedelta(hours=limit * 4)
            elif timeframe == '1d':
                start_time = end_time - timedelta(days=limit)
            else:
                start_time = end_time - timedelta(hours=limit)
            
            # Fetch candles (CoinbaseClient.get_candles signature: pair, granularity, start, end)
            candles = await self.bot.exchange.get_candles(pair, granularity, start_time, end_time)
            
            # Format for charting library
            formatted_candles = []
            for candle in (candles[-limit:] if candles else []):  # Take last N candles
                # Get time value - handle different formats
                time_val = 0
                if 'time' in candle:
                    if hasattr(candle['time'], 'timestamp'):
                        time_val = int(candle['time'].timestamp())
                    elif isinstance(candle['time'], (int, float)):
                        time_val = int(candle['time'])
                elif 'timestamp' in candle:
                    time_val = int(candle['timestamp'])
                elif 'start' in candle and hasattr(candle['start'], 'timestamp'):
                    time_val = int(candle['start'].timestamp())
                
                formatted_candles.append({
                    'time': time_val,
                    'open': float(candle.get('open', 0)),
                    'high': float(candle.get('high', 0)),
                    'low': float(candle.get('low', 0)),
                    'close': float(candle.get('close', 0)),
                    'volume': float(candle.get('volume', 0))
                })
            
            return web.json_response({
                'pair': pair,
                'timeframe': timeframe,
                'candles': formatted_candles
            })
        except Exception as e:
            logger.error(f"Error getting chart candles: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_chart_indicators(self, request):
        """Get technical indicators for chart overlay."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            pair = request.query.get('pair', 'BTC-USD')
            timeframe = request.query.get('timeframe', '1h')
            
            # Get current market data which includes indicators
            market_data_all = await self.bot.exchange.get_market_data([pair])
            market_data = market_data_all.get(pair, {})
            
            indicators = {
                'price': float(market_data.get('price', 0)),
                'ema_50': float(market_data.get('ema_50', 0)) if market_data.get('ema_50') else None,
                'rsi': float(market_data.get('rsi', 0)) if market_data.get('rsi') else None,
                'volume': float(market_data.get('volume', 0)),
                'volume_avg': float(market_data.get('volume_avg', 0))
            }
            
            return web.json_response({
                'pair': pair,
                'timeframe': timeframe,
                'indicators': indicators
            })
        except Exception as e:
            logger.error(f"Error getting chart indicators: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def create_advanced_order(self, request):
        """Create a new advanced order."""
        if not self.bot or not self.db_manager:
            return web.json_response({'error': 'Bot or database not initialized'}, status=500)
        
        try:
            user_id = request.get('user_id')
            data = await request.json()
            
            order_type = data.get('order_type')
            if not order_type:
                return web.json_response({'error': 'order_type is required'}, status=400)
            
            # Create order via order manager
            result = await self.bot.order_manager.create_order(order_type, data)
            
            if not result.get('success'):
                return web.json_response({'error': result.get('error', 'Failed to create order')}, status=400)
            
            order = result['order']
            
            # Save to database
            if self.db_manager:
                await self.db_manager.save_advanced_order({
                    'order_id': order['order_id'],
                    'order_type': order['order_type'],
                    'pair': order['pair'],
                    'side': order['side'],
                    'size': order['size'],
                    'filled_size': order.get('filled_size', 0),
                    'status': order['status'],
                    'order_data': order  # Store full order data
                }, user_id=user_id)
            
            return web.json_response({
                'success': True,
                'order': order
            })
        
        except Exception as e:
            logger.error(f"Error creating advanced order: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def list_advanced_orders(self, request):
        """List advanced orders with optional filtering."""
        if not self.db_manager:
            return web.json_response({'error': 'Database not initialized'}, status=500)
        
        try:
            user_id = request.get('user_id')
            pair = request.query.get('pair')
            status = request.query.get('status')
            order_type = request.query.get('order_type')
            
            orders = await self.db_manager.get_advanced_orders(
                user_id=user_id,
                pair=pair,
                status=status,
                order_type=order_type
            )
            
            return web.json_response({
                'success': True,
                'orders': orders
            })
        
        except Exception as e:
            logger.error(f"Error listing advanced orders: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_advanced_order(self, request):
        """Get a specific advanced order by ID."""
        if not self.bot or not self.db_manager:
            return web.json_response({'error': 'Bot or database not initialized'}, status=500)
        
        try:
            order_id = request.match_info['order_id']
            user_id = request.get('user_id')
            
            # First try to get from order manager (active orders)
            order = await self.bot.order_manager.get_order(order_id)
            
            if not order:
                # Try database
                orders = await self.db_manager.get_advanced_orders(user_id=user_id)
                order = next((o for o in orders if o.get('order_id') == order_id), None)
            
            if not order:
                return web.json_response({'error': 'Order not found'}, status=404)
            
            return web.json_response({
                'success': True,
                'order': order
            })
        
        except Exception as e:
            logger.error(f"Error getting advanced order: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def cancel_advanced_order(self, request):
        """Cancel an advanced order."""
        if not self.bot or not self.db_manager:
            return web.json_response({'error': 'Bot or database not initialized'}, status=500)
        
        try:
            order_id = request.match_info['order_id']
            
            # Cancel via order manager
            cancelled = await self.bot.order_manager.cancel_order(order_id)
            
            if cancelled:
                # Update database
                await self.db_manager.update_advanced_order(order_id, {'status': 'cancelled'})
                
                return web.json_response({
                    'success': True,
                    'message': 'Order cancelled successfully'
                })
            else:
                return web.json_response({'error': 'Order not found or already cancelled'}, status=404)
        
        except Exception as e:
            logger.error(f"Error cancelling advanced order: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    # Grid Trading Endpoints
    async def create_grid(self, request):
        """Create a new grid trading strategy."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            user_id = request.get('user_id')
            data = await request.json()
            
            result = await self.bot.grid_manager.create_grid(
                pair=data.get('pair'),
                lower_price=float(data.get('lower_price', 0)),
                upper_price=float(data.get('upper_price', 0)),
                grid_count=int(data.get('grid_count', 10)),
                order_size=float(data.get('order_size', 0)),
                side=data.get('side', 'BOTH')
            )
            
            if not result.get('success'):
                return web.json_response({'error': result.get('error', 'Failed to create grid')}, status=400)
            
            # Save to database if needed (can be added later)
            
            return web.json_response({
                'success': True,
                'grid': result['grid']
            })
        
        except Exception as e:
            logger.error(f"Error creating grid: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def list_grids(self, request):
        """List grid trading strategies."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            pair = request.query.get('pair')
            status = request.query.get('status')
            
            grids = await self.bot.grid_manager.list_grids(pair=pair, status=status)
            
            return web.json_response({
                'success': True,
                'grids': grids
            })
        
        except Exception as e:
            logger.error(f"Error listing grids: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_grid(self, request):
        """Get a specific grid strategy."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            grid_id = request.match_info['grid_id']
            
            grid = await self.bot.grid_manager.get_grid(grid_id)
            
            if not grid:
                return web.json_response({'error': 'Grid not found'}, status=404)
            
            return web.json_response({
                'success': True,
                'grid': grid
            })
        
        except Exception as e:
            logger.error(f"Error getting grid: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def stop_grid(self, request):
        """Stop a grid trading strategy."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            grid_id = request.match_info['grid_id']
            
            stopped = await self.bot.grid_manager.stop_grid(grid_id)
            
            if stopped:
                return web.json_response({
                    'success': True,
                    'message': 'Grid stopped successfully'
                })
            else:
                return web.json_response({'error': 'Grid not found'}, status=404)
        
        except Exception as e:
            logger.error(f"Error stopping grid: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def pause_grid(self, request):
        """Pause a grid trading strategy."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            grid_id = request.match_info['grid_id']
            
            paused = await self.bot.grid_manager.pause_grid(grid_id)
            
            if paused:
                return web.json_response({
                    'success': True,
                    'message': 'Grid paused successfully'
                })
            else:
                return web.json_response({'error': 'Grid not found'}, status=404)
        
        except Exception as e:
            logger.error(f"Error pausing grid: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def resume_grid(self, request):
        """Resume a grid trading strategy."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            grid_id = request.match_info['grid_id']
            
            resumed = await self.bot.grid_manager.resume_grid(grid_id)
            
            if resumed:
                return web.json_response({
                    'success': True,
                    'message': 'Grid resumed successfully'
                })
            else:
                return web.json_response({'error': 'Grid not found'}, status=404)
        
        except Exception as e:
            logger.error(f"Error resuming grid: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    # DCA Endpoints
    async def create_dca(self, request):
        """Create a new DCA strategy."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            user_id = request.get('user_id')
            data = await request.json()
            
            result = await self.bot.dca_manager.create_dca(
                pair=data.get('pair'),
                side=data.get('side'),
                amount=float(data.get('amount', 0)),
                interval=data.get('interval', 'daily'),
                total_amount=float(data.get('total_amount', 0)) if data.get('total_amount') else None,
                start_price=float(data.get('start_price', 0)) if data.get('start_price') else None,
                end_price=float(data.get('end_price', 0)) if data.get('end_price') else None
            )
            
            if not result.get('success'):
                return web.json_response({'error': result.get('error', 'Failed to create DCA')}, status=400)
            
            return web.json_response({
                'success': True,
                'strategy': result['strategy']
            })
        
        except Exception as e:
            logger.error(f"Error creating DCA: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def list_dca(self, request):
        """List DCA strategies."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            pair = request.query.get('pair')
            status = request.query.get('status')
            
            strategies = await self.bot.dca_manager.list_dca_strategies(pair=pair, status=status)
            
            return web.json_response({
                'success': True,
                'strategies': strategies
            })
        
        except Exception as e:
            logger.error(f"Error listing DCA strategies: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_dca(self, request):
        """Get a specific DCA strategy."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            dca_id = request.match_info['dca_id']
            
            strategy = await self.bot.dca_manager.get_dca(dca_id)
            
            if not strategy:
                return web.json_response({'error': 'DCA strategy not found'}, status=404)
            
            return web.json_response({
                'success': True,
                'strategy': strategy
            })
        
        except Exception as e:
            logger.error(f"Error getting DCA: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def stop_dca(self, request):
        """Stop a DCA strategy."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            dca_id = request.match_info['dca_id']
            
            stopped = await self.bot.dca_manager.stop_dca(dca_id)
            
            if stopped:
                return web.json_response({
                    'success': True,
                    'message': 'DCA strategy stopped successfully'
                })
            else:
                return web.json_response({'error': 'DCA strategy not found'}, status=404)
        
        except Exception as e:
            logger.error(f"Error stopping DCA: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def pause_dca(self, request):
        """Pause a DCA strategy."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            dca_id = request.match_info['dca_id']
            
            paused = await self.bot.dca_manager.pause_dca(dca_id)
            
            if paused:
                return web.json_response({
                    'success': True,
                    'message': 'DCA strategy paused successfully'
                })
            else:
                return web.json_response({'error': 'DCA strategy not found'}, status=404)
        
        except Exception as e:
            logger.error(f"Error pausing DCA: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    async def resume_dca(self, request):
        """Resume a DCA strategy."""
        if not self.bot:
            return web.json_response({'error': 'Bot not initialized'}, status=500)
        
        try:
            dca_id = request.match_info['dca_id']
            
            resumed = await self.bot.dca_manager.resume_dca(dca_id)
            
            if resumed:
                return web.json_response({
                    'success': True,
                    'message': 'DCA strategy resumed successfully'
                })
            else:
                return web.json_response({'error': 'DCA strategy not found'}, status=404)
        
        except Exception as e:
            logger.error(f"Error resuming DCA: {e}", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)

def create_app(bot_instance=None, db_manager=None) -> web.Application:
    """Create and return API application."""
    api = TradingBotAPI(bot_instance=bot_instance, db_manager=db_manager)
    return api.app


async def run_api(app: web.Application, host: str = '0.0.0.0', port: int = 8000):
    """Run API server."""
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    logger.info(f"API server started on {host}:{port}")
