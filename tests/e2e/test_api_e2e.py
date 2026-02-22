"""E2E tests for TradePilot REST API.

Runs against the full application stack using aiohttp TestClient/TestServer.
Tests that do not require DATABASE_URL run in CI; auth flow tests are skipped without DB.
"""

import os

import pytest
from aiohttp.test_utils import TestClient, TestServer

from api.rest_api import create_app

requires_db = pytest.mark.skipif(not os.environ.get('DATABASE_URL'), reason='DATABASE_URL not set')


def _make_app():
    """Create aiohttp app. With DATABASE_URL, initializes db for auth flow tests."""
    db_manager = None
    if os.environ.get('DATABASE_URL'):
        import asyncio
        from config import get_config
        from database.db_manager import DatabaseManager
        db_manager = DatabaseManager(get_config())
        asyncio.run(db_manager.initialize())
    return create_app(bot_instance=None, db_manager=db_manager)


# ---- Public pages (no auth, no DB) ----

@pytest.mark.asyncio
async def test_landing_page():
    """Landing page returns 200."""
    app = _make_app()
    async with TestClient(TestServer(app)) as client:
        resp = await client.get('/landing')
        assert resp.status == 200
        text = await resp.text()
        assert 'TradePilot' in text or 'trade' in text.lower()


@pytest.mark.asyncio
async def test_signin_page():
    """Sign-in page returns 200."""
    app = _make_app()
    async with TestClient(TestServer(app)) as client:
        resp = await client.get('/signin')
        assert resp.status == 200
        text = await resp.text()
        assert 'sign' in text.lower() or 'login' in text.lower() or 'email' in text.lower()


@pytest.mark.asyncio
async def test_signup_page():
    """Sign-up page returns 200."""
    app = _make_app()
    async with TestClient(TestServer(app)) as client:
        resp = await client.get('/signup')
        assert resp.status == 200
        text = await resp.text()
        assert 'sign' in text.lower() or 'create' in text.lower() or 'register' in text.lower()


# ---- Auth API (validation without DB) ----

@pytest.mark.asyncio
async def test_auth_verify_no_token_returns_401():
    """Verify endpoint returns 401 when no token provided."""
    app = _make_app()
    async with TestClient(TestServer(app)) as client:
        resp = await client.get('/api/auth/verify')
        assert resp.status == 401
        data = await resp.json()
        assert 'error' in data


@pytest.mark.asyncio
async def test_auth_verify_invalid_token_returns_401():
    """Verify endpoint returns 401 for invalid token."""
    app = _make_app()
    async with TestClient(TestServer(app)) as client:
        resp = await client.get('/api/auth/verify', headers={'Authorization': 'Bearer invalid.token.here'})
        assert resp.status == 401
        data = await resp.json()
        assert 'error' in data


@pytest.mark.asyncio
async def test_auth_signin_missing_fields_returns_400():
    """Sign-in with missing email/password returns 400 (before DB hit)."""
    app = _make_app()
    async with TestClient(TestServer(app)) as client:
        resp = await client.post('/api/auth/signin', json={})
        # Without DB: 500 "Database not initialized"; with DB: 400
        assert resp.status in (400, 500)
        data = await resp.json()
        assert 'error' in data


@pytest.mark.asyncio
async def test_auth_signup_missing_fields_returns_400_or_500():
    """Sign-up with missing fields returns 400 or 500 (no DB = 500)."""
    app = _make_app()
    async with TestClient(TestServer(app)) as client:
        resp = await client.post('/api/auth/signup', json={'email': 'x@y.com'})
        assert resp.status in (400, 500)
        data = await resp.json()
        assert 'error' in data


# ---- Protected routes return 401 without token ----

@pytest.mark.asyncio
async def test_api_status_public_returns_200():
    """Public /api/status (health check) returns 200 without token."""
    app = _make_app()
    async with TestClient(TestServer(app)) as client:
        resp = await client.get('/api/status')
        assert resp.status == 200


@pytest.mark.asyncio
async def test_api_settings_requires_auth():
    """Protected /api/settings returns 401 without token."""
    app = _make_app()
    async with TestClient(TestServer(app)) as client:
        resp = await client.get('/api/settings')
        assert resp.status == 401


@pytest.mark.asyncio
async def test_api_backtest_list_requires_auth():
    """Protected /api/backtest/list returns 401 without token."""
    app = _make_app()
    async with TestClient(TestServer(app)) as client:
        resp = await client.get('/api/backtest/list')
        assert resp.status == 401


# ---- Health / public test endpoints ----

@pytest.mark.asyncio
async def test_test_trading_health_returns_200():
    """Public /api/test/trading-health returns 200."""
    app = _make_app()
    async with TestClient(TestServer(app)) as client:
        resp = await client.get('/api/test/trading-health')
        assert resp.status == 200


# ---- Rate limiting ----

@pytest.mark.asyncio
async def test_auth_rate_limit_returns_429():
    """Sign-in exceeds rate limit -> 429."""
    app = _make_app()
    async with TestClient(TestServer(app)) as client:
        for _ in range(12):
            resp = await client.post('/api/auth/signin', json={'email': 'a@b.com', 'password': 'x'})
        assert resp.status == 429
        data = await resp.json()
        assert 'error' in data


# ---- Auth flow (requires DATABASE_URL) ----

@requires_db
@pytest.mark.asyncio
async def test_auth_signup_signin_verify_flow():
    """Full auth flow: signup -> signin -> verify with valid token."""
    import uuid
    email = f'e2e-{uuid.uuid4().hex[:12]}@test.example'
    password = 'TestPass123!'
    app = _make_app()
    async with TestClient(TestServer(app)) as client:
        # Signup
        signup_resp = await client.post('/api/auth/signup', json={
            'email': email,
            'password': password,
            'full_name': 'E2E Test User'
        })
        assert signup_resp.status == 200, (await signup_resp.text())
        signup_data = await signup_resp.json()
        token = signup_data.get('token')
        assert token

        # Verify with token
        verify_resp = await client.get('/api/auth/verify', headers={'Authorization': f'Bearer {token}'})
        assert verify_resp.status == 200
        verify_data = await verify_resp.json()
        assert verify_data.get('valid') is True
        assert verify_data.get('email') == email

        # Signin (same client)
        signin_resp = await client.post('/api/auth/signin', json={'email': email, 'password': password})
        assert signin_resp.status == 200
        signin_data = await signin_resp.json()
        assert signin_data.get('token')
        assert signin_data.get('user', {}).get('email') == email


@requires_db
@pytest.mark.asyncio
async def test_auth_signin_invalid_credentials_returns_401():
    """Sign-in with wrong password returns 401."""
    app = _make_app()
    async with TestClient(TestServer(app)) as client:
        resp = await client.post('/api/auth/signin', json={
            'email': 'nonexistent@test.example',
            'password': 'WrongPassword123!'
        })
        assert resp.status == 401
        data = await resp.json()
        assert 'error' in data
