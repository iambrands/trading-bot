const API_BASE = '/api';
let refreshInterval;
let currentPage = 'overview';

// Guard flags to prevent AI Analysis auto-refresh loops on Market Conditions page
// (updateMarketConditions runs on the global 5s refresh interval)
let marketAiAutoLoaded = false;
let aiAnalysisInFlight = false;

// Track previous state for change detection
let previousPositions = [];
let previousTrades = [];
let previousTradeCount = 0;

// Toast Notification System
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: '',
        error: '',
        warning: '',
        info: ''
    };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <div class="toast-content">
            <div class="toast-message">${message}</div>
        </div>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

function buildAuthedUrl(path) {
    try {
        const token = localStorage.getItem('auth_token');
        if (!token) return path;
        const url = new URL(path, window.location.origin);
        // Only add if not already present
        if (!url.searchParams.get('token')) {
            url.searchParams.set('token', token);
        }
        return url.pathname + url.search + url.hash;
    } catch (e) {
        return path;
    }
}

// Mobile Menu Toggle
function toggleMobileMenu() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    const toggle = document.getElementById('mobileMenuToggle');
    
    if (sidebar) sidebar.classList.toggle('active');
    if (overlay) overlay.classList.toggle('active');
    if (toggle) toggle.classList.toggle('active');
}

function closeMobileMenu() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    const toggle = document.getElementById('mobileMenuToggle');
    
    if (sidebar) sidebar.classList.remove('active');
    if (overlay) overlay.classList.remove('active');
    if (toggle) toggle.classList.remove('active');
}

// Page title mapping
const pageTitles = {
    'overview': 'Overview',
    'market': 'Market Conditions',
    'positions': 'Active Positions',
    'trades': 'Trade History',
    'performance': 'Performance Analytics',
    'portfolio': 'Portfolio Analytics',
    'charts': 'Advanced Charts',
    'orders': 'Advanced Orders',
    'grid': 'Grid Trading & DCA',
    'backtest': 'Strategy Backtesting',
    'logs': 'System Logs',
    'settings': 'Settings'
};

// Connection Status Management
function updateConnectionStatus(status) {
    const statusEl = document.getElementById('connectionStatusSidebar');
    if (!statusEl) return;
    
    const dot = statusEl.querySelector('.status-dot');
    const text = statusEl.querySelector('.status-text');
    
    if (dot) {
        if (status === 'connected') {
            dot.style.background = '#10b981';
        } else if (status === 'disconnected') {
            dot.style.background = '#ef4444';
        } else {
            dot.style.background = '#f59e0b';
        }
    }
    
    if (text) {
        text.textContent = status === 'connected' ? 'Connected' : 
                          status === 'disconnected' ? 'Disconnected' : 
                          'Connecting...';
    }
}

// Monitor connection status
let lastSuccessfulRequest = Date.now();
setInterval(() => {
    const timeSinceLastSuccess = Date.now() - lastSuccessfulRequest;
    if (timeSinceLastSuccess > 15000) {
        updateConnectionStatus('disconnected');
    } else if (timeSinceLastSuccess > 5000) {
        updateConnectionStatus('connecting');
    } else {
        updateConnectionStatus('connected');
    }
}, 2000);

// Navigation
document.addEventListener('DOMContentLoaded', async () => {
    // Check authentication first
    const token = localStorage.getItem('auth_token');
    if (!token) {
        // No token, redirect to landing page
        window.location.href = '/landing';
        return;
    }
    
    // Verify token is still valid
    try {
        const verifyResponse = await fetch(`${API_BASE}/auth/verify`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });
        
        if (!verifyResponse.ok) {
            // Invalid token, redirect to landing
            localStorage.removeItem('auth_token');
            window.location.href = '/landing';
            return;
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        // If server is down, still allow access (it will fail gracefully in API calls)
    }
    
    // Register Service Worker for PWA
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/service-worker.js')
            .then((registration) => {
                console.log('Service Worker registered:', registration);
            })
            .catch((error) => {
                console.error('Service Worker registration failed:', error);
            });
    }
    
    // Request notification permission (on user interaction)
    function requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission().then((permission) => {
                if (permission === 'granted') {
                    showToast('Notifications enabled', 'success');
                }
            });
        }
    }
    
    // Request permission when user clicks anywhere (first interaction)
    let notificationPermissionRequested = false;
    document.addEventListener('click', () => {
        if (!notificationPermissionRequested && 'Notification' in window) {
            notificationPermissionRequested = true;
            requestNotificationPermission();
        }
    }, { once: true });
    
    // Setup mobile menu toggle
    const mobileToggle = document.getElementById('mobileMenuToggle');
    const overlay = document.getElementById('overlay');
    
    if (mobileToggle) {
        mobileToggle.addEventListener('click', toggleMobileMenu);
    }
    
    if (overlay) {
        overlay.addEventListener('click', closeMobileMenu);
    }
    
    // Setup navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            const page = link.dataset.page;
            // Settings and Help are standalone pages, redirect to them
            if (page === 'settings') {
                window.location.href = buildAuthedUrl('/settings');
                return;
            }
            if (page === 'help') {
                window.location.href = buildAuthedUrl('/help');
                return;
            }
            e.preventDefault();
            navigateToPage(page);
            closeMobileMenu(); // Close mobile menu when navigating
        });
    });

    // Setup routing
    const path = window.location.pathname;
    if (path === '/market-conditions') navigateToPage('market');
    else if (path === '/positions') navigateToPage('positions');
    else if (path === '/trades') navigateToPage('trades');
    else if (path === '/performance') navigateToPage('performance');
    else if (path === '/portfolio') navigateToPage('portfolio');
    else if (path === '/charts') navigateToPage('charts');
    else if (path === '/orders') navigateToPage('orders');
    else if (path === '/grid') navigateToPage('grid');
    else if (path === '/logs') navigateToPage('logs');
    else if (path === '/settings') window.location.href = buildAuthedUrl('/settings');
    else if (path === '/help') window.location.href = buildAuthedUrl('/help');
    else navigateToPage('overview');

    // Initial load
    updateCurrentPage();
    refreshInterval = setInterval(updateCurrentPage, 5000);
    
    // Initialize onboarding for new users (after a short delay to let page load)
    setTimeout(() => {
        if (typeof initOnboarding === 'function') {
            initOnboarding();
        }
    }, 1500);
});

function navigateToPage(page) {
    // Settings and Help are standalone pages, redirect to them
    if (page === 'settings') {
        window.location.href = buildAuthedUrl('/settings');
        return;
    }
    if (page === 'help') {
        window.location.href = buildAuthedUrl('/help');
        return;
    }
    
    // Destroy all charts when leaving performance or portfolio page
    if ((currentPage === 'performance' && page !== 'performance') || 
        (currentPage === 'portfolio' && page !== 'portfolio')) {
        // Get canvas elements
        const equityCtx = document.getElementById('equityChart');
        const pnlCtx = document.getElementById('pnlChart');
        const winRateCtx = document.getElementById('winRateChart');
        
        // Destroy equity chart
        if (equityChart) {
            try { equityChart.destroy(); } catch(e) {}
            equityChart = null;
        }
        if (equityCtx) {
            const existing = Chart.getChart(equityCtx);
            if (existing) {
                try { existing.destroy(); } catch(e) {}
            }
        }
        
        // Destroy P&L chart
        if (pnlChart) {
            try { pnlChart.destroy(); } catch(e) {}
            pnlChart = null;
        }
        if (pnlCtx) {
            const existing = Chart.getChart(pnlCtx);
            if (existing) {
                try { existing.destroy(); } catch(e) {}
            }
        }
        
        // Destroy win rate chart
        if (winRateChart) {
            try { winRateChart.destroy(); } catch(e) {}
            winRateChart = null;
        }
        if (winRateCtx) {
            const existing = Chart.getChart(winRateCtx);
            if (existing) {
                try { existing.destroy(); } catch(e) {}
            }
        }
    }
    
    // Reset AI auto-load flag when leaving market page so it can auto-run once next time
    if (currentPage === 'market' && page !== 'market') {
        marketAiAutoLoaded = false;
    }

    currentPage = page;
    
    // Update page title
    const pageTitleEl = document.getElementById('pageTitle');
    if (pageTitleEl && pageTitles[page]) {
        pageTitleEl.textContent = pageTitles[page];
    }
    
    // Update nav
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.page === page) link.classList.add('active');
    });

    // Show page
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    const pageEl = document.getElementById(`page-${page}`);
    if (pageEl) pageEl.classList.add('active');

    // Update URL
    const paths = {
        'overview': '/',
        'market': '/market-conditions',
        'positions': '/positions',
        'trades': '/trades',
        'performance': '/performance',
        'portfolio': '/portfolio',
        'charts': '/charts',
        'orders': '/orders',
        'grid': '/grid',
        'backtest': '/backtest',
        'logs': '/logs',
        'help': '/help',
        'settings': '/settings'
    };
    window.history.pushState({}, '', paths[page] || '/');

    updateCurrentPage();
}

// API Functions
async function fetchAPI(endpoint, options = {}) {
    try {
        const token = localStorage.getItem('auth_token');
        const headers = {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        const fetchOptions = {
            ...options,
            headers: headers,
            credentials: 'include' // Include cookies
        };
        
        // Handle body if it's an object (convert to JSON string)
        if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
            fetchOptions.body = JSON.stringify(options.body);
        }
        
        const response = await fetch(`${API_BASE}${endpoint}`, fetchOptions);
        
        if (response.status === 401) {
            // Token expired or invalid, redirect to landing
            localStorage.removeItem('auth_token');
            window.location.href = '/landing';
            return null;
        }
        
        if (!response.ok) {
            if (response.status === 401) {
                // Token expired or invalid, redirect to landing
                localStorage.removeItem('auth_token');
                window.location.href = '/landing';
                return null;
            }
            throw new Error(`HTTP ${response.status}`);
        }
        lastSuccessfulRequest = Date.now();
        updateConnectionStatus('connected');
        return await response.json();
    } catch (error) {
        // Handle connection errors gracefully
        if (error.message && (error.message.includes('Failed to fetch') || error.message.includes('ERR_CONNECTION_REFUSED'))) {
            // Only log once per endpoint to avoid spam
            const errorKey = `conn_error_${endpoint}`;
            if (!window[errorKey]) {
                console.warn(`Server connection error for ${endpoint}. Retrying...`);
                window[errorKey] = true;
                // Clear the flag after 5 seconds to allow retry logging
                setTimeout(() => { window[errorKey] = false; }, 5000);
            }
            updateConnectionStatus('disconnected');
            // Don't redirect on connection errors - server might be starting
            return null;
        }
        // Log other errors normally
        if (error.message) {
            console.error(`Error fetching ${endpoint}:`, error.message);
        }
        return null;
    }
}

// Logout function - make it globally available immediately
window.logout = function logout() {
    localStorage.removeItem('auth_token');
    fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        credentials: 'include'
    }).catch(() => {
        // Ignore errors, still redirect
    }).finally(() => {
        window.location.href = '/landing';
    });
};

async function controlBot(action) {
    try {
        const token = localStorage.getItem('auth_token');
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        const response = await fetch(`${API_BASE}/${action}`, {
            method: 'POST',
            headers: headers,
            credentials: 'include'
        });
        
        if (response.status === 401) {
            // Token expired or invalid, redirect to landing
            localStorage.removeItem('auth_token');
            window.location.href = '/landing';
            return;
        }
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({error: 'Unknown error'}));
            showToast('Error: ' + (errorData.error || `HTTP ${response.status}`), 'error');
            return;
        }
        
        const result = await response.json();
        showToast(result.message || 'Action completed', 'success');
        updateCurrentPage();
    } catch (error) {
        console.error('Control bot error:', error);
        if (error.message && (error.message.includes('Failed to fetch') || error.message.includes('ERR_CONNECTION_REFUSED'))) {
            showToast('Cannot connect to server. Please check if the server is running.', 'error');
            updateConnectionStatus('disconnected');
        } else {
            showToast('Error: ' + (error.message || 'Unknown error occurred'), 'error');
        }
    }
}

// Formatting
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value);
}

function formatPercent(value) {
    if (value === undefined || value === null || isNaN(value)) {
        return '0.00%';
    }
    return `${value >= 0 ? '+' : ''}${Number(value).toFixed(2)}%`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        let dateStr = String(dateString).trim();
        
        // Handle ISO format already (from API conversion)
        if (dateStr.includes('T') && (dateStr.includes('Z') || dateStr.includes('+'))) {
            const date = new Date(dateStr);
            if (!isNaN(date.getTime())) {
                return date.toLocaleString();
            }
        }
        
        // Handle log timestamp format: "2025-11-25 22:01:23,330"
        if (dateStr.includes(',') && dateStr.match(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+/)) {
            // Replace comma with dot and space with T for ISO format
            dateStr = dateStr.replace(' ', 'T').replace(',', '.');
            // Ensure milliseconds are 3 digits and add Z
            if (dateStr.includes('.')) {
                const parts = dateStr.split('.');
                const ms = parts[1] ? parts[1].substring(0, 3).padEnd(3, '0') : '000';
                dateStr = parts[0] + '.' + ms + 'Z';
            } else {
                dateStr += '.000Z';
            }
        }
        
        // Try parsing the date
        const date = new Date(dateStr);
        
        // Check if date is valid
        if (isNaN(date.getTime())) {
            // Try without milliseconds
            const withoutMs = dateStr.split('.')[0].split(',')[0];
            const date2 = new Date(withoutMs);
            if (!isNaN(date2.getTime())) {
                return date2.toLocaleString();
            }
            // Last resort: return the original string
            return dateString;
        }
        
        return date.toLocaleString();
    } catch (e) {
        console.warn('Date formatting error:', e, dateString);
        return String(dateString) || 'N/A';
    }
}

// Update functions
async function updateCurrentPage() {
    // Always update status badge regardless of which page we're on
    // This ensures the status badge shows current bot status on all pages
    try {
        const statusData = await fetchAPI('/status');
        if (statusData && statusData.status) {
            updateStatusBadge(statusData.status);
        }
    } catch (error) {
        console.warn('Failed to update status badge:', error);
    }
    
    // Hide AI Analysis card on all pages except market conditions
    const aiAnalysisCard = document.getElementById('aiAnalysisCard');
    if (aiAnalysisCard && currentPage !== 'market') {
        aiAnalysisCard.style.display = 'none';
    }
    
    switch(currentPage) {
        case 'overview':
            await updateOverview();
            break;
        case 'market':
            await updateMarketConditions();
            break;
        case 'positions':
            await updatePositionsPage();
            break;
        case 'trades':
            await updateTradesPage();
            break;
        case 'performance':
            await updatePerformancePage();
            break;
        case 'portfolio':
            await updatePortfolioPage();
            break;
        case 'charts':
            await updateChartsPage();
            break;
        case 'orders':
            await updateOrdersPage();
            break;
        case 'grid':
            await updateGridPage();
            break;
        case 'backtest':
            await updateBacktestPage();
            break;
        case 'settings':
            // Settings is a standalone page, redirect to it
            window.location.href = '/settings';
            break;
        case 'help':
            // Help is a standalone page, redirect to it
            window.location.href = '/help';
            break;
        case 'logs':
            await updateLogsPage();
            // Auto-refresh logs every 5 seconds when on logs page
            if (!window.logsInterval) {
                window.logsInterval = setInterval(() => {
                    if (currentPage === 'logs') updateLogsPage();
                }, 5000);
            }
            break;
    }
}

// Overview Page
async function updateOverview() {
    const [statusData, performanceData] = await Promise.all([
        updateStatus(),
        updatePerformance(),
        updateRisk(),
        updatePositions()
    ]);
    
    // Update quick stats with data
    if (statusData || performanceData) {
        updateQuickStats(statusData, performanceData);
    }
    
    const lastUpdateEl = document.getElementById('lastUpdate');
    if (lastUpdateEl) {
        lastUpdateEl.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
    }
}

function updateStatusBadge(status) {
    const badge = document.getElementById('statusBadge');
    if (badge) {
        badge.textContent = status.toUpperCase();
        badge.className = `status-badge status-${status.toLowerCase()}`;
    }
}

