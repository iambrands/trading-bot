#!/usr/bin/env python3
"""
Claude AI Diagnostic Test Script
Tests the Claude AI integration endpoint on Railway
"""

import requests
import json
import sys
import os
from typing import Dict, Any

# Colors for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.NC}")
    print(f"{Colors.BLUE}{text}{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}\n")

def print_test(test_name: str):
    """Print a test name."""
    print(f"{Colors.YELLOW}[TEST] {test_name}...{Colors.NC}")

def print_success(message: str):
    """Print a success message."""
    print(f"{Colors.GREEN}✅ {message}{Colors.NC}")

def print_error(message: str):
    """Print an error message."""
    print(f"{Colors.RED}❌ {message}{Colors.NC}")

def print_warning(message: str):
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.NC}")

def print_info(message: str):
    """Print an info message."""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.NC}")

def test_server_connectivity(url: str) -> bool:
    """Test if the server is reachable."""
    print_test("Server Connectivity")
    try:
        response = requests.get(f"{url}/api/status", timeout=10)
        if response.status_code == 200:
            print_success("Server is reachable")
            return True
        else:
            print_error(f"Server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"Server is not reachable: {e}")
        print_info("Please check if Railway deployment is running")
        return False

def test_ai_status(url: str) -> Dict[str, Any]:
    """Test the AI status endpoint."""
    print_test("AI Status Endpoint")
    try:
        response = requests.get(f"{url}/api/ai/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
            
            configured = data.get('configured', False)
            enabled = data.get('enabled', False)
            
            if configured:
                print_success("API key is configured")
            else:
                print_error("API key is NOT configured")
                print_info("Please add CLAUDE_API_KEY to Railway environment variables")
                return {'success': False, 'data': data}
            
            if enabled:
                print_success("Claude AI is enabled")
            else:
                print_warning("Claude AI is configured but disabled")
                print_info("Check API key format - should start with 'sk-ant-' and be 50+ characters")
            
            return {'success': configured, 'data': data}
        else:
            print_error(f"Status endpoint returned {response.status_code}")
            return {'success': False, 'error': f"HTTP {response.status_code}"}
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to reach status endpoint: {e}")
        return {'success': False, 'error': str(e)}

def test_claude_diagnostic(url: str) -> Dict[str, Any]:
    """Test the comprehensive Claude AI diagnostic endpoint."""
    print_test("Comprehensive Claude AI Diagnostic")
    try:
        response = requests.get(f"{url}/api/test/claude-ai", timeout=60)  # Longer timeout for API call
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
            
            test_results = data.get('test_results', {})
            
            # Parse results
            env_result = test_results.get('environment', {})
            import_result = test_results.get('import', {})
            init_result = test_results.get('initialization', {})
            api_result = test_results.get('api_call', {})
            
            print(f"\n{Colors.BLUE}Diagnostic Results:{Colors.NC}")
            print(f"  Environment: {env_result.get('api_key_to_use', 'UNKNOWN')}")
            print(f"  Import: {'✅' if import_result.get('success') else '❌'}")
            print(f"  Initialization: {'✅' if init_result.get('success') else '❌'}")
            print(f"  API Call: {'✅' if api_result.get('success') else '❌'}")
            
            # Check API response details
            if api_result.get('success'):
                response_length = api_result.get('response_length', 0)
                response_preview = api_result.get('response_preview', '')
                
                if response_length > 0:
                    print_success(f"API returned {response_length} characters")
                    if response_preview:
                        print(f"\n{Colors.BLUE}Response preview:{Colors.NC}")
                        print(response_preview[:500])
                else:
                    print_warning("API call succeeded but returned empty response")
                    print_info("Check Railway logs for '[_call_claude]' messages")
            
            # Check for errors or warnings
            if 'error' in data:
                print_error(f"Diagnostic error: {data['error']}")
            
            if 'warning' in data:
                print_warning(f"Warning: {data['warning']}")
            
            if 'fix' in data:
                print_info(f"Suggested fix: {data['fix']}")
            
            return {'success': True, 'data': data}
        else:
            error_data = response.json() if response.content else {}
            print_error(f"Diagnostic endpoint returned {response.status_code}")
            print(json.dumps(error_data, indent=2))
            return {'success': False, 'error': f"HTTP {response.status_code}", 'data': error_data}
    except requests.exceptions.Timeout:
        print_error("Diagnostic test timed out (60 seconds)")
        print_info("This might indicate the Claude API is slow or unresponsive")
        return {'success': False, 'error': 'Timeout'}
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to reach diagnostic endpoint: {e}")
        return {'success': False, 'error': str(e)}

def main():
    """Main test execution."""
    print_header("Claude AI Diagnostic Test")
    
    # Get Railway URL
    railway_url = os.getenv('RAILWAY_URL', 'https://web-production-f8308.up.railway.app')
    print(f"Railway URL: {railway_url}\n")
    
    # Test 1: Server connectivity
    if not test_server_connectivity(railway_url):
        sys.exit(1)
    
    # Test 2: AI Status
    status_result = test_ai_status(railway_url)
    if not status_result.get('success'):
        print_error("AI status check failed. Cannot proceed.")
        sys.exit(1)
    
    # Test 3: Comprehensive diagnostic
    diagnostic_result = test_claude_diagnostic(railway_url)
    
    # Summary
    print_header("Summary")
    
    if diagnostic_result.get('success'):
        data = diagnostic_result.get('data', {})
        test_results = data.get('test_results', {})
        api_result = test_results.get('api_call', {})
        response_length = api_result.get('response_length', 0)
        
        if api_result.get('success') and response_length > 0:
            print_success("All tests passed! Claude AI is working correctly.")
            sys.exit(0)
        elif api_result.get('success') and response_length == 0:
            print_warning("API call works but returns empty response.")
            print_info("Check Railway logs for response parsing issues.")
            sys.exit(1)
        else:
            print_error("API call failed. Check the diagnostic output above.")
            sys.exit(1)
    else:
        print_error("Diagnostic test failed. Check the output above.")
        sys.exit(1)

if __name__ == '__main__':
    main()

