// Newsletter page JS - for logged-in users

// State
let currentAudioUrl = null;
let currentNewsletterData = null;
let currentUser = null;
let currentSlide = 0;
let visibleSlides = [];

// DOM Helpers
const $ = (id) => document.getElementById(id);
const showElement = (id) => $(id)?.classList.add('show');
const hideElement = (id) => $(id)?.classList.remove('show');
const setDisplay = (id, display) => { const el = $(id); if (el) el.style.display = display; };


// Carousel Functions
function updateCarousel() {
    const track = $('carousel-track');
    if (track && visibleSlides.length > 0) {
        const slideIndex = visibleSlides.indexOf(currentSlide);
        const actualIndex = slideIndex >= 0 ? slideIndex : 0;
        track.style.transform = `translateX(-${actualIndex * 100}%)`;
    }
    updateNewsTabs();
}

function updateNewsTabs() {
    const tabs = document.querySelectorAll('.news-tab');
    tabs.forEach(tab => {
        const index = parseInt(tab.dataset.index);
        const isVisible = visibleSlides.includes(index);
        tab.classList.toggle('active', index === currentSlide);
        tab.classList.toggle('disabled', !isVisible);
        tab.setAttribute('aria-selected', index === currentSlide ? 'true' : 'false');
        tab.setAttribute('aria-disabled', !isVisible ? 'true' : 'false');
    });
}

function goToSlide(index) {
    if (visibleSlides.includes(index)) {
        currentSlide = index;
        updateCarousel();
    }
}

function initCarousel(selectedCategories) {
    const categoryOrder = CONFIG.CATEGORIES;

    // Build array of visible slide indices
    visibleSlides = [];
    categoryOrder.forEach((cat, index) => {
        const section = $(`${cat}-section`);
        if (section) {
            if (selectedCategories.includes(cat)) {
                section.style.display = 'block';
                visibleSlides.push(index);
            } else {
                section.style.display = 'none';
            }
        }
    });

    // Start at first visible slide
    currentSlide = visibleSlides.length > 0 ? visibleSlides[0] : 0;
    updateCarousel();
}

// User menu
function toggleUserMenu() {
    const menu = document.querySelector('.user-menu');
    if (menu) {
        menu.classList.toggle('show');
    }
}

// Close user menu when clicking outside
document.addEventListener('click', function(event) {
    const menu = document.querySelector('.user-menu');
    const greeting = document.querySelector('.user-greeting');
    if (menu && menu.classList.contains('show')) {
        if (!menu.contains(event.target) && greeting && !greeting.contains(event.target)) {
            menu.classList.remove('show');
        }
    }
});

function handleLogout() {
    localStorage.removeItem('user');
    window.location.href = '/';
}

function setupUserGreeting() {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
        try {
            currentUser = JSON.parse(savedUser);
            const headerRight = $('header-right');
            if (headerRight && currentUser) {
                const today = new Date();
                const dateStr = today.toLocaleDateString('en-US', {
                    weekday: 'short',
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric'
                });
                headerRight.innerHTML = `
                    <button class="feedback-link" type="button" onclick="openModal('feedback-modal')">Leave Feedback</button>
                    <span class="header-divider"></span>
                    <span class="header-date">${dateStr}</span>
                    <span class="header-divider"></span>
                    <div class="user-menu-container">
                        <button type="button" class="user-greeting" onclick="toggleUserMenu()" aria-expanded="false" aria-haspopup="true">Hi, ${currentUser.name || currentUser.email.split('@')[0]}</button>
                        <div class="user-menu" role="menu">
                            <button class="user-menu-item" onclick="handleLogout()" role="menuitem">Log Out</button>
                        </div>
                    </div>
                `;
            }
        } catch (e) {
            // Invalid user data, redirect to login
            localStorage.removeItem('user');
            window.location.href = '/';
        }
    } else {
        // Not logged in, redirect to landing page
        window.location.href = '/';
    }
}

// Override shared updateFilterState to also reset podcast when categories change
const _baseUpdateFilterState = updateFilterState;
updateFilterState = function() {
    _baseUpdateFilterState();
    if (currentAudioUrl) {
        resetPodcastToGenerate();
    }
};

