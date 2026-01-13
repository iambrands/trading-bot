/**
 * Trade Journal Functions
 * Handles trade journaling, notes, tags, and analytics
 */

// Common tag suggestions
const COMMON_TAGS = [
    'good-setup',
    'bad-setup',
    'emotions',
    'discipline',
    'mistake',
    'fomo',
    'revenge',
    'patience',
    'breakout',
    'reversal',
    'followed-plan',
    'deviated-plan'
];

let allJournalTrades = [];
let tagStatistics = {};

// Load journal trades
async function loadJournalTrades() {
    const listContainer = document.getElementById('journalTradesList');
    if (!listContainer) return;

    try {
        listContainer.innerHTML = '<div class="loading">Loading trades...</div>';
        
        // Get all trades
        const trades = await fetchAPI('/trades?limit=200');
        if (!trades || !trades.trades) {
            listContainer.innerHTML = '<p style="text-align: center; color: var(--gray-500);">No trades found.</p>';
            return;
        }

        allJournalTrades = trades.trades || [];
        
        // Apply filters
        const filteredTrades = applyJournalFilters(allJournalTrades);
        
        // Populate tag filter dropdown
        populateTagFilter();
        populatePairFilter();
        
        // Display trades
        displayJournalTrades(filteredTrades);
        
    } catch (error) {
        console.error('Error loading journal trades:', error);
        listContainer.innerHTML = '<p style="color: var(--danger-red);">Error loading trades. Please try again.</p>';
    }
}

function applyJournalFilters(trades) {
    const searchTerm = (document.getElementById('journalSearch')?.value || '').toLowerCase();
    const tagFilter = document.getElementById('journalTagFilter')?.value || '';
    const pairFilter = document.getElementById('journalPairFilter')?.value || '';
    const outcomeFilter = document.getElementById('journalOutcomeFilter')?.value || '';

    return trades.filter(trade => {
        // Search filter (notes)
        if (searchTerm) {
            const notes = (trade.notes || '').toLowerCase();
            if (!notes.includes(searchTerm)) {
                return false;
            }
        }

        // Tag filter
        if (tagFilter) {
            const tags = trade.tags || [];
            if (!tags.includes(tagFilter)) {
                return false;
            }
        }

        // Pair filter
        if (pairFilter && trade.pair !== pairFilter) {
            return false;
        }

        // Outcome filter
        if (outcomeFilter) {
            const pnl = parseFloat(trade.pnl || 0);
            if (outcomeFilter === 'win' && pnl <= 0) {
                return false;
            }
            if (outcomeFilter === 'loss' && pnl >= 0) {
                return false;
            }
        }

        return true;
    });
}

function populateTagFilter() {
    const tagFilter = document.getElementById('journalTagFilter');
    if (!tagFilter) return;

    // Collect all unique tags from trades
    const allTags = new Set();
    allJournalTrades.forEach(trade => {
        if (trade.tags && Array.isArray(trade.tags)) {
            trade.tags.forEach(tag => allTags.add(tag));
        }
    });

    // Clear and populate
    tagFilter.innerHTML = '<option value="">All Tags</option>';
    Array.from(allTags).sort().forEach(tag => {
        const option = document.createElement('option');
        option.value = tag;
        option.textContent = tag;
        tagFilter.appendChild(option);
    });
}

function populatePairFilter() {
    const pairFilter = document.getElementById('journalPairFilter');
    if (!pairFilter) return;

    // Collect all unique pairs
    const allPairs = new Set();
    allJournalTrades.forEach(trade => {
        if (trade.pair) {
            allPairs.add(trade.pair);
        }
    });

    // Clear and populate
    pairFilter.innerHTML = '<option value="">All Pairs</option>';
    Array.from(allPairs).sort().forEach(pair => {
        const option = document.createElement('option');
        option.value = pair;
        option.textContent = pair;
        pairFilter.appendChild(option);
    });
}

