"""
Heroku entry point for the Trading Bot API.
This file allows Heroku to run just the API server without the trading bot.
"""
import os
import asyncio
import logging
from aiohttp import web
from api.rest_api import create_app, run_api
from database.db_manager import DatabaseManager
from config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def init_app():
    """Initialize the web application."""
    try:
        config = get_config()

        # If RUN_BOT=true, we boot the full TradingBot instance (initialized but not started).
        # This is useful on Railway where Start Command / CMD selection can be confusing.
        run_bot = os.getenv('RUN_BOT', 'false').lower() == 'true'
        
        # Create database manager and initialize it
        db_manager = DatabaseManager(config)
        logger.info("Initializing database...")
        db_initialized = await db_manager.initialize()
        
        if not db_initialized:
            logger.warning("Database initialization failed, but continuing anyway. Some features may not work.")
        else:
            logger.info("Database initialized successfully")
        
        bot_instance = None
        if run_bot:
            try:
                from main import TradingBot
                bot_instance = TradingBot()
                logger.info("RUN_BOT=true: initializing TradingBot (paper trading supported)")
                ok = await bot_instance.initialize()
                if not ok:
                    logger.error("TradingBot initialization failed; continuing in API-only mode")
                    bot_instance = None
                else:
                    logger.info("TradingBot initialized successfully (waiting for /api/start)")
            except Exception as e:
                logger.error(f"Failed to initialize TradingBot; continuing in API-only mode: {e}", exc_info=True)
                bot_instance = None

        # If we created a bot, prefer its DB manager; otherwise use the API-only db_manager.
        app = create_app(bot_instance=bot_instance, db_manager=(getattr(bot_instance, 'db', None) or db_manager))
        logger.info("Application initialized successfully")
        return app
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}", exc_info=True)
        raise


async def main():
    """Main entry point for Heroku."""
    try:
        # Get port from Heroku environment variable
        port = int(os.environ.get('PORT', 4000))
        
        logger.info(f"Starting API server on port {port}")
        logger.info(f"Environment: {os.environ.get('ENVIRONMENT', 'development')}")
        
        # Create and initialize app
        app = await init_app()
        
        # Run the server (this sets up and starts the server)
        logger.info("Setting up web server...")
        await run_api(app, host='0.0.0.0', port=port)
        
        # Keep the server running
        logger.info("API server started successfully, waiting for requests...")
        
        # Wait indefinitely to keep the server alive
        try:
            await asyncio.Event().wait()  # Wait indefinitely
        except KeyboardInterrupt:
            logger.info("Shutting down API server...")
    except Exception as e:
        logger.error(f"Failed to start API server: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("API server stopped")

