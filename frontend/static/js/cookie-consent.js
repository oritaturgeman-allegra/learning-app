// Cookie Consent Management
// Stores preferences in localStorage with 12-month expiry

const COOKIE_CONSENT_KEY = 'cookieConsent';
const COOKIE_CONSENT_VERSION = 1;
const CONSENT_EXPIRY_DAYS = 365;

/**
 * Get stored cookie consent preferences
 * @returns {Object|null} Consent object or null if not set/expired
 */
function getCookieConsent() {
    try {
        const stored = localStorage.getItem(COOKIE_CONSENT_KEY);
        if (!stored) return null;

        const consent = JSON.parse(stored);

        // Check if consent has expired (12 months)
        const consentDate = new Date(consent.timestamp);
        const now = new Date();
        const daysDiff = (now - consentDate) / (1000 * 60 * 60 * 24);

        if (daysDiff > CONSENT_EXPIRY_DAYS) {
            localStorage.removeItem(COOKIE_CONSENT_KEY);
            return null;
        }

        // Check version - if policy updated, may need to re-consent
        if (consent.version !== COOKIE_CONSENT_VERSION) {
            localStorage.removeItem(COOKIE_CONSENT_KEY);
            return null;
        }

        return consent;
    } catch (e) {
        localStorage.removeItem(COOKIE_CONSENT_KEY);
        return null;
    }
}

/**
 * Save cookie consent preferences
 * @param {boolean} analytics - Whether analytics cookies are allowed
 * @param {boolean} preferences - Whether preference cookies are allowed
 */
function saveCookieConsent(analytics, preferences) {
    const consent = {
        timestamp: new Date().toISOString(),
        essential: true, // Always true
        analytics: analytics,
        preferences: preferences,
        version: COOKIE_CONSENT_VERSION
    };

    localStorage.setItem(COOKIE_CONSENT_KEY, JSON.stringify(consent));
    hideCookieBanner();

    // Trigger custom event for analytics to listen to
    window.dispatchEvent(new CustomEvent('cookieConsentUpdated', { detail: consent }));
}

/**
 * Check if a specific cookie category is allowed
 * @param {string} category - 'essential', 'analytics', or 'preferences'
 * @returns {boolean} Whether the category is allowed
 */
function hasConsent(category) {
    if (category === 'essential') return true;

    const consent = getCookieConsent();
    if (!consent) return false;

    return consent[category] === true;
}

/**
 * Show the cookie consent banner
 */
function showCookieBanner() {
    const banner = document.getElementById('cookie-banner');
    if (banner) {
        banner.style.display = 'block';
        // Trigger animation on next frame
        requestAnimationFrame(() => {
            banner.classList.add('show');
        });
    }
}

/**
 * Hide the cookie consent banner
 */
function hideCookieBanner() {
    const banner = document.getElementById('cookie-banner');
    if (banner) {
        banner.classList.remove('show');
        setTimeout(() => {
            banner.style.display = 'none';
        }, 400);
    }
}

/**
 * Accept all cookies
 */
function acceptAllCookies() {
    saveCookieConsent(true, true);
}

/**
 * Reject non-essential cookies
 */
function rejectNonEssentialCookies() {
    saveCookieConsent(false, false);
}

/**
 * Show customize options
 */
function showCookieCustomize() {
    const simple = document.getElementById('cookie-actions-simple');
    const customize = document.getElementById('cookie-customize');

    if (simple) simple.style.display = 'none';
    if (customize) customize.style.display = 'flex';

    // Pre-populate with current preferences if they exist
    const consent = getCookieConsent();
    if (consent) {
        const analyticsCheckbox = document.getElementById('cookie-analytics');
        const preferencesCheckbox = document.getElementById('cookie-preferences');

        if (analyticsCheckbox) analyticsCheckbox.checked = consent.analytics;
        if (preferencesCheckbox) preferencesCheckbox.checked = consent.preferences;
    }
}

/**
 * Hide customize options, show simple view
 */
function hideCookieCustomize() {
    const simple = document.getElementById('cookie-actions-simple');
    const customize = document.getElementById('cookie-customize');

    if (simple) simple.style.display = 'flex';
    if (customize) customize.style.display = 'none';
}

/**
 * Save custom cookie preferences
 */
function saveCustomCookies() {
    const analytics = document.getElementById('cookie-analytics')?.checked || false;
    const preferences = document.getElementById('cookie-preferences')?.checked || false;

    saveCookieConsent(analytics, preferences);
}

/**
 * Open cookie settings (for "Manage Cookies" link)
 */
function openCookieSettings() {
    // Show the banner with customize view
    showCookieBanner();
    showCookieCustomize();
}

/**
 * Initialize cookie consent on page load
 */
function initCookieConsent() {
    const consent = getCookieConsent();

    if (!consent) {
        // No consent stored or expired - show banner
        // Small delay for better UX (page loads first)
        setTimeout(showCookieBanner, 500);
    } else {
        // Consent exists - trigger event so analytics can initialize if allowed
        window.dispatchEvent(new CustomEvent('cookieConsentUpdated', { detail: consent }));
    }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCookieConsent);
} else {
    initCookieConsent();
}

// Expose functions globally for onclick handlers
window.acceptAllCookies = acceptAllCookies;
window.rejectNonEssentialCookies = rejectNonEssentialCookies;
window.showCookieCustomize = showCookieCustomize;
window.hideCookieCustomize = hideCookieCustomize;
window.saveCustomCookies = saveCustomCookies;
window.openCookieSettings = openCookieSettings;
window.hasConsent = hasConsent;
