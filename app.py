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

# Step 5: Configure logging AFTER imports
print("Step 5: Configuring logging...", file=sys.stderr, flush=True)
try:
    print("  Setting up log buffer...", file=sys.stderr, flush=True)
    log_buffer_handler = setup_log_buffer(max_size=1000)
    print("  ✅ Log buffer setup OK", file=sys.stderr, flush=True)
    
    print("  Calling logging.basicConfig...", file=sys.stderr, flush=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr),  # Use stderr for Railway
            log_buffer_handler  # Keep last 1000 log entries in memory
        ]
    )
    print("  ✅ logging.basicConfig OK", file=sys.stderr, flush=True)
except Exception as e:
    print(f"  ❌ Logging configuration FAILED: {e}", file=sys.stderr, flush=True)
    import traceback
    traceback.print_exc(file=sys.stderr)
    # Continue anyway - we'll use print statements

print("Step 6: Getting logger...", file=sys.stderr, flush=True)
logger = logging.getLogger(__name__)
print("  ✅ Logger obtained", file=sys.stderr, flush=True)

# Log startup info
print("Step 7: Logging startup info...", file=sys.stderr, flush=True)
try:
    logger.info("=" * 60)
    logger.info("TRADEPILOT STARTING")
    logger.info(f"PORT: {os.environ.get('PORT', 'NOT SET - using default 4000')}")
    logger.info(f"RAILWAY_ENVIRONMENT: {os.environ.get('RAILWAY_ENVIRONMENT', 'not set')}")
    logger.info(f"ENVIRONMENT: {os.environ.get('ENVIRONMENT', 'development')}")
    logger.info(f"RUN_BOT: {os.environ.get('RUN_BOT', 'false')}")
    logger.info("=" * 60)
    print("  ✅ Startup info logged", file=sys.stderr, flush=True)
except Exception as e:
    print(f"  ❌ Logging startup info FAILED: {e}", file=sys.stderr, flush=True)
    import traceback
    traceback.print_exc(file=sys.stderr)

print("Step 8: About to define async functions...", file=sys.stderr, flush=True)


