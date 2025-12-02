// Authentication JavaScript for signup and signin

const API_BASE = '/api';

// Helper function to show alerts
function showAlert(message, type = 'error') {
    const alert = document.getElementById('alert');
    alert.textContent = message;
    alert.className = `alert alert-${type}`;
    alert.style.display = 'block';
    
    setTimeout(() => {
        alert.style.display = 'none';
    }, 5000);
}

// Signup form handler
document.addEventListener('DOMContentLoaded', () => {
    const signupForm = document.getElementById('signupForm');
    const signinForm = document.getElementById('signinForm');
    
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleSignup();
        });
    }
    
    if (signinForm) {
        signinForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleSignin();
        });
    }
});

async function handleSignup() {
    const form = document.getElementById('signupForm');
    const submitBtn = form.querySelector('button[type="submit"]');
    
    const fullName = document.getElementById('full_name').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    
    // Validation
    if (!fullName || !email || !password || !confirmPassword) {
        showAlert('Please fill in all fields');
        return;
    }
    
    if (password.length < 8) {
        showAlert('Password must be at least 8 characters long');
        return;
    }
    
    if (password !== confirmPassword) {
        showAlert('Passwords do not match');
        return;
    }
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showAlert('Please enter a valid email address');
        return;
    }
    
    // Disable button and show loading
    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating Account...';
    
    try {
        const response = await fetch(`${API_BASE}/auth/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email,
                password,
                full_name: fullName
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('Account created successfully! Redirecting...', 'success');
            // Store token
            localStorage.setItem('auth_token', data.token);
            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        } else {
            showAlert(data.error || 'Failed to create account. Please try again.');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Create Account';
        }
    } catch (error) {
        console.error('Signup error:', error);
        showAlert('An error occurred. Please try again.');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create Account';
    }
}

async function handleSignin() {
    const form = document.getElementById('signinForm');
    const submitBtn = form.querySelector('button[type="submit"]');
    
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    
    // Validation
    if (!email || !password) {
        showAlert('Please fill in all fields');
        return;
    }
    
    // Disable button and show loading
    submitBtn.disabled = true;
    submitBtn.textContent = 'Signing In...';
    
    try {
        const response = await fetch(`${API_BASE}/auth/signin`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email,
                password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('Signed in successfully! Redirecting...', 'success');
            // Store token
            localStorage.setItem('auth_token', data.token);
            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = '/';
            }, 1000);
        } else {
            showAlert(data.error || 'Invalid email or password');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Sign In';
        }
    } catch (error) {
        console.error('Signin error:', error);
        showAlert('An error occurred. Please try again.');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Sign In';
    }
}

// Check if user is authenticated on page load
window.addEventListener('load', () => {
    const token = localStorage.getItem('auth_token');
    const currentPath = window.location.pathname;
    
    // If user has token and is on auth pages, redirect to dashboard
    if (token && (currentPath === '/signin' || currentPath === '/signup')) {
        window.location.href = '/';
    }
});