function displayJournalTrades(trades) {
    const listContainer = document.getElementById('journalTradesList');
    if (!listContainer) return;

    if (trades.length === 0) {
        listContainer.innerHTML = '<p style="text-align: center; color: var(--gray-500); padding: 2rem;">No trades match your filters.</p>';
        return;
    }

    listContainer.innerHTML = trades.map(trade => {
        const pnl = parseFloat(trade.pnl || 0);
        const pnlPct = parseFloat(trade.pnl_pct || 0);
        const isWin = pnl > 0;
        const exitTime = trade.exit_time ? new Date(trade.exit_time).toLocaleString() : 'Open';
        const tags = trade.tags || [];
        const notes = trade.notes || '';

        return `
            <div class="journal-trade-card" data-trade-id="${trade.id}">
                <div class="journal-trade-header">
                    <div class="journal-trade-info">
                        <h4>${escapeHtml(trade.pair)} ${escapeHtml(trade.side)}</h4>
                        <span class="journal-trade-date">${exitTime}</span>
                    </div>
                    <div class="journal-trade-pnl ${isWin ? 'pnl-positive' : 'pnl-negative'}">
                        ${isWin ? '+' : ''}$${pnl.toFixed(2)} (${isWin ? '+' : ''}${pnlPct.toFixed(2)}%)
                    </div>
                </div>
                <div class="journal-trade-details">
                    <div class="journal-detail-row">
                        <span><strong>Entry:</strong> $${parseFloat(trade.entry_price).toFixed(2)}</span>
                        <span><strong>Exit:</strong> $${trade.exit_price ? parseFloat(trade.exit_price).toFixed(2) : 'N/A'}</span>
                        <span><strong>Size:</strong> ${parseFloat(trade.size).toFixed(4)}</span>
                    </div>
                    ${trade.exit_reason ? `<div class="journal-exit-reason">Exit: ${escapeHtml(trade.exit_reason)}</div>` : ''}
                </div>
                <div class="journal-tags-section">
                    <div class="journal-tags-display">
                        ${tags.map(tag => `<span class="journal-tag">${escapeHtml(tag)}</span>`).join('')}
                    </div>
                    <button class="btn-secondary btn-sm" onclick="editTradeJournal(${trade.id})">Edit</button>
                </div>
                ${notes ? `<div class="journal-notes-preview">${escapeHtml(notes)}</div>` : ''}
            </div>
        `;
    }).join('');
}

