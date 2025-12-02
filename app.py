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
    # Create app without bot instance (API-only mode)
    app = create_app(bot_instance=None, db_manager=None)
    return app


async def main():
    """Main entry point for Heroku."""
    # Get port from Heroku environment variable
    port = int(os.environ.get('PORT', 4000))
    
    logger.info(f"Starting API server on port {port}")
    
    # Create and initialize app
    app = await init_app()
    
    # Run the server (this sets up and starts the server)
    await run_api(app, host='0.0.0.0', port=port)
    
    # Keep the server running
    logger.info("API server started, waiting for requests...")
    try:
        await asyncio.Event().wait()  # Wait indefinitely
    except KeyboardInterrupt:
        logger.info("Shutting down API server...")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("API server stopped")

