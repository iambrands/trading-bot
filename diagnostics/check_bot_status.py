#!/usr/bin/env python3
"""
Check Bot Running Status

Checks if the bot process is running and examines recent logs.

Usage:
    python diagnostics/check_bot_status.py
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def check_process_running():
    """Check if bot process is running"""
    print("=" * 60)
    print("Bot Process Status Check")
    print("=" * 60 + "\n")
    
    # Check for Python processes
    try:
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        lines = result.stdout.split('\n')
        
        # Look for bot processes
        bot_processes = []
        for line in lines:
            if 'python' in line.lower() and ('main.py' in line or 'tradingbot' in line.lower() or 'bot' in line.lower()):
                bot_processes.append(line)
        
        if bot_processes:
            print("✅ Bot process(es) found:")
            for proc in bot_processes:
                print(f"   {proc[:100]}...")
            return True
        else:
            print("❌ No bot process found")
            print("\nThe bot is not currently running.")
            print("Start it with:")
            print("   python main.py")
            print("   or")
            print("   systemctl start trading-bot  # if using systemd")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not check processes: {e}")
        return None

def check_log_file():
    """Check recent log entries"""
    print("\n" + "=" * 60)
    print("Recent Log Check")
    print("=" * 60 + "\n")
    
    log_files = [
        'tradingbot.log',
        'logs/tradingbot.log',
        '/var/log/tradingbot/app.log'
    ]
    
    log_file = None
    for path in log_files:
        if os.path.exists(path):
            log_file = path
            break
    
    if not log_file:
        print("⚠️  No log file found")
        print("   Checked locations:")
        for path in log_files:
            print(f"     - {path}")
        return False
    
    print(f"✓ Found log file: {log_file}")
    
    try:
        # Get file size and modification time
        stat = os.stat(log_file)
        size_mb = stat.st_size / (1024 * 1024)
        mod_time = datetime.fromtimestamp(stat.st_mtime)
        age_seconds = (datetime.now() - mod_time).total_seconds()
        age_minutes = age_seconds / 60
        age_hours = age_minutes / 60
        
        print(f"   Size: {size_mb:.2f} MB")
        print(f"   Last modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if age_hours < 1:
            print(f"   Age: {age_minutes:.1f} minutes ago ✅")
        elif age_hours < 24:
            print(f"   Age: {age_hours:.1f} hours ago ⚠️")
        else:
            print(f"   Age: {age_hours/24:.1f} days ago ❌")
            print("   ⚠️  Log file is very old - bot may not be running!")
        
        # Read last 20 lines
        print("\n   Last 20 log entries:")
        print("   " + "-" * 56)
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                last_lines = lines[-20:] if len(lines) > 20 else lines
                for line in last_lines:
                    # Truncate very long lines
                    line = line.strip()
                    if len(line) > 80:
                        line = line[:77] + "..."
                    print(f"   {line}")
        except Exception as e:
            print(f"   ⚠️  Could not read log file: {e}")
        
        # Check for errors
        print("\n   Checking for errors in last 100 lines...")
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                error_lines = [l for l in lines[-100:] if 'error' in l.lower() or 'exception' in l.lower() or 'failed' in l.lower()]
                
                if error_lines:
                    print(f"   ⚠️  Found {len(error_lines)} error/exception/failed messages:")
                    for err_line in error_lines[-5:]:  # Last 5 errors
                        err_line = err_line.strip()
                        if len(err_line) > 80:
                            err_line = err_line[:77] + "..."
                        print(f"      {err_line}")
                else:
                    print("   ✓ No recent errors found")
        except Exception as e:
            print(f"   ⚠️  Could not check for errors: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading log file: {e}")
        return False

def check_api_health():
    """Check if API server is running (if applicable)"""
    print("\n" + "=" * 60)
    print("API Server Check")
    print("=" * 60 + "\n")
    
    # Try to connect to API if it's running
    try:
        import requests
        response = requests.get('http://localhost:4000/api/status', timeout=2)
        if response.status_code == 200:
            data = response.json()
            print("✅ API server is running")
            print(f"   Status: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"⚠️  API server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️  API server not accessible (might not be running)")
        print("   This is OK if running bot-only mode")
        return None
    except ImportError:
        print("⚠️  requests library not available (skipping API check)")
        return None
    except Exception as e:
        print(f"⚠️  Could not check API: {e}")
        return None

def main():
    """Run all checks"""
    print("\n" + "=" * 60)
    print("Bot Status Diagnostic")
    print("=" * 60 + "\n")
    
    process_ok = check_process_running()
    log_ok = check_log_file()
    api_ok = check_api_health()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"\nProcess Running: {'✅ YES' if process_ok else '❌ NO'}")
    print(f"Log File: {'✅ FOUND' if log_ok else '❌ NOT FOUND'}")
    if api_ok is not None:
        print(f"API Server: {'✅ RUNNING' if api_ok else '⚠️  NOT ACCESSIBLE'}")
    
    if process_ok and log_ok:
        print("\n✅ Bot appears to be running")
        print("\nNext steps:")
        print("  1. Run: python diagnostics/test_strategy_signals.py")
        print("  2. Run: python diagnostics/test_api_connection.py")
        print("  3. Check logs for signal generation")
    elif not process_ok:
        print("\n❌ Bot is NOT running")
        print("\nAction needed:")
        print("  1. Start the bot: python main.py")
        print("  2. Check for errors on startup")
        print("  3. Verify configuration")
    else:
        print("\n⚠️  Status unclear - check logs manually")
    
    print("\n" + "=" * 60)
    
    return 0 if (process_ok and log_ok) else 1

if __name__ == '__main__':
    sys.exit(main())

