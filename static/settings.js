const API_BASE = '/api';

// Selected trading pairs
let selectedPairs = [];

// Load current settings on page load
document.addEventListener('DOMContentLoaded', async () => {
    // Initialize selected pairs display first (even if empty)
    updateSelectedPairsDisplay();
    
    await loadSettings();
    await loadTemplates();
    await loadAvailableCoins();
    await loadSystemInfo();
    loadUserInfo();
    
    // Form submission
    document.getElementById('settingsForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await saveSettings();
    });
    
    // Logs filter and search (not used on settings page, but kept for compatibility)
    // These elements don't exist on settings page, so these listeners won't be attached
});

// Load system information
async function loadSystemInfo() {
    try {
        const [statusResponse, settingsResponse] = await Promise.all([
            fetch(`${API_BASE}/status`).catch(() => null),
            fetch(`${API_BASE}/settings`).catch(() => null)
        ]);
        
        // Bot status
        const botStatusEl = document.getElementById('botStatus');
        if (botStatusEl) {
            if (statusResponse && statusResponse.ok) {
                const status = await statusResponse.json();
                botStatusEl.textContent = status.status || 'Unknown';
                botStatusEl.style.color = status.status === 'running' ? 'var(--success-green)' : 
                                         status.status === 'paused' ? 'var(--accent-gold)' : 'var(--danger-red)';
            } else {
                botStatusEl.textContent = 'Not Available';
                botStatusEl.style.color = 'var(--gray-500)';
            }
        }
        
        // Database status
        const dbStatusEl = document.getElementById('dbStatus');
        if (dbStatusEl) {
            dbStatusEl.textContent = 'Connected';
            dbStatusEl.style.color = 'var(--success-green)';
        }
        
        // API status
        const apiStatusEl = document.getElementById('apiStatus');
        if (apiStatusEl) {
            if (statusResponse && statusResponse.ok) {
                apiStatusEl.textContent = 'Connected';
                apiStatusEl.style.color = 'var(--success-green)';
            } else {
                apiStatusEl.textContent = 'Disconnected';
                apiStatusEl.style.color = 'var(--danger-red)';
            }
        }
        
        // Paper trading status
        const paperStatusEl = document.getElementById('paperTradingStatus');
        if (paperStatusEl) {
            if (settingsResponse && settingsResponse.ok) {
                const settings = await settingsResponse.json();
                paperStatusEl.textContent = settings.paper_trading ? 'Enabled' : 'Disabled';
                paperStatusEl.style.color = settings.paper_trading ? 'var(--accent-gold)' : 'var(--gray-600)';
            } else {
                paperStatusEl.textContent = 'Unknown';
            }
        }
    } catch (error) {
        console.error('Error loading system info:', error);
    }
}

