/**
 * Automated Browser Testing Script for Trading Bot Dashboard
 * 
 * This script uses Puppeteer to automatically test all dashboard tabs and features,
 * checking for JavaScript errors, API errors, and UI issues.
 * 
 * Installation:
 *   npm install puppeteer
 * 
 * Usage:
 *   node test-dashboard.js
 */

const puppeteer = require('puppeteer');

const DASHBOARD_URL = 'http://localhost:4000';
const TEST_USER = {
    email: 'test@example.com',
    password: 'testpassword123'
};

// Helper function to wait (replaces deprecated waitForTimeout)
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// List of all tabs to test
const TABS = [
    { name: 'Overview', path: '/', page: 'overview' },
    { name: 'Market Conditions', path: '/market-conditions', page: 'market' },
    { name: 'Positions', path: '/positions', page: 'positions' },
    { name: 'Trade History', path: '/trades', page: 'trades' },
    { name: 'Performance', path: '/performance', page: 'performance' },
    { name: 'Portfolio', path: '/portfolio', page: 'portfolio' },
    { name: 'Charts', path: '/charts', page: 'charts' },
    { name: 'Advanced Orders', path: '/orders', page: 'orders' },
    { name: 'Grid Trading', path: '/grid', page: 'grid' },
    { name: 'Strategy Backtesting', path: '/backtest', page: 'backtest' },
    { name: 'Logs', path: '/logs', page: 'logs' },
    { name: 'Settings', path: '/settings', page: 'settings' }
];

let testResults = {
    passed: 0,
    failed: 0,
    errors: []
};

