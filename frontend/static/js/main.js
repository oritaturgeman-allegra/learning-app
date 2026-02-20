// Landing page JS - for logged-out users
// Note: Modal functions are in modals.js (shared with newsletter.js)

// DOM Helpers
const $ = (id) => document.getElementById(id);
const showElement = (id) => $(id)?.classList.add('show');
const hideElement = (id) => $(id)?.classList.remove('show');

// Auth state
let currentUser = null;

// Password visibility toggle
function togglePasswordVisibility(inputId, button) {
    const input = $(inputId);
    const eyeIcon = button.querySelector('.eye-icon');
    const eyeOffIcon = button.querySelector('.eye-off-icon');

    if (input.type === 'password') {
        input.type = 'text';
        eyeIcon.style.display = 'none';
        eyeOffIcon.style.display = 'block';
        button.setAttribute('aria-label', 'Hide password');
    } else {
        input.type = 'password';
        eyeIcon.style.display = 'block';
        eyeOffIcon.style.display = 'none';
        button.setAttribute('aria-label', 'Show password');
    }
}

// Auth error helpers
function showAuthError(elementId, message) {
    const errorEl = $(elementId);
    if (errorEl) {
        errorEl.textContent = message;

        const form = errorEl.closest('form');
        if (form) {
            form.querySelectorAll('input[aria-describedby*="' + elementId + '"]').forEach(input => {
                input.setAttribute('aria-invalid', 'true');
            });
        }
    }
}

function hideAuthError(elementId) {
    const errorEl = $(elementId);
    if (errorEl) {
        errorEl.textContent = '';

        const form = errorEl.closest('form');
        if (form) {
            form.querySelectorAll('input[aria-describedby*="' + elementId + '"]').forEach(input => {
                input.setAttribute('aria-invalid', 'false');
            });
        }
    }
}

// Auth handlers
async function handleLogin(event) {
    event.preventDefault();
    const email = $('login-email').value;
    const password = $('login-password').value;
    const submitBtn = event.target.querySelector('button[type="submit"]');

    hideAuthError('login-error');

    try {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Logging in...';

        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
        }

        currentUser = data.user;
        localStorage.setItem('user', JSON.stringify(currentUser));
        closeModal('login-modal');
        console.log('Login successful:', currentUser.email);

        // Pre-fetch newsletter data before navigating
        submitBtn.textContent = 'Loading newsletter...';
        await prefetchNewsletter();
        window.location.href = '/newsletter';

    } catch (error) {
        showAuthError('login-error', error.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Sign in';
    }
}