function updateQuickStats(statusData, performanceData) {
    // Update quick stats summary
    if (statusData && statusData.balance) {
        const balanceEl = document.getElementById('quickBalance');
        if (balanceEl) {
            balanceEl.textContent = formatCurrency(statusData.balance);
        }
    }
    
    if (statusData && statusData.positions_count !== undefined) {
        const positionsEl = document.getElementById('quickPositions');
        if (positionsEl) {
            positionsEl.textContent = statusData.positions_count;
        }
    }
    
    if (performanceData) {
        const pnlEl = document.getElementById('quickPnl');
        if (pnlEl && performanceData.total_pnl !== undefined) {
            const pnl = parseFloat(performanceData.total_pnl || 0);
            pnlEl.textContent = formatCurrency(pnl);
            pnlEl.className = `stat-value ${pnl >= 0 ? 'positive' : 'negative'}`;
        }
        
        const winRateEl = document.getElementById('quickWinRate');
        if (winRateEl && performanceData.win_rate !== undefined) {
            const winRate = parseFloat(performanceData.win_rate || 0);
            winRateEl.textContent = winRate.toFixed(1) + '%';
        }
    }
}

async function updateStatus() {
    const data = await fetchAPI('/status');
    if (!data) return null;

    updateStatusBadge(data.status);
    const accountStatus = document.getElementById('accountStatus');
    if (accountStatus) {
        accountStatus.innerHTML = `
            <div class="metric">
                <span class="metric-label">Balance</span>
                <span class="metric-value">${formatCurrency(data.balance)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Positions</span>
                <span class="metric-value">${data.positions_count}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Mode</span>
                <span class="metric-value">${data.paper_trading ? '📝 Paper Trading' : '💰 Live Trading'}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Environment</span>
                <span class="metric-value">${data.environment}</span>
            </div>
        `;
    }
    return data;
}

async function updatePerformance() {
    const data = await fetchAPI('/performance');
    if (!data) return null;

    const perf = document.getElementById('performanceMetrics');
    if (perf) {
        const totalPnl = data.total_pnl || 0;
        const dailyPnl = data.daily_pnl || 0;
        const roiPct = data.roi_pct || data.total_roi || 0;
        const winRate = data.win_rate || 0;
        const totalTrades = data.total_trades || 0;
        const profitFactor = data.profit_factor || 0;
        
        perf.innerHTML = `
            <div class="metric">
                <span class="metric-label">Total P&L</span>
                <span class="metric-value ${totalPnl >= 0 ? 'positive' : 'negative'}">
                    ${formatCurrency(totalPnl)}
                </span>
            </div>
            <div class="metric">
                <span class="metric-label">Daily P&L</span>
                <span class="metric-value ${dailyPnl >= 0 ? 'positive' : 'negative'}">
                    ${formatCurrency(dailyPnl)}
                </span>
            </div>
            <div class="metric">
                <span class="metric-label">ROI</span>
                <span class="metric-value ${roiPct >= 0 ? 'positive' : 'negative'}">
                    ${formatPercent(roiPct)}
                </span>
            </div>
            <div class="metric">
                <span class="metric-label">Win Rate</span>
                <span class="metric-value">${Number(winRate).toFixed(2)}%</span>
            </div>
            <div class="metric">
                <span class="metric-label">Total Trades</span>
                <span class="metric-value">${totalTrades}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Profit Factor</span>
                <span class="metric-value">${Number(profitFactor).toFixed(2)}</span>
            </div>
        `;
    }
    return data;
}

async function updateRisk() {
    const data = await fetchAPI('/risk');
    if (!data) return;

    const risk = document.getElementById('riskMetrics');
    if (risk) {
        const exposure = data.total_exposure || 0;
        const exposurePct = data.exposure_pct || data.total_exposure_pct || 0;
        const dailyPnl = data.daily_pnl || 0;
        const positionsCount = data.positions_count || 0;
        const maxPositions = data.max_positions || 0;
        
        risk.innerHTML = `
            <div class="metric">
                <span class="metric-label">Total Exposure</span>
                <span class="metric-value">${formatCurrency(exposure)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Exposure %</span>
                <span class="metric-value">${Number(exposurePct).toFixed(2)}%</span>
            </div>
            <div class="metric">
                <span class="metric-label">Daily P&L</span>
                <span class="metric-value ${dailyPnl >= 0 ? 'positive' : 'negative'}">
                    ${formatCurrency(dailyPnl)}
                </span>
            </div>
            <div class="metric">
                <span class="metric-label">Open Positions</span>
                <span class="metric-value">${positionsCount} / ${maxPositions}</span>
            </div>
        `;
    }
}

async function updatePositions() {
    const data = await fetchAPI('/positions');
    const positions = document.getElementById('positions');
    if (!positions) return;

    if (!data || !data.positions || data.positions.length === 0) {
        positions.innerHTML = '<div class="empty-state">No active positions</div>';
        return;
    }

    let html = '<div class="table-wrapper"><table><thead><tr>';
    html += '<th>Pair</th><th>Side</th><th>Size</th><th>Entry Price</th><th>Current Price</th>';
    html += '<th>P&L</th><th>P&L %</th><th>Entry Time</th></tr></thead><tbody>';

    data.positions.forEach(pos => {
        html += '<tr>';
        html += `<td><strong>${pos.pair}</strong></td>`;
        html += `<td><span style="color: ${pos.side === 'LONG' ? 'var(--success)' : 'var(--danger)'}">${pos.side}</span></td>`;
        html += `<td>${parseFloat(pos.size).toFixed(6)}</td>`;
        html += `<td>${formatCurrency(pos.entry_price)}</td>`;
        html += `<td>${formatCurrency(pos.current_price)}</td>`;
        html += `<td class="${pos.current_pnl >= 0 ? 'positive' : 'negative'}">${formatCurrency(pos.current_pnl)}</td>`;
        html += `<td class="${pos.current_pnl_pct >= 0 ? 'positive' : 'negative'}">${formatPercent(pos.current_pnl_pct)}</td>`;
        html += `<td>${formatDate(pos.entry_time)}</td>`;
        html += '</tr>';
    });

    html += '</tbody></table></div>';
    positions.innerHTML = html;
}

// Market Conditions Page
async function updateMarketConditions() {
    const container = document.getElementById('marketConditions');
    if (!container) {
        console.error('Market conditions container not found');
        return;
    }
    
    try {
        const data = await fetchAPI('/market-conditions');
        if (!data) {
            container.innerHTML = '<div class="error">Failed to load market conditions. API may not be available.</div>';
            return;
        }

        let html = '<div class="summary-box card" style="margin-bottom: 1.5rem;"><h2>Summary</h2>';
        html += `<p>Bot Status: <strong>${data.bot_status}</strong></p>`;
        html += `<p>Ready to Trade: <strong>${data.summary.ready_to_trade ? 'Yes' : 'No'}</strong></p>`;
        html += `<p>Current Positions: <strong>${data.summary.current_positions} / ${data.summary.max_positions}</strong></p>`;
        html += '</div>';

        for (const [pair, condition] of Object.entries(data.conditions)) {
            if (condition.status === 'insufficient_data') {
                html += `<div class="market-pair"><h2>${pair}</h2>`;
                html += `<p class="error">${condition.message}</p>`;
                html += `<p>Candles: ${condition.candles_count} / ${condition.required_candles}</p>`;
                html += '</div>';
                continue;
            }

            const ind = condition.indicators;
            html += `<div class="market-pair">`;
            html += `<div class="pair-header">`;
            html += `<span class="pair-name">${pair}</span>`;
            html += `<span class="current-price">${formatCurrency(ind.price)}</span>`;
            html += `</div>`;

            html += `<div class="indicators-grid">`;
            html += `<div class="indicator-box"><div class="indicator-label">Price</div><div class="indicator-value">${formatCurrency(ind.price)}</div></div>`;
            html += `<div class="indicator-box"><div class="indicator-label">EMA(50)</div><div class="indicator-value">${formatCurrency(ind.ema)}</div></div>`;
            html += `<div class="indicator-box"><div class="indicator-label">RSI(14)</div><div class="indicator-value">${ind.rsi.toFixed(2)}</div></div>`;
            html += `<div class="indicator-box"><div class="indicator-label">Volume Ratio</div><div class="indicator-value">${ind.volume_ratio.toFixed(2)}x</div></div>`;
            html += `</div>`;

            // Long signal
            const long = condition.long_signal;
            html += `<div class="signal-box ${long.meets_threshold ? 'long' : 'neutral'}">`;
            html += `<h3>LONG Signal ${long.meets_threshold ? '✓' : '✗'}</h3>`;
            html += `<div class="condition-check"><span class="check-icon ${long.checks.price_above_ema ? 'check-pass' : 'check-fail'}">${long.checks.price_above_ema ? '✓' : '✗'}</span> Price > EMA: ${long.checks.price_above_ema ? 'Yes' : 'No'}</div>`;
            html += `<div class="condition-check"><span class="check-icon ${long.checks.rsi_in_range ? 'check-pass' : 'check-fail'}">${long.checks.rsi_in_range ? '✓' : '✗'}</span> RSI in range (${long.rsi_range}): ${long.checks.rsi_in_range ? 'Yes' : 'No'}</div>`;
            html += `<div class="condition-check"><span class="check-icon ${long.checks.volume_sufficient ? 'check-pass' : 'check-fail'}">${long.checks.volume_sufficient ? '✓' : '✗'}</span> Volume > ${long.volume_required}: ${long.checks.volume_sufficient ? 'Yes' : 'No'}</div>`;
            html += `<p><strong>Confidence:</strong> ${long.confidence.toFixed(1)}% (Need ${condition.requirements.min_confidence}%)</p>`;
            html += `</div>`;

            // Short signal
            const short = condition.short_signal;
            html += `<div class="signal-box ${short.meets_threshold ? 'short' : 'neutral'}">`;
            html += `<h3>SHORT Signal ${short.meets_threshold ? '✓' : '✗'}</h3>`;
            html += `<div class="condition-check"><span class="check-icon ${short.checks.price_below_ema ? 'check-pass' : 'check-fail'}">${short.checks.price_below_ema ? '✓' : '✗'}</span> Price < EMA: ${short.checks.price_below_ema ? 'Yes' : 'No'}</div>`;
            html += `<div class="condition-check"><span class="check-icon ${short.checks.rsi_in_range ? 'check-pass' : 'check-fail'}">${short.checks.rsi_in_range ? '✓' : '✗'}</span> RSI in range (${short.rsi_range}): ${short.checks.rsi_in_range ? 'Yes' : 'No'}</div>`;
            html += `<div class="condition-check"><span class="check-icon ${short.checks.volume_sufficient ? 'check-pass' : 'check-fail'}">${short.checks.volume_sufficient ? '✓' : '✗'}</span> Volume > ${short.volume_required}: ${short.checks.volume_sufficient ? 'Yes' : 'No'}</div>`;
            html += `<p><strong>Confidence:</strong> ${short.confidence.toFixed(1)}% (Need ${condition.requirements.min_confidence}%)</p>`;
            html += `</div>`;

            // Blockers
            if (condition.blockers && condition.blockers.length > 0) {
                html += `<div class="blockers"><h3>Blockers</h3><ul>`;
                condition.blockers.forEach(blocker => {
                    html += `<li>${blocker}</li>`;
                });
                html += `</ul></div>`;
            }

            html += `</div>`;
        }

        // Show AI Analysis section
        const aiAnalysisCard = document.getElementById('aiAnalysisCard');
        if (aiAnalysisCard) {
            aiAnalysisCard.style.display = 'block';
            // Auto-load AI analysis only ONCE per visit to the Market page.
            // Without this guard it re-runs every 5 seconds (page refresh interval).
            if (!marketAiAutoLoaded) {
                marketAiAutoLoaded = true;
                setTimeout(() => {
                    getAIAnalysis();
                }, 500);
            }
        }

        container.innerHTML = html;
    } catch (error) {
        console.error('Error updating market conditions:', error);
        container.innerHTML = `<div class="error">Error loading market conditions: ${error.message}</div>`;
    }
}

// Positions Page
async function updatePositionsPage() {
    const container = document.getElementById('positionsPage');
    if (!container) {
        console.error('Positions page container not found');
        return;
    }
    
    try {
        const data = await fetchAPI('/positions');
        if (!data) {
            container.innerHTML = '<div class="error">Failed to load positions. API may not be available.</div>';
            return;
        }
    
        // Detect new positions for push notifications
        const currentPositions = data.positions || [];
        if (currentPositions.length > previousPositions.length && previousPositions.length > 0) {
            const newPositions = currentPositions.filter(pos => 
                !previousPositions.some(prev => prev.pair === pos.pair && prev.entry_time === pos.entry_time)
            );
            newPositions.forEach(pos => {
                sendPushNotification(
                    `New Position: ${pos.pair}`,
                    `${pos.side} position opened. Entry: ${formatCurrency(parseFloat(pos.entry_price))}`,
                    { tag: `position-${pos.pair}` }
                );
            });
        }
        previousPositions = [...currentPositions];
    
        if (currentPositions.length === 0) {
            container.innerHTML = '<div class="empty-state">No active positions</div>';
            return;
        }

        let html = '<div class="card"><h2>Active Positions</h2><div class="table-wrapper"><table><thead><tr>';
        html += '<th>Pair</th><th>Side</th><th>Entry Price</th><th>Current Price</th>';
        html += '<th>Size</th><th>P&L</th><th>P&L %</th><th>Entry Time</th><th>Actions</th>';
        html += '</tr></thead><tbody>';

        data.positions.forEach(pos => {
            const pnl = parseFloat(pos.unrealized_pnl || 0);
            const pnlPct = parseFloat(pos.unrealized_pnl_pct || 0);
            html += '<tr>';
            html += `<td><strong>${pos.pair}</strong></td>`;
            html += `<td><span class="status-badge ${pos.side === 'LONG' ? 'status-running' : 'status-stopped'}" style="font-size: 0.75rem; padding: 0.25rem 0.5rem;">${pos.side}</span></td>`;
            html += `<td>${formatCurrency(parseFloat(pos.entry_price))}</td>`;
            html += `<td>${formatCurrency(parseFloat(pos.current_price))}</td>`;
            html += `<td>${parseFloat(pos.size).toFixed(6)}</td>`;
            html += `<td class="${pnl >= 0 ? 'positive' : 'negative'}">${formatCurrency(pnl)}</td>`;
            html += `<td class="${pnlPct >= 0 ? 'positive' : 'negative'}">${formatPercent(pnlPct)}</td>`;
            html += `<td>${formatDate(pos.entry_time)}</td>`;
            html += `<td><button class="btn btn-stop" onclick="controlBot('close-position', {pair: '${pos.pair}'})" style="padding: 0.5rem 1rem; font-size: 0.875rem;">Close</button></td>`;
            html += '</tr>';
        });

        html += '</tbody></table></div></div>';
        container.innerHTML = html;
    } catch (error) {
        console.error('Error updating positions page:', error);
        container.innerHTML = `<div class="error">Error loading positions: ${error.message}</div>`;
    }
}

// Trades Page
async function updateTradesPage() {
    const container = document.getElementById('tradesPage');
    if (!container) {
        console.error('Trades page container not found');
        return;
    }
    
    try {
        const data = await fetchAPI('/trades?limit=50');
        if (!data) {
            container.innerHTML = '<div class="error">Failed to load trades. API may not be available.</div>';
            return;
        }

        if (!data.trades || data.trades.length === 0) {
            container.innerHTML = '<div class="empty-state">No trades yet</div>';
            return;
        }

    let html = '<div class="table-wrapper"><table><thead><tr>';
    html += '<th>Time</th><th>Pair</th><th>Side</th><th>Entry</th><th>Exit</th>';
    html += '<th>Size</th><th>P&L</th><th>P&L %</th><th>Reason</th></tr></thead><tbody>';

    data.trades.slice(0, 50).forEach(trade => {
        const pnl = parseFloat(trade.pnl || 0);
        const pnlPct = parseFloat(trade.pnl_pct || 0);
        html += '<tr>';
        html += `<td>${formatDate(trade.entry_time)}</td>`;
        html += `<td><strong>${trade.pair}</strong></td>`;
        html += `<td><span style="color: ${trade.side === 'LONG' ? 'var(--success)' : 'var(--danger)'}">${trade.side}</span></td>`;
        html += `<td>${formatCurrency(parseFloat(trade.entry_price))}</td>`;
        html += `<td>${trade.exit_price ? formatCurrency(parseFloat(trade.exit_price)) : '-'}</td>`;
        html += `<td>${parseFloat(trade.size).toFixed(6)}</td>`;
        html += `<td class="${pnl >= 0 ? 'positive' : 'negative'}">${formatCurrency(pnl)}</td>`;
        html += `<td class="${pnlPct >= 0 ? 'positive' : 'negative'}">${formatPercent(pnlPct)}</td>`;
        html += `<td>${trade.exit_reason || '-'}</td>`;
        html += '</tr>';
    });

        html += '</tbody></table></div>';
        container.innerHTML = html;
    } catch (error) {
        console.error('Error updating trades:', error);
        container.innerHTML = `<div class="error">Error loading trades: ${error.message}</div>`;
    }
}

