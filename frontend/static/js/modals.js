// Shared modal functions - used by both landing page and newsletter page

// Modal accessibility state
let modalTriggerElement = null;
let activeFocusTrap = null;

// Get all focusable elements within a container
function getFocusableElements(container) {
    const focusableSelectors = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
    return Array.from(container.querySelectorAll(focusableSelectors)).filter(el => !el.disabled && el.offsetParent !== null);
}

// Focus trap handler
function handleFocusTrap(e) {
    const modal = document.querySelector('.auth-modal-overlay.show .auth-modal');
    if (!modal) return;

    const focusable = getFocusableElements(modal);
    if (focusable.length === 0) return;

    const firstFocusable = focusable[0];
    const lastFocusable = focusable[focusable.length - 1];

    if (e.key === 'Tab') {
        if (e.shiftKey) {
            if (document.activeElement === firstFocusable) {
                e.preventDefault();
                lastFocusable.focus();
            }
        } else {
            if (document.activeElement === lastFocusable) {
                e.preventDefault();
                firstFocusable.focus();
            }
        }
    }
}

// Hide background content from screen readers
function setBackgroundAccessibility(hidden) {
    const mainContent = document.querySelector('.container');
    const header = document.querySelector('.header');
    const footer = document.querySelector('.footer');

    [mainContent, header, footer].forEach(el => {
        if (el) {
            if (hidden) {
                el.setAttribute('aria-hidden', 'true');
                el.setAttribute('inert', '');
            } else {
                el.removeAttribute('aria-hidden');
                el.removeAttribute('inert');
            }
        }
    });
}

// Modal Functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modalTriggerElement = document.activeElement;

        modal.style.display = 'flex';
        requestAnimationFrame(() => {
            modal.classList.add('show');
        });
        document.body.style.overflow = 'hidden';

        setBackgroundAccessibility(true);

        setTimeout(() => {
            const modalContent = modal.querySelector('.auth-modal');
            const focusable = getFocusableElements(modalContent);
            if (focusable.length > 0) {
                focusable[0].focus();
            }
        }, 100);

        if (!activeFocusTrap) {
            activeFocusTrap = handleFocusTrap;
            document.addEventListener('keydown', activeFocusTrap);
        }
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        // Reset feedback form if closing feedback modal
        if (modalId === 'feedback-modal') {
            resetFeedbackForm();
        }

        modal.classList.remove('show');
        setTimeout(() => {
            modal.style.display = 'none';
            document.body.style.overflow = '';

            setBackgroundAccessibility(false);

            if (modalTriggerElement && modalTriggerElement.focus) {
                modalTriggerElement.focus();
                modalTriggerElement = null;
            }

            if (activeFocusTrap) {
                document.removeEventListener('keydown', activeFocusTrap);
                activeFocusTrap = null;
            }
        }, 300);
    }
}

function switchModal(fromModalId, toModalId) {
    const fromModal = document.getElementById(fromModalId);
    const toModal = document.getElementById(toModalId);

    if (fromModal && toModal) {
        fromModal.classList.remove('show');

        setTimeout(() => {
            fromModal.style.display = 'none';
            toModal.style.display = 'flex';

            setTimeout(() => {
                toModal.classList.add('show');
                const modalContent = toModal.querySelector('.auth-modal');
                const focusable = getFocusableElements(modalContent);
                if (focusable.length > 0) {
                    focusable[0].focus();
                }
            }, 80);
        }, 280);
    }
}

// Close modal when clicking outside
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('auth-modal-overlay')) {
        closeModal(e.target.id);
    }
});

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const openModalEl = document.querySelector('.auth-modal-overlay.show');
        if (openModalEl) {
            closeModal(openModalEl.id);
        }
    }
});

// ============================================
// Feedback Modal Functions
// ============================================

let feedbackFiles = [];

const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
const ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/webm', 'video/quicktime'];
const MAX_IMAGE_SIZE = 10 * 1024 * 1024; // 10MB for images
const MAX_VIDEO_SIZE = 50 * 1024 * 1024; // 50MB for videos
const MAX_FILES = 5;