// Handle "Get My Newsletter" button click — on newsletter page, runs analysis
function handleGetNewsletter() {
    runAnalysis();
}

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

// Time Formatting
function formatTime(seconds) {
    if (isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function formatRelativeTime(isoTimestamp) {
    const diffMs = Date.now() - new Date(isoTimestamp).getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);

    if (diffHours < 1) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${Math.floor(diffHours / 24)}d ago`;
}

function formatTimeUntilRefresh(isoTimestamp) {
    const expiresAt = new Date(isoTimestamp).getTime() + CONFIG.CACHE_TTL_MINUTES * 60000;
    const diffMs = expiresAt - Date.now();

    if (diffMs <= 0) return 'now';

    const diffMins = Math.ceil(diffMs / 60000);
    if (diffMins < 60) return `${diffMins}m`;

    const hours = Math.floor(diffMins / 60);
    const mins = diffMins % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
}

// Market Analysis
async function runAnalysis() {
    const selectedCategories = getSelectedCategories();
    if (selectedCategories.length === 0) {
        displayError('Please select at least one news category');
        return;
    }

    const runBtn = $('get-newsletter-btn');
    runBtn.classList.add('loading');
    runBtn.disabled = true;
    runBtn.querySelector('.btn-text').textContent = 'Loading...';
    hideElement('result');
    $('error').textContent = '';  // Clear error - CSS :empty handles visibility

    // Clear previous audio to prevent error alerts
    const audio = $('podcast-audio');
    audio.pause();
    audio.src = '';
    audio.load();

    try {
        // Include user_id if logged in
        const userIdParam = currentUser?.id ? `&user_id=${currentUser.id}` : '';
        const url = `/api/analyze?language=en&categories=${selectedCategories.join(',')}${userIdParam}`;

        const response = await fetch(url);
        const data = await response.json();

        if (!response.ok) {
            // API returned an error (e.g., 500 from LLM failure)
            const errorMsg = data.detail || data.error || 'Unknown error occurred';
            displayError(errorMsg);
            return;
        }

        if (data.success) {
            displayResult(data);
        } else {
            displayError(data.error || 'Unknown error');
        }
    } catch (error) {
        console.error('Analysis error:', error);
        displayError(error.message);
    } finally {
        runBtn.classList.remove('loading');
        runBtn.disabled = false;
        runBtn.querySelector('.btn-text').textContent = 'Get My Newsletter';
        updateFilterState();
    }
}

// Rendering
function renderBullet(bulletText, source) {
    if (!source) {
        return `<div class="bullet-item"><div class="bullet-text">${bulletText}</div></div>`;
    }

    const badges = [
        source.source ? `<span class="source-badge">${source.source}</span>` : '',
        source.published_at ? `<span class="timestamp-badge">${formatRelativeTime(source.published_at)}</span>` : '',
        source.link ? `<a href="${source.link}" class="link-badge" target="_blank" rel="noopener noreferrer">🔗 Read Source</a>` : ''
    ].filter(Boolean).join('');

    const metaHtml = badges ? `<div class="bullet-meta">${badges}</div>` : '';
    return `<div class="bullet-item"><div class="bullet-text">${bulletText}</div>${metaHtml}</div>`;
}

function renderArticles(sources) {
    if (!sources?.length) {
        return `<div class="no-news-message">${CONFIG.MESSAGES.NO_NEWS}</div>`;
    }
    return sources.map(source => {
        return renderBullet(source.ai_title, source);
    }).join('');
}

// Display Results
function displayResult(data) {
    const result = data.data;
    const counts = data.input_counts;
    const sourcesMetadata = result.sources_metadata || {};
    const selectedCategories = getSelectedCategories();

    currentNewsletterData = result;
    resetPodcastPlayer();

    $('stats').innerHTML = selectedCategories
        .map(cat => {
            const config = CONFIG.CATEGORY_CONFIG[cat];
            const count = counts[config.countKey] || 0;
            return `<div class="stat-item"><div class="stat-number">${count}</div><div class="stat-label">${config.label}</div></div>`;
        })
        .join('');

    CONFIG.CATEGORIES.forEach(cat => {
        const bullets = $(`${cat}-bullets`);
        const isSelected = selectedCategories.includes(cat);

        if (isSelected && bullets) {
            const articles = sourcesMetadata[cat] || [];
            bullets.innerHTML = renderArticles(articles);
        }
    });

    // Initialize carousel with selected categories
    initCarousel(selectedCategories);

    // Update sentiment chart with real data from LLM
    if (result.sentiment && typeof updateSentimentData === 'function') {
        updateSentimentData(result.sentiment, data.sentiment_history);
    }

    showElement('result');

    // Hide skeleton section after showing results
    const skeletonSection = $('skeleton-section');
    if (skeletonSection) skeletonSection.style.display = 'none';

    // Reset podcast to generate state (user clicks "Generate Podcast" when ready)
    resetPodcastToGenerate();
}

function displayError(message) {
    // Set error text - CSS :empty selector handles visibility
    // aria-live="assertive" on #error handles screen reader announcement
    $('error').textContent = `Error: ${message}`;
}

// Podcast
function resetPodcastPlayer() {
    hideElement('podcast-controls');
    currentAudioUrl = null;

    const audio = $('podcast-audio');
    audio.pause();
    audio.src = '';

    $('play-pause-btn').textContent = CONFIG.ICONS.PLAY;
    $('progress-fill').style.width = '0%';
    $('current-time').textContent = '0:00';
    $('duration').textContent = '0:00';
}

function resetPodcastToGenerate() {
    // Show generate button, hide player controls and messages
    const btn = $('generate-podcast-btn');
    if (btn) {
        btn.style.display = '';
        btn.disabled = false;
        btn.classList.remove('loading');
        btn.querySelector('.btn-text').textContent = 'Generate Podcast';
    }
    hideElement('podcast-controls');
    const msg = $('podcast-message');
    if (msg) msg.textContent = '';
    currentAudioUrl = null;
}

async function generatePodcast() {
    const selectedCategories = getSelectedCategories();
    if (selectedCategories.length === 0) {
        const msg = $('podcast-message');
        if (msg) msg.textContent = 'Select at least one category';
        return;
    }

    if (!currentUser?.id) {
        const msg = $('podcast-message');
        if (msg) msg.textContent = 'Log in to generate a podcast';
        return;
    }

    const btn = $('generate-podcast-btn');
    const msg = $('podcast-message');

    // Set generating state
    btn.classList.add('loading');
    btn.disabled = true;
    btn.querySelector('.btn-text').textContent = 'Generating...';
    if (msg) msg.textContent = '';

    try {
        const response = await fetch('/api/podcast/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                categories: selectedCategories,
                user_id: currentUser.id,
            }),
        });

        const data = await response.json();

        if (response.status === 429) {
            // Daily limit reached
            btn.style.display = 'none';
            if (msg) msg.textContent = data.detail || 'Today\'s podcast delivered! More podcasts? Premium plans coming soon.';
            return;
        }

        if (!response.ok) {
            btn.classList.remove('loading');
            btn.disabled = false;
            btn.querySelector('.btn-text').textContent = 'Generate Podcast';
            if (msg) msg.textContent = data.detail || 'Failed to generate podcast';
            return;
        }

        if (data.success) {
            // Hide generate button, show player
            btn.style.display = 'none';
            if (msg) msg.textContent = '';
            currentAudioUrl = data.audio_url;
            showElement('podcast-controls');
            loadAudio(currentAudioUrl);
        }

    } catch (error) {
        console.error('Failed to generate podcast:', error);
        btn.classList.remove('loading');
        btn.disabled = false;
        btn.querySelector('.btn-text').textContent = 'Generate Podcast';
        if (msg) msg.textContent = 'Network error. Please try again.';
    }
}

// Audio Player
function loadAudio(audioUrl) {
    const audio = $('podcast-audio');
    const newAudio = audio.cloneNode(false);
    newAudio.id = 'podcast-audio';
    newAudio.preload = 'metadata';
    newAudio.src = audioUrl;
    audio.parentNode.replaceChild(newAudio, audio);
    newAudio.load();

    newAudio.addEventListener('loadedmetadata', () => $('duration').textContent = formatTime(newAudio.duration));
    newAudio.addEventListener('timeupdate', () => {
        const progress = (newAudio.currentTime / newAudio.duration) * 100;
        $('progress-fill').style.width = `${progress}%`;
        $('current-time').textContent = formatTime(newAudio.currentTime);
        $('progress-bar').setAttribute('aria-valuenow', Math.round(progress));
    });
    newAudio.addEventListener('ended', () => {
        $('play-pause-btn').textContent = CONFIG.ICONS.PLAY;
        $('play-pause-btn').setAttribute('aria-label', 'Play podcast');
    });
    newAudio.addEventListener('play', () => {
        $('play-pause-btn').textContent = CONFIG.ICONS.PAUSE;
        $('play-pause-btn').setAttribute('aria-label', 'Pause podcast');
    });
    newAudio.addEventListener('pause', () => {
        $('play-pause-btn').textContent = CONFIG.ICONS.PLAY;
        $('play-pause-btn').setAttribute('aria-label', 'Play podcast');
    });
    newAudio.addEventListener('error', () => {
        if (newAudio.src && newAudio.src !== window.location.href) {
            alert('Failed to load audio. Please try generating the podcast again.');
        }
    });
}

async function togglePlayPause() {
    const audio = $('podcast-audio');
    if (!audio.src) {
        alert('Please generate a podcast first');
        return;
    }

    try {
        if (audio.paused) await audio.play();
        else audio.pause();
    } catch (error) {
        console.error('Playback error:', error);
        alert('Failed to play audio: ' + error.message);
    }
}

function seekAudio(event) {
    const audio = $('podcast-audio');
    const rect = $('progress-bar').getBoundingClientRect();
    const percentage = (event.clientX - rect.left) / rect.width;
    audio.currentTime = audio.duration * percentage;
}

function setSpeed(speed) {
    $('podcast-audio').playbackRate = speed;
    document.querySelectorAll('.speed-btn').forEach(btn => {
        const btnSpeed = parseFloat(btn.textContent);
        btn.classList.toggle('active', btnSpeed === speed);
    });
}

async function downloadPodcast() {
    if (!currentAudioUrl) {
        alert('No podcast available to download');
        return;
    }

    const downloadBtn = $('download-btn');
    const originalText = downloadBtn.innerHTML;

    try {
        downloadBtn.innerHTML = '⏳ Downloading...';
        downloadBtn.disabled = true;

        const response = await fetch(currentAudioUrl);
        if (!response.ok) throw new Error('Download failed');

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `capital-market-newsletter-${new Date().toISOString().split('T')[0]}.mp3`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    } catch (error) {
        alert('Failed to download podcast: ' + error.message);
    } finally {
        downloadBtn.innerHTML = originalText;
        downloadBtn.disabled = false;
    }
}

// Keyboard Navigation

/**
 * Handle keyboard for podcast play button (Space to play/pause)
 */
function handlePodcastKeydown(e) {
    if (e.key === ' ' || e.key === 'Spacebar') {
        e.preventDefault();
        togglePlayPause();
    }
}

/**
 * Initialize keyboard navigation (called on page load)
 */
function initKeyboardNavigation() {
    // Podcast play button Space key
    const playBtn = $('play-pause-btn');
    if (playBtn) {
        playBtn.addEventListener('keydown', handlePodcastKeydown);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupUserGreeting();
    loadSavedFilters();
    updateChipOverflow();
    updateAllTimezones();
    setInterval(updateAllTimezones, CONFIG.TIMEZONE_UPDATE_INTERVAL_MS);
    initKeyboardNavigation();

    // Check for pre-fetched data from landing page, otherwise fetch fresh
    const prefetched = sessionStorage.getItem('prefetchedNewsletter');
    if (prefetched) {
        sessionStorage.removeItem('prefetchedNewsletter');
        try {
            const data = JSON.parse(prefetched);
            const skeletonSection = $('skeleton-section');
            if (skeletonSection) skeletonSection.style.display = 'none';
            displayResult(data);
        } catch {
            runAnalysis();
        }
    } else {
        runAnalysis();
    }

    // Update date when tab becomes visible again (handles overnight tabs)
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
            updateAllTimezones();
        }
    });
});