// Performance Page
let equityChart = null;
let pnlChart = null;
let winRateChart = null;

async function updatePerformancePage() {
    const container = document.getElementById('performancePage');
    if (!container) {
        console.error('Performance page container not found');
        return;
    }
    
    try {
        const data = await fetchAPI('/performance');
        if (!data) {
            container.innerHTML = '<div class="error">Failed to load performance data. API may not be available.</div>';
            return;
        }

        container.innerHTML = `
            <div class="grid">
                <div class="card">
                    <h2>Account</h2>
                    <div class="metric"><span class="metric-label">Balance</span><span class="metric-value">${formatCurrency(data.account_balance)}</span></div>
                    <div class="metric"><span class="metric-label">Initial Balance</span><span class="metric-value">${formatCurrency(data.initial_balance)}</span></div>
                    <div class="metric"><span class="metric-label">ROI</span><span class="metric-value ${data.roi_pct >= 0 ? 'positive' : 'negative'}">${formatPercent(data.roi_pct)}</span></div>
                </div>
                <div class="card">
                    <h2>P&L</h2>
                    <div class="metric"><span class="metric-label">Total P&L</span><span class="metric-value ${data.total_pnl >= 0 ? 'positive' : 'negative'}">${formatCurrency(data.total_pnl)}</span></div>
                    <div class="metric"><span class="metric-label">Daily P&L</span><span class="metric-value ${data.daily_pnl >= 0 ? 'positive' : 'negative'}">${formatCurrency(data.daily_pnl)}</span></div>
                    <div class="metric"><span class="metric-label">Gross Profit</span><span class="metric-value positive">${formatCurrency(data.gross_profit)}</span></div>
                    <div class="metric"><span class="metric-label">Gross Loss</span><span class="metric-value negative">${formatCurrency(data.gross_loss)}</span></div>
                </div>
                <div class="card">
                    <h2>Statistics</h2>
                    <div class="metric"><span class="metric-label">Total Trades</span><span class="metric-value">${data.total_trades}</span></div>
                    <div class="metric"><span class="metric-label">Win Rate</span><span class="metric-value">${data.win_rate.toFixed(2)}%</span></div>
                    <div class="metric"><span class="metric-label">Profit Factor</span><span class="metric-value">${data.profit_factor.toFixed(2)}</span></div>
                    <div class="metric"><span class="metric-label">Sharpe Ratio</span><span class="metric-value">${data.sharpe_ratio.toFixed(2)}</span></div>
                    <div class="metric"><span class="metric-label">Max Drawdown</span><span class="metric-value">${formatPercent(data.max_drawdown)}</span></div>
                </div>
            </div>
        `;

        // Show charts container - ONLY on performance page
        if (currentPage === 'performance') {
            const chartsContainer = document.querySelector('.charts-container');
            if (chartsContainer) {
                chartsContainer.style.display = 'block';
                // Update charts (destroy existing ones first)
                try {
                    await updateCharts(data);
                } catch (error) {
                    console.error('Error rendering charts:', error);
                    // Charts will fail gracefully
                }
            }
        }
    } catch (error) {
        console.error('Error updating performance:', error);
        container.innerHTML = `<div class="error">Error loading performance: ${error.message}</div>`;
    }
}

async function updateCharts(performanceData) {
    // Only update charts if we're on performance page
    if (currentPage !== 'performance') {
        return;
    }
    
    try {
        // Destroy ALL existing charts FIRST before creating new ones
        // Use Chart.js getChart() method to find existing charts on canvases
        const equityCtx = document.getElementById('equityChart');
        const pnlCtx = document.getElementById('pnlChart');
        const winRateCtx = document.getElementById('winRateChart');
        
        // Destroy equity chart - check both variable and canvas
        if (equityChart) {
            try {
                equityChart.destroy();
            } catch (e) {
                console.warn('Error destroying equity chart variable:', e);
            }
        }
        if (equityCtx) {
            const existingChart = Chart.getChart(equityCtx);
            if (existingChart) {
                try {
                    existingChart.destroy();
                } catch (e) {
                    console.warn('Error destroying existing equity chart from canvas:', e);
                }
            }
        }
        equityChart = null;
        
        // Destroy P&L chart - check both variable and canvas
        if (pnlChart) {
            try {
                pnlChart.destroy();
            } catch (e) {
                console.warn('Error destroying P&L chart variable:', e);
            }
        }
        if (pnlCtx) {
            const existingChart = Chart.getChart(pnlCtx);
            if (existingChart) {
                try {
                    existingChart.destroy();
                } catch (e) {
                    console.warn('Error destroying existing P&L chart from canvas:', e);
                }
            }
        }
        pnlChart = null;
        
        // Destroy win rate chart - check both variable and canvas
        if (winRateChart) {
            try {
                winRateChart.destroy();
            } catch (e) {
                console.warn('Error destroying win rate chart variable:', e);
            }
        }
        if (winRateCtx) {
            const existingChart = Chart.getChart(winRateCtx);
            if (existingChart) {
                try {
                    existingChart.destroy();
                } catch (e) {
                    console.warn('Error destroying existing win rate chart from canvas:', e);
                }
            }
        }
        winRateChart = null;
        
        // Longer delay to ensure canvas is fully released
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Double-check that all charts are destroyed before creating new ones
        if (equityCtx && Chart.getChart(equityCtx)) {
            try {
                Chart.getChart(equityCtx).destroy();
                await new Promise(resolve => setTimeout(resolve, 100));
            } catch (e) {
                console.warn('Error in final equity chart cleanup:', e);
            }
        }
        if (pnlCtx && Chart.getChart(pnlCtx)) {
            try {
                Chart.getChart(pnlCtx).destroy();
                await new Promise(resolve => setTimeout(resolve, 100));
            } catch (e) {
                console.warn('Error in final P&L chart cleanup:', e);
            }
        }
        if (winRateCtx && Chart.getChart(winRateCtx)) {
            try {
                Chart.getChart(winRateCtx).destroy();
                await new Promise(resolve => setTimeout(resolve, 100));
            } catch (e) {
                console.warn('Error in final win rate chart cleanup:', e);
            }
        }
        
        // Get equity curve data
        const equityData = await fetchAPI('/equity-curve?limit=100');
        
        // Equity Curve Chart (equityCtx already declared above)
        if (equityCtx) {
            // Final check - ensure canvas is free
            if (Chart.getChart(equityCtx)) {
                console.warn('Warning: Equity chart canvas still has a chart, attempting to destroy...');
                Chart.getChart(equityCtx).destroy();
                await new Promise(resolve => setTimeout(resolve, 100));
            }
            
            const labels = equityData?.equity_curve?.map((p, i) => i) || [];
            const balances = equityData?.equity_curve?.map(p => p.balance) || [performanceData.initial_balance];
            
            equityChart = new Chart(equityCtx, {
                type: 'line',
                data: {
                labels: labels,
                datasets: [{
                    label: 'Account Balance',
                    data: balances,
                    borderColor: 'rgb(102, 126, 234)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: true },
                    tooltip: {
                        callbacks: {
                            label: (context) => formatCurrency(context.parsed.y)
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: (value) => formatCurrency(value)
                        }
                    }
                }
            }
            });
        }
        
        // P&L Chart (pnlCtx already declared above)
        if (pnlCtx) {
            // Final check - ensure canvas is free
            if (Chart.getChart(pnlCtx)) {
                console.warn('Warning: P&L chart canvas still has a chart, attempting to destroy...');
                Chart.getChart(pnlCtx).destroy();
                await new Promise(resolve => setTimeout(resolve, 100));
            }
            
            // Get daily P&L history
            const dailyData = await fetchAPI('/daily-pnl?limit=30');
            const pnlLabels = dailyData?.daily_pnl || [];
            
            pnlChart = new Chart(pnlCtx, {
                type: 'bar',
                data: {
                labels: pnlLabels.map((_, i) => `Day ${i + 1}`),
                datasets: [{
                    label: 'Daily P&L',
                    data: pnlLabels.map(d => d.daily_pnl || 0),
                    backgroundColor: (ctx) => {
                        const value = ctx.parsed?.y ?? ctx.raw ?? 0;
                        return value >= 0 ? 'rgba(16, 185, 129, 0.7)' : 'rgba(239, 68, 68, 0.7)';
                    }
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (context) => formatCurrency(context.parsed.y)
                        }
                    }
                },
                scales: {
                    y: {
                        ticks: {
                            callback: (value) => formatCurrency(value)
                        }
                    }
                }
            }
        });
        }
        
        // Win Rate Pie Chart (winRateCtx already declared above)
        if (winRateCtx) {
            // Final check - ensure canvas is free
            if (Chart.getChart(winRateCtx)) {
                console.warn('Warning: Win rate chart canvas still has a chart, attempting to destroy...');
                Chart.getChart(winRateCtx).destroy();
                await new Promise(resolve => setTimeout(resolve, 100));
            }
            
            const winning = performanceData.winning_trades || 0;
            const losing = performanceData.losing_trades || 0;
            
            winRateChart = new Chart(winRateCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Winning Trades', 'Losing Trades'],
                    datasets: [{
                        data: [winning, losing],
                        backgroundColor: ['rgba(16, 185, 129, 0.7)', 'rgba(239, 68, 68, 0.7)']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { position: 'bottom' }
                    }
                }
            });
        }
    } catch (error) {
        console.error('Error updating charts:', error);
        // Charts will fail gracefully without breaking the page
    }
}

// Logs Page
async function updateLogsPage() {
    const container = document.getElementById('logsContainer');
    if (!container) {
        console.error('Logs container not found');
        return;
    }
    
    try {
        const logs = await fetchAPI('/logs');
        if (!logs) {
            container.innerHTML = '<div class="error">Failed to load logs. API may not be available.</div>';
            return;
        }
    
        const levelFilter = document.getElementById('logLevelFilter')?.value || 'ALL';
        const searchTerm = document.getElementById('logSearch')?.value.toLowerCase() || '';
        
        let filteredLogs = logs?.logs || [];
        
        if (levelFilter !== 'ALL') {
            filteredLogs = filteredLogs.filter(log => log.level === levelFilter);
        }
        
        if (searchTerm) {
            filteredLogs = filteredLogs.filter(log => 
                log.message.toLowerCase().includes(searchTerm)
            );
        }
        
        if (filteredLogs.length === 0) {
            container.innerHTML = '<div class="empty-state">No logs found</div>';
            return;
        }
        
        let html = '<div class="logs-list">';
        filteredLogs.slice(-100).reverse().forEach(log => {
            const levelClass = log.level?.toLowerCase() || 'info';
            html += `<div class="log-entry log-${levelClass}">`;
            html += `<span class="log-time">${formatDate(log.timestamp)}</span>`;
            html += `<span class="log-level">${log.level || 'INFO'}</span>`;
            html += `<span class="log-message">${log.message || ''}</span>`;
            html += `</div>`;
        });
        html += '</div>';
        
        container.innerHTML = html;
    } catch (error) {
        console.error('Error updating logs:', error);
        container.innerHTML = `<div class="error">Error loading logs: ${error.message}</div>`;
    }
}

function clearLogs() {
    document.getElementById('logsContainer').innerHTML = '<div class="empty-state">Logs cleared</div>';
}

function downloadLogs() {
    window.location.href = '/api/logs/download';
}

// Backtesting Functions
let backtestListInterval = null;
let runningBacktestId = null;
let runningBacktestPromise = null;
let backtestListCurrentPage = 1;
let backtestListItemsPerPage = 10;
let backtestListFilteredData = [];
let backtestListAllData = [];

async function updateBacktestPage() {
    // Load the backtest list (it will use cache if available)
    await loadBacktestList();
    
    // Check if there was a running backtest from before navigation
    try {
        const runningInfo = sessionStorage.getItem('runningBacktest');
        if (runningInfo) {
            const info = JSON.parse(runningInfo);
            const resultsCard = document.getElementById('backtestResultsCard');
            const content = document.getElementById('backtestResultsContent');
            
            if (resultsCard && content) {
                resultsCard.style.display = 'block';
                const started = new Date(info.started);
                const elapsed = Math.round((Date.now() - started.getTime()) / 1000);
                const minutes = Math.floor(elapsed / 60);
                const seconds = elapsed % 60;
                
                content.innerHTML = '<div class="loading" style="padding: 2rem; text-align: center;"><div style="font-size: 1.1rem; margin-bottom: 0.5rem; font-weight: 600;">Backtest May Still Be Running</div><div style="margin-bottom: 0.5rem;">Pair: ' + info.pair + '</div><div style="margin-bottom: 0.5rem;">Period: ' + info.days + ' days</div><div style="margin-bottom: 0.5rem; color: var(--gray-500);">Started: ' + started.toLocaleTimeString() + '</div><div style="margin-bottom: 0.5rem; color: var(--gray-500);">Elapsed: ' + minutes + 'm ' + seconds + 's</div><small style="color: var(--gray-500);">Checking for completed results... The backtest list below may show new results.</small></div>';
            }
            
            // Check if backtest completed by looking at the list
            setTimeout(async () => {
                await loadBacktestList(); // Refresh to see if it completed
                // Clear the running flag if enough time has passed (5 minutes)
                const runningBacktest = JSON.parse(sessionStorage.getItem('runningBacktest') || '{}');
                if (runningBacktest.startTime) {
                    const started = new Date(parseInt(runningBacktest.startTime, 10));
                    const elapsed = Math.round((Date.now() - started.getTime()) / 1000);
                    if (elapsed > 300) { // 5 minutes
                        sessionStorage.removeItem('runningBacktest');
                    }
                }
            }, 2000);
        }
    } catch (e) {
        console.warn('Could not check for running backtest:', e);
    }
    
    // Check if there's a currently running backtest
    if (runningBacktestId || runningBacktestPromise) {
        // Show running indicator
        const resultsCard = document.getElementById('backtestResultsCard');
        const content = document.getElementById('backtestResultsContent');
        if (resultsCard && content && !content.innerHTML.includes('running')) {
            resultsCard.style.display = 'block';
            content.innerHTML = '<div class="loading" style="padding: 2rem; text-align: center;">Backtest is running in the background...<br><small>You can navigate away and return later. The backtest will continue.</small></div>';
        }
    }
}