function handleFeedbackFileSelect(event) {
    const files = Array.from(event.target.files);
    const attachmentsContainer = document.getElementById('feedback-attachments');

    files.forEach(file => {
        if (feedbackFiles.length >= MAX_FILES) {
            showFeedbackError(`Maximum ${MAX_FILES} files allowed`);
            return;
        }

        const isImage = ALLOWED_IMAGE_TYPES.includes(file.type);
        const isVideo = ALLOWED_VIDEO_TYPES.includes(file.type);

        if (!isImage && !isVideo) {
            showFeedbackError('Only images and videos are allowed');
            return;
        }

        const maxSize = isVideo ? MAX_VIDEO_SIZE : MAX_IMAGE_SIZE;
        const maxSizeLabel = isVideo ? '50MB' : '10MB';
        if (file.size > maxSize) {
            showFeedbackError(`File "${file.name}" is too large (max ${maxSizeLabel})`);
            return;
        }

        feedbackFiles.push(file);

        const item = document.createElement('div');
        item.className = 'feedback-attachment-item';
        item.dataset.fileName = file.name;

        if (isImage) {
            const img = document.createElement('img');
            img.src = URL.createObjectURL(file);
            img.alt = file.name;
            item.appendChild(img);
        }

        const nameSpan = document.createElement('span');
        nameSpan.className = 'file-name';
        nameSpan.textContent = file.name;
        item.appendChild(nameSpan);

        const removeBtn = document.createElement('button');
        removeBtn.className = 'feedback-attachment-remove';
        removeBtn.type = 'button';
        removeBtn.innerHTML = '&times;';
        removeBtn.setAttribute('aria-label', `Remove ${file.name}`);
        removeBtn.onclick = () => removeFeedbackFile(file.name);
        item.appendChild(removeBtn);

        attachmentsContainer.appendChild(item);
    });

    event.target.value = '';
}

function removeFeedbackFile(fileName) {
    feedbackFiles = feedbackFiles.filter(f => f.name !== fileName);

    const attachmentsContainer = document.getElementById('feedback-attachments');
    const item = attachmentsContainer.querySelector(`[data-file-name="${fileName}"]`);
    if (item) {
        item.remove();
    }
}

function showFeedbackError(message) {
    const errorEl = document.getElementById('feedback-error');
    if (errorEl) {
        errorEl.textContent = message;
    }
}

function hideFeedbackError() {
    const errorEl = document.getElementById('feedback-error');
    if (errorEl) {
        errorEl.textContent = '';
    }
}

function resetFeedbackForm() {
    const form = document.getElementById('feedback-form');
    if (form) {
        form.reset();
    }
    feedbackFiles = [];
    const attachmentsContainer = document.getElementById('feedback-attachments');
    if (attachmentsContainer) {
        attachmentsContainer.innerHTML = '';
    }
    hideFeedbackError();
}

async function handleFeedbackSubmit(event) {
    event.preventDefault();

    const feedbackText = document.getElementById('feedback-text').value.trim();
    const submitBtn = document.getElementById('feedback-submit-btn');

    hideFeedbackError();

    if (!feedbackText) {
        showFeedbackError('Please enter your feedback');
        return;
    }

    try {
        submitBtn.disabled = true;
        submitBtn.classList.add('loading');

        const formData = new FormData();
        formData.append('feedback_text', feedbackText);

        // Include user info if logged in
        const savedUser = localStorage.getItem('user');
        if (savedUser) {
            try {
                const user = JSON.parse(savedUser);
                if (user.name) formData.append('user_name', user.name);
                if (user.email) formData.append('user_email', user.email);
            } catch (e) {
                // Ignore parse errors, send without user info
            }
        }

        feedbackFiles.forEach(file => {
            formData.append('files', file);
        });

        const response = await fetch('/api/feedback', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to send feedback');
        }

        resetFeedbackForm();
        closeModal('feedback-modal');
        showFeedbackToast('Thank you for your feedback!');

    } catch (error) {
        showFeedbackError(error.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.classList.remove('loading');
    }
}

function showFeedbackToast(message) {
    const toast = document.createElement('div');
    toast.className = 'feedback-toast';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 100px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, #a4b894 0%, #7d9966 100%);
        color: white;
        padding: 14px 28px;
        border-radius: 12px;
        font-size: 14px;
        font-weight: 500;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        z-index: 3000;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;

    document.body.appendChild(toast);

    requestAnimationFrame(() => {
        toast.style.opacity = '1';
    });

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Handle keyboard for upload button
document.addEventListener('DOMContentLoaded', () => {
    const uploadBtn = document.querySelector('.feedback-upload-btn');
    if (uploadBtn) {
        uploadBtn.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                uploadBtn.querySelector('input').click();
            }
        });
    }
});


