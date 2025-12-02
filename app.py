"""
Heroku entry point for the Trading Bot API.
This file allows Heroku to run just the API server without the trading bot.
"""
import os
import asyncio
import logging
from aiohttp import web
from api.rest_api import create_app, run_api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def init_app():
    """Initialize the web application."""
    try:
        # Create app without bot instance (API-only mode)
        app = create_app(bot_instance=None, db_manager=None)
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

