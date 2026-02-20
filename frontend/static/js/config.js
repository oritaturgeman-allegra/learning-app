// Capital Market Newsletter - Configuration Constants

const CONFIG = {
    // Categories
    CATEGORIES: ['us', 'israel', 'ai', 'crypto', 'space', 'infrastructure', 'energy'],

    CATEGORY_CONFIG: {
        us: { countKey: 'us_news', label: '🇺🇸 U.S. News' },
        israel: { countKey: 'israel_news', label: '🇮🇱 Israeli News' },
        ai: { countKey: 'ai_news', label: '🤖 AI News' },
        crypto: { countKey: 'crypto_news', label: '₿ Crypto News' },
        space: { countKey: 'space_news', label: '🚀 Space News' },
        infrastructure: { countKey: 'infrastructure_news', label: '🏗️ Infrastructure News' },
        energy: { countKey: 'energy_news', label: '⚡ Energy News' }
    },

    // Analysis progress stages (weighted by actual time: RSS ~5s, LLM ~60s)
    ANALYSIS_STAGES: [
        { pct: 5, msg: 'Connecting to market sources...' },
        { pct: 8, msg: 'Fetching US market news...' },
        { pct: 11, msg: 'Fetching Israeli market news...' },
        { pct: 14, msg: 'Fetching AI industry news...' },
        { pct: 17, msg: 'Fetching crypto news...' },
        { pct: 20, msg: 'Analyzing articles with AI...' },
        { pct: 28, msg: 'Generating market summary...' },
        { pct: 36, msg: 'Creating article titles...' },
        { pct: 44, msg: 'Processing insights...' },
        { pct: 52, msg: 'Building podcast script...' },
        { pct: 60, msg: 'Finalizing content...' },
        { pct: 68, msg: 'Almost there...' },
        { pct: 76, msg: 'Wrapping up analysis...' },
        { pct: 84, msg: 'Preparing your newsletter...' },
        { pct: 92, msg: 'Just a moment...' }
    ],

    // Cache settings
    CACHE_TTL_MINUTES: 60,

    // Date/time formatting
    DATE_OPTIONS: {
        weekday: 'short',
        day: 'numeric',
        month: 'short',
        year: 'numeric'
    },

    TIME_OPTIONS: {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    },

    // Timezones
    TIMEZONES: {
        US: 'America/New_York',
        ISRAEL: 'Asia/Jerusalem'
    },

    // UI timing
    PROGRESS_INTERVAL_MS: 4500,  // ~65s total / 15 stages = ~4.3s per stage
    TIMEZONE_UPDATE_INTERVAL_MS: 60000,
    COMPLETION_DELAY_MS: 500,
    PODCAST_COMPLETE_DELAY_MS: 1000,

    // Messages
    MESSAGES: {
        NO_NEWS: 'No news in the last 12 hours',
        CACHE_FRESH: 'Fresh results',
        PODCAST_CACHED: '✨ Podcast ready!',
        PODCAST_SUCCESS: '✨ Podcast ready!',
        PODCAST_CANCELLED: 'Podcast generation cancelled',
        ANALYSIS_COMPLETE: 'Complete!'
    },

    // Icons
    ICONS: {
        CACHE_FRESH: '✨',
        SOURCE_ACTIVE: '✓',
        SOURCE_INACTIVE: '⊘',
        PLAY: '▶',
        PAUSE: '⏸'
    }
};
