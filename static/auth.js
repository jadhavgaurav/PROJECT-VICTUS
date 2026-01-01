// Authentication JavaScript for login and signup pages

class AuthManager {
    constructor() {
        // Init will be called after DOM is ready
    }

    async init() {
        // Check if we're on login or signup page
        const loginForm = document.getElementById('login-form');
        const signupForm = document.getElementById('signup-form');
        
        if (loginForm) {
            this.setupLogin();
        }
        
        if (signupForm) {
            this.setupSignup();
        }
        
        // Setup OAuth buttons (async - checks if Microsoft is available)
        await this.setupOAuth();
        
        // Check for token in URL (OAuth callback)
        this.handleOAuthCallback();
    }

    setupLogin() {
        const form = document.getElementById('login-form');
        const loginBtn = document.getElementById('login-btn');
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            loginBtn.disabled = true;
            loginBtn.textContent = 'Logging in...';
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    // Store token
                    localStorage.setItem('victus_token', data.access_token);
                    localStorage.setItem('victus_user', JSON.stringify(data.user));
                    
                    // Redirect to main app
                    window.location.href = '/';
                } else {
                    this.showError(data.detail || 'Login failed. Please check your credentials.');
                    loginBtn.disabled = false;
                    loginBtn.textContent = 'Login';
                }
            } catch (error) {
                this.showError('An error occurred. Please try again.');
                loginBtn.disabled = false;
                loginBtn.textContent = 'Login';
            }
        });
    }

    setupSignup() {
        const form = document.getElementById('signup-form');
        const signupBtn = document.getElementById('signup-btn');
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            
            if (password !== confirmPassword) {
                this.showError('Passwords do not match.');
                return;
            }
            
            if (password.length < 8) {
                this.showError('Password must be at least 8 characters long.');
                return;
            }
            
            signupBtn.disabled = true;
            signupBtn.textContent = 'Creating account...';
            
            const formData = {
                email: document.getElementById('email').value,
                username: document.getElementById('username').value,
                password: password,
                full_name: document.getElementById('full_name').value || null
            };
            
            try {
                const response = await fetch('/api/auth/signup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                let data;
                try {
                    data = await response.json();
                } catch (e) {
                    // If response is not JSON, get text
                    const text = await response.text();
                    console.error('Signup error response:', text);
                    this.showError('Signup failed. Please check your input and try again.');
                    signupBtn.disabled = false;
                    signupBtn.textContent = 'Sign Up';
                    return;
                }
                
                if (response.ok) {
                    // Store token
                    localStorage.setItem('victus_token', data.access_token);
                    localStorage.setItem('victus_user', JSON.stringify(data.user));
                    
                    // Show success and redirect
                    this.showSuccess('Account created successfully! Redirecting...');
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 1500);
                } else {
                    // Show specific error message
                    const errorMsg = data.detail || data.message || 'Signup failed. Please try again.';
                    this.showError(errorMsg);
                    signupBtn.disabled = false;
                    signupBtn.textContent = 'Sign Up';
                }
            } catch (error) {
                console.error('Signup error:', error);
                this.showError(`An error occurred: ${error.message || 'Please try again.'}`);
                signupBtn.disabled = false;
                signupBtn.textContent = 'Sign Up';
            }
        });
    }

    async setupOAuth() {
        // Google login/signup
        const googleBtn = document.getElementById('google-login') || document.getElementById('google-signup');
        if (googleBtn) {
            googleBtn.addEventListener('click', async () => {
                try {
                    const response = await fetch('/api/auth/google/login');
                    const data = await response.json();
                    if (response.ok && data.auth_url) {
                        window.location.href = data.auth_url;
                    } else {
                        this.showError(data.detail || 'Google OAuth not available. Please use email/password.');
                    }
                } catch (error) {
                    this.showError('Google OAuth not available. Please use email/password.');
                }
            });
        }
        
        // Microsoft login/signup - Check if available on page load
        const microsoftBtn = document.getElementById('microsoft-login') || document.getElementById('microsoft-signup');
        if (microsoftBtn) {
            // Check if Microsoft OAuth is configured
            try {
                const checkResponse = await fetch('/api/auth/microsoft/login');
                if (!checkResponse.ok) {
                    // Hide Microsoft button if not configured
                    microsoftBtn.style.display = 'none';
                    return;
                }
            } catch (error) {
                // Hide Microsoft button if check fails
                microsoftBtn.style.display = 'none';
                return;
            }
            
            microsoftBtn.addEventListener('click', async () => {
                try {
                    const response = await fetch('/api/auth/microsoft/login');
                    const data = await response.json();
                    if (response.ok && data.auth_url) {
                        window.location.href = data.auth_url;
                    } else {
                        this.showError(data.detail || 'Microsoft OAuth not available. Please use email/password.');
                    }
                } catch (error) {
                    this.showError('Microsoft OAuth not available. Please use email/password.');
                }
            });
        }
    }

    handleOAuthCallback() {
        // Check for token in URL (from OAuth callback)
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token');
        
        if (token) {
            localStorage.setItem('victus_token', token);
            // Clean URL
            window.history.replaceState({}, document.title, '/');
            // Redirect to main app
            window.location.href = '/';
        }
        
        // Check for error
        const error = urlParams.get('error');
        if (error) {
            this.showError('OAuth authentication failed. Please try again.');
        }
    }

    showError(message) {
        const errorDiv = document.getElementById('error-message');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 5000);
        }
    }

    showSuccess(message) {
        const successDiv = document.getElementById('success-message');
        if (successDiv) {
            successDiv.textContent = message;
            successDiv.style.display = 'block';
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    const authManager = new AuthManager();
    await authManager.init();
});