async function editTradeJournal(tradeId) {
    try {
        // Get trade details
        const trade = await fetchAPI(`/api/trades/${tradeId}`);
        if (!trade) {
            alert('Trade not found');
            return;
        }

        // Create/edit modal
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.id = 'journalEditModal';
        modal.style.display = 'flex';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 600px;">
                <div class="modal-header">
                    <h2>Edit Trade Journal</h2>
                    <button class="modal-close" onclick="closeJournalModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>Trade: ${escapeHtml(trade.pair)} ${escapeHtml(trade.side)}</label>
                        <div style="color: var(--gray-600); font-size: 0.875rem;">
                            Entry: $${parseFloat(trade.entry_price).toFixed(2)} | 
                            Exit: ${trade.exit_price ? '$' + parseFloat(trade.exit_price).toFixed(2) : 'N/A'} | 
                            P&L: $${parseFloat(trade.pnl || 0).toFixed(2)}
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Tags</label>
                        <div id="journalTagsInput" style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.5rem;">
                            ${(trade.tags || []).map(tag => `
                                <span class="journal-tag journal-tag-editable" data-tag="${escapeHtml(tag)}">
                                    ${escapeHtml(tag)}
                                    <button onclick="removeTag('${escapeHtml(tag)}')" style="margin-left: 0.5rem; background: none; border: none; cursor: pointer; color: var(--gray-600);">×</button>
                                </span>
                            `).join('')}
                        </div>
                        <div style="display: flex; gap: 0.5rem;">
                            <select id="journalTagSelect" class="form-input" style="flex: 1;">
                                <option value="">Add a tag...</option>
                                ${COMMON_TAGS.filter(tag => !(trade.tags || []).includes(tag)).map(tag => 
                                    `<option value="${escapeHtml(tag)}">${escapeHtml(tag)}</option>`
                                ).join('')}
                            </select>
                            <input type="text" id="journalCustomTag" placeholder="Custom tag..." class="form-input" style="flex: 1;">
                            <button class="btn-secondary" onclick="addTag()">Add</button>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Notes</label>
                        <textarea id="journalNotesInput" class="form-input" rows="6" placeholder="Add your thoughts about this trade...">${escapeHtml(trade.notes || '')}</textarea>
                        <small class="form-help">What did you learn? What would you do differently?</small>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="closeJournalModal()">Cancel</button>
                    <button class="btn-primary" onclick="saveTradeJournal(${tradeId})">Save</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        
        // Store current tags for editing
        window.currentJournalTags = [...(trade.tags || [])];
        window.currentJournalTradeId = tradeId;

        // Tag selection handler
        document.getElementById('journalTagSelect').addEventListener('change', function() {
            if (this.value) {
                addTagToCurrent(this.value);
                this.value = '';
            }
        });

        // Enter key on custom tag
        document.getElementById('journalCustomTag').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                if (this.value.trim()) {
                    addTagToCurrent(this.value.trim());
                    this.value = '';
                }
            }
        });

    } catch (error) {
        console.error('Error loading trade for editing:', error);
        alert('Error loading trade details');
    }
}

function addTagToCurrent(tag) {
    if (!tag || !tag.trim()) return;
    tag = tag.trim().toLowerCase().replace(/\s+/g, '-');
    
    if (window.currentJournalTags.includes(tag)) {
        return; // Already added
    }
    
    window.currentJournalTags.push(tag);
    updateTagsDisplay();
}

function removeTag(tag) {
    window.currentJournalTags = window.currentJournalTags.filter(t => t !== tag);
    updateTagsDisplay();
}

function updateTagsDisplay() {
    const tagsInput = document.getElementById('journalTagsInput');
    if (!tagsInput) return;
    
    tagsInput.innerHTML = window.currentJournalTags.map(tag => `
        <span class="journal-tag journal-tag-editable" data-tag="${escapeHtml(tag)}">
            ${escapeHtml(tag)}
            <button onclick="removeTag('${escapeHtml(tag)}')" style="margin-left: 0.5rem; background: none; border: none; cursor: pointer; color: var(--gray-600);">×</button>
        </span>
    `).join('');
    
    // Update tag select options
    const tagSelect = document.getElementById('journalTagSelect');
    if (tagSelect) {
        tagSelect.innerHTML = '<option value="">Add a tag...</option>' +
            COMMON_TAGS.filter(tag => !window.currentJournalTags.includes(tag)).map(tag => 
                `<option value="${escapeHtml(tag)}">${escapeHtml(tag)}</option>`
            ).join('');
    }
}

function addTag() {
    const customTagInput = document.getElementById('journalCustomTag');
    if (customTagInput && customTagInput.value.trim()) {
        addTagToCurrent(customTagInput.value.trim());
        customTagInput.value = '';
    }
}