async function loadBacktestList() {
    const container = document.getElementById('backtestList');
    if (!container) {
        console.warn('Backtest list container not found');
        return;
    }
    
    // Don't clear if already showing data (preserve state when navigating)
    const currentContent = container.innerHTML;
    const isShowingData = currentContent && !currentContent.includes('Loading') && !currentContent.includes('No backtests');
    
    try {
        // Only show loading if container is empty
        if (!isShowingData) {
            container.innerHTML = '<div class="loading">Loading backtests...</div>';
        }
        
        const data = await fetchAPI('/backtest/list');
        console.log('Backtest list API response:', data);
        if (!data || !data.backtests) {
            console.warn('No backtest data received:', data);
            // Only show empty state if we don't have cached data
            if (!isShowingData) {
                container.innerHTML = '<div class="empty-state">No backtests yet. Run your first backtest above!</div>';
                document.getElementById('backtestPagination')?.setAttribute('style', 'display: none !important');
            }
            return;
        }
        
        if (data.backtests.length === 0) {
            // Show empty state
            container.innerHTML = '<div class="empty-state">No backtests yet. Run your first backtest above!</div>';
            document.getElementById('backtestPagination')?.setAttribute('style', 'display: none !important');
            console.log('No backtests found in database');
            return;
        }
        
        // Store all data
        backtestListAllData = [...data.backtests].sort((a, b) => {
            const dateA = a.created_at ? new Date(a.created_at).getTime() : 0;
            const dateB = b.created_at ? new Date(b.created_at).getTime() : 0;
            return dateB - dateA; // Newest first
        });
        
        // Apply filters and render
        filterBacktestList();
        
        // Store the list in sessionStorage for persistence
        try {
            sessionStorage.setItem('backtestList', JSON.stringify(data.backtests));
        } catch (e) {
            console.warn('Could not store backtest list in sessionStorage:', e);
        }
    } catch (error) {
        console.error('Error loading backtest list:', error);
        
        // Try to load from cache if API fails
        try {
            const cached = sessionStorage.getItem('backtestList');
            if (cached && !isShowingData) {
                const cachedList = JSON.parse(cached);
                if (cachedList && cachedList.length > 0) {
                    // Show cached data with a notice
                    container.innerHTML = `<div class="warning" style="padding: 1rem; margin-bottom: 1rem; background: rgba(251, 191, 36, 0.1); border: 1px solid var(--accent-gold); border-radius: 8px;">Showing cached backtest list. <button onclick="loadBacktestList()" class="btn btn-primary btn-sm" style="margin-left: 0.5rem;">Refresh</button></div>`;
                    return;
                }
            }
        } catch (e) {
            console.warn('Could not load cached backtest list:', e);
        }
        
        container.innerHTML = `<div class="error">Error loading backtests: ${error.message}. <button onclick="loadBacktestList()" class="btn btn-primary btn-sm" style="margin-top: 0.5rem;">Retry</button></div>`;
        document.getElementById('backtestPagination')?.setAttribute('style', 'display: none !important');
    }
}

function filterBacktestList() {
    const pairFilter = document.getElementById('backtestFilterPair')?.value || '';
    const periodFilter = document.getElementById('backtestFilterPeriod')?.value || '';
    
    // Filter data
    backtestListFilteredData = backtestListAllData.filter(bt => {
        // Pair filter
        if (pairFilter && bt.pair !== pairFilter) {
            return false;
        }
        
        // Period filter
        if (periodFilter) {
            const startDate = bt.start_date ? new Date(bt.start_date) : null;
            const endDate = bt.end_date ? new Date(bt.end_date) : null;
            const days = startDate && endDate ? Math.round((endDate - startDate) / (1000 * 60 * 60 * 24)) : 0;
            
            if (periodFilter === '14+') {
                if (days < 14) return false;
            } else {
                const filterDays = parseInt(periodFilter);
                if (days !== filterDays) return false;
            }
        }
        
        return true;
    });
    
    // Reset to page 1 when filtering
    backtestListCurrentPage = 1;
    
    // Render the filtered list
    renderBacktestList();
}

function renderBacktestList() {
    const container = document.getElementById('backtestList');
    if (!container) return;
    
    if (backtestListFilteredData.length === 0) {
        container.innerHTML = '<div class="empty-state">No backtests match your filters. <button onclick="document.getElementById(\'backtestFilterPair\').value=\'\'; document.getElementById(\'backtestFilterPeriod\').value=\'\'; filterBacktestList();" class="btn btn-secondary btn-sm" style="margin-left: 0.5rem;">Clear Filters</button></div>';
        document.getElementById('backtestPagination')?.setAttribute('style', 'display: none !important');
        return;
    }
    
    // Calculate pagination
    const totalPages = Math.ceil(backtestListFilteredData.length / backtestListItemsPerPage);
    const startIndex = (backtestListCurrentPage - 1) * backtestListItemsPerPage;
    const endIndex = Math.min(startIndex + backtestListItemsPerPage, backtestListFilteredData.length);
    const paginatedData = backtestListFilteredData.slice(startIndex, endIndex);
    
    // Build table
    let html = '<div class="table-wrapper" style="max-height: 600px; overflow-y: auto;"><table><thead><tr>';
    html += '<th>Name</th><th>Pair</th><th>Period</th><th>P&L</th><th>ROI</th><th>Win Rate</th><th>Trades</th><th>Date</th><th>Actions</th>';
    html += '</tr></thead><tbody>';
    
    paginatedData.forEach(bt => {
        const pnl = parseFloat(bt.total_pnl || 0);
        const roi = parseFloat(bt.roi_pct || 0);
        const winRate = parseFloat(bt.win_rate || 0);
        const trades = parseInt(bt.total_trades || 0);
        
        // Calculate period
        const startDate = bt.start_date ? new Date(bt.start_date) : null;
        const endDate = bt.end_date ? new Date(bt.end_date) : null;
        const days = startDate && endDate ? Math.round((endDate - startDate) / (1000 * 60 * 60 * 24)) : 'N/A';
        
        html += '<tr>';
        html += `<td><strong>${escapeHtml(bt.name || 'Unnamed')}</strong></td>`;
        html += `<td><span class="badge" style="padding: 0.25rem 0.5rem; background: var(--blue-100); color: var(--blue-700); border-radius: 4px; font-size: 0.875rem;">${escapeHtml(bt.pair || 'N/A')}</span></td>`;
        html += `<td>${days} days</td>`;
        html += `<td class="${pnl >= 0 ? 'positive' : 'negative'}" style="font-weight: 600;">${formatCurrency(pnl)}</td>`;
        html += `<td class="${roi >= 0 ? 'positive' : 'negative'}" style="font-weight: 600;">${formatPercent(roi)}</td>`;
        html += `<td>${winRate.toFixed(2)}%</td>`;
        html += `<td>${trades}</td>`;
        html += `<td style="font-size: 0.875rem; color: var(--gray-600);">${bt.created_at ? formatDate(bt.created_at) : 'N/A'}</td>`;
        html += `<td><button class="btn btn-primary btn-sm" onclick="viewBacktest(${bt.id})" style="padding: 0.4rem 0.8rem; font-size: 0.8125rem;">View</button></td>`;
        html += '</tr>';
    });
    
    html += '</tbody></table></div>';
    container.innerHTML = html;
    
    // Update pagination controls
    const paginationEl = document.getElementById('backtestPagination');
    if (paginationEl) {
        paginationEl.style.display = 'flex';
        document.getElementById('backtestPageInfo').textContent = `${startIndex + 1}-${endIndex}`;
        document.getElementById('backtestTotalCount').textContent = backtestListFilteredData.length;
        document.getElementById('backtestCurrentPage').textContent = backtestListCurrentPage;
        
        const prevBtn = document.getElementById('backtestPrevPage');
        const nextBtn = document.getElementById('backtestNextPage');
        if (prevBtn) prevBtn.disabled = backtestListCurrentPage === 1;
        if (nextBtn) nextBtn.disabled = backtestListCurrentPage >= totalPages;
    }
}

function changeBacktestPage(direction) {
    const totalPages = Math.ceil(backtestListFilteredData.length / backtestListItemsPerPage);
    const newPage = backtestListCurrentPage + direction;
    
    if (newPage >= 1 && newPage <= totalPages) {
        backtestListCurrentPage = newPage;
        renderBacktestList();
        // Scroll to top of list
        const container = document.getElementById('backtestList');
        if (container) {
            container.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
}

// Quick run backtest function for common periods
async function runQuickBacktest(days) {
    const pair = document.getElementById('backtestPair')?.value || 'BTC-USD';
    const balance = document.getElementById('backtestBalance')?.value || 100000;
    const pairNames = {
        'BTC-USD': 'BTC',
        'ETH-USD': 'ETH',
        'SOL-USD': 'SOL'
    };
    const pairName = pairNames[pair] || pair.split('-')[0];
    const name = `${pairName} ${days}-DAY`;
    
    // Set form values
    if (document.getElementById('backtestPair')) {
        document.getElementById('backtestPair').value = pair;
    }
    if (document.getElementById('backtestDays')) {
        document.getElementById('backtestDays').value = days;
    }
    if (document.getElementById('backtestBalance')) {
        document.getElementById('backtestBalance').value = balance;
    }
    if (document.getElementById('backtestName')) {
        document.getElementById('backtestName').value = name;
    }
    
    // Run the backtest
    await runBacktestInternal(pair, days, parseFloat(balance), name);
}

async function runBacktest(event) {
    if (event) {
        event.preventDefault();
    }
    
    const pair = document.getElementById('backtestPair').value;
    const days = parseInt(document.getElementById('backtestDays').value);
    const balance = parseFloat(document.getElementById('backtestBalance').value);
    const name = document.getElementById('backtestName').value || `${pair.split('-')[0]} ${days}-day test`;
    
    await runBacktestInternal(pair, days, balance, name);
}

async function runBacktestInternal(pair, days, balance, name) {
    const runBtn = document.getElementById('runBacktestBtn');
    const btnText = document.getElementById('backtestBtnText');
    const loadingText = document.getElementById('backtestLoading');
    
    // Show running state immediately
    if (runBtn) {
        runBtn.disabled = true;
        if (btnText) btnText.style.display = 'none';
        if (loadingText) loadingText.style.display = 'inline';
    }
    
    // Show results card with running message
    const resultsCard = document.getElementById('backtestResultsCard');
    const content = document.getElementById('backtestResultsContent');
    if (resultsCard && content) {
        resultsCard.style.display = 'block';
        content.innerHTML = '<div class="loading" style="padding: 2rem; text-align: center;"><div style="font-size: 1.1rem; margin-bottom: 0.5rem;">Running backtest for ' + pair + ' over ' + days + ' days...</div><small>This may take a few moments. You can navigate away and return later.</small></div>';
        resultsCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    showToast(`Running backtest for ${pair} over ${days} days...`, 'info');
    
    // Store backtest info in sessionStorage so we can check status later
    const backtestStartTime = new Date().toISOString();
    try {
        sessionStorage.setItem('runningBacktest', JSON.stringify({
            pair: pair,
            days: days,
            name: name,
            started: backtestStartTime
        }));
    } catch (e) {
        console.warn('Could not store running backtest info:', e);
    }
    
    // Store that a backtest is running
    runningBacktestId = Date.now(); // Use timestamp as ID
    const thisBacktestId = runningBacktestId;
    
    // Run backtest in background - don't block on navigation
    runningBacktestPromise = (async () => {
        try {
            const requestBody = {
                pair,
                days,
                initial_balance: balance,
                name
            };
            console.log('🚀 Sending backtest request to:', `${API_BASE}/backtest/run`, requestBody);
            console.log('🚀 Auth token exists:', !!localStorage.getItem('auth_token'));
            
            // Create abort controller for timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout
            
            let response;
            try {
                response = await fetch(`${API_BASE}/backtest/run`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                    },
                    credentials: 'include',
                    body: JSON.stringify(requestBody),
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId); // Clear timeout if request succeeds
                console.log('📡 Backtest response received - status:', response.status, response.statusText);
                console.log('📡 Response headers:', Object.fromEntries(response.headers.entries()));
            } catch (fetchError) {
                clearTimeout(timeoutId); // Clear timeout on error
                console.error('❌❌❌ FETCH ERROR (network/connection):', fetchError);
                if (fetchError.name === 'AbortError') {
                    throw new Error('Backtest request timed out after 60 seconds. The server may be processing a long backtest. Please try a shorter period (1-3 days) or check back later.');
                } else if (fetchError.name === 'TypeError' && fetchError.message.includes('fetch')) {
                    throw new Error('Network error: Could not connect to server. Please check your internet connection and try again.');
                } else {
                    throw new Error(`Request failed: ${fetchError.message}`);
                }
            }
            
            // Only process if this is still the current backtest
            if (runningBacktestId !== thisBacktestId) {
                console.log('Backtest result received but different backtest is now running');
                return;
            }
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({error: 'Backtest failed'}));
                const errorMsg = errorData.error || 'Backtest failed';
                // Include recommendation if provided
                if (errorData.recommendation) {
                    throw new Error(`${errorMsg}\n\n${errorData.recommendation}\n\nOptimal periods: ${errorData.optimal_periods || '1-7 days for scalping'}`);
                }
                throw new Error(errorMsg);
            }
            
            const result = await response.json();
            
            if (result.success) {
                // Clear running backtest flag
                try {
                    sessionStorage.removeItem('runningBacktest');
                } catch (e) {}
                
                // Handle both result.results and result.backtest formats
                const backtestResults = result.results || result.backtest;
                if (backtestResults) {
                    console.log('Backtest completed successfully:', backtestResults);
                    // Only update UI if we're still on the backtest page
                    if (currentPage === 'backtest') {
                        displayBacktestResults(backtestResults);
                        showToast('Backtest completed successfully!', 'success');
                    }
                } else {
                    console.warn('Backtest completed but no results in response:', result);
                    // Still refresh the list to see if it was saved
                    if (currentPage === 'backtest') {
                        showToast('Backtest completed but no results returned. Check the backtest list below.', 'warning');
                    }
                }
                
                // Always refresh the list to show saved backtests
                await loadBacktestList();
            } else {
                throw new Error(result.error || 'Backtest failed');
            }
            
        } catch (error) {
            console.error('❌ Backtest error:', error);
            console.error('❌ Error details:', {
                message: error.message,
                stack: error.stack,
                name: error.name
            });
            
            // Clear running backtest flag on error
            try {
                sessionStorage.removeItem('runningBacktest');
            } catch (e) {}
            
            // Only show error if we're still on the backtest page
            if (currentPage === 'backtest') {
                // Format error message (replace \n with <br> for HTML display)
                const errorHtml = error.message.replace(/\n/g, '<br>');
                showToast(`Backtest failed: ${error.message.split('\n')[0]}`, 'error');
                
                // Show error in results card with full details
                if (resultsCard && content) {
                    resultsCard.style.display = 'block';
                    content.innerHTML = `<div class="error" style="padding: 2rem; text-align: center; color: var(--red-600);">${errorHtml}<br><small style="color: var(--gray-500);">Check browser console (F12) for details</small></div>`;
                }
            }
        } finally {
            // Only reset button if we're still on backtest page and this is the current backtest
            if (runningBacktestId === thisBacktestId && currentPage === 'backtest') {
                runBtn.disabled = false;
                btnText.style.display = 'inline';
                loadingText.style.display = 'none';
            }
            
            // Clear running state
            if (runningBacktestId === thisBacktestId) {
                runningBacktestId = null;
                runningBacktestPromise = null;
            }
            
            // Update status badge
            try {
                const statusData = await fetchAPI('/status');
                if (statusData && statusData.status) {
                    updateStatusBadge(statusData.status);
                }
            } catch (e) {
                console.warn('Failed to update status:', e);
            }
        }
    })();
    
    // Don't await - let it run in background
    // This allows navigation without cancelling the request
    
    // Also set up periodic checking for results if user navigates away
    const checkInterval = setInterval(async () => {
        // If backtest completed or we navigated away, check for new results
        if (runningBacktestId === null || currentPage !== 'backtest') {
            if (currentPage === 'backtest') {
                await loadBacktestList(); // Refresh list when returning
            }
            clearInterval(checkInterval);
        }
    }, 3000); // Check every 3 seconds
    
    // Clean up interval after 5 minutes
    setTimeout(() => clearInterval(checkInterval), 5 * 60 * 1000);
}