async function runTests() {
    console.log('🚀 Starting Dashboard Automated Tests...\n');
    
    const browser = await puppeteer.launch({
        headless: false, // Set to true for headless mode
        devtools: false,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    try {
        const page = await browser.newPage();
        
        // Set up console and error listeners
        page.on('console', msg => {
            const type = msg.type();
            const text = msg.text();
            
            if (type === 'error') {
                testResults.errors.push({
                    type: 'Console Error',
                    message: text,
                    page: 'Unknown'
                });
                console.log(`❌ Console Error: ${text}`);
            }
        });

        page.on('pageerror', error => {
            testResults.errors.push({
                type: 'Page Error',
                message: error.message,
                stack: error.stack,
                page: 'Unknown'
            });
            console.log(`❌ Page Error: ${error.message}`);
        });

        page.on('requestfailed', request => {
            const url = request.url();
            // Ignore favicon and common non-critical resources
            if (!url.includes('favicon') && !url.includes('ads') && !url.includes('analytics')) {
                testResults.errors.push({
                    type: 'Network Error',
                    message: `Failed: ${request.method()} ${request.url()}`,
                    status: request.failure()?.errorText || 'Unknown',
                    page: 'Unknown'
                });
                const status = request.failure()?.errorText || '';
                console.log(`❌ Network Error: ${request.method()} ${url} ${status}`);
            }
        });
        
        // Track response status codes
        page.on('response', response => {
            const url = response.url();
            const status = response.status();
            
            // Only log 4xx and 5xx errors, ignore favicon and common resources
            if (status >= 400 && !url.includes('favicon') && !url.includes('ads')) {
                // Don't log 401 if we're not authenticated yet (expected)
                if (status === 401 && url.includes('/api/')) {
                    // Expected during authentication
                    return;
                }
                
                // Don't log 404 for icons (PWA manifest - non-critical)
                if (status === 404 && (url.includes('icon-') || url.includes('.png') || url.includes('.ico'))) {
                    // Non-critical PWA icon missing
                    return;
                }
                
                testResults.errors.push({
                    type: 'HTTP Error',
                    message: `${status} ${response.statusText()}: ${url}`,
                    status: status,
                    page: 'Unknown'
                });
                console.log(`❌ HTTP ${status}: ${url}`);
            }
        });

        // Navigate to landing page
        console.log('📄 Navigating to landing page...');
        await page.goto(`${DASHBOARD_URL}/landing`, { waitUntil: 'networkidle2' });
        await delay(2000);

        // Try to sign in (if authentication is set up)
        console.log('🔐 Attempting to sign in...');
        console.log('💡 Note: You may need to sign in manually. The browser window will stay open.');
        console.log('💡 After signing in, the tests will continue automatically...\n');
        
        try {
            // Check if we're already on dashboard (already signed in)
            const currentUrl = page.url();
            if (currentUrl.includes('/landing')) {
                // Try to find sign in link using XPath or standard selectors
                const signInLink = await page.evaluateHandle(() => {
                    // Try multiple ways to find sign in link
                    const links = Array.from(document.querySelectorAll('a'));
                    return links.find(link => 
                        link.href.includes('signin') || 
                        link.textContent.trim().toLowerCase().includes('sign in')
                    );
                });
                
                if (signInLink && signInLink.asElement()) {
                    await signInLink.asElement().click();
                    await delay(1000);

                    // Fill in sign in form if it exists
                    const emailInput = await page.$('input[type="email"], input[name="email"]');
                    const passwordInput = await page.$('input[type="password"], input[name="password"]');
                    
                    if (emailInput && passwordInput) {
                        await emailInput.type(TEST_USER.email);
                        await passwordInput.type(TEST_USER.password);
                        
                        // Find submit button
                        const submitButton = await page.evaluateHandle(() => {
                            const buttons = Array.from(document.querySelectorAll('button'));
                            return buttons.find(btn => 
                                btn.type === 'submit' || 
                                btn.textContent.trim().toLowerCase().includes('sign in')
                            );
                        });
                        
                        if (submitButton && submitButton.asElement()) {
                            await submitButton.asElement().click();
                            await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 5000 }).catch(() => {});
                            await delay(2000);
                        }
                    } else {
                        console.log('⚠️  Sign in form not found. Please sign in manually...');
                        await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 30000 }).catch(() => {});
                    }
                } else {
                    console.log('⚠️  Sign in link not found. Please sign in manually...');
                }
            } else {
                console.log('✅ Already on dashboard (may be signed in)');
            }
        } catch (error) {
            console.log('⚠️  Could not auto-sign in:', error.message);
            console.log('💡 Please sign in manually in the browser window...');
            console.log('💡 Waiting 10 seconds for manual sign in...\n');
            await delay(10000);
        }
        
        // Check if we're authenticated by trying to access dashboard
        await page.goto(`${DASHBOARD_URL}/`, { waitUntil: 'networkidle2', timeout: 10000 }).catch(() => {});
        const finalUrl = page.url();
        if (finalUrl.includes('/landing')) {
            console.log('⚠️  Still not authenticated. Please sign in manually and press Enter...');
            await new Promise(resolve => {
                process.stdin.once('data', () => resolve());
            });
        } else {
            console.log('✅ Authentication successful!\n');
        }

        // Test each tab
        for (const tab of TABS) {
            console.log(`\n📑 Testing: ${tab.name} (${tab.path})`);
            
            try {
                // Navigate to tab
                await page.goto(`${DASHBOARD_URL}${tab.path}`, { 
                    waitUntil: 'networkidle2',
                    timeout: 10000 
                });
                
                await delay(2000); // Wait for page to load

                // Check for JavaScript errors on this page
                const consoleErrors = await page.evaluate(() => {
                    return window.consoleErrors || [];
                });

                // Network errors are already tracked by the global response handler above

                // Wait for any async operations
                await delay(2000);

                // Check if page loaded correctly
                const pageLoaded = await page.evaluate(() => {
                    // Check if main content exists
                    const pageContainer = document.querySelector('.page, [id^="page-"], main');
                    return pageContainer !== null;
                });

                if (pageLoaded) {
                    console.log(`   ✅ Page loaded successfully`);
                    testResults.passed++;
                } else {
                    console.log(`   ❌ Page did not load correctly`);
                    testResults.failed++;
                    testResults.errors.push({
                        type: 'Page Load',
                        message: `${tab.name} page did not load correctly`,
                        page: tab.name
                    });
                }

                // Test specific features for each tab
                await testTabFeatures(page, tab);

            } catch (error) {
                console.log(`   ❌ Error testing ${tab.name}: ${error.message}`);
                testResults.failed++;
                testResults.errors.push({
                    type: 'Test Error',
                    message: error.message,
                    page: tab.name,
                    stack: error.stack
                });
            }
        }

        // Generate test report
        console.log('\n' + '='.repeat(60));
        console.log('📊 TEST RESULTS');
        console.log('='.repeat(60));
        console.log(`✅ Passed: ${testResults.passed}`);
        console.log(`❌ Failed: ${testResults.failed}`);
        console.log(`📝 Total Errors Found: ${testResults.errors.length}`);
        
        if (testResults.errors.length > 0) {
            console.log('\n🔍 ERROR DETAILS:');
            
            // Group errors by type for better readability
            const errorsByType = {};
            testResults.errors.forEach(error => {
                const type = error.type;
                if (!errorsByType[type]) {
                    errorsByType[type] = [];
                }
                errorsByType[type].push(error);
            });
            
            Object.keys(errorsByType).forEach(type => {
                console.log(`\n📌 ${type} (${errorsByType[type].length}):`);
                errorsByType[type].forEach((error, index) => {
                    console.log(`   ${index + 1}. ${error.message}`);
                    if (error.status) {
                        console.log(`      Status: ${error.status}`);
                    }
                    if (error.page && error.page !== 'Unknown') {
                        console.log(`      Page: ${error.page}`);
                    }
                });
            });
            
            // Filter out expected errors (401 during auth, favicon, icons, etc.)
            const criticalErrors = testResults.errors.filter(err => {
                const msg = err.message.toLowerCase();
                return !msg.includes('favicon') && 
                       !(msg.includes('401') && msg.includes('/api/')) && 
                       !msg.includes('ads') &&
                       !msg.includes('analytics') &&
                       !(msg.includes('404') && (msg.includes('icon') || msg.includes('.png'))) &&
                       !(err.status === 'net::ERR_ABORTED'); // Navigation timing
            });
            
            if (criticalErrors.length < testResults.errors.length) {
                console.log(`\n⚠️  Filtered ${testResults.errors.length - criticalErrors.length} expected/non-critical errors`);
                console.log(`   (401 auth, favicon, PWA icons, navigation timing)`);
                console.log(`📊 Critical Errors Remaining: ${criticalErrors.length}`);
                
                if (criticalErrors.length > 0) {
                    console.log(`\n🔍 CRITICAL ERRORS ONLY:`);
                    criticalErrors.forEach((error, index) => {
                        console.log(`   ${index + 1}. [${error.page || 'Unknown'}] ${error.type}`);
                        console.log(`      ${error.message}`);
                    });
                }
            }
        }

        console.log('\n✅ Testing complete!');

    } catch (error) {
        console.error('💥 Fatal error:', error);
    } finally {
        await browser.close();
    }
}