// Load user information
function loadUserInfo() {
    try {
        const token = localStorage.getItem('auth_token');
        if (!token) return;
        
        // Try to decode JWT to get user info (simple base64 decode)
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            const userEmailEl = document.getElementById('userEmail');
            if (userEmailEl && payload.email) {
                userEmailEl.textContent = payload.email;
            }
        } catch (e) {
            // JWT decode failed, try to get from API
            fetch(`${API_BASE}/auth/verify`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            }).then(response => {
                if (response.ok) {
                    return response.json();
                }
            }).then(data => {
                if (data && data.email) {
                    const userEmailEl = document.getElementById('userEmail');
                    if (userEmailEl) {
                        userEmailEl.textContent = data.email;
                    }
                }
            }).catch(() => {
                // Ignore errors
            });
        }
        
        // Account created date (would need API endpoint for this)
        const accountCreatedEl = document.getElementById('accountCreated');
        if (accountCreatedEl) {
            accountCreatedEl.textContent = 'N/A';
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

// Export settings to JSON file
function exportSettings() {
    try {
        const formData = new FormData(document.getElementById('settingsForm'));
        const settings = {};
        
        for (const [key, value] of formData.entries()) {
            if (key === 'trading_pairs') {
                settings[key] = selectedPairs;
            } else {
                settings[key] = value;
            }
        }
        
        const settingsJson = JSON.stringify(settings, null, 2);
        const blob = new Blob([settingsJson], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `trading-bot-settings-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showAlert('Settings exported successfully!', 'success');
    } catch (error) {
        console.error('Error exporting settings:', error);
        showAlert('Failed to export settings', 'error');
    }
}

// Import settings from JSON file
function importSettings() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        try {
            const text = await file.text();
            const settings = JSON.parse(text);
            
            if (!confirm('Import these settings? This will overwrite your current settings.')) {
                return;
            }
            
            // Populate form fields
            for (const [key, value] of Object.entries(settings)) {
                const field = document.getElementById(key);
                if (field) {
                    if (field.type === 'checkbox') {
                        field.checked = value;
                    } else {
                        field.value = value;
                    }
                }
            }
            
            // Handle trading pairs
            if (settings.trading_pairs && Array.isArray(settings.trading_pairs)) {
                selectedPairs = settings.trading_pairs;
                updateSelectedPairsDisplay();
                updateTradingPairsInput();
            }
            
            showAlert('Settings imported successfully! Click "Save Settings" to apply.', 'success');
        } catch (error) {
            console.error('Error importing settings:', error);
            showAlert('Failed to import settings. Please check the file format.', 'error');
        }
    };
    input.click();
}

async function loadSettings() {
    try {
        const response = await fetch(`${API_BASE}/settings`);
        if (!response.ok) throw new Error('Failed to load settings');
        
        const settings = await response.json();
        
        // Populate form fields
        for (const [key, value] of Object.entries(settings)) {
            const field = document.getElementById(key);
            if (field) {
                if (field.type === 'checkbox') {
                    field.checked = value;
                } else {
                    field.value = value;
                }
            }
        }
        
        // Handle trading pairs array
        if (settings.trading_pairs && Array.isArray(settings.trading_pairs)) {
            selectedPairs = settings.trading_pairs;
            updateSelectedPairsDisplay();
            updateTradingPairsInput();
        } else if (settings.trading_pairs && typeof settings.trading_pairs === 'string') {
            selectedPairs = settings.trading_pairs.split(',').map(p => p.trim()).filter(p => p);
            updateSelectedPairsDisplay();
            updateTradingPairsInput();
        }
        
    } catch (error) {
        console.error('Error loading settings:', error);
        showAlert('Failed to load settings. Using defaults.', 'error');
    }
}

async function saveSettings() {
    try {
        const formData = new FormData(document.getElementById('settingsForm'));
        const settings = {};
        
        // ALWAYS set trading_pairs from selectedPairs array (this is the source of truth)
        if (selectedPairs.length > 0) {
            settings.trading_pairs = selectedPairs;
            console.log(`💾 SAVING SETTINGS - sending ${selectedPairs.length} trading pairs:`, selectedPairs);
        } else {
            console.warn('⚠️ WARNING: No trading pairs selected!');
            settings.trading_pairs = []; // Explicitly set empty array
        }
        
        // Convert form data to object
        for (const [key, value] of formData.entries()) {
            // Skip trading_pairs from form - we're using selectedPairs array instead
            if (key === 'trading_pairs') {
                continue; // Already set above from selectedPairs
            } else if (key === 'paper_trading' || key === 'use_real_market_data') {
                settings[key] = true; // Checkboxes are only included if checked
            } else {
                // Convert numbers
                const numValue = parseFloat(value);
                settings[key] = isNaN(numValue) ? value : numValue;
            }
        }
        
        // Handle unchecked checkboxes
        if (!formData.has('paper_trading')) settings.paper_trading = false;
        if (!formData.has('use_real_market_data')) settings.use_real_market_data = false;
        
        // Validate ranges
        if (!validateSettings(settings)) {
            return;
        }
        
        console.log(`💾 SAVING SETTINGS - Final settings object:`, {
            ...settings,
            trading_pairs_count: settings.trading_pairs ? settings.trading_pairs.length : 0,
            trading_pairs: settings.trading_pairs
        });
        
        const response = await fetch(`${API_BASE}/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to save settings');
        }
        
        const result = await response.json();
        let message = result.message || 'Settings saved successfully!';
        
        // If trading pairs were updated, inform user
        if (result.trading_pairs_updated) {
            message += ' New trading pairs will appear on Market Conditions page shortly. Please refresh the Market Conditions page in 10-15 seconds.';
        }
        
        showAlert(message, 'success');
        
        // If trading pairs were updated, refresh settings display after a short delay
        if (result.trading_pairs_updated) {
            setTimeout(async () => {
                await loadSettings();
            }, 2000);
        }
        
    } catch (error) {
        console.error('Error saving settings:', error);
        showAlert('Error: ' + error.message, 'error');
    }
}

function validateSettings(settings) {
    // Validate RSI ranges
    if (settings.rsi_long_min >= settings.rsi_long_max) {
        showAlert('RSI Long Min must be less than RSI Long Max', 'error');
        return false;
    }
    
    if (settings.rsi_short_min >= settings.rsi_short_max) {
        showAlert('RSI Short Min must be less than RSI Short Max', 'error');
        return false;
    }
    
    // Validate take profit/stop loss
    if (settings.take_profit_min >= settings.take_profit_max) {
        showAlert('Take Profit Min must be less than Take Profit Max', 'error');
        return false;
    }
    
    if (settings.stop_loss_min >= settings.stop_loss_max) {
        showAlert('Stop Loss Min must be less than Stop Loss Max', 'error');
        return false;
    }
    
    // Validate trading pairs format
    if (settings.trading_pairs && settings.trading_pairs.length === 0) {
        showAlert('At least one trading pair is required', 'error');
        return false;
    }
    
    return true;
}

function resetToDefaults() {
    if (!confirm('Reset all settings to default values?')) return;
    
    // Default values
    document.getElementById('ema_period').value = 50;
    document.getElementById('rsi_period').value = 14;
    document.getElementById('volume_period').value = 20;
    document.getElementById('volume_multiplier').value = 1.5;
    document.getElementById('min_confidence').value = 70;
    document.getElementById('loop_interval').value = 5;
    
    document.getElementById('rsi_long_min').value = 55;
    document.getElementById('rsi_long_max').value = 70;
    document.getElementById('rsi_short_min').value = 30;
    document.getElementById('rsi_short_max').value = 45;
    
    document.getElementById('risk_per_trade').value = 0.25;
    document.getElementById('max_positions').value = 2;
    document.getElementById('daily_loss_limit').value = 2000;
    document.getElementById('max_position_size').value = 50;
    document.getElementById('position_timeout').value = 10;
    
    document.getElementById('take_profit_min').value = 0.15;
    document.getElementById('take_profit_max').value = 0.40;
    document.getElementById('stop_loss_min').value = 0.10;
    document.getElementById('stop_loss_max').value = 0.50;
    
    selectedPairs = ['BTC-USD', 'ETH-USD'];
    updateSelectedPairsDisplay();
    updateTradingPairsInput();
    document.getElementById('paper_trading').checked = true;
    document.getElementById('use_real_market_data').checked = true;
    
    showAlert('Settings reset to defaults. Click Save to apply.', 'success');
}

async function restartBot() {
    try {
        // Stop bot first
        await fetch(`${API_BASE}/stop`, { method: 'POST' });
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Start bot
        const response = await fetch(`${API_BASE}/start`, { method: 'POST' });
        const result = await response.json();
        
        showAlert('Bot restarted successfully!', 'success');
    } catch (error) {
        console.error('Error restarting bot:', error);
        showAlert('Error restarting bot: ' + error.message, 'error');
    }
}

function showAlert(message, type) {
    const alert = document.getElementById('alert');
    alert.textContent = message;
    alert.className = `alert alert-${type}`;
    alert.style.display = 'block';
    
    setTimeout(() => {
        alert.style.display = 'none';
    }, 5000);
}

// Coin Selection Functions
async function loadAvailableCoins() {
    try {
        const response = await fetch(`${API_BASE}/available-coins`);
        const data = await response.json();
        
        const selector = document.getElementById('coinSelector');
        if (selector && data.available_pairs) {
            selector.innerHTML = '<option value="">Select a coin to add...</option>';
            data.available_pairs.forEach(pair => {
                const option = document.createElement('option');
                option.value = pair;
                option.textContent = pair;
                selector.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading available coins:', error);
    }
}

function addCoin() {
    const selector = document.getElementById('coinSelector');
    if (!selector) {
        console.error('coinSelector not found');
        alert('Error: Coin selector not found. Please refresh the page.');
        return;
    }
    
    const pair = selector.value;
    
    if (!pair) {
        alert('Please select a coin first');
        return;
    }
    
    if (selectedPairs.includes(pair)) {
        alert('Coin already added');
        return;
    }
    
    selectedPairs.push(pair);
    console.log('Added coin:', pair, 'Total pairs:', selectedPairs); // Debug log
    updateSelectedPairsDisplay();
    updateTradingPairsInput();
    
    // Show success feedback
    const container = document.getElementById('selectedPairs');
    if (container) {
        container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

function removeCoin(pair) {
    selectedPairs = selectedPairs.filter(p => p !== pair);
    updateSelectedPairsDisplay();
    updateTradingPairsInput();
}

function updateSelectedPairsDisplay() {
    const container = document.getElementById('selectedPairs');
    if (!container) {
        console.error('selectedPairs container not found');
        return;
    }
    
    console.log('Updating selected pairs display:', selectedPairs); // Debug log
    
    if (selectedPairs.length === 0) {
        container.innerHTML = '<div style="padding: 1rem; background: #f3f4f6; border-radius: 8px; color: #6b7280;">No coins selected. Select a coin and click "+ Add Coin" to add it.</div>';
        return;
    }
    
    let html = '<div style="display: flex; flex-wrap: wrap; gap: 0.5rem; min-height: 2rem;">';
    selectedPairs.forEach(pair => {
        html += `<span style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background: #3b82f6; color: white; border-radius: 20px; font-weight: 500;">
            ${pair}
            <button type="button" onclick="removeCoin('${pair}')" style="background: rgba(255,255,255,0.3); border: none; color: white; border-radius: 50%; width: 20px; height: 20px; cursor: pointer; font-size: 0.9em; line-height: 1; padding: 0; display: flex; align-items: center; justify-content: center;">×</button>
        </span>`;
    });
    html += '</div>';
    container.innerHTML = html;
    
    // Also clear the selector dropdown
    const selector = document.getElementById('coinSelector');
    if (selector) {
        selector.value = '';
    }
}

function updateTradingPairsInput() {
    document.getElementById('trading_pairs').value = selectedPairs.join(', ');
}

// Template Functions
async function loadTemplates() {
    try {
        const response = await fetch(`${API_BASE}/settings/templates/list`);
        const data = await response.json();
        
        const selector = document.getElementById('templateSelector');
        if (selector && data.templates) {
            selector.innerHTML = '<option value="">Select a template to load...</option>';
            data.templates.forEach(name => {
                const option = document.createElement('option');
                option.value = name;
                option.textContent = name;
                selector.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading templates:', error);
    }
}

async function saveTemplate() {
    const name = document.getElementById('templateName').value.trim();
    if (!name) {
        alert('Please enter a template name');
        return;
    }
    
    // Get current settings
    const formData = new FormData(document.getElementById('settingsForm'));
    const settings = {};
    
    for (const [key, value] of formData.entries()) {
        if (key === 'trading_pairs') {
            settings[key] = selectedPairs.length > 0 ? selectedPairs : value.split(',').map(p => p.trim()).filter(p => p);
        } else if (key === 'paper_trading' || key === 'use_real_market_data') {
            settings[key] = true;
        } else {
            const numValue = parseFloat(value);
            settings[key] = isNaN(numValue) ? value : numValue;
        }
    }
    
    if (!formData.has('paper_trading')) settings.paper_trading = false;
    if (!formData.has('use_real_market_data')) settings.use_real_market_data = false;
    
    try {
        const response = await fetch(`${API_BASE}/settings/templates`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, settings })
        });
        
        const result = await response.json();
        if (response.ok) {
            showAlert(result.message || 'Template saved successfully!', 'success');
            document.getElementById('templateName').value = '';
            await loadTemplates();
        } else {
            showAlert('Error: ' + (result.error || 'Failed to save template'), 'error');
        }
    } catch (error) {
        showAlert('Error saving template: ' + error.message, 'error');
    }
}

async function loadTemplate() {
    const name = document.getElementById('templateSelector').value;
    if (!name) {
        alert('Please select a template');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/settings/templates?name=${encodeURIComponent(name)}`);
        if (!response.ok) throw new Error('Failed to load template');
        
        const data = await response.json();
        const template = data.templates?.find(t => t.name === name);
        
        if (!template || !template.data) {
            showAlert('Template not found', 'error');
            return;
        }
        
        // Load template settings into form
        const settings = template.data;
        
        // Update form fields
        for (const [key, value] of Object.entries(settings)) {
            const field = document.getElementById(key);
            if (field) {
                if (field.type === 'checkbox') {
                    field.checked = value;
                } else if (key === 'trading_pairs') {
                    selectedPairs = Array.isArray(value) ? value : (value ? value.split(',').map(p => p.trim()).filter(p => p) : []);
                    updateSelectedPairsDisplay();
                    updateTradingPairsInput();
                } else {
                    field.value = value;
                }
            }
        }
        
        showAlert(`Template "${name}" loaded successfully!`, 'success');
    } catch (error) {
        showAlert('Error loading template: ' + error.message, 'error');
    }
}

async function deleteTemplate() {
    const name = document.getElementById('templateSelector').value;
    if (!name) {
        alert('Please select a template to delete');
        return;
    }
    
    if (!confirm(`Delete template "${name}"?`)) return;
    
    try {
        const response = await fetch(`${API_BASE}/settings/templates/${encodeURIComponent(name)}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        if (response.ok) {
            showAlert(result.message || 'Template deleted successfully!', 'success');
            document.getElementById('templateSelector').value = '';
            await loadTemplates();
        } else {
            showAlert('Error: ' + (result.error || 'Failed to delete template'), 'error');
        }
    } catch (error) {
        showAlert('Error deleting template: ' + error.message, 'error');
    }
}