function displayBacktestResults(results) {
    const card = document.getElementById('backtestResultsCard');
    const content = document.getElementById('backtestResultsContent');
    
    if (!card || !content) return;
    
    const pnl = parseFloat(results.total_pnl || 0);
    const roi = parseFloat(results.roi_pct || 0);
    const winRate = parseFloat(results.win_rate || 0);
    
    let html = '<div class="backtest-results">';
    html += '<div class="grid" style="grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem;">';
    html += `<div class="metric"><span class="metric-label">Total P&L</span><span class="metric-value ${pnl >= 0 ? 'positive' : 'negative'}">${formatCurrency(pnl)}</span></div>`;
    html += `<div class="metric"><span class="metric-label">ROI</span><span class="metric-value ${roi >= 0 ? 'positive' : 'negative'}">${formatPercent(roi)}</span></div>`;
    html += `<div class="metric"><span class="metric-label">Win Rate</span><span class="metric-value">${winRate.toFixed(2)}%</span></div>`;
    html += `<div class="metric"><span class="metric-label">Total Trades</span><span class="metric-value">${results.total_trades || 0}</span></div>`;
    html += '</div>';
    
    html += '<div class="grid" style="grid-template-columns: repeat(4, 1fr); gap: 1rem;">';
    html += `<div class="metric"><span class="metric-label">Profit Factor</span><span class="metric-value">${(parseFloat(results.profit_factor || 0)).toFixed(2)}</span></div>`;
    html += `<div class="metric"><span class="metric-label">Max Drawdown</span><span class="metric-value">${(parseFloat(results.max_drawdown || 0)).toFixed(2)}%</span></div>`;
    html += `<div class="metric"><span class="metric-label">Avg Win</span><span class="metric-value">${formatCurrency(parseFloat(results.avg_win || 0))}</span></div>`;
    html += `<div class="metric"><span class="metric-label">Avg Loss</span><span class="metric-value">${formatCurrency(parseFloat(results.avg_loss || 0))}</span></div>`;
    html += '</div>';
    
    html += '</div>';
    
    // Add AI Analysis section with better structure
    html += '<div class="backtest-ai-section" style="margin-top: 2.5rem; padding-top: 2rem; border-top: 3px solid var(--gray-300);">';
    html += '<div class="ai-analysis-header" style="margin-bottom: 1.5rem;">';
    html += '<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">';
    html += '<div>';
    html += '<h3 style="margin: 0 0 0.25rem 0; font-size: 1.5rem; font-weight: 700; color: var(--gray-900);">AI Analysis</h3>';
    html += '<p class="ai-analysis-subtitle" style="margin: 0; font-size: 0.875rem; color: var(--gray-500);">Powered by Claude AI • Get insights on your backtest results</p>';
    html += '</div>';
    html += '<button class="btn btn-primary" id="analyzeBacktestBtn" style="min-width: 150px;">Analyze Results</button>';
    html += '</div>';
    html += '</div>';
    html += '<div id="backtestAIAnalysisContent" style="display: none; margin-top: 1.5rem;"></div>';
    html += '</div>';
    
    content.innerHTML = html;
    card.style.display = 'block';
    
    // Set up button click handler after DOM update
    setTimeout(() => {
        const analyzeBtn = document.getElementById('analyzeBacktestBtn');
        if (analyzeBtn) {
            analyzeBtn.onclick = () => getBacktestAIAnalysis(results);
        }
    }, 100);
    
    // Scroll to results
    card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

async function viewBacktest(id) {
    try {
        showToast('Loading backtest details...', 'info');
        
        const data = await fetchAPI(`/backtest/results/${id}`);
        if (data && data.backtest) {
            displayBacktestResults(data.backtest);
            // Scroll to results
            const resultsCard = document.getElementById('backtestResultsCard');
            if (resultsCard) {
                resultsCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
            showToast('Backtest details loaded', 'success');
        } else {
            throw new Error('Backtest not found or invalid response');
        }
    } catch (error) {
        console.error('Error loading backtest:', error);
        showToast(`Failed to load backtest: ${error.message}`, 'error');
        
        // Show error in results card if possible
        const resultsCard = document.getElementById('backtestResultsCard');
        const content = document.getElementById('backtestResultsContent');
        if (resultsCard && content) {
            resultsCard.style.display = 'block';
            content.innerHTML = `<div class="error" style="padding: 2rem; text-align: center;">Failed to load backtest: ${escapeHtml(error.message)}</div>`;
        }
        showToast(`Error: ${error.message}`, 'error');
    }
}

async function getBacktestAIAnalysis(results) {
    const analysisContent = document.getElementById('backtestAIAnalysisContent');
    if (!analysisContent) return;
    
    try {
        analysisContent.style.display = 'block';
        analysisContent.innerHTML = '<div class="loading">Analyzing backtest results with AI...</div>';
        
        // Get strategy config if available
        const strategyConfig = null; // Can be enhanced later to fetch current config
        
        // Extract only summary metrics to avoid "Request Entity Too Large" error
        // Don't send all trades - just the summary statistics
        const summaryResults = {
            total_pnl: results.total_pnl || 0,
            roi_pct: results.roi_pct || 0,
            total_trades: results.total_trades || 0,
            winning_trades: results.winning_trades || 0,
            losing_trades: results.losing_trades || 0,
            win_rate: results.win_rate || 0,
            profit_factor: results.profit_factor || 0,
            sharpe_ratio: results.sharpe_ratio || 0,
            max_drawdown: results.max_drawdown || 0,
            avg_win: results.avg_win || 0,
            avg_loss: results.avg_loss || 0,
            gross_profit: results.gross_profit || 0,
            gross_loss: results.gross_loss || 0,
            initial_balance: results.initial_balance || 0,
            final_balance: results.final_balance || 0,
            start_date: results.start_date || null,
            end_date: results.end_date || null,
            pair: results.pair || 'N/A'
        };
        
        // Only include a sample of trades if they exist (limit to 10 most recent)
        if (results.trades && Array.isArray(results.trades)) {
            summaryResults.trade_sample = results.trades.slice(-10).map(trade => ({
                pair: trade.pair,
                side: trade.side,
                entry_price: trade.entry_price,
                exit_price: trade.exit_price,
                pnl: trade.pnl,
                pnl_pct: trade.pnl_pct,
                entry_time: trade.entry_time,
                exit_time: trade.exit_time
            }));
        }
        
        const token = localStorage.getItem('auth_token');
        const response = await fetch(`${API_BASE}/ai/analyze-backtest`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': token ? `Bearer ${token}` : ''
            },
            credentials: 'include',
            body: JSON.stringify({
                results: summaryResults,
                strategy_config: strategyConfig
            })
        });
        
        // Handle authentication errors
        if (response.status === 401) {
            showToast('Session expired. Please sign in again.', 'error');
            setTimeout(() => {
                window.location.href = '/landing';
            }, 2000);
            return;
        }
        
        // Handle 404 errors
        if (response.status === 404) {
            throw new Error('AI analysis endpoint not found. The feature may not be available.');
        }
        
        // Try to parse JSON response
        let result;
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            result = await response.json();
        } else {
            // If not JSON, read as text to see what we got
            const text = await response.text();
            throw new Error(`Server returned non-JSON response: ${text.substring(0, 100)}`);
        }
        
        if (!response.ok) {
            throw new Error(result.error || `AI analysis failed (${response.status})`);
        }
        
        if (result.success && result.analysis) {
            analysisContent.innerHTML = formatAIAnalysis(result.analysis);
            showToast('AI analysis complete!', 'success');
        } else {
            throw new Error(result.error || 'No analysis received');
        }
    } catch (error) {
        console.error('AI backtest analysis error:', error);
        let errorMessage = error.message || 'Unknown error occurred';
        
        // Handle JSON parse errors specifically
        if (error instanceof SyntaxError && error.message.includes('JSON')) {
            errorMessage = 'Server returned invalid response. The AI analysis feature may not be configured correctly.';
        }
        
        analysisContent.innerHTML = `<div class="error">AI analysis error: ${escapeHtml(errorMessage)}<br><small>Please check that CLAUDE_API_KEY is configured in .env</small></div>`;
        showToast(`AI analysis failed: ${errorMessage}`, 'error');
    }
}

// Format AI Analysis with professional styling
function formatAIAnalysis(text) {
    if (!text) return '<div class="ai-analysis-empty">No analysis available</div>';
    
    // Remove any intro text before sections
    text = text.trim();
    
    // Split into sections based on headers
    const sections = [];
    let currentSection = { type: 'intro', content: [] };
    
    // Split by common section markers
    const lines = text.split('\n');
    
    lines.forEach((line, index) => {
        line = line.trim();
        
        // Skip empty lines and intro sentences
        if (line.length === 0) {
            return;
        }
        
        // Detect section headers in various formats:
        // 1. Markdown headers: ## Header or ### Header
        // 2. Numbered headers: 1. Header, 2. Header
        // 3. Bold headers: **Header:**
        // 4. Plain headers ending with colon: "Header:"
        // 5. Headers in numbered list format: "1. Market Overview:"
        let headerMatch = null;
        let headerText = null;
        
        // Markdown headers (## Header or ### Header)
        if (line.match(/^#{2,3}\s+(.+)$/)) {
            headerText = line.replace(/^#+\s+/, '').trim();
            headerMatch = true;
        }
        // Numbered headers with bold markdown (1. **Market Overview**:)
        else if (line.match(/^\d+\.\s+\*\*(.+?)\*\*:?\s*$/)) {
            headerText = line.replace(/^\d+\.\s+\*\*/, '').replace(/\*\*:?\s*$/, '').trim();
            headerMatch = true;
        }
        // Numbered headers with colon (1. Market Overview:)
        else if (line.match(/^\d+\.\s+([A-Z][^:]{5,45}):\s*$/)) {
            headerText = line.replace(/^\d+\.\s+/, '').replace(/:\s*$/, '').trim();
            headerMatch = true;
        }
        // Numbered headers without colon (must be short and capital letter start)
        else if (line.match(/^\d+\.\s+([A-Z][A-Za-z\s]{4,40})\s*$/) && line.length < 50) {
            headerText = line.replace(/^\d+\.\s+/, '').trim();
            headerMatch = true;
        }
        // Bold headers (**Market Overview:**)
        else if (line.match(/^\*\*(.+?)\*\*:?\s*$/)) {
            headerText = line.replace(/^\*\*/, '').replace(/\*\*:?\s*$/, '').trim();
            headerMatch = true;
        }
        // Headers ending with colon (Market Overview:)
        else if (line.match(/^[A-Z][^:]{2,45}:\s*$/) && !line.includes('.') && line.length < 50) {
            headerText = line.replace(/:\s*$/, '').trim();
            headerMatch = true;
        }
        
        if (headerMatch && headerText) {
            // Save previous section
            if (currentSection.content.length > 0 || currentSection.header) {
                sections.push(currentSection);
            }
            // Start new section
            currentSection = {
                type: getSectionType(headerText),
                header: headerText,
                content: []
            };
        } else {
            // Add to current section content
            currentSection.content.push(line);
        }
    });
    
    // Add the last section
    if (currentSection.content.length > 0 || currentSection.header) {
        sections.push(currentSection);
    }
    
    // If no sections found, treat entire text as intro
    if (sections.length === 0 || (sections.length === 1 && !sections[0].header)) {
        // Try to find sections in paragraph format
        const fullText = lines.join(' ');
        const sectionMatches = fullText.match(/(\d+\.\s+[A-Z][^:]+:)/g);
        if (sectionMatches && sectionMatches.length > 0) {
            sections.length = 0;
            sectionMatches.forEach((match, idx) => {
                const headerText = match.replace(/^\d+\.\s+/, '').replace(/:\s*$/, '').trim();
                sections.push({
                    type: getSectionType(headerText),
                    header: headerText,
                    content: []
                });
            });
        } else {
            sections.length = 0;
            sections.push({ type: 'intro', content: lines.filter(l => l.trim().length > 0) });
        }
    }
    
    // Build HTML
    let html = '<div class="ai-analysis-container">';
    
    sections.forEach(section => {
        // Skip intro sections without headers
        if (!section.header && section.type === 'intro') {
            // Render intro content at the top
            if (section.content.length > 0) {
                const introText = section.content.join(' ').trim();
                if (introText.length > 0 && !introText.match(/^(here is|this is|below is)/i)) {
                    html += `<div class="ai-intro-text">${formatMarkdown(introText)}</div>`;
                }
            }
            return;
        }
        
        const sectionClass = `ai-section ai-section-${section.type}`;
        html += `<div class="${sectionClass}">`;
        
        if (section.header) {
            html += `<div class="ai-section-header">`;
            html += `<div class="ai-section-icon-wrapper">`;
            html += `<span class="ai-section-icon-text">${getSectionIcon(section.type)}</span>`;
            html += `</div>`;
            html += `<h3 class="ai-section-title">${escapeHtml(section.header)}</h3>`;
            html += `</div>`;
        }
        
        html += `<div class="ai-section-content">`;
        
        // Process content into paragraphs and lists
        let inList = false;
        let paragraphText = '';
        
        section.content.forEach((line, idx) => {
            line = line.trim();
            if (line.length === 0) {
                if (paragraphText) {
                    if (inList) {
                        html += '</ul>';
                        inList = false;
                    }
                    html += `<p>${formatMarkdown(paragraphText)}</p>`;
                    paragraphText = '';
                }
                if (inList) {
                    html += '</ul>';
                    inList = false;
                }
                return;
            }
            
            // Check if it's a list item
            const listMatch = line.match(/^[-*•]\s+(.+)$/);
            if (listMatch) {
                if (paragraphText) {
                    html += `<p>${formatMarkdown(paragraphText)}</p>`;
                    paragraphText = '';
                }
                if (!inList) {
                    html += '<ul class="ai-list">';
                    inList = true;
                }
                const listText = listMatch[1].trim();
                html += `<li>${formatMarkdown(listText)}</li>`;
            } else {
                // Close list if open
                if (inList) {
                    html += '</ul>';
                    inList = false;
                }
                // Add to paragraph or start new one
                if (paragraphText) {
                    paragraphText += ' ' + line;
                } else {
                    paragraphText = line;
                }
            }
        });
        
        // Close any open paragraph or list
        if (paragraphText) {
            html += `<p>${formatMarkdown(paragraphText)}</p>`;
        }
        if (inList) {
            html += '</ul>';
        }
        
        html += `</div></div>`;
    });
    
    html += '</div>';
    return html;
}

function getSectionType(header) {
    const lower = header.toLowerCase();
    if (lower.includes('overview') || lower.includes('summary')) return 'overview';
    if (lower.includes('opportunit') || lower.includes('trading')) return 'opportunities';
    if (lower.includes('risk') || lower.includes('warning') || lower.includes('concern')) return 'risks';
    if (lower.includes('recommend') || lower.includes('suggest') || lower.includes('action')) return 'recommendations';
    if (lower.includes('conclusion')) return 'conclusion';
    return 'general';
}

function getSectionIcon(type) {
    const icons = {
        'overview': 'OV',
        'opportunities': 'OP',
        'risks': 'RK',
        'recommendations': 'RC',
        'conclusion': 'CN',
        'general': 'GN',
        'intro': 'IN'
    };
    return icons[type] || icons['general'];
}

function formatMarkdown(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code>$1</code>');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// AI Analysis Functions
async function getAIAnalysis() {
    const analysisCard = document.getElementById('aiAnalysisCard');
    const analysisContent = document.getElementById('aiAnalysisContent');
    
    if (!analysisCard || !analysisContent) return;
    
    try {
        // Prevent concurrent runs (e.g. refresh loop + user click)
        if (aiAnalysisInFlight) return;
        aiAnalysisInFlight = true;

        analysisCard.style.display = 'block';
        analysisContent.innerHTML = '<div class="loading">Analyzing market conditions with AI...</div>';
        
        // Get current market data
        const marketData = await fetchAPI('/market-conditions');
        if (!marketData) {
            throw new Error('Failed to fetch market data');
        }
        
        const response = await fetch(`${API_BASE}/ai/analyze-market`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
            },
            credentials: 'include',
            body: JSON.stringify({
                market_data: marketData,
                trading_signals: marketData
            })
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({error: 'AI analysis failed'}));
            throw new Error(error.error || 'AI analysis not available');
        }
        
        const result = await response.json();
        
        if (result.success && result.analysis) {
            // Format AI response with professional section-based formatting
            const formattedAnalysis = formatAIAnalysis(result.analysis);
            analysisContent.innerHTML = formattedAnalysis;
            showToast('AI analysis complete!', 'success');
        } else {
            throw new Error('No analysis received');
        }
        
    } catch (error) {
        console.error('AI analysis error:', error);
        analysisContent.innerHTML = `<div class="error">
            <p>${error.message}</p>
            <p><small>Make sure CLAUDE_API_KEY is configured in .env file</small></p>
        </div>`;
        showToast('AI analysis failed', 'error');
    } finally {
        aiAnalysisInFlight = false;
    }
}

// AI Help Function - Context-aware help throughout dashboard
async function getAIHelp(topic, context = {}) {
    const questions = {
        'account-status': 'Explain what the account status metrics mean and how to interpret them',
        'performance': 'Explain the performance metrics shown here. What do win rate, profit factor, and Sharpe ratio mean?',
        'risk': 'Help me understand the risk metrics. What should I watch for?',
        'strategy': 'Explain how the trading strategy works in simple terms',
        'backtest': 'How do I use backtesting effectively? What should I look for in results?'
    };
    
    const question = questions[topic] || `Help me understand ${topic}`;
    
    try {
        showToast('Getting AI help...', 'info');
        
        // Get current context if available
        let fullContext = context;
        if (topic === 'performance' || topic === 'account-status') {
            try {
                const perf = await fetchAPI('/performance');
                const status = await fetchAPI('/status');
                fullContext = { performance: perf, status: status, ...context };
            } catch (e) {
                // Ignore errors getting context
            }
        }
        
        const response = await fetch(`${API_BASE}/ai/guidance`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
            },
            credentials: 'include',
            body: JSON.stringify({
                question: question,
                context: fullContext
            })
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({error: 'AI help unavailable'}));
            showToast(`AI help: ${error.error || 'Please configure CLAUDE_API_KEY in .env'}`, 'warning');
            return;
        }
        
        const result = await response.json();
        
        if (result.success && result.guidance) {
            // Create a modal or show in a toast
            showAIHelpModal(result.guidance, topic);
        }
    } catch (error) {
        console.error('AI help error:', error);
        showToast('AI help unavailable. Configure CLAUDE_API_KEY in .env', 'warning');
    }
}