async function saveTradeJournal(tradeId) {
    const notes = document.getElementById('journalNotesInput')?.value || '';
    const tags = window.currentJournalTags || [];

    try {
        const token = localStorage.getItem('auth_token');
        if (!token) {
            alert('Not authenticated');
            return;
        }

        const response = await fetch(`/api/trades/${tradeId}/journal`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ notes, tags })
        });

        if (response.ok) {
            closeJournalModal();
            loadJournalTrades();
            loadTagStatistics();
            // Also refresh trade history if on that page
            if (typeof updateTradesPage === 'function') {
                updateTradesPage();
            }
            showToast('Journal updated successfully', 'success');
        } else {
            const error = await response.json();
            alert('Error saving journal: ' + (error.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error saving journal:', error);
        alert('Error saving journal. Please try again.');
    }
}

function closeJournalModal() {
    const modal = document.getElementById('journalEditModal');
    if (modal) {
        modal.remove();
    }
    window.currentJournalTags = [];
    window.currentJournalTradeId = null;
}

async function loadTagStatistics() {
    const statsContainer = document.getElementById('tagStatistics');
    if (!statsContainer) return;

    try {
        const analytics = await fetchAPI('/journal/analytics');
        if (!analytics || !analytics.tag_statistics) {
            statsContainer.innerHTML = '<p style="color: var(--gray-500);">No tag statistics available yet. Add tags to your trades to see insights.</p>';
            return;
        }

        tagStatistics = analytics.tag_statistics;
        
        const stats = Object.entries(tagStatistics).sort((a, b) => b[1].count - a[1].count);
        
        if (stats.length === 0) {
            statsContainer.innerHTML = '<p style="color: var(--gray-500);">No tags found. Add tags to your trades to see statistics.</p>';
            return;
        }

        statsContainer.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem;">
                ${stats.map(([tag, data]) => `
                    <div class="tag-stat-card">
                        <div class="tag-stat-header">
                            <span class="journal-tag">${escapeHtml(tag)}</span>
                            <span class="tag-stat-count">${data.count} trades</span>
                        </div>
                        <div class="tag-stat-metrics">
                            <div class="tag-stat-metric">
                                <span class="metric-label">Win Rate:</span>
                                <span class="metric-value ${data.win_rate >= 50 ? 'positive' : 'negative'}">
                                    ${data.win_rate.toFixed(1)}%
                                </span>
                            </div>
                            <div class="tag-stat-metric">
                                <span class="metric-label">Avg P&L:</span>
                                <span class="metric-value ${data.avg_pnl_pct >= 0 ? 'positive' : 'negative'}">
                                    ${data.avg_pnl_pct >= 0 ? '+' : ''}${data.avg_pnl_pct.toFixed(2)}%
                                </span>
                            </div>
                            <div class="tag-stat-metric">
                                <span class="metric-label">Total P&L:</span>
                                <span class="metric-value ${data.total_pnl >= 0 ? 'positive' : 'negative'}">
                                    $${data.total_pnl >= 0 ? '+' : ''}${data.total_pnl.toFixed(2)}
                                </span>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    } catch (error) {
        console.error('Error loading tag statistics:', error);
        statsContainer.innerHTML = '<p style="color: var(--danger-red);">Error loading statistics.</p>';
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Make functions globally accessible
window.loadJournalTrades = loadJournalTrades;
window.editTradeJournal = editTradeJournal;
window.saveTradeJournal = saveTradeJournal;
window.closeJournalModal = closeJournalModal;
window.removeTag = removeTag;
window.addTag = addTag;

// Initialize filters
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('journalSearch');
    const tagFilter = document.getElementById('journalTagFilter');
    const pairFilter = document.getElementById('journalPairFilter');
    const outcomeFilter = document.getElementById('journalOutcomeFilter');
    
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            const filtered = applyJournalFilters(allJournalTrades);
            displayJournalTrades(filtered);
        });
    }
    
    if (tagFilter) {
        tagFilter.addEventListener('change', () => {
            const filtered = applyJournalFilters(allJournalTrades);
            displayJournalTrades(filtered);
        });
    }
    
    if (pairFilter) {
        pairFilter.addEventListener('change', () => {
            const filtered = applyJournalFilters(allJournalTrades);
            displayJournalTrades(filtered);
        });
    }
    
    if (outcomeFilter) {
        outcomeFilter.addEventListener('change', () => {
            const filtered = applyJournalFilters(allJournalTrades);
            displayJournalTrades(filtered);
        });
    }
});