// ============================================
// Version Update Modal
// ============================================

const VERSION_STORAGE_KEY = 'last_seen_version';

// Get the app version embedded in the page (set via data attribute on the modal)
function getPageVersion() {
    const badge = document.querySelector('.version-badge');
    return badge ? badge.textContent.trim().replace(/^v/, '') : null;
}

// Check if a version update popup should be shown (on page load)
function checkVersionUpdate() {
    const modal = document.getElementById('version-update-modal');
    if (!modal) return;

    const pageVersion = getPageVersion();
    if (!pageVersion) return;

    const lastSeen = localStorage.getItem(VERSION_STORAGE_KEY);

    // First-time visitor — save version silently, don't show popup
    if (!lastSeen) {
        localStorage.setItem(VERSION_STORAGE_KEY, pageVersion);
        return;
    }

    // Returning visitor with same version — nothing to show
    if (lastSeen === pageVersion) return;

    // Page reload (stale-tab refresh or manual F5) — user already
    // saw the "Update Available" prompt or initiated the reload,
    // so silently save the new version without showing "What's New"
    const navEntry = performance.getEntriesByType('navigation')[0];
    if (navEntry && navEntry.type === 'reload') {
        localStorage.setItem(VERSION_STORAGE_KEY, pageVersion);
        return;
    }

    // Fresh navigation with version change — show "What's New" popup
    openModal('version-update-modal');
}

// Dismiss the popup and save current version
function dismissVersionUpdate() {
    const pageVersion = getPageVersion();
    if (pageVersion) {
        localStorage.setItem(VERSION_STORAGE_KEY, pageVersion);
    }
    closeModal('version-update-modal');
}

// Stale tab detection: check server version on visibilitychange
async function checkServerVersion() {
    const modal = document.getElementById('version-update-modal');
    if (!modal) return;

    const pageVersion = getPageVersion();
    if (!pageVersion) return;

    try {
        const response = await fetch('/api/version');
        if (!response.ok) return;

        const data = await response.json();
        const serverVersion = data.version;

        // Server version matches page version — no update available
        if (serverVersion === pageVersion) return;

        // Server has a newer version than what's in this page's HTML
        // Show refresh prompt (different UI from the changelog)
        showStaleTabRefresh(serverVersion, data.changelog || []);
    } catch {
        // Network error — silently ignore
    }
}

// Show the modal in "refresh mode" for stale tabs
function showStaleTabRefresh(serverVersion, changelog) {
    const modal = document.getElementById('version-update-modal');
    if (!modal) return;

    // Already showing? Don't re-trigger
    if (modal.classList.contains('show')) return;

    // Update modal content for stale tab mode
    const title = modal.querySelector('#version-modal-title');
    if (title) {
        // Keep the logo, update text
        const logo = title.querySelector('img');
        title.textContent = '';
        if (logo) title.appendChild(logo);
        title.appendChild(document.createTextNode(' Update Available'));
    }

    const badge = modal.querySelector('.version-badge');
    if (badge) badge.textContent = `v${serverVersion}`;

    // Add subtle refresh notice above changelog, then repopulate changelog from server
    const changelogEl = modal.querySelector('#version-changelog');
    if (changelogEl) {
        // Add refresh notice before changelog
        const notice = document.createElement('p');
        notice.className = 'version-refresh-notice';
        notice.textContent = 'A newer version is available with improvements and fixes.';
        changelogEl.parentNode.insertBefore(notice, changelogEl);

        // Repopulate changelog from server response
        changelogEl.innerHTML = '';
        changelog.forEach(entry => {
            const li = document.createElement('li');
            li.className = 'version-changelog-item';
            li.innerHTML = `<span class="version-changelog-version">v${entry.version}</span><span class="version-changelog-text">${entry.text}</span>`;
            changelogEl.appendChild(li);
        });
    }

    // Replace "Got it" button with "Refresh" button
    const actionsEl = modal.querySelector('.version-modal-actions');
    if (actionsEl) {
        actionsEl.innerHTML = '<button type="button" class="version-refresh-btn" onclick="location.reload()">Refresh</button>';
    }

    openModal('version-update-modal');
}

// Initialize version check on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    // Small delay to avoid blocking initial render
    setTimeout(checkVersionUpdate, 500);
});

// Check for updates when tab becomes visible (handles stale tabs)
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        checkServerVersion();
    }
});