async def init_app():
    """Initialize the web application."""
    print("=" * 60, file=sys.stderr, flush=True)
    print("init_app() CALLED", file=sys.stderr, flush=True)
    print("=" * 60, file=sys.stderr, flush=True)
    
    try:
        # Step 1: Load configuration
        print("init_app() Step 1: Loading configuration...", file=sys.stderr, flush=True)
        logger.info("Step 1: Loading configuration...")
        print("  Calling get_config()...", file=sys.stderr, flush=True)
        config = get_config()
        print("  ✅ Config loaded successfully", file=sys.stderr, flush=True)
        logger.info("Step 2: Configuration loaded")
        print(f"  Config ENVIRONMENT: {config.ENVIRONMENT}", file=sys.stderr, flush=True)
        print(f"  Config DATABASE_URL present: {'YES' if hasattr(config, 'DB_HOST') and config.DB_HOST else 'NO'}", file=sys.stderr, flush=True)

        # Step 2: Check RUN_BOT
        print("init_app() Step 2: Checking RUN_BOT env var...", file=sys.stderr, flush=True)
        run_bot = os.getenv('RUN_BOT', 'false').lower() == 'true'
        print(f"  RUN_BOT = {run_bot}", file=sys.stderr, flush=True)
        logger.info(f"Step 3: RUN_BOT={run_bot}")
        
        # Step 3: Create database manager
        print("init_app() Step 3: Creating DatabaseManager...", file=sys.stderr, flush=True)
        logger.info("Step 4: Creating database manager...")
        print("  Instantiating DatabaseManager(config)...", file=sys.stderr, flush=True)
        try:
            db_manager = DatabaseManager(config)
            print("  ✅ DatabaseManager created", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"  ❌ DatabaseManager creation FAILED: {e}", file=sys.stderr, flush=True)
            import traceback
            traceback.print_exc(file=sys.stderr)
            db_manager = None
        
        # Step 4: Initialize database connection
        if db_manager:
            print("init_app() Step 4: Initializing database connection...", file=sys.stderr, flush=True)
            logger.info("Step 5: Initializing database connection...")
            print("  Calling db_manager.initialize() with 30s timeout...", file=sys.stderr, flush=True)
            
            # Add timeout to database initialization to prevent hanging
            try:
                db_initialized = await asyncio.wait_for(db_manager.initialize(), timeout=30.0)
                print(f"  ✅ Database initialized: {db_initialized}", file=sys.stderr, flush=True)
            except asyncio.TimeoutError:
                print("  ❌ DATABASE TIMEOUT after 30s - continuing without DB", file=sys.stderr, flush=True)
                logger.error("Database initialization timed out after 30 seconds!")
                db_initialized = False
            except Exception as e:
                print(f"  ❌ Database initialization error: {e}", file=sys.stderr, flush=True)
                import traceback
                traceback.print_exc(file=sys.stderr)
                db_initialized = False
            
            if not db_initialized:
                logger.warning("Database initialization failed, but continuing anyway. Some features may not work.")
            else:
                logger.info("Step 6: Database initialized successfully")
        else:
            print("init_app() Step 4: Skipping database (DatabaseManager creation failed)", file=sys.stderr, flush=True)
            db_initialized = False
        
        # Step 5: TradingBot initialization (if RUN_BOT=true)
        bot_instance = None
        if run_bot:
            print("init_app() Step 5: Initializing TradingBot (RUN_BOT=true)...", file=sys.stderr, flush=True)
            try:
                print("  Importing TradingBot from main...", file=sys.stderr, flush=True)
                logger.info("Step 7: Importing TradingBot...")
                from main import TradingBot
                print("  ✅ TradingBot imported", file=sys.stderr, flush=True)
                
                print("  Creating TradingBot instance...", file=sys.stderr, flush=True)
                logger.info("Step 8: Creating TradingBot instance...")
                bot_instance = TradingBot()
                print("  ✅ TradingBot instance created", file=sys.stderr, flush=True)
                
                print("  Initializing TradingBot (60s timeout)...", file=sys.stderr, flush=True)
                logger.info("Step 9: Initializing TradingBot (this may take a moment)...")
                
                # Add timeout to bot initialization to prevent hanging
                try:
                    ok = await asyncio.wait_for(bot_instance.initialize(), timeout=60.0)
                    print(f"  ✅ TradingBot initialized: {ok}", file=sys.stderr, flush=True)
                except asyncio.TimeoutError:
                    print("  ❌ BOT TIMEOUT after 60s - continuing in API-only mode", file=sys.stderr, flush=True)
                    logger.error("TradingBot initialization timed out after 60 seconds!")
                    ok = False
                except Exception as e:
                    print(f"  ❌ Bot initialization error: {e}", file=sys.stderr, flush=True)
                    import traceback
                    traceback.print_exc(file=sys.stderr)
                    ok = False
                
                if not ok:
                    logger.error("TradingBot initialization failed; continuing in API-only mode")
                    bot_instance = None
                else:
                    logger.info("Step 10: TradingBot initialized successfully")
                    print("  Starting TradingBot trading loop...", file=sys.stderr, flush=True)
                    try:
                        # Start the trading loop (runs in background, don't await)
                        asyncio.create_task(bot_instance.start())
                        print("  ✅ TradingBot trading loop started (running in background)", file=sys.stderr, flush=True)
                        logger.info("Step 11: TradingBot trading loop started")
                    except Exception as start_err:
                        print(f"  ⚠️ Warning: Failed to start trading loop: {start_err}", file=sys.stderr, flush=True)
                        logger.warning(f"Failed to start trading loop (continuing anyway): {start_err}")
                        import traceback
                        traceback.print_exc(file=sys.stderr)
            except Exception as e:
                print(f"  ❌ TradingBot setup FAILED: {e}", file=sys.stderr, flush=True)
                import traceback
                traceback.print_exc(file=sys.stderr)
                logger.error(f"Failed to initialize TradingBot; continuing in API-only mode: {e}", exc_info=True)
                bot_instance = None
        else:
            print("init_app() Step 5: Skipping TradingBot (RUN_BOT=false)", file=sys.stderr, flush=True)
            logger.info("Step 7: Skipping TradingBot initialization (RUN_BOT=false)")

        # Step 6: Create web application
        print("init_app() Step 6: Creating web application...", file=sys.stderr, flush=True)
        logger.info("Step 11: Creating web application...")
        print("  Calling create_app()...", file=sys.stderr, flush=True)
        try:
            # If we created a bot, prefer its DB manager; otherwise use the API-only db_manager.
            app = create_app(bot_instance=bot_instance, db_manager=(getattr(bot_instance, 'db', None) or db_manager))
            print("  ✅ Web application created", file=sys.stderr, flush=True)
            logger.info("Step 12: Application initialized successfully")
        except Exception as e:
            print(f"  ❌ create_app() FAILED: {e}", file=sys.stderr, flush=True)
            import traceback
            traceback.print_exc(file=sys.stderr)
            raise
        
        print("=" * 60, file=sys.stderr, flush=True)
        print("init_app() COMPLETED SUCCESSFULLY", file=sys.stderr, flush=True)
        print("=" * 60, file=sys.stderr, flush=True)
        return app
    except Exception as e:
        print("=" * 60, file=sys.stderr, flush=True)
        print(f"init_app() FAILED: {e}", file=sys.stderr, flush=True)
        print("=" * 60, file=sys.stderr, flush=True)
        logger.error(f"Failed to initialize application: {e}", exc_info=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise


async def main():
    """Main entry point for Heroku."""
    print("=" * 60, file=sys.stderr, flush=True)
    print("main() async function CALLED", file=sys.stderr, flush=True)
    print("=" * 60, file=sys.stderr, flush=True)
    try:
        # Get port from Heroku environment variable
        print("main() Step 1: Getting PORT from environment...", file=sys.stderr, flush=True)
        port = int(os.environ.get('PORT', 4000))
        print(f"  ✅ PORT = {port}", file=sys.stderr, flush=True)
        
        logger.info(f"🚀 Starting API server on port {port}")
        logger.info(f"Environment: {os.environ.get('ENVIRONMENT', 'development')}")
        
        # Create and initialize app
        print("main() Step 2: Calling init_app()...", file=sys.stderr, flush=True)
        logger.info("📦 Initializing application...")
        app = await init_app()
        print("  ✅ init_app() returned successfully", file=sys.stderr, flush=True)
        logger.info("✅ Application initialized")
        
        # Run the server (this sets up and starts the server)
        print("=" * 60, file=sys.stderr, flush=True)
        print("main() Step 3: STARTING WEB SERVER", file=sys.stderr, flush=True)
        print(f"  Host: 0.0.0.0", file=sys.stderr, flush=True)
        print(f"  Port: {port}", file=sys.stderr, flush=True)
        print("=" * 60, file=sys.stderr, flush=True)
        logger.info(f"🌐 Setting up web server on 0.0.0.0:{port}...")
        
        print("  Calling run_api()...", file=sys.stderr, flush=True)
        try:
            await run_api(app, host='0.0.0.0', port=port)
            print("  ✅ run_api() completed", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"  ❌ run_api() FAILED: {e}", file=sys.stderr, flush=True)
            import traceback
            traceback.print_exc(file=sys.stderr)
            raise
        
        # Keep the server running
        print("=" * 60, file=sys.stderr, flush=True)
        print("✅ SERVER IS RUNNING", file=sys.stderr, flush=True)
        print(f"   URL: http://0.0.0.0:{port}", file=sys.stderr, flush=True)
        print("=" * 60, file=sys.stderr, flush=True)
        logger.info("✅ API server started successfully, waiting for requests...")
        logger.info("=" * 60)
        logger.info("TRADEPILOT IS READY")
        logger.info(f"Server listening on http://0.0.0.0:{port}")
        logger.info("=" * 60)
        
        # Wait indefinitely to keep the server alive
        print("  Waiting indefinitely to keep server alive...", file=sys.stderr, flush=True)
        try:
            await asyncio.Event().wait()  # Wait indefinitely
        except KeyboardInterrupt:
            print("  KeyboardInterrupt received", file=sys.stderr, flush=True)
            logger.info("Shutting down API server...")
    except Exception as e:
        print("=" * 60, file=sys.stderr, flush=True)
        print(f"main() FAILED: {e}", file=sys.stderr, flush=True)
        print("=" * 60, file=sys.stderr, flush=True)
        logger.error(f"❌ Failed to start API server: {e}", exc_info=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise


print("Step 9: Checking if __name__ == '__main__'...", file=sys.stderr, flush=True)
print(f"  __name__ = {__name__}", file=sys.stderr, flush=True)

if __name__ == '__main__':
    print("Step 10: Entering if __name__ == '__main__' block", file=sys.stderr, flush=True)
    print("  About to call asyncio.run(main())...", file=sys.stderr, flush=True)
    try:
        asyncio.run(main())
        print("  ✅ asyncio.run(main()) completed", file=sys.stderr, flush=True)
    except KeyboardInterrupt:
        print("  KeyboardInterrupt received", file=sys.stderr, flush=True)
        logger.info("API server stopped")
    except Exception as e:
        print(f"  ❌ Exception in asyncio.run(main()): {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise
else:
    print(f"Step 10: Not in __main__ block (__name__={__name__})", file=sys.stderr, flush=True)