function showAIHelpModal(content, topic) {
    // Create modal overlay
    const modal = document.createElement('div');
    modal.className = 'ai-help-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.8);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
    `;
    
    // Format content
    let formattedContent = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');
    
    modal.innerHTML = `
        <div style="background: #1a1a1a; border-radius: 12px; padding: 2rem; max-width: 600px; max-height: 80vh; overflow-y: auto; border: 2px solid #333;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h2 style="color: #fff; margin: 0;">AI Help: ${topic}</h2>
                <button onclick="this.closest('.ai-help-modal').remove()" style="background: none; border: none; color: #fff; font-size: 1.5rem; cursor: pointer;">×</button>
            </div>
            <div style="color: #ddd; line-height: 1.6;">
                <p>${formattedContent}</p>
            </div>
            <button onclick="this.closest('.ai-help-modal').remove()" style="margin-top: 1rem; padding: 0.75rem 1.5rem; background: var(--primary); color: white; border: none; border-radius: 8px; cursor: pointer; width: 100%;">Close</button>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close on outside click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// Trade Export Functions
async function exportTrades(format) {
    try {
        const token = localStorage.getItem('auth_token');
        const headers = {};
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        // Get date range from UI if available (future enhancement)
        const url = `/api/trades/export?format=${format}`;
        
        showToast(`Exporting trades as ${format.toUpperCase()}...`, 'info');
        
        const response = await fetch(url, {
            headers: headers,
            credentials: 'include'
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({error: 'Export failed'}));
            showToast('Export failed: ' + (error.error || 'Unknown error'), 'error');
            return;
        }
        
        // Download the file
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = response.headers.get('Content-Disposition')?.split('filename=')[1]?.replace(/"/g, '') || `trades_export.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(downloadUrl);
        
        showToast(`Trades exported successfully as ${format.toUpperCase()}!`, 'success');
    } catch (error) {
        console.error('Export error:', error);
        showToast('Export failed: ' + error.message, 'error');
    }
}

// Portfolio Analytics Functions
let allocationChart = null;
let pnlByPairChart = null;
let portfolioValueChart = null;

async function updatePortfolioPage() {
    try {
        const data = await fetchAPI('/portfolio/analytics');
        if (!data) {
            const container = document.getElementById('page-portfolio');
            if (container) {
                const content = container.querySelector('.portfolio-summary, #portfolioSummary');
                if (content) {
                    content.innerHTML = '<div class="empty-state">No portfolio data available yet. Start trading to see analytics.</div>';
                }
            }
            return;
        }
        
        // Update summary cards - wrap in try-catch to prevent errors from breaking the page
        if (typeof updatePortfolioSummary === 'function') {
            try {
                updatePortfolioSummary(data);
            } catch (err) {
                console.warn('Error updating portfolio summary:', err);
                // Continue with other updates
            }
        }
        
        // Update statistics table
        if (typeof updatePairStatistics === 'function') {
            try {
                updatePairStatistics(data);
            } catch (err) {
                console.warn('Error updating pair statistics:', err);
                // Continue with other updates
            }
        }
        
        // Render charts
        if (typeof renderPortfolioCharts === 'function') {
            try {
                await renderPortfolioCharts(data);
            } catch (err) {
                console.warn('Error rendering portfolio charts:', err);
                // Continue - charts are optional
            }
        }
        
    } catch (error) {
        // Extract error message safely
        let errorMsg = 'Error loading portfolio data';
        try {
            if (error instanceof Error) {
                errorMsg = error.message || error.toString();
            } else if (typeof error === 'string') {
                errorMsg = error;
            } else if (error && typeof error === 'object') {
                // Try to extract message from object
                errorMsg = error.message || error.error || error.toString() || 'Unknown error';
            }
        } catch (e) {
            // If we can't extract the message, use default
            errorMsg = 'Error loading portfolio data';
        }
        
        console.error('Error updating portfolio page:', errorMsg);
        
        // Display error in UI
        const container = document.getElementById('page-portfolio');
        if (container) {
            const content = container.querySelector('.portfolio-summary, #portfolioSummary, .card') || container;
            if (content) {
                content.innerHTML = `<div class="error">Error loading portfolio: ${escapeHtml(String(errorMsg))}</div>`;
            }
        }
    }
}

function updatePortfolioSummary(data) {
    try {
        if (!data) {
            console.warn('updatePortfolioSummary: No data provided');
            return;
        }
        
        const portfolioValue = parseFloat(data.portfolio_value || 0);
        const initialBalance = parseFloat(data.initial_balance || 0);
        const totalPnl = parseFloat(data.total_pnl || 0);
        const roiPct = parseFloat(data.roi_pct || 0);
        const winStreak = data.win_streak || 0;
        const lossStreak = data.loss_streak || 0;
        
        // Update portfolio value
        const valueEl = document.getElementById('portfolioValue');
        if (valueEl) {
            valueEl.textContent = formatCurrency(portfolioValue);
        }
        
        // Update portfolio change
        const changeEl = document.getElementById('portfolioChange');
        if (changeEl) {
            const change = roiPct;
            changeEl.textContent = `${change >= 0 ? '+' : ''}${formatPercent(change)}`;
            changeEl.className = `metric-label ${change >= 0 ? 'positive' : 'negative'}`;
        }
        
        // Update P&L
        const pnlEl = document.getElementById('portfolioPnl');
        if (pnlEl) {
            pnlEl.textContent = formatCurrency(totalPnl);
            pnlEl.className = `metric-value ${totalPnl >= 0 ? 'positive' : 'negative'}`;
        }
        
        // Update ROI
        const roiEl = document.getElementById('portfolioRoi');
        if (roiEl) {
            roiEl.textContent = formatPercent(roiPct);
            roiEl.className = roiPct >= 0 ? 'positive' : 'negative';
        }
        
        // Update streaks
        const winStreakEl = document.getElementById('winStreak');
        if (winStreakEl) {
            winStreakEl.textContent = winStreak;
        }
        
        const lossStreakEl = document.getElementById('lossStreak');
        if (lossStreakEl) {
            lossStreakEl.textContent = lossStreak;
        }
    } catch (error) {
        console.error('Error in updatePortfolioSummary:', error);
        throw error; // Re-throw to be caught by parent
    }
}

function updatePairStatistics(data) {
    try {
        const container = document.getElementById('pairStatistics');
        if (!container) {
            console.warn('updatePairStatistics: pairStatistics container not found');
            return;
        }
        
        if (!data) {
            container.innerHTML = '<div class="empty-state">No data available.</div>';
            return;
        }
        
        const pnlByPair = data.pnl_by_pair || {};
        const tradesByPair = data.trades_by_pair || {};
        
        if (Object.keys(pnlByPair).length === 0) {
            container.innerHTML = '<div class="empty-state">No trading data yet. Start trading to see statistics.</div>';
            return;
        }
        
        let html = '<div class="table-wrapper"><table><thead><tr>';
        html += '<th>Trading Pair</th><th>Total Trades</th><th>Winning</th><th>Losing</th>';
        html += '<th>Win Rate</th><th>Total P&L</th><th>Total Volume</th>';
        html += '</tr></thead><tbody>';
        
        // Sort by total P&L (descending)
        const sortedPairs = Object.entries(pnlByPair).sort((a, b) => {
            const pnlA = parseFloat(a[1]?.total_pnl || 0);
            const pnlB = parseFloat(b[1]?.total_pnl || 0);
            return pnlB - pnlA;
        });
        
        sortedPairs.forEach(([pair, stats]) => {
            if (!stats) return;
            const pnl = parseFloat(stats.total_pnl || 0);
            html += '<tr>';
            html += `<td><strong>${escapeHtml(String(pair))}</strong></td>`;
            html += `<td>${stats.total_trades || 0}</td>`;
            html += `<td class="positive">${stats.winning_trades || 0}</td>`;
            html += `<td class="negative">${stats.losing_trades || 0}</td>`;
            html += `<td>${parseFloat(stats.win_rate || 0).toFixed(2)}%</td>`;
            html += `<td class="${pnl >= 0 ? 'positive' : 'negative'}">${formatCurrency(pnl)}</td>`;
            html += `<td>${formatCurrency(parseFloat(stats.total_volume || 0))}</td>`;
            html += '</tr>';
        });
        
        html += '</tbody></table></div>';
        container.innerHTML = html;
    } catch (error) {
        console.error('Error in updatePairStatistics:', error);
        const container = document.getElementById('pairStatistics');
        if (container) {
            container.innerHTML = '<div class="error">Error loading statistics. Please try again.</div>';
        }
        throw error; // Re-throw to be caught by parent
    }
}

async function renderPortfolioCharts(data) {
    try {
        if (!data) {
            console.warn('renderPortfolioCharts: No data provided');
            return;
        }
        
        // Destroy existing charts if they exist
        if (allocationChart) {
            try { allocationChart.destroy(); } catch(e) {}
            allocationChart = null;
        }
        if (pnlByPairChart) {
            try { pnlByPairChart.destroy(); } catch(e) {}
            pnlByPairChart = null;
        }
        if (portfolioValueChart) {
            try { portfolioValueChart.destroy(); } catch(e) {}
            portfolioValueChart = null;
        }
        
        // Wait a bit for canvas to be ready
        await new Promise(resolve => setTimeout(resolve, 200));
    
    // Render Asset Allocation Chart (Pie Chart)
    const allocationCtx = document.getElementById('allocationChart');
    if (allocationCtx && data.asset_allocation) {
        const allocation = data.asset_allocation;
        const labels = Object.keys(allocation);
        const percentages = Object.values(allocation).map(a => a.percentage);
        
        if (labels.length > 0) {
            allocationChart = new Chart(allocationCtx, {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        data: percentages,
                        backgroundColor: [
                            'rgba(37, 99, 235, 0.8)',
                            'rgba(16, 185, 129, 0.8)',
                            'rgba(251, 191, 36, 0.8)',
                            'rgba(239, 68, 68, 0.8)',
                            'rgba(139, 92, 246, 0.8)',
                            'rgba(236, 72, 153, 0.8)'
                        ],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    return `${label}: ${value.toFixed(2)}%`;
                                }
                            }
                        }
                    }
                }
            });
        }
    }
    
    // Render P&L by Pair Chart (Bar Chart)
    const pnlByPairCtx = document.getElementById('pnlByPairChart');
    if (pnlByPairCtx && data.pnl_by_pair) {
        const pnlData = data.pnl_by_pair;
        const pairs = Object.keys(pnlData);
        const pnlValues = Object.values(pnlData).map(d => d.total_pnl);
        
        if (pairs.length > 0) {
            pnlByPairChart = new Chart(pnlByPairCtx, {
                type: 'bar',
                data: {
                    labels: pairs,
                    datasets: [{
                        label: 'P&L',
                        data: pnlValues,
                        backgroundColor: pnlValues.map(v => v >= 0 ? 'rgba(16, 185, 129, 0.8)' : 'rgba(239, 68, 68, 0.8)'),
                        borderColor: pnlValues.map(v => v >= 0 ? 'rgba(16, 185, 129, 1)' : 'rgba(239, 68, 68, 1)'),
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `P&L: ${formatCurrency(context.parsed.y)}`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return formatCurrency(value);
                                }
                            }
                        }
                    }
                }
            });
        }
    }
    
    // Render Portfolio Value Over Time Chart (Line Chart)
    const portfolioValueCtx = document.getElementById('portfolioValueChart');
    if (portfolioValueCtx && data.portfolio_history && data.portfolio_history.length > 0) {
        const history = data.portfolio_history;
        const timestamps = history.map(h => {
            try {
                return new Date(h.timestamp).toLocaleDateString();
            } catch(e) {
                return '';
            }
        });
        const values = history.map(h => parseFloat(h.balance || 0));
        
        portfolioValueChart = new Chart(portfolioValueCtx, {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [{
                    label: 'Portfolio Value',
                    data: values,
                    borderColor: 'rgba(37, 99, 235, 1)',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Value: ${formatCurrency(context.parsed.y)}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return formatCurrency(value);
                            }
                        }
                    }
                }
            }
        });
    }
    } catch (error) {
        console.error('Error in renderPortfolioCharts:', error);
        // Don't throw - charts are optional, just log the error
    }
}

async function generateTaxReport() {
    const year = document.getElementById('taxYear')?.value || new Date().getFullYear();
    const method = document.getElementById('taxMethod')?.value || 'FIFO';
    const container = document.getElementById('taxReportContent');
    
    if (!container) return;
    
    try {
        container.innerHTML = '<div class="loading">Generating tax report...</div>';
        
        const data = await fetchAPI(`/portfolio/tax-report?year=${year}&method=${method}`);
        if (!data) {
            throw new Error('Failed to load tax report');
        }
        
        const realizedGains = data.realized_gains || { count: 0, total: 0, trades: [] };
        const realizedLosses = data.realized_losses || { count: 0, total: 0, trades: [] };
        const netRealized = parseFloat(data.net_realized || 0);
        
        let html = '<div class="tax-report-summary" style="margin-bottom: 2rem;">';
        html += `<div class="card" style="display: inline-block; margin-right: 1rem; padding: 1rem;"><strong>Realized Gains:</strong> ${formatCurrency(realizedGains.total)} (${realizedGains.count} trades)</div>`;
        html += `<div class="card" style="display: inline-block; margin-right: 1rem; padding: 1rem;"><strong>Realized Losses:</strong> ${formatCurrency(realizedLosses.total)} (${realizedLosses.count} trades)</div>`;
        html += `<div class="card" style="display: inline-block; padding: 1rem;"><strong>Net Realized:</strong> <span class="${netRealized >= 0 ? 'positive' : 'negative'}">${formatCurrency(netRealized)}</span></div>`;
        html += '</div>';
        
        html += '<div class="table-wrapper"><table><thead><tr>';
        html += '<th>Pair</th><th>Entry Time</th><th>Exit Time</th><th>Size</th>';
        html += '<th>Entry Price</th><th>Exit Price</th><th>Cost Basis</th><th>Proceeds</th>';
        html += `<th>${netRealized >= 0 ? 'Gain' : 'Loss'}</th></tr></thead><tbody>`;
        
        // Combine gains and losses
        const allTrades = [
            ...realizedGains.trades.map(t => ({...t, type: 'gain'})),
            ...realizedLosses.trades.map(t => ({...t, type: 'loss'}))
        ].sort((a, b) => new Date(b.exit_time) - new Date(a.exit_time));
        
        allTrades.forEach(trade => {
            html += '<tr>';
            html += `<td><strong>${escapeHtml(trade.pair)}</strong></td>`;
            html += `<td>${formatDate(trade.entry_time)}</td>`;
            html += `<td>${formatDate(trade.exit_time)}</td>`;
            html += `<td>${parseFloat(trade.size).toFixed(6)}</td>`;
            html += `<td>${formatCurrency(parseFloat(trade.entry_price))}</td>`;
            html += `<td>${formatCurrency(parseFloat(trade.exit_price))}</td>`;
            html += `<td>${formatCurrency(parseFloat(trade.cost_basis))}</td>`;
            html += `<td>${formatCurrency(parseFloat(trade.proceeds))}</td>`;
            if (trade.type === 'gain') {
                html += `<td class="positive">${formatCurrency(parseFloat(trade.gain))}</td>`;
            } else {
                html += `<td class="negative">-${formatCurrency(parseFloat(trade.loss))}</td>`;
            }
            html += '</tr>';
        });
        
        html += '</tbody></table></div>';
        container.innerHTML = html;
        
        showToast('Tax report generated successfully', 'success');
    } catch (error) {
        console.error('Error generating tax report:', error);
        container.innerHTML = `<div class="error">Error generating tax report: ${escapeHtml(error.message)}</div>`;
        showToast(`Tax report failed: ${error.message}`, 'error');
    }
}

