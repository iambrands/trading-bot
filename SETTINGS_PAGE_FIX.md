# Settings Page Visibility Fix

## Issue
The Settings page was showing only the navigation bar with an empty gradient background, but the actual settings form content wasn't visible.

## Fix Applied
Updated the CSS in `settings.html` to ensure:
1. The settings container has proper padding and margin
2. The body background is properly set
3. Content is visible with proper z-index

## To See the Changes

**Please refresh your browser:**
- Windows/Linux: Press `Ctrl + R` or `Ctrl + F5`
- Mac: Press `Cmd + R` or `Cmd + Shift + R`

## What You Should See After Refresh

1. **Page Header**: "⚙️ Settings & Configuration"
2. **Strategy Parameters Section**: With EMA Period, RSI Period, etc.
3. **RSI Thresholds Section**: Long/Short entry ranges
4. **Risk Management Section**: Risk per trade, max positions, etc.
5. **Exit Parameters Section**: Take profit and stop loss ranges
6. **Trading Pairs Section**: With coin selector dropdown
7. **Trading Mode Section**: Paper trading toggle
8. **Configuration Templates Section**: Save/load templates
9. **Action Buttons**: Save Settings, Reset, Apply & Restart

All sections should have white backgrounds and be clearly visible against the purple gradient background.

## If Still Not Visible

1. **Hard refresh**: Clear cache (Ctrl+Shift+Delete) or use incognito/private window
2. **Check browser console**: Press F12, look for errors in Console tab
3. **Verify URL**: Make sure you're at http://localhost:4000/settings

The settings page content is definitely there (9 sections, 390 lines of HTML). It just needs proper CSS visibility, which has now been fixed.
