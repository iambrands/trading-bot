// Onboarding Modal System
let onboardingStep = 0;
let onboardingData = {
    completed: false,
    step: 0,
    skipped: false
};

// Onboarding steps
const onboardingSteps = [
    {
        title: "Welcome to TradePilot! 🚀",
        content: `
            <p>Let's get you started with TradePilot. This quick tour will help you understand the key features.</p>
            <p><strong>What you'll learn:</strong></p>
            <ul style="text-align: left; display: inline-block; margin-top: 1rem;">
                <li>How to navigate the dashboard</li>
                <li>How to configure your trading strategy</li>
                <li>How to monitor your bot's performance</li>
                <li>How to manage risk settings</li>
            </ul>
            <p style="margin-top: 1.5rem;"><strong>This will only take 2-3 minutes!</strong></p>
        `,
        target: null,
        position: 'center'
    },
    {
        title: "Dashboard Overview 📊",
        content: `
            <p>The <strong>Overview</strong> page is your main control center:</p>
            <ul style="text-align: left; display: inline-block; margin-top: 1rem;">
                <li><strong>Status Badge</strong> - Shows if bot is RUNNING, PAUSED, or STOPPED</li>
                <li><strong>Quick Stats</strong> - Account balance, P&L, positions count</li>
                <li><strong>Control Buttons</strong> - Start, Pause, Stop, Kill Switch</li>
                <li><strong>Recent Activity</strong> - Latest trades and positions</li>
            </ul>
            <p style="margin-top: 1rem;"><strong>Tip:</strong> Always check the bot status before starting!</p>
        `,
        target: '.page-title',
        position: 'bottom'
    },
    {
        title: "Navigation Menu 📱",
        content: `
            <p>The left sidebar gives you access to all features:</p>
            <ul style="text-align: left; display: inline-block; margin-top: 1rem;">
                <li><strong>Overview</strong> - Main dashboard</li>
                <li><strong>Market Conditions</strong> - See why trades trigger or don't</li>
                <li><strong>Positions</strong> - Active trades</li>
                <li><strong>Trade History</strong> - All past trades</li>
                <li><strong>Performance</strong> - Analytics and charts</li>
                <li><strong>Settings</strong> - Configure your bot</li>
                <li><strong>Help</strong> - FAQs and guides</li>
            </ul>
            <p style="margin-top: 1rem;"><strong>Click any menu item to navigate!</strong></p>
        `,
        target: '.sidebar',
        position: 'right'
    },
    {
        title: "Market Conditions 🔍",
        content: `
            <p>The <strong>Market Conditions</strong> page shows you exactly why trades are or aren't happening:</p>
            <ul style="text-align: left; display: inline-block; margin-top: 1rem;">
                <li>Real-time price, EMA, RSI, and volume data</li>
                <li>LONG and SHORT signal conditions</li>
                <li>Confidence scores for each signal</li>
                <li>Blockers preventing trades</li>
                <li>AI-powered market analysis</li>
            </ul>
            <p style="margin-top: 1rem;"><strong>Use this page to understand bot behavior!</strong></p>
        `,
        target: null,
        position: 'center'
    },
    {
        title: "Configure Your Settings ⚙️",
        content: `
            <p><strong>Before you start trading, configure your settings:</strong></p>
            <ol style="text-align: left; display: inline-block; margin-top: 1rem;">
                <li>Go to <strong>Settings</strong> page</li>
                <li>Review and adjust:
                    <ul>
                        <li>Strategy parameters (EMA, RSI, Volume)</li>
                        <li>Risk management (risk per trade, loss limits)</li>
                        <li>Trading pairs</li>
                        <li>Trading mode (paper vs live)</li>
                    </ul>
                </li>
                <li>Save your settings</li>
                <li>Apply & Restart Bot to activate changes</li>
            </ol>
            <p style="margin-top: 1rem;"><strong>Start with paper trading mode for safety!</strong></p>
        `,
        target: null,
        position: 'center'
    },
    {
        title: "Risk Management 🛡️",
        content: `
            <p><strong>Important safety features to configure:</strong></p>
            <ul style="text-align: left; display: inline-block; margin-top: 1rem;">
                <li><strong>Risk Per Trade</strong> - How much to risk per trade (default: 0.25%)</li>
                <li><strong>Daily Loss Limit</strong> - Auto-stop at this loss (default: $2,000)</li>
                <li><strong>Max Positions</strong> - Limit simultaneous trades (default: 2)</li>
                <li><strong>Position Timeout</strong> - Force close after X minutes (default: 10)</li>
                <li><strong>Emergency Kill Switch</strong> - Instant stop button</li>
            </ul>
            <p style="margin-top: 1rem;"><strong>Always set appropriate risk limits before trading!</strong></p>
        `,
        target: null,
        position: 'center'
    },
    {
        title: "Monitor Performance 📈",
        content: `
            <p><strong>Track your bot's performance:</strong></p>
            <ul style="text-align: left; display: inline-block; margin-top: 1rem;">
                <li><strong>Performance Page</strong> - Win rate, profit factor, Sharpe ratio</li>
                <li><strong>Positions Page</strong> - Active trades with real-time P&L</li>
                <li><strong>Trade History</strong> - Complete audit trail</li>
                <li><strong>Charts</strong> - Visual performance metrics</li>
                <li><strong>Portfolio</strong> - Asset allocation and analytics</li>
            </ul>
            <p style="margin-top: 1rem;"><strong>Regular monitoring helps optimize your strategy!</strong></p>
        `,
        target: null,
        position: 'center'
    },
    {
        title: "You're All Set! 🎉",
        content: `
            <p><strong>Congratulations! You're ready to start trading.</strong></p>
            <p>Here's your checklist:</p>
            <ol style="text-align: left; display: inline-block; margin-top: 1rem;">
                <li>✅ Review your settings</li>
                <li>✅ Set appropriate risk limits</li>
                <li>✅ Start in paper trading mode</li>
                <li>✅ Monitor the Market Conditions page</li>
                <li>✅ Watch your first trades execute</li>
                <li>✅ Review performance regularly</li>
            </ol>
            <p style="margin-top: 1.5rem;"><strong>Need help? Check the Help & FAQs page anytime!</strong></p>
            <p><strong>Good luck and happy trading! 🚀</strong></p>
        `,
        target: null,
        position: 'center'
    }
];

