/**
 * TradePilot Onboarding System
 * Handles welcome modal, guided tour, and onboarding flow
 */

class OnboardingManager {
    constructor() {
        this.apiBase = '/api';
        this.tourSteps = this.getTourSteps();
        this.currentStep = 0;
        this.tourActive = false;
        this.init();
    }

    init() {
        // Check onboarding status on load
        this.checkOnboardingStatus();
        
        // Load tour progress from localStorage
        const savedStep = localStorage.getItem('onboarding_tour_step');
        if (savedStep !== null) {
            this.currentStep = parseInt(savedStep, 10);
        }
    }

    async checkOnboardingStatus() {
        try {
            const token = localStorage.getItem('auth_token');
            if (!token) return;

            const response = await fetch(`${this.apiBase}/user/onboarding-status`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const status = await response.json();
                if (!status.completed && !status.disclaimer_acknowledged) {
                    // Show welcome modal for first-time users
                    this.showWelcomeModal();
                } else if (!status.completed) {
                    // User acknowledged disclaimer but hasn't completed tour
                    // Don't show welcome modal again
                }
            }
        } catch (error) {
            console.error('Error checking onboarding status:', error);
        }
    }

    showWelcomeModal() {
        const modal = document.createElement('div');
        modal.id = 'welcomeModal';
        modal.className = 'onboarding-modal-overlay';
        modal.innerHTML = `
            <div class="onboarding-modal">
                <div class="onboarding-modal-header">
                    <h2>Welcome to TradePilot</h2>
                    <p class="subtitle">The Trading Bot That Makes You Smarter</p>
                </div>
                <div class="onboarding-modal-body">
                    <div class="value-props">
                        <div class="value-prop">
                            <div class="value-prop-icon">📚</div>
                            <h3>Learn as You Trade</h3>
                            <p>Understand every decision the bot makes with real-time explanations</p>
                        </div>
                        <div class="value-prop">
                            <div class="value-prop-icon">🎯</div>
                            <h3>Proven Strategy</h3>
                            <p>EMA + RSI + Volume strategy with confidence scoring for high-quality trades</p>
                        </div>
                        <div class="value-prop">
                            <div class="value-prop-icon">🛡️</div>
                            <h3>Risk Management First</h3>
                            <p>Built-in position sizing, stop losses, and daily loss limits</p>
                        </div>
                    </div>
                    
                    <div class="disclaimer-section">
                        <label class="disclaimer-checkbox">
                            <input type="checkbox" id="disclaimerCheckbox">
                            <span>I acknowledge that cryptocurrency trading involves substantial risk of loss. I understand that past performance does not guarantee future results, and I should only trade with funds I can afford to lose.</span>
                        </label>
                    </div>
                </div>
                <div class="onboarding-modal-footer">
                    <button class="btn-secondary" id="skipWelcomeBtn">Skip for Now</button>
                    <button class="btn-primary" id="startTourBtn" disabled>Start Tour</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Enable/disable Start Tour button based on checkbox
        const checkbox = document.getElementById('disclaimerCheckbox');
        const startBtn = document.getElementById('startTourBtn');
        
        checkbox.addEventListener('change', () => {
            startBtn.disabled = !checkbox.checked;
        });

        // Button handlers
        document.getElementById('skipWelcomeBtn').addEventListener('click', () => {
            this.acknowledgeDisclaimer();
            modal.remove();
        });

        startBtn.addEventListener('click', () => {
            if (checkbox.checked) {
                this.acknowledgeDisclaimer();
                modal.remove();
                this.startTour();
            }
        });
    }

    async acknowledgeDisclaimer() {
        try {
            const token = localStorage.getItem('auth_token');
            if (!token) return;

            const response = await fetch(`${this.apiBase}/user/acknowledge-disclaimer`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                console.log('Disclaimer acknowledged');
            }
        } catch (error) {
            console.error('Error acknowledging disclaimer:', error);
        }
    }

    getTourSteps() {
        return [
            {
                target: '[data-page="overview"]',
                title: 'Dashboard - Your Command Center',
                content: 'This is your command center. See your bot status, account balance, and P&L at a glance. Monitor all your trading activity from here.',
                position: 'right'
            },
            {
                target: '[data-page="market"]',
                title: 'Market Conditions - Real-Time Analysis',
                content: 'Watch real-time analysis of each trading pair. See why trades are or aren\'t triggering, view current indicators, and understand market conditions.',
                position: 'right'
            },
            {
                target: '.bot-controls, #botControlButton',
                title: 'Bot Controls',
                content: 'Start, pause, or stop your bot here. The bot will only execute trades when it\'s in "Running" status.',
                position: 'bottom'
            },
            {
                target: '[data-page="charts"]',
                title: 'Charts - Visualize Price Action',
                content: 'Visualize price action with your strategy indicators overlaid. See EMA, RSI, and volume on interactive charts.',
                position: 'right'
            },
            {
                target: '[data-page="settings"]',
                title: 'Settings - Configure Your Strategy',
                content: 'Configure your strategy parameters and risk limits. Adjust EMA periods, RSI ranges, volume multipliers, and more.',
                position: 'right'
            },
            {
                target: '[data-page="backtest"]',
                title: 'Backtest - Test Before You Trade',
                content: 'Test your strategy on historical data before going live. Run backtests to see how your strategy would have performed.',
                position: 'right'
            }
        ];
    }

    startTour(stepIndex = 0) {
        this.currentStep = stepIndex;
        this.tourActive = true;
        localStorage.setItem('onboarding_tour_step', stepIndex.toString());
        
        // Navigate to overview if not already there
        if (window.currentPage !== 'overview') {
            if (typeof navigateToPage === 'function') {
                navigateToPage('overview');
            }
        }

        // Wait for page to be ready, then show step
        setTimeout(() => {
            this.showTourStep(this.currentStep);
        }, 500);
    }

    showTourStep(stepIndex) {
        if (stepIndex >= this.tourSteps.length) {
            this.completeTour();
            return;
        }

        const step = this.tourSteps[stepIndex];
        const targetElement = document.querySelector(step.target);

        if (!targetElement) {
            console.warn(`Tour step ${stepIndex}: Target element not found: ${step.target}`);
            // Try next step
            this.currentStep++;
            setTimeout(() => this.showTourStep(this.currentStep), 300);
            return;
        }

        // Remove existing tour overlay
        const existingOverlay = document.getElementById('tourOverlay');
        if (existingOverlay) {
            existingOverlay.remove();
        }

        // Create overlay
        const overlay = document.createElement('div');
        overlay.id = 'tourOverlay';
        overlay.className = 'tour-overlay';

        // Highlight target element
        const rect = targetElement.getBoundingClientRect();
        const highlight = document.createElement('div');
        highlight.className = 'tour-highlight';
        highlight.style.cssText = `
            position: fixed;
            top: ${rect.top}px;
            left: ${rect.left}px;
            width: ${rect.width}px;
            height: ${rect.height}px;
            border: 3px solid #3b82f6;
            border-radius: 8px;
            box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.7);
            z-index: 9998;
            pointer-events: none;
        `;

        // Create tooltip
        const tooltip = document.createElement('div');
        tooltip.className = `tour-tooltip tour-tooltip-${step.position}`;
        tooltip.innerHTML = `
            <div class="tour-tooltip-header">
                <h3>${step.title}</h3>
                <div class="tour-progress">Step ${stepIndex + 1} of ${this.tourSteps.length}</div>
            </div>
            <div class="tour-tooltip-body">
                <p>${step.content}</p>
            </div>
            <div class="tour-tooltip-footer">
                <button class="btn-secondary tour-skip-btn">Skip Tour</button>
                <div class="tour-nav-buttons">
                    ${stepIndex > 0 ? '<button class="btn-secondary tour-back-btn">Back</button>' : ''}
                    <button class="btn-primary tour-next-btn">${stepIndex === this.tourSteps.length - 1 ? 'Finish' : 'Next'}</button>
                </div>
            </div>
        `;

        // Position tooltip
        const tooltipTop = step.position === 'bottom' ? rect.bottom + 20 : rect.top;
        const tooltipLeft = rect.left;
        tooltip.style.cssText = `
            position: fixed;
            top: ${tooltipTop}px;
            left: ${tooltipLeft}px;
            max-width: 400px;
            z-index: 9999;
        `;

        overlay.appendChild(highlight);
        overlay.appendChild(tooltip);
        document.body.appendChild(overlay);

        // Scroll to element if needed
        targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Button handlers
        tooltip.querySelector('.tour-next-btn').addEventListener('click', () => {
            this.currentStep++;
            localStorage.setItem('onboarding_tour_step', this.currentStep.toString());
            this.showTourStep(this.currentStep);
        });

        if (stepIndex > 0) {
            tooltip.querySelector('.tour-back-btn').addEventListener('click', () => {
                this.currentStep--;
                localStorage.setItem('onboarding_tour_step', this.currentStep.toString());
                this.showTourStep(this.currentStep);
            });
        }

        tooltip.querySelector('.tour-skip-btn').addEventListener('click', () => {
            this.skipTour();
        });
    }

    async completeTour() {
        this.tourActive = false;
        localStorage.removeItem('onboarding_tour_step');

        // Remove overlay
        const overlay = document.getElementById('tourOverlay');
        if (overlay) {
            overlay.remove();
        }

        // Mark onboarding as complete
        try {
            const token = localStorage.getItem('auth_token');
            if (!token) return;

            const response = await fetch(`${this.apiBase}/user/complete-onboarding`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                console.log('Onboarding completed');
                this.showTourCompleteMessage();
            }
        } catch (error) {
            console.error('Error completing onboarding:', error);
        }
    }

    skipTour() {
        this.tourActive = false;
        localStorage.removeItem('onboarding_tour_step');

        const overlay = document.getElementById('tourOverlay');
        if (overlay) {
            overlay.remove();
        }
    }

    showTourCompleteMessage() {
        const message = document.createElement('div');
        message.className = 'toast toast-success';
        message.textContent = '🎉 Welcome tour completed! You\'re all set to start trading.';
        document.body.appendChild(message);

        setTimeout(() => {
            message.classList.add('show');
        }, 100);

        setTimeout(() => {
            message.classList.remove('show');
            setTimeout(() => message.remove(), 300);
        }, 5000);
    }
}

// Initialize onboarding manager when DOM is ready
let onboardingManager;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        onboardingManager = new OnboardingManager();
        window.onboardingManager = onboardingManager;
    });
} else {
    onboardingManager = new OnboardingManager();
    window.onboardingManager = onboardingManager;
}