async function exportTaxReport() {
    const year = document.getElementById('taxYear')?.value || new Date().getFullYear();
    const method = document.getElementById('taxMethod')?.value || 'FIFO';
    
    try {
        const data = await fetchAPI(`/portfolio/tax-report?year=${year}&method=${method}`);
        if (!data) {
            throw new Error('Failed to load tax report');
        }
        
        // Create CSV content
        let csv = 'Pair,Entry Time,Exit Time,Size,Entry Price,Exit Price,Cost Basis,Proceeds,Gain/Loss\n';
        
        const allTrades = [
            ...(data.realized_gains?.trades || []).map(t => ({...t, type: 'gain', amount: t.gain})),
            ...(data.realized_losses?.trades || []).map(t => ({...t, type: 'loss', amount: -t.loss}))
        ].sort((a, b) => new Date(b.exit_time) - new Date(a.exit_time));
        
        allTrades.forEach(trade => {
            csv += `"${trade.pair}","${trade.entry_time}","${trade.exit_time}",${trade.size},${trade.entry_price},${trade.exit_price},${trade.cost_basis},${trade.proceeds},${trade.amount}\n`;
        });
        
        // Download CSV
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `tax-report-${year}-${method}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showToast('Tax report exported successfully', 'success');
    } catch (error) {
        console.error('Error exporting tax report:', error);
        showToast(`Export failed: ${error.message}`, 'error');
    }
}

// Advanced Charts Functions
let priceChart = null;
let rsiChart = null;
let volumeChart = null;

async function updateChartsPage() {
    const container = document.getElementById('page-charts');
    if (!container) {
        console.error('Charts page container not found');
        return;
    }
    
    // Load chart data and render
    await updateAdvancedChart();
}

async function updateAdvancedChart() {
    try {
        // Check if LightweightCharts is available
        if (!window.LightweightCharts || typeof window.LightweightCharts.createChart !== 'function') {
            console.error('LightweightCharts not available');
            showToast('Charting library not loaded. Please refresh the page.', 'error');
            return;
        }
        
        const pair = document.getElementById('chartPair')?.value || 'BTC-USD';
        const timeframe = document.getElementById('chartTimeframe')?.value || '1h';
        
        // Fetch candle data
        const candlesData = await fetchAPI(`/charts/candles?pair=${pair}&timeframe=${timeframe}&limit=100`);
        if (!candlesData || !candlesData.candles) {
            showToast('Failed to load chart data', 'error');
            return;
        }
        
        // Fetch indicators
        const indicatorsData = await fetchAPI(`/charts/indicators?pair=${pair}&timeframe=${timeframe}`);
        
        // Render charts
        renderPriceChart(candlesData.candles, indicatorsData?.indicators);
        renderRSIChart(candlesData.candles);
        renderVolumeChart(candlesData.candles);
        updateIndicatorsSummary(indicatorsData?.indicators || {});
        
    } catch (error) {
        console.error('Error updating advanced chart:', error);
        showToast(`Chart error: ${error.message}`, 'error');
    }
}

function renderPriceChart(candles, indicators) {
    const container = document.getElementById('priceChartContainer');
    if (!container) {
        console.warn('Price chart container not found');
        return;
    }
    
    // Check if LightweightCharts is loaded - try multiple possible namespaces
    let createChartFn = null;
    if (window.LightweightCharts && typeof window.LightweightCharts.createChart === 'function') {
        createChartFn = window.LightweightCharts.createChart;
    } else if (window.lightweightCharts && typeof window.lightweightCharts.createChart === 'function') {
        createChartFn = window.lightweightCharts.createChart;
    } else if (typeof window.createChart === 'function') {
        createChartFn = window.createChart;
    }
    
    if (!createChartFn) {
        console.error('LightweightCharts library not loaded or createChart function not found');
        container.innerHTML = '<div class="error">Charting library not loaded. Please refresh the page.</div>';
        return;
    }
    
    // Clear existing chart
    if (priceChart) {
        try {
            priceChart.remove();
        } catch(e) {
            console.warn('Error removing existing chart:', e);
        }
        priceChart = null;
    }
    
    container.innerHTML = '';
    const canvas = document.createElement('canvas');
    canvas.id = 'priceChart';
    container.appendChild(canvas);
    
    if (!canvas) return;
    
    // Create chart
    let chart;
    try {
        chart = createChartFn(canvas, {
            width: container.clientWidth || 800,
            height: 500,
            layout: {
                backgroundColor: '#ffffff',
                textColor: '#333',
            },
            grid: {
                vertLines: { color: '#f0f0f0' },
                horzLines: { color: '#f0f0f0' },
            },
            timeScale: {
                timeVisible: true,
                secondsVisible: false,
            },
        });
        
        if (!chart) {
            throw new Error('Chart creation returned null or undefined');
        }
        
        // Verify chart has required methods
        if (!chart || typeof chart.addCandlestickSeries !== 'function') {
            console.error('Chart object:', chart);
            console.error('Chart methods:', chart ? Object.keys(chart).filter(k => typeof chart[k] === 'function') : 'null');
            throw new Error(`Chart object does not have addCandlestickSeries method. Chart type: ${typeof chart}`);
        }
    } catch (error) {
        console.error('Error creating chart:', error);
        container.innerHTML = `<div class="error">Error creating chart: ${error.message}<br><small>Please check browser console for details.</small></div>`;
        return;
    }
    
    // Add candlestick series
    let candlestickSeries;
    try {
        if (!chart || typeof chart.addCandlestickSeries !== 'function') {
            throw new Error('Chart object is invalid or addCandlestickSeries method not available');
        }
        
        candlestickSeries = chart.addCandlestickSeries({
            upColor: '#10b981',
            downColor: '#ef4444',
            borderVisible: false,
            wickUpColor: '#10b981',
            wickDownColor: '#ef4444',
        });
    } catch (error) {
        console.error('Error adding candlestick series:', error);
        container.innerHTML = `<div class="error">Error adding candlestick series: ${error.message}</div>`;
        return;
    }
    
    // Format candles for Lightweight Charts (ensure time is in correct format)
    const formattedCandles = candles.map(c => {
        let timeValue = c.time;
        // Convert Unix timestamp to seconds if needed
        if (typeof timeValue === 'number' && timeValue > 1e10) {
            timeValue = Math.floor(timeValue / 1000);
        }
        return {
            time: timeValue,
            open: parseFloat(c.open),
            high: parseFloat(c.high),
            low: parseFloat(c.low),
            close: parseFloat(c.close),
        };
    });
    
    candlestickSeries.setData(formattedCandles);
    
    // Add EMA line if enabled and available
    const showEMA = document.getElementById('showEMA')?.checked;
    if (showEMA && formattedCandles.length >= 50) {
        const emaSeries = chart.addLineSeries({
            color: '#2563eb',
            lineWidth: 2,
            title: 'EMA(50)',
        });
        
        // Calculate EMA values from candles
        const emaValues = calculateEMA(formattedCandles, 50);
        if (emaValues.length > 0) {
            emaSeries.setData(emaValues);
        }
    }
    
    // Add Bollinger Bands if enabled
    const showBollinger = document.getElementById('showBollinger')?.checked;
    if (showBollinger && formattedCandles.length > 20) {
        const bb = calculateBollingerBands(formattedCandles, 20, 2);
        
        const upperBand = chart.addLineSeries({
            color: '#f59e0b',
            lineWidth: 1,
            lineStyle: 2, // Dashed
            title: 'BB Upper',
        });
        upperBand.setData(bb.upper);
        
        const middleBand = chart.addLineSeries({
            color: '#6b7280',
            lineWidth: 1,
            lineStyle: 2,
            title: 'BB Middle (SMA)',
        });
        middleBand.setData(bb.middle);
        
        const lowerBand = chart.addLineSeries({
            color: '#f59e0b',
            lineWidth: 1,
            lineStyle: 2,
            title: 'BB Lower',
        });
        lowerBand.setData(bb.lower);
    }
    
    // Auto-scale
    chart.timeScale().fitContent();
    
    // Handle resize
    window.addEventListener('resize', () => {
        chart.applyOptions({ width: container.clientWidth });
    });
    
    priceChart = chart;
}

function renderRSIChart(candles) {
    const container = document.getElementById('rsiChartContainer');
    if (!container || !window.Chart) {
        return;
    }
    
    // Destroy existing chart
    if (rsiChart) {
        try { rsiChart.destroy(); } catch(e) {}
        rsiChart = null;
    }
    
    // Calculate RSI
    const rsiValues = calculateRSI(candles.map(c => c.close), 14);
    const labels = candles.map((c, i) => {
        const date = new Date(c.time * 1000);
        return date.toLocaleDateString();
    });
    
    const ctx = container.querySelector('canvas') || document.createElement('canvas');
    if (!container.querySelector('canvas')) {
        container.innerHTML = '';
        container.appendChild(ctx);
    }
    
    rsiChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels.slice(-rsiValues.length),
            datasets: [{
                label: 'RSI(14)',
                data: rsiValues,
                borderColor: '#f59e0b',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                borderWidth: 2,
                fill: true,
            }, {
                label: 'Overbought (70)',
                data: Array(rsiValues.length).fill(70),
                borderColor: '#ef4444',
                borderDash: [5, 5],
                borderWidth: 1,
                pointRadius: 0,
            }, {
                label: 'Oversold (30)',
                data: Array(rsiValues.length).fill(30),
                borderColor: '#10b981',
                borderDash: [5, 5],
                borderWidth: 1,
                pointRadius: 0,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                }
            },
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    ticks: {
                        stepSize: 10,
                    }
                }
            }
        }
    });
}

function renderVolumeChart(candles) {
    const container = document.getElementById('volumeChartContainer');
    if (!container || !window.Chart) {
        return;
    }
    
    // Destroy existing chart
    if (volumeChart) {
        try { volumeChart.destroy(); } catch(e) {}
        volumeChart = null;
    }
    
    const labels = candles.map((c, i) => {
        const date = new Date(c.time * 1000);
        return date.toLocaleDateString();
    });
    
    const ctx = container.querySelector('canvas') || document.createElement('canvas');
    if (!container.querySelector('canvas')) {
        container.innerHTML = '';
        container.appendChild(ctx);
    }
    
    volumeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Volume',
                data: candles.map(c => c.volume),
                backgroundColor: candles.map((c, i) => 
                    i > 0 && c.close > candles[i-1].close ? 'rgba(16, 185, 129, 0.6)' : 'rgba(239, 68, 68, 0.6)'
                ),
                borderColor: candles.map((c, i) => 
                    i > 0 && c.close > candles[i-1].close ? '#10b981' : '#ef4444'
                ),
                borderWidth: 1,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                }
            }
        }
    });
}

function updateIndicatorsSummary(indicators) {
    const container = document.getElementById('indicatorsSummary');
    if (!container) return;
    
    if (!indicators || Object.keys(indicators).length === 0) {
        container.innerHTML = '<div class="empty-state">No indicators data available</div>';
        return;
    }
    
    let html = '<div class="grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">';
    
    if (indicators.price) {
        html += `<div class="card"><h3>Price</h3><div class="metric-value">${formatCurrency(indicators.price)}</div></div>`;
    }
    
    if (indicators.ema_50) {
        html += `<div class="card"><h3>EMA(50)</h3><div class="metric-value">${formatCurrency(indicators.ema_50)}</div></div>`;
    }
    
    if (indicators.rsi !== null && indicators.rsi !== undefined) {
        const rsi = parseFloat(indicators.rsi);
        const rsiClass = rsi > 70 ? 'negative' : rsi < 30 ? 'positive' : '';
        html += `<div class="card"><h3>RSI(14)</h3><div class="metric-value ${rsiClass}">${rsi.toFixed(2)}</div></div>`;
    }
    
    if (indicators.volume) {
        html += `<div class="card"><h3>Volume</h3><div class="metric-value">${formatNumber(indicators.volume)}</div></div>`;
    }
    
    if (indicators.volume_avg) {
        html += `<div class="card"><h3>Avg Volume</h3><div class="metric-value">${formatNumber(indicators.volume_avg)}</div></div>`;
    }
    
    html += '</div>';
    container.innerHTML = html;
}

// Technical indicator calculations
function calculateEMA(data, period) {
    const ema = [];
    const multiplier = 2 / (period + 1);
    
    // Start with SMA
    let sum = 0;
    for (let i = 0; i < period && i < data.length; i++) {
        sum += data[i].close;
    }
    let emaValue = sum / Math.min(period, data.length);
    
    // Calculate EMA for remaining points
    for (let i = 0; i < data.length; i++) {
        if (i < period - 1) {
            ema.push({ time: data[i].time, value: null });
        } else {
            if (i === period - 1) {
                emaValue = sum / period;
            } else {
                emaValue = (data[i].close - emaValue) * multiplier + emaValue;
            }
            ema.push({ time: data[i].time, value: emaValue });
        }
    }
    
    return ema.filter(e => e.value !== null);
}

function calculateBollingerBands(data, period, numStdDev) {
    const sma = [];
    const upper = [];
    const lower = [];
    
    for (let i = period - 1; i < data.length; i++) {
        // Calculate SMA
        let sum = 0;
        for (let j = i - period + 1; j <= i; j++) {
            sum += data[j].close;
        }
        const smaValue = sum / period;
        
        // Calculate standard deviation
        let variance = 0;
        for (let j = i - period + 1; j <= i; j++) {
            variance += Math.pow(data[j].close - smaValue, 2);
        }
        const stdDev = Math.sqrt(variance / period);
        
        sma.push({ time: data[i].time, value: smaValue });
        upper.push({ time: data[i].time, value: smaValue + (numStdDev * stdDev) });
        lower.push({ time: data[i].time, value: smaValue - (numStdDev * stdDev) });
    }
    
    return { middle: sma, upper, lower };
}

function calculateRSI(prices, period) {
    const rsi = [];
    const gains = [];
    const losses = [];
    
    // Calculate price changes
    for (let i = 1; i < prices.length; i++) {
        const change = prices[i] - prices[i - 1];
        gains.push(change > 0 ? change : 0);
        losses.push(change < 0 ? Math.abs(change) : 0);
    }
    
    // Calculate initial average gain and loss
    let avgGain = 0;
    let avgLoss = 0;
    for (let i = 0; i < period && i < gains.length; i++) {
        avgGain += gains[i];
        avgLoss += losses[i];
    }
    avgGain /= Math.min(period, gains.length);
    avgLoss /= Math.min(period, losses.length);
    
    // Calculate RSI
    for (let i = 0; i < prices.length - 1; i++) {
        if (i < period - 1) {
            rsi.push(null);
        } else {
            if (i === period - 1) {
                // First RSI calculation
            } else {
                // Smoothed averages
                avgGain = (avgGain * (period - 1) + gains[i - 1]) / period;
                avgLoss = (avgLoss * (period - 1) + losses[i - 1]) / period;
            }
            
            if (avgLoss === 0) {
                rsi.push(100);
            } else {
                const rs = avgGain / avgLoss;
                rsi.push(100 - (100 / (1 + rs)));
            }
        }
    }
    
    return rsi.filter(r => r !== null);
}

function formatNumber(value) {
    if (value >= 1e9) return (value / 1e9).toFixed(2) + 'B';
    if (value >= 1e6) return (value / 1e6).toFixed(2) + 'M';
    if (value >= 1e3) return (value / 1e3).toFixed(2) + 'K';
    return value.toFixed(2);
}

// Make updateAdvancedChart globally accessible
window.updateAdvancedChart = updateAdvancedChart;

// Advanced Orders Functions
async function updateOrdersPage() {
    try {
        await listAdvancedOrders();
    } catch (error) {
        console.error('Error updating orders page:', error);
        const container = document.getElementById('ordersList');
        if (container) {
            container.innerHTML = '<div class="error">Failed to load orders: ' + error.message + '</div>';
        }
    }
}

async function listAdvancedOrders() {
    const container = document.getElementById('ordersList');
    if (!container) return;
    
    try {
        const data = await fetchAPI('/orders');
        if (!data || !data.orders) {
            container.innerHTML = '<div class="empty-state">No orders found</div>';
            return;
        }
        
        if (data.orders.length === 0) {
            container.innerHTML = '<div class="empty-state">No active orders</div>';
            return;
        }
        
        let html = '<div class="table-wrapper"><table><thead><tr>';
        html += '<th>Type</th><th>Pair</th><th>Side</th><th>Size</th><th>Status</th><th>Created</th><th>Actions</th></tr></thead><tbody>';
        
        data.orders.forEach(order => {
            html += '<tr>';
            html += `<td><strong>${order.type || 'N/A'}</strong></td>`;
            html += `<td>${order.pair || 'N/A'}</td>`;
            html += `<td>${order.side || 'N/A'}</td>`;
            html += `<td>${parseFloat(order.size || 0).toFixed(6)}</td>`;
            html += `<td><span class="status-badge status-${(order.status || 'unknown').toLowerCase()}">${order.status || 'Unknown'}</span></td>`;
            html += `<td>${formatDate(order.created_at)}</td>`;
            html += `<td><button class="btn btn-small" onclick="viewOrderDetails('${order.id}')">View</button> <button class="btn btn-small btn-danger" onclick="cancelOrder('${order.id}')">Cancel</button></td>`;
            html += '</tr>';
        });
        
        html += '</tbody></table></div>';
        container.innerHTML = html;
    } catch (error) {
        console.error('Error listing orders:', error);
        container.innerHTML = '<div class="error">Failed to load orders: ' + error.message + '</div>';
    }
}

function showCreateOrderModal() {
    const modal = document.getElementById('createOrderModal');
    if (modal) {
        modal.style.display = 'block';
    }
}

function closeCreateOrderModal() {
    const modal = document.getElementById('createOrderModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function updateOrderForm() {
    const orderType = document.getElementById('orderTypeSelect')?.value;
    // Show/hide fields based on order type
    ['trailingStopFields', 'ocoFields', 'bracketFields', 'stopLimitFields', 'icebergFields'].forEach(id => {
        const fields = document.getElementById(id);
        if (fields) {
            fields.style.display = 'none';
        }
    });
    
    if (orderType) {
        const fieldsId = orderType.replace('_', '') + 'Fields';
        const fields = document.getElementById(fieldsId);
        if (fields) {
            fields.style.display = 'block';
        }
    }
}

async function createOrder(event) {
    if (event) event.preventDefault();
    
    try {
        const orderType = document.getElementById('orderTypeSelect')?.value;
        const pair = document.getElementById('orderPair')?.value;
        const side = document.getElementById('orderSide')?.value;
        const size = parseFloat(document.getElementById('orderSize')?.value || 0);
        
        if (!orderType || !pair || !side || !size) {
            showToast('Please fill in all required fields', 'error');
            return;
        }
        
        const orderData = {
            type: orderType,
            pair: pair,
            side: side,
            size: size
        };
        
        // Add type-specific fields
        if (orderType === 'trailing_stop') {
            orderData.trailing_percent = parseFloat(document.getElementById('trailingPercent')?.value || 0);
            orderData.initial_price = parseFloat(document.getElementById('trailingInitialPrice')?.value || 0);
        }
        // Add other order type fields as needed...
        
        const response = await fetchAPI('/orders/create', {
            method: 'POST',
            body: JSON.stringify(orderData)
        });
        
        if (response && response.order_id) {
            showToast('Order created successfully', 'success');
            closeCreateOrderModal();
            await listAdvancedOrders();
        } else {
            showToast('Failed to create order', 'error');
        }
    } catch (error) {
        console.error('Error creating order:', error);
        showToast('Error creating order: ' + error.message, 'error');
    }
}

async function cancelOrder(orderId) {
    if (!confirm('Are you sure you want to cancel this order?')) return;
    
    try {
        const response = await fetchAPI(`/orders/${orderId}`, {
            method: 'DELETE'
        });
        
        if (response) {
            showToast('Order cancelled successfully', 'success');
            await listAdvancedOrders();
        }
    } catch (error) {
        console.error('Error cancelling order:', error);
        showToast('Error cancelling order: ' + error.message, 'error');
    }
}

async function viewOrderDetails(orderId) {
    try {
        const order = await fetchAPI(`/orders/${orderId}`);
        if (order) {
            alert('Order Details:\n' + JSON.stringify(order, null, 2));
        }
    } catch (error) {
        console.error('Error fetching order details:', error);
        showToast('Error loading order details: ' + error.message, 'error');
    }
}

// Make functions globally accessible
window.showCreateOrderModal = showCreateOrderModal;
window.closeCreateOrderModal = closeCreateOrderModal;
window.updateOrderForm = updateOrderForm;
window.createOrder = createOrder;
window.cancelOrder = cancelOrder;
window.viewOrderDetails = viewOrderDetails;
window.listAdvancedOrders = listAdvancedOrders;
window.loadOrders = listAdvancedOrders;

// Grid Trading Functions
async function updateGridPage() {
    try {
        await listGridStrategies();
        await listDCAStrategies();
    } catch (error) {
        console.error('Error updating grid page:', error);
    }
}

async function listGridStrategies() {
    const container = document.getElementById('gridsList');
    if (!container) return;
    
    try {
        const data = await fetchAPI('/grid');
        if (!data || !data.strategies) {
            container.innerHTML = '<div class="empty-state">No grid strategies found</div>';
            return;
        }
        
        if (data.strategies.length === 0) {
            container.innerHTML = '<div class="empty-state">No active grid strategies</div>';
            return;
        }
        
        let html = '<div class="table-wrapper"><table><thead><tr>';
        html += '<th>Pair</th><th>Status</th><th>Grid Levels</th><th>Range</th><th>Created</th><th>Actions</th></tr></thead><tbody>';
        
        data.strategies.forEach(grid => {
            html += '<tr>';
            html += `<td><strong>${grid.pair || 'N/A'}</strong></td>`;
            html += `<td><span class="status-badge status-${(grid.status || 'unknown').toLowerCase()}">${grid.status || 'Unknown'}</span></td>`;
            html += `<td>${grid.grid_levels || 'N/A'}</td>`;
            html += `<td>${grid.lower_price || 'N/A'} - ${grid.upper_price || 'N/A'}</td>`;
            html += `<td>${formatDate(grid.created_at)}</td>`;
            html += `<td>
                <button class="btn btn-small" onclick="startGrid('${grid.id}')">Start</button>
                <button class="btn btn-small" onclick="pauseGrid('${grid.id}')">Pause</button>
                <button class="btn btn-small btn-danger" onclick="stopGrid('${grid.id}')">Stop</button>
            </td>`;
            html += '</tr>';
        });
        
        html += '</tbody></table></div>';
        container.innerHTML = html;
    } catch (error) {
        console.error('Error listing grids:', error);
        container.innerHTML = '<div class="empty-state">Failed to load grid strategies</div>';
    }
}

async function listDCAStrategies() {
    const container = document.getElementById('dcaList');
    if (!container) return;
    
    try {
        const data = await fetchAPI('/dca');
        if (!data || !data.strategies) {
            container.innerHTML = '<div class="empty-state">No DCA strategies found</div>';
            return;
        }
        
        if (data.strategies.length === 0) {
            container.innerHTML = '<div class="empty-state">No active DCA strategies</div>';
            return;
        }
        
        let html = '<div class="table-wrapper"><table><thead><tr>';
        html += '<th>Pair</th><th>Side</th><th>Status</th><th>Amount</th><th>Interval</th><th>Created</th><th>Actions</th></tr></thead><tbody>';
        
        data.strategies.forEach(dca => {
            html += '<tr>';
            html += `<td><strong>${dca.pair || 'N/A'}</strong></td>`;
            html += `<td>${dca.side || 'N/A'}</td>`;
            html += `<td><span class="status-badge status-${(dca.status || 'unknown').toLowerCase()}">${dca.status || 'Unknown'}</span></td>`;
            html += `<td>${formatCurrency(dca.amount_per_interval || 0)}</td>`;
            html += `<td>${dca.interval || 'N/A'}</td>`;
            html += `<td>${formatDate(dca.created_at)}</td>`;
            html += `<td>
                <button class="btn btn-small" onclick="startDCA('${dca.id}')">Start</button>
                <button class="btn btn-small" onclick="pauseDCA('${dca.id}')">Pause</button>
                <button class="btn btn-small btn-danger" onclick="stopDCA('${dca.id}')">Stop</button>
            </td>`;
            html += '</tr>';
        });
        
        html += '</tbody></table></div>';
        container.innerHTML = html;
    } catch (error) {
        console.error('Error listing DCA strategies:', error);
        container.innerHTML = '<div class="empty-state">Failed to load DCA strategies</div>';
    }
}

async function createGrid(event) {
    if (event) event.preventDefault();
    
    try {
        const pair = document.getElementById('gridPair')?.value;
        const lowerPrice = parseFloat(document.getElementById('gridLowerPrice')?.value || 0);
        const upperPrice = parseFloat(document.getElementById('gridUpperPrice')?.value || 0);
        const gridLevels = parseInt(document.getElementById('gridLevels')?.value || 10);
        const side = document.getElementById('gridSide')?.value || 'BOTH';
        
        if (!pair || !lowerPrice || !upperPrice || !gridLevels) {
            showToast('Please fill in all required fields', 'error');
            return;
        }
        
        const gridData = {
            pair: pair,
            lower_price: lowerPrice,
            upper_price: upperPrice,
            grid_levels: gridLevels,
            side: side
        };
        
        const response = await fetchAPI('/grid/create', {
            method: 'POST',
            body: JSON.stringify(gridData)
        });
        
        if (response && response.id) {
            showToast('Grid strategy created successfully', 'success');
            closeCreateGridModal();
            await listGridStrategies();
        } else {
            showToast('Failed to create grid strategy', 'error');
        }
    } catch (error) {
        console.error('Error creating grid:', error);
        showToast('Error creating grid: ' + error.message, 'error');
    }
}

async function createDCA(event) {
    if (event) event.preventDefault();
    
    try {
        const pair = document.getElementById('dcaPair')?.value;
        const side = document.getElementById('dcaSide')?.value;
        const amount = parseFloat(document.getElementById('dcaAmount')?.value || 0);
        const interval = document.getElementById('dcaInterval')?.value;
        const totalAmount = document.getElementById('dcaTotalAmount')?.value ? parseFloat(document.getElementById('dcaTotalAmount').value) : null;
        const endPrice = document.getElementById('dcaEndPrice')?.value ? parseFloat(document.getElementById('dcaEndPrice').value) : null;
        
        if (!pair || !side || !amount || !interval) {
            showToast('Please fill in all required fields', 'error');
            return;
        }
        
        const dcaData = {
            pair: pair,
            side: side,
            amount_per_interval: amount,
            interval: interval
        };
        
        if (totalAmount) dcaData.total_amount = totalAmount;
        if (endPrice) dcaData.end_price = endPrice;
        
        const response = await fetchAPI('/dca/create', {
            method: 'POST',
            body: JSON.stringify(dcaData)
        });
        
        if (response && response.id) {
            showToast('DCA strategy created successfully', 'success');
            closeCreateDCAModal();
            await listDCAStrategies();
        } else {
            showToast('Failed to create DCA strategy', 'error');
        }
    } catch (error) {
        console.error('Error creating DCA:', error);
        showToast('Error creating DCA: ' + error.message, 'error');
    }
}

async function startGrid(gridId) {
    try {
        await fetchAPI(`/grid/${gridId}/start`, { method: 'POST' });
        showToast('Grid strategy started', 'success');
        await listGridStrategies();
    } catch (error) {
        showToast('Error starting grid: ' + error.message, 'error');
    }
}

async function pauseGrid(gridId) {
    try {
        await fetchAPI(`/grid/${gridId}/pause`, { method: 'POST' });
        showToast('Grid strategy paused', 'success');
        await listGridStrategies();
    } catch (error) {
        showToast('Error pausing grid: ' + error.message, 'error');
    }
}

async function stopGrid(gridId) {
    if (!confirm('Are you sure you want to stop this grid strategy?')) return;
    try {
        await fetchAPI(`/grid/${gridId}/stop`, { method: 'POST' });
        showToast('Grid strategy stopped', 'success');
        await listGridStrategies();
    } catch (error) {
        showToast('Error stopping grid: ' + error.message, 'error');
    }
}

async function startDCA(dcaId) {
    try {
        await fetchAPI(`/dca/${dcaId}/start`, { method: 'POST' });
        showToast('DCA strategy started', 'success');
        await listDCAStrategies();
    } catch (error) {
        showToast('Error starting DCA: ' + error.message, 'error');
    }
}

async function pauseDCA(dcaId) {
    try {
        await fetchAPI(`/dca/${dcaId}/pause`, { method: 'POST' });
        showToast('DCA strategy paused', 'success');
        await listDCAStrategies();
    } catch (error) {
        showToast('Error pausing DCA: ' + error.message, 'error');
    }
}

async function stopDCA(dcaId) {
    if (!confirm('Are you sure you want to stop this DCA strategy?')) return;
    try {
        await fetchAPI(`/dca/${dcaId}/stop`, { method: 'POST' });
        showToast('DCA strategy stopped', 'success');
        await listDCAStrategies();
    } catch (error) {
        showToast('Error stopping DCA: ' + error.message, 'error');
    }
}

// Make functions globally accessible
window.updateGridPage = updateGridPage;
window.listGridStrategies = listGridStrategies;
window.listDCAStrategies = listDCAStrategies;
window.createGrid = createGrid;
window.createDCA = createDCA;
window.startGrid = startGrid;
window.pauseGrid = pauseGrid;
window.stopGrid = stopGrid;
window.startDCA = startDCA;
window.pauseDCA = pauseDCA;
window.stopDCA = stopDCA;
window.loadGrids = listGridStrategies;
window.loadDCAs = listDCAStrategies;

// Grid Trading & DCA Modal Functions
function showCreateGridModal() {
    const modal = document.getElementById('createGridModal');
    if (modal) {
        modal.style.display = 'block';
    }
}

function closeCreateGridModal() {
    const modal = document.getElementById('createGridModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function showCreateDCAModal() {
    const modal = document.getElementById('createDCAModal');
    if (modal) {
        modal.style.display = 'block';
    }
}

function closeCreateDCAModal() {
    const modal = document.getElementById('createDCAModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function switchGridTab(tab) {
    // Update tab buttons
    const gridTabBtn = document.getElementById('gridTabBtn');
    const dcaTabBtn = document.getElementById('dcaTabBtn');
    const gridTabContent = document.getElementById('gridTabContent');
    const dcaTabContent = document.getElementById('dcaTabContent');
    
    if (tab === 'grid') {
        if (gridTabBtn) gridTabBtn.classList.add('active');
        if (dcaTabBtn) dcaTabBtn.classList.remove('active');
        if (gridTabContent) gridTabContent.style.display = 'block';
        if (dcaTabContent) dcaTabContent.style.display = 'none';
    } else if (tab === 'dca') {
        if (gridTabBtn) gridTabBtn.classList.remove('active');
        if (dcaTabBtn) dcaTabBtn.classList.add('active');
        if (gridTabContent) gridTabContent.style.display = 'none';
        if (dcaTabContent) dcaTabContent.style.display = 'block';
    }
}

// Make functions globally accessible
window.showCreateGridModal = showCreateGridModal;
window.closeCreateGridModal = closeCreateGridModal;
window.showCreateDCAModal = showCreateDCAModal;
window.closeCreateDCAModal = closeCreateDCAModal;
window.switchGridTab = switchGridTab;

// Auto-refresh logs page
if (currentPage === 'logs') {
    setInterval(updateLogsPage, 5000);
}