async function testTabFeatures(page, tab) {
    switch (tab.page) {
        case 'overview':
            // Test bot controls
            const startButton = await page.evaluateHandle(() => {
                const buttons = Array.from(document.querySelectorAll('button'));
                return buttons.find(btn => 
                    btn.textContent.trim().includes('Start') || 
                    btn.onclick || 
                    btn.getAttribute('onclick')?.includes('start')
                );
            });
            if (startButton && startButton.asElement()) {
                console.log('   ✅ Start button found');
            }
            break;

        case 'market':
            // Test AI Analysis button
            const aiButton = await page.evaluateHandle(() => {
                const buttons = Array.from(document.querySelectorAll('button'));
                return buttons.find(btn => 
                    btn.textContent.trim().includes('AI Analysis') || 
                    btn.id.includes('ai')
                );
            });
            if (aiButton && aiButton.asElement()) {
                console.log('   ✅ AI Analysis button found');
            }
            break;

        case 'grid':
            // Test grid modal buttons
            const createGridBtn = await page.evaluateHandle(() => {
                const buttons = Array.from(document.querySelectorAll('button'));
                return buttons.find(btn => btn.textContent.trim().includes('Create Grid'));
            });
            if (createGridBtn && createGridBtn.asElement()) {
                console.log('   ✅ Create Grid button found');
                try {
                    // Try clicking (but don't submit)
                    await createGridBtn.asElement().click();
                    await delay(500);
                    const modal = await page.$('#createGridModal, .modal');
                    if (modal) {
                        console.log('   ✅ Grid modal opens');
                        // Close modal - find cancel button using evaluateHandle
                        const closeBtn = await page.evaluateHandle(() => {
                            const buttons = Array.from(document.querySelectorAll('button, .modal-close'));
                            return buttons.find(btn => 
                                btn.textContent.trim().includes('Cancel') ||
                                btn.classList.contains('modal-close')
                            );
                        });
                        if (closeBtn && closeBtn.asElement()) {
                            await closeBtn.asElement().click();
                        } else {
                            // Try using Escape key
                            await page.keyboard.press('Escape');
                        }
                    }
                } catch (error) {
                    console.log(`   ⚠️  Modal test skipped: ${error.message}`);
                }
            }
            break;

        case 'charts':
            // Check if charts container exists
            const chartContainer = await page.$('#priceChartContainer, .chart-container');
            if (chartContainer) {
                console.log('   ✅ Chart container found');
            }
            break;

        case 'backtest':
            // Test backtest form
            const backtestForm = await page.$('#backtestForm, form');
            if (backtestForm) {
                console.log('   ✅ Backtest form found');
            }
            break;
    }
}

// Run tests
runTests().catch(console.error);

