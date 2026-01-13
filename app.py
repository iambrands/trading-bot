#!/usr/bin/env python3
"""
Heroku entry point for the Trading Bot API.
This file allows Heroku to run just the API server without the trading bot.
"""
# CRITICAL: These lines must be FIRST - before any other imports
import sys
import os

# Force unbuffered output so logs appear immediately in Railway
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__
os.environ['PYTHONUNBUFFERED'] = '1'

# CRITICAL: Print startup info BEFORE any imports to catch crashes
print("=" * 60, file=sys.stderr, flush=True)
print("TRADEPILOT BOOT SEQUENCE", file=sys.stderr, flush=True)
print(f"Python: {sys.version}", file=sys.stderr, flush=True)
print(f"PORT env: {os.environ.get('PORT', 'NOT SET')}", file=sys.stderr, flush=True)
print(f"PWD: {os.getcwd()}", file=sys.stderr, flush=True)
print(f"Python executable: {sys.executable}", file=sys.stderr, flush=True)
print("=" * 60, file=sys.stderr, flush=True)

# Step 1: Import standard library
print("Step 1: Importing standard library...", file=sys.stderr, flush=True)
try:
    import asyncio
    import logging
    print("  ✅ Standard library OK", file=sys.stderr, flush=True)
except Exception as e:
    print(f"  ❌ Standard library FAILED: {e}", file=sys.stderr, flush=True)
    sys.exit(1)

# Step 2: Import aiohttp
print("Step 2: Importing aiohttp...", file=sys.stderr, flush=True)
try:
    from aiohttp import web
    print("  ✅ aiohttp OK", file=sys.stderr, flush=True)
except Exception as e:
    print(f"  ❌ aiohttp FAILED: {e}", file=sys.stderr, flush=True)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

# Step 3: Import local modules one by one
print("Step 3: Importing local modules...", file=sys.stderr, flush=True)

try:
    from config import get_config
    print("  ✅ config.get_config OK", file=sys.stderr, flush=True)
except Exception as e:
    print(f"  ❌ config.get_config FAILED: {e}", file=sys.stderr, flush=True)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

try:
    from database.db_manager import DatabaseManager
    print("  ✅ database.db_manager OK", file=sys.stderr, flush=True)
except Exception as e:
    print(f"  ❌ database.db_manager FAILED: {e}", file=sys.stderr, flush=True)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

try:
    from utils.log_buffer import setup_log_buffer
    print("  ✅ utils.log_buffer OK", file=sys.stderr, flush=True)
except Exception as e:
    print(f"  ❌ utils.log_buffer FAILED: {e}", file=sys.stderr, flush=True)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

try:
    from api.rest_api import create_app, run_api
    print("  ✅ api.rest_api OK", file=sys.stderr, flush=True)
except Exception as e:
    print(f"  ❌ api.rest_api FAILED: {e}", file=sys.stderr, flush=True)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

print("Step 4: All imports successful!", file=sys.stderr, flush=True)

# Configure logging AFTER imports
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),  # Use stderr for Railway
        setup_log_buffer(max_size=1000)  # Keep last 1000 log entries in memory
    ]
)

logger = logging.getLogger(__name__)

# Log startup info
logger.info("=" * 60)
logger.info("TRADEPILOT STARTING")
logger.info(f"PORT: {os.environ.get('PORT', 'NOT SET - using default 4000')}")
logger.info(f"RAILWAY_ENVIRONMENT: {os.environ.get('RAILWAY_ENVIRONMENT', 'not set')}")
logger.info(f"ENVIRONMENT: {os.environ.get('ENVIRONMENT', 'development')}")
logger.info(f"RUN_BOT: {os.environ.get('RUN_BOT', 'false')}")
logger.info("=" * 60)


async def init_app():
    """Initialize the web application."""
    try:
        logger.info("Step 1: Loading configuration...")
        config = get_config()
        logger.info("Step 2: Configuration loaded")

        # If RUN_BOT=true, we boot the full TradingBot instance (initialized but not started).
        # This is useful on Railway where Start Command / CMD selection can be confusing.
        run_bot = os.getenv('RUN_BOT', 'false').lower() == 'true'
        logger.info(f"Step 3: RUN_BOT={run_bot}")
        
        # Create database manager and initialize it
        logger.info("Step 4: Creating database manager...")
        db_manager = DatabaseManager(config)
        logger.info("Step 5: Initializing database connection...")
        
        # Add timeout to database initialization to prevent hanging
        try:
            db_initialized = await asyncio.wait_for(db_manager.initialize(), timeout=30.0)
        except asyncio.TimeoutError:
            logger.error("Database initialization timed out after 30 seconds!")
            db_initialized = False
        
        if not db_initialized:
            logger.warning("Database initialization failed, but continuing anyway. Some features may not work.")
        else:
            logger.info("Step 6: Database initialized successfully")
        
        bot_instance = None
        if run_bot:
            try:
                logger.info("Step 7: Importing TradingBot...")
                from main import TradingBot
                logger.info("Step 8: Creating TradingBot instance...")
                bot_instance = TradingBot()
                logger.info("Step 9: Initializing TradingBot (this may take a moment)...")
                
                # Add timeout to bot initialization to prevent hanging
                try:
                    ok = await asyncio.wait_for(bot_instance.initialize(), timeout=60.0)
                except asyncio.TimeoutError:
                    logger.error("TradingBot initialization timed out after 60 seconds!")
                    ok = False
                
                if not ok:
                    logger.error("TradingBot initialization failed; continuing in API-only mode")
                    bot_instance = None
                else:
                    logger.info("Step 10: TradingBot initialized successfully (waiting for /api/start)")
            except Exception as e:
                logger.error(f"Failed to initialize TradingBot; continuing in API-only mode: {e}", exc_info=True)
                bot_instance = None
        else:
            logger.info("Step 7: Skipping TradingBot initialization (RUN_BOT=false)")

        logger.info("Step 11: Creating web application...")
        # If we created a bot, prefer its DB manager; otherwise use the API-only db_manager.
        app = create_app(bot_instance=bot_instance, db_manager=(getattr(bot_instance, 'db', None) or db_manager))
        logger.info("Step 12: Application initialized successfully")
        return app
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}", exc_info=True)
        raise


async def main():
    """Main entry point for Heroku."""
    try:
        # Get port from Heroku environment variable
        port = int(os.environ.get('PORT', 4000))
        
        logger.info(f"🚀 Starting API server on port {port}")
        logger.info(f"Environment: {os.environ.get('ENVIRONMENT', 'development')}")
        
        # Create and initialize app
        logger.info("📦 Initializing application...")
        app = await init_app()
        logger.info("✅ Application initialized")
        
        # Run the server (this sets up and starts the server)
        logger.info(f"🌐 Setting up web server on 0.0.0.0:{port}...")
        await run_api(app, host='0.0.0.0', port=port)
        
        # Keep the server running
        logger.info("✅ API server started successfully, waiting for requests...")
        logger.info("=" * 60)
        logger.info("TRADEPILOT IS READY")
        logger.info(f"Server listening on http://0.0.0.0:{port}")
        logger.info("=" * 60)
        
        # Wait indefinitely to keep the server alive
        try:
            await asyncio.Event().wait()  # Wait indefinitely
        except KeyboardInterrupt:
            logger.info("Shutting down API server...")
    except Exception as e:
        logger.error(f"❌ Failed to start API server: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("API server stopped")