// Initialize onboarding
function initOnboarding() {
    // Check if user has already completed onboarding
    const onboardingStatus = localStorage.getItem('onboarding_completed');
    if (onboardingStatus === 'true') {
        return; // Don't show onboarding if already completed
    }
    
    // Check if user is new (first login or no trades yet)
    checkIfNewUser().then(isNew => {
        if (isNew) {
            // Wait a bit for page to fully load
            setTimeout(() => {
                showOnboardingModal();
            }, 1000);
        }
    });
}

// Check if user is new
async function checkIfNewUser() {
    try {
        // Check if user has any trades
        const token = localStorage.getItem('auth_token');
        if (!token) return false;
        
        const response = await fetch('/api/trades?limit=1', {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            // If no trades, consider user as new
            return !data.trades || data.trades.length === 0;
        }
        return true; // Default to new user if check fails
    } catch (error) {
        return true; // Default to new user if check fails
    }
}

// Show onboarding modal
function showOnboardingModal() {
    // Create modal overlay
    let overlay = document.getElementById('onboardingOverlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'onboardingOverlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        document.body.appendChild(overlay);
    }
    
    // Create modal
    let modal = document.getElementById('onboardingModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'onboardingModal';
        modal.style.cssText = `
            background: white;
            border-radius: 12px;
            padding: 2rem;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            position: relative;
            z-index: 10001;
        `;
        overlay.appendChild(modal);
    }
    
    overlay.style.display = 'flex';
    updateOnboardingStep();
}

// Update onboarding step
function updateOnboardingStep() {
    const modal = document.getElementById('onboardingModal');
    const overlay = document.getElementById('onboardingOverlay');
    if (!modal || !overlay) return;
    
    const step = onboardingSteps[onboardingStep];
    if (!step) {
        completeOnboarding();
        return;
    }
    
    const progress = ((onboardingStep + 1) / onboardingSteps.length * 100).toFixed(0);
    
    modal.innerHTML = `
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h2 style="margin: 0; font-size: 1.5rem; color: #1f2937;">${step.title}</h2>
                <button id="onboardingClose" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #6b7280; padding: 0; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;">&times;</button>
            </div>
            <div style="background: #e5e7eb; height: 4px; border-radius: 2px; overflow: hidden;">
                <div style="background: linear-gradient(135deg, #2563eb, #1e40af); height: 100%; width: ${progress}%; transition: width 0.3s;"></div>
            </div>
            <div style="text-align: center; margin-top: 0.5rem; font-size: 0.875rem; color: #6b7280;">
                Step ${onboardingStep + 1} of ${onboardingSteps.length}
            </div>
        </div>
        
        <div style="color: #374151; line-height: 1.7; text-align: center;">
            ${step.content}
        </div>
        
        <div style="display: flex; justify-content: space-between; margin-top: 2rem; gap: 1rem;">
            <button id="onboardingSkip" style="padding: 0.75rem 1.5rem; border: 2px solid #d1d5db; background: white; border-radius: 8px; cursor: pointer; font-weight: 600; color: #6b7280; flex: 1;">
                Skip Tour
            </button>
            <div style="display: flex; gap: 0.5rem; flex: 1;">
                ${onboardingStep > 0 ? `
                    <button id="onboardingPrev" style="padding: 0.75rem 1.5rem; border: none; background: #f3f4f6; border-radius: 8px; cursor: pointer; font-weight: 600; color: #374151; flex: 1;">
                        Previous
                    </button>
                ` : '<div style="flex: 1;"></div>'}
                <button id="onboardingNext" style="padding: 0.75rem 1.5rem; border: none; background: linear-gradient(135deg, #2563eb, #1e40af); color: white; border-radius: 8px; cursor: pointer; font-weight: 600; flex: 1;">
                    ${onboardingStep === onboardingSteps.length - 1 ? 'Get Started!' : 'Next'}
                </button>
            </div>
        </div>
    `;
    
    // Add event listeners
    document.getElementById('onboardingClose').onclick = skipOnboarding;
    document.getElementById('onboardingSkip').onclick = skipOnboarding;
    
    if (onboardingStep > 0) {
        document.getElementById('onboardingPrev').onclick = () => {
            onboardingStep--;
            updateOnboardingStep();
        };
    }
    
    document.getElementById('onboardingNext').onclick = () => {
        if (onboardingStep < onboardingSteps.length - 1) {
            onboardingStep++;
            updateOnboardingStep();
        } else {
            completeOnboarding();
        }
    };
}

// Complete onboarding
function completeOnboarding() {
    localStorage.setItem('onboarding_completed', 'true');
    const overlay = document.getElementById('onboardingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// Skip onboarding
function skipOnboarding() {
    if (confirm('Skip the onboarding tour? You can access the Help & FAQs page anytime for guidance.')) {
        completeOnboarding();
    }
}

// Show onboarding again (for testing or if user wants to revisit)
function showOnboardingAgain() {
    localStorage.removeItem('onboarding_completed');
    onboardingStep = 0;
    showOnboardingModal();
}

// Export for use in dashboard
if (typeof window !== 'undefined') {
    window.showOnboardingAgain = showOnboardingAgain;
}