async function handleSignup(event) {
    event.preventDefault();
    const email = $('signup-email').value;
    const password = $('signup-password').value;
    const confirmPassword = $('signup-confirm-password').value;
    const submitBtn = event.target.querySelector('button[type="submit"]');

    hideAuthError('signup-error');

    if (password !== confirmPassword) {
        showAuthError('signup-error', 'Passwords do not match');
        return;
    }

    try {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Creating account...';

        const response = await fetch('/api/auth/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (!response.ok) {
            let errorMsg = 'Signup failed';
            if (data.detail) {
                if (Array.isArray(data.detail)) {
                    errorMsg = data.detail.map(err => err.msg).join('. ');
                } else {
                    errorMsg = data.detail;
                }
            }
            throw new Error(errorMsg);
        }

        currentUser = data.user;
        localStorage.setItem('user', JSON.stringify(currentUser));
        console.log('Signup successful:', currentUser.email);

        if (!currentUser.email_verified) {
            showVerificationPendingMessage(currentUser.email);
        } else {
            closeModal('signup-modal');
            submitBtn.textContent = 'Loading newsletter...';
            await prefetchNewsletter();
            window.location.href = '/newsletter';
        }

    } catch (error) {
        showAuthError('signup-error', error.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create account';
    }
}

function handleGoogleAuth(mode = 'signup') {
    console.log(`Google auth requested (mode: ${mode})`);
    window.location.href = `/api/auth/google?mode=${mode}`;
}

function showVerificationPendingMessage(email) {
    const modal = $('signup-modal');
    const modalContent = modal.querySelector('.auth-modal');

    modalContent.innerHTML = `
        <button class="auth-modal-close" onclick="closeModal('signup-modal')">&times;</button>
        <div style="text-align: center; padding: 20px;">
            <div style="width: 64px; height: 64px; background: linear-gradient(135deg, #a4b894 0%, #7d9966 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px;">
                <svg width="32" height="32" fill="none" stroke="white" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                </svg>
            </div>
            <h2 style="color: #2e2e2e; margin-bottom: 16px;">Check Your Email</h2>
            <p style="color: #555555; margin-bottom: 8px;">We've sent a verification link to:</p>
            <p style="color: #2e2e2e; font-weight: 600; margin-bottom: 24px;">${email}</p>
            <p style="color: #888888; font-size: 14px; margin-bottom: 24px;">Click the link in the email to verify your account and start using Your Newsletter, Your Way.</p>
            <button onclick="resendVerificationEmail('${email}')" style="background: #f7f4ef; color: #2e2e2e; border: 1px solid #e6e0d8; padding: 14px 24px; font-size: 15px; font-weight: 600; border-radius: 12px; cursor: pointer; margin-right: 12px; transition: all 0.2s ease;">Resend Email</button>
            <button onclick="closeModal('signup-modal')" style="background: linear-gradient(135deg, #d9a090 0%, #c9886a 100%); color: #fcfbf8; border: none; padding: 14px 24px; font-size: 15px; font-weight: 600; border-radius: 12px; cursor: pointer; transition: all 0.2s ease;">Got it</button>
        </div>
    `;
}

async function resendVerificationEmail(email) {
    try {
        const response = await fetch('/api/auth/resend-verification', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });

        const data = await response.json();
        if (data.success) {
            alert('Verification email sent! Please check your inbox.');
        } else {
            alert('Failed to resend email. Please try again.');
        }
    } catch (error) {
        alert('Failed to resend email. Please try again.');
    }
}

// Check for existing session on page load - redirect to newsletter if logged in
async function checkExistingSession() {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
        try {
            currentUser = JSON.parse(savedUser);
            await prefetchNewsletter();
            window.location.href = '/newsletter';
        } catch (e) {
            localStorage.removeItem('user');
        }
    }
}

// Pre-fetch newsletter data before navigating to /newsletter
async function prefetchNewsletter() {
    try {
        const selectedCategories = getSelectedCategories();
        const userIdParam = currentUser?.id ? `&user_id=${currentUser.id}` : '';
        const url = `/api/analyze?language=en&categories=${selectedCategories.join(',')}${userIdParam}`;

        const response = await fetch(url);
        const data = await response.json();

        if (response.ok && data.success) {
            sessionStorage.setItem('prefetchedNewsletter', JSON.stringify(data));
        }
    } catch (error) {
        // Silently fail - newsletter page will fetch on its own
        console.log('Pre-fetch failed, newsletter will load normally:', error.message);
    }
}

// Handle "Get My Newsletter" button click - opens login modal on landing page
function handleGetNewsletter() {
    openModal('login-modal');
}

document.addEventListener('DOMContentLoaded', () => {
    loadSavedFilters();
    updateChipOverflow();
    checkExistingSession();
});

// Timezone Display
function updateAllTimezones() {
    const now = new Date();
    const dateBadge = $('date-badge');
    const timeUs = $('time-us');
    const timeIl = $('time-il');
    const headerDate = document.querySelector('.header-date');

    if (dateBadge) dateBadge.textContent = now.toLocaleDateString('en-US', CONFIG.DATE_OPTIONS);
    if (timeUs) timeUs.textContent = now.toLocaleString('en-US', { ...CONFIG.TIME_OPTIONS, timeZone: CONFIG.TIMEZONES.US });
    if (timeIl) timeIl.textContent = now.toLocaleString('en-US', { ...CONFIG.TIME_OPTIONS, timeZone: CONFIG.TIMEZONES.ISRAEL });
    if (headerDate) headerDate.textContent = now.toLocaleDateString('en-US', CONFIG.DATE_OPTIONS);
}

updateAllTimezones();
setInterval(updateAllTimezones, CONFIG.TIMEZONE_UPDATE_INTERVAL_MS);

// Update date when tab becomes visible again (handles overnight tabs)
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        updateAllTimezones();
    }
});
