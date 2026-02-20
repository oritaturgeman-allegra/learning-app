/**
 * Sentiment Chart Component
 * Displays 7-day market sentiment with line chart
 * Uses rolling 7-day window where today is always the rightmost point
 */

// Static weekday names for lookup
const WEEKDAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

// Today is always at index 6 (rightmost position in the chart)
const TODAY_INDEX = 6;

/**
 * Get rolling 7-day labels ending with today
 * Example: If today is Thursday, returns ['Fri', 'Sat', 'Sun', 'Mon', 'Tue', 'Wed', 'Thu']
 * @returns {string[]} Array of 7 weekday names, today at index 6
 */
function getRollingDayLabels() {
    const now = new Date();
    // getUTCDay() returns 0=Sun, 1=Mon, ... 6=Sat
    // Convert to 0=Mon, 1=Tue, ... 6=Sun
    const todayWeekday = (now.getUTCDay() + 6) % 7;

    const labels = [];
    for (let i = 6; i >= 0; i--) {
        // Calculate weekday for (today - i days)
        const weekdayIdx = (todayWeekday - i + 7) % 7;
        labels.push(WEEKDAY_NAMES[weekdayIdx]);
    }
    return labels;
}

// Initialize sentiment data with rolling 7-day labels
function initializeSentimentData() {
    const dayLabels = getRollingDayLabels();
    const defaultDays = dayLabels.map(day => ({ day, sentiment: 0 }));

    const data = { all: { days: JSON.parse(JSON.stringify(defaultDays)) } };
    CONFIG.CATEGORIES.forEach(cat => {
        data[cat] = { days: JSON.parse(JSON.stringify(defaultDays)) };
    });
    return data;
}

// Sentiment data - initialized with neutral values, updated with real data from API
let sentimentData = initializeSentimentData();

// Track which markets have data for "All" calculation
let marketsWithData = [];

/**
 * Update sentiment data with real values from the LLM analysis.
 * Uses historical data from database if available, otherwise just updates today.
 * Data is stored chronologically: index 0 = 6 days ago, index 6 = today.
 * @param {Object} newSentiment - Object with market keys (us, israel, ai, crypto) and scores (0-100)
 * @param {Object} sentimentHistory - Optional historical data: {market: [day0, day1, ..., day6]} where day6=today
 */
function updateSentimentData(newSentiment, sentimentHistory) {
    if (!newSentiment) return;

    console.log('[Sentiment] Received data:', newSentiment);
    console.log('[Sentiment] History:', sentimentHistory);

    // Get today's day label for logging
    const dayLabels = getRollingDayLabels();
    const todayLabel = dayLabels[TODAY_INDEX];
    console.log(`[Sentiment] Today is ${todayLabel} (always at index ${TODAY_INDEX})`);

    const markets = CONFIG.CATEGORIES;
    marketsWithData = [];

    // Reset all sentiment data to 0 with fresh rolling labels
    sentimentData = initializeSentimentData();

    // Update tabs visibility and data
    markets.forEach(market => {
        const tab = document.querySelector(`.sentiment-tab[data-market="${market}"]`);

        if (newSentiment[market] !== undefined && sentimentData[market]) {
            // If we have historical data, map it directly (already in chronological order)
            if (sentimentHistory && sentimentHistory[market]) {
                for (let i = 0; i < 7; i++) {
                    // History index maps directly to array index (0=6 days ago, 6=today)
                    sentimentData[market].days[i].sentiment = sentimentHistory[market][i] || 0;
                }
                console.log(`[Sentiment] Loaded history for ${market}:`, sentimentHistory[market]);
            }
            // Always update today with the fresh sentiment (overrides history for today)
            sentimentData[market].days[TODAY_INDEX].sentiment = newSentiment[market];
            console.log(`[Sentiment] Updated ${market} today (${todayLabel}): ${newSentiment[market]}`);
            marketsWithData.push(market);

            // Enable tab
            if (tab) {
                tab.style.opacity = '1';
                tab.style.pointerEvents = 'auto';
            }
        } else {
            // Disable tab for markets without data
            if (tab) {
                tab.style.opacity = '0.4';
                tab.style.pointerEvents = 'none';
            }
        }
    });

    // Calculate "All" sum from markets with data
    const allTab = document.querySelector('.sentiment-tab[data-market="all"]');
    if (marketsWithData.length > 0) {
        // Calculate sum for each day
        for (let dayIndex = 0; dayIndex < 7; dayIndex++) {
            let sum = 0;
            marketsWithData.forEach(market => {
                sum += sentimentData[market].days[dayIndex].sentiment;
            });
            sentimentData.all.days[dayIndex].sentiment = sum;
        }
        console.log(`[Sentiment] All sum (today): ${sentimentData.all.days[TODAY_INDEX].sentiment}`);

        // Enable "All" tab
        if (allTab) {
            allTab.style.opacity = '1';
            allTab.style.pointerEvents = 'auto';
        }

        // Switch to "All" tab by default
        switchSentimentMarket('all');
    } else {
        // Disable "All" tab if no markets have data
        if (allTab) {
            allTab.style.opacity = '0.4';
            allTab.style.pointerEvents = 'none';
        }
    }
}

let currentMarket = 'all';
let chartTooltip = null;

/**
 * Create or get the chart tooltip element
 */
function getChartTooltip() {
    if (!chartTooltip) {
        chartTooltip = document.createElement('div');
        chartTooltip.className = 'chart-tooltip';
        document.body.appendChild(chartTooltip);
    }
    return chartTooltip;
}

/**
 * Show tooltip on dot hover
 */
function showChartTooltip(event) {
    const dot = event.currentTarget;
    const tooltip = getChartTooltip();
    const day = dot.getAttribute('data-day');
    const sentiment = dot.getAttribute('data-sentiment');

    tooltip.textContent = `${day}: ${sentiment}`;

    // Position tooltip above the mouse cursor
    tooltip.style.left = `${event.pageX}px`;
    tooltip.style.top = `${event.pageY - 10}px`;

    tooltip.classList.add('show');
}

/**
 * Hide tooltip
 */
function hideChartTooltip() {
    const tooltip = getChartTooltip();
    tooltip.classList.remove('show');
}

/**
 * Calculate 7-day average sentiment
 */
function calculateAverage(days) {
    const sum = days.reduce((acc, d) => acc + d.sentiment, 0);
    return Math.round(sum / days.length);
}

/**
 * Get sentiment label based on score
 * ≥70: Bullish, 50-70: Neutral, <50: Bearish
 * For "all" market, thresholds scale with number of markets
 */
function getSentimentLabel(score, marketCount = 1) {
    const bullishThreshold = 70 * marketCount;
    const neutralThreshold = 50 * marketCount;
    if (score >= bullishThreshold) return 'Bullish';
    if (score >= neutralThreshold) return 'Neutral';
    return 'Bearish';
}

/**
 * Get sentiment class based on score
 * ≥70: bullish (#7d9966), 50-70: neutral (#7a9ab8), <50: bearish (#d9a090)
 * For "all" market, thresholds scale with number of markets
 */
function getSentimentClass(score, marketCount = 1) {
    const bullishThreshold = 70 * marketCount;
    const neutralThreshold = 50 * marketCount;
    if (score >= bullishThreshold) return 'bullish';
    if (score >= neutralThreshold) return 'neutral';
    return 'bearish';
}

/**
 * Get chart color based on score
 * ≥70: #7d9966 (green), 50-70: #7a9ab8 (blue), <50: #d9a090 (coral)
 * For "all" market, thresholds scale with number of markets
 */
function getChartColor(score, marketCount = 1) {
    const bullishThreshold = 70 * marketCount;
    const neutralThreshold = 50 * marketCount;
    if (score >= bullishThreshold) return '#7d9966';
    if (score >= neutralThreshold) return '#7a9ab8';
    return '#d9a090';
}

/**
 * Update Y-axis labels based on max score
 */
function updateYAxisLabels(maxScore) {
    const yAxis = document.getElementById('chart-y-axis');
    if (!yAxis) return;

    // Generate 5 labels from max to 0
    const labels = [];
    for (let i = 0; i <= 4; i++) {
        labels.push(Math.round(maxScore * (1 - i / 4)));
    }
    yAxis.innerHTML = labels.map(val => `<span>${val}</span>`).join('');
}

/**
 * Render the sentiment chart SVG
 */
function renderSentimentChart(market) {
    const data = sentimentData[market];
    if (!data) return;

    const days = data.days;
    const chartLine = document.getElementById('chart-line');
    const chartArea = document.getElementById('chart-area');
    const chartDots = document.getElementById('chart-dots');

    if (!chartLine || !chartArea || !chartDots) return;

    // SVG dimensions
    const width = 300;
    const height = 100;
    const padding = 5;

    // For "all" market, scale based on number of selected markets (max = markets * 100)
    const maxScore = (market === 'all' && marketsWithData.length > 0)
        ? marketsWithData.length * 100
        : 100;

    // Calculate points
    const points = days.map((d, i) => {
        const x = padding + (i * (width - 2 * padding) / (days.length - 1));
        const y = height - (d.sentiment / maxScore * height);
        return { x, y, sentiment: d.sentiment };
    });

    // Update Y-axis labels
    updateYAxisLabels(maxScore);

    // Create line path
    const linePath = points.map((p, i) => {
        return (i === 0 ? 'M' : 'L') + p.x + ',' + p.y;
    }).join(' ');

    // Create area path (closed shape)
    const areaPath = linePath +
        ' L' + points[points.length - 1].x + ',' + height +
        ' L' + points[0].x + ',' + height +
        ' Z';

    // Calculate color based on today's sentiment - for "all" market, use dynamic thresholds
    const marketCount = (market === 'all') ? marketsWithData.length : 1;
    const todaySentiment = days[TODAY_INDEX].sentiment;
    const chartColor = getChartColor(todaySentiment, marketCount);

    // Set line path and color
    chartLine.setAttribute('d', linePath);
    chartLine.setAttribute('stroke', chartColor);

    // Set area path and update gradient color
    chartArea.setAttribute('d', areaPath);

    // Update gradient stops color
    const gradient = document.getElementById('sentiment-gradient');
    if (gradient) {
        const stops = gradient.querySelectorAll('stop');
        stops.forEach(stop => {
            stop.style.stopColor = chartColor;
        });
    }

    // Clear and render dots with dynamic color
    chartDots.innerHTML = '';
    points.forEach((p, i) => {
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('class', 'chart-dot');
        circle.setAttribute('cx', p.x);
        circle.setAttribute('cy', p.y);
        circle.setAttribute('r', '4');
        circle.setAttribute('fill', chartColor);
        circle.style.cursor = 'pointer';

        // Store data for tooltip (use setAttribute for SVG elements)
        circle.setAttribute('data-day', days[i].day);
        circle.setAttribute('data-sentiment', p.sentiment);

        // Tooltip events
        circle.addEventListener('mouseenter', showChartTooltip);
        circle.addEventListener('mouseleave', hideChartTooltip);

        chartDots.appendChild(circle);
    });

    // Update x-axis labels to match actual days
    const xAxis = document.getElementById('chart-x-axis');
    if (xAxis) {
        xAxis.innerHTML = days.map(d =>
            `<span class="chart-x-label">${d.day}</span>`
        ).join('');
    }

    // Update score and label - always show today's value
    const todayScore = days[TODAY_INDEX].sentiment;

    // For "all" market, use dynamic thresholds based on number of markets
    const isAllMarket = (market === 'all');
    const labelMarketCount = isAllMarket ? marketsWithData.length : 1;
    const label = getSentimentLabel(todayScore, labelMarketCount);
    const sentimentClass = getSentimentClass(todayScore, labelMarketCount);

    const scoreEl = document.getElementById('sentiment-score');
    const labelEl = document.getElementById('sentiment-label');
    const sublabelEl = document.getElementById('sentiment-sublabel');

    if (scoreEl) {
        scoreEl.textContent = todayScore;
        scoreEl.className = 'sentiment-score ' + sentimentClass;
    }

    if (labelEl) {
        labelEl.textContent = label;
        labelEl.className = 'sentiment-label ' + sentimentClass;
    }

    // Update sublabel with day name
    if (sublabelEl) {
        sublabelEl.textContent = `Today (${days[TODAY_INDEX].day})`;
    }
}

/**
 * Switch to a different market tab
 */
function switchSentimentMarket(market) {
    currentMarket = market;

    // Update active tab and aria-selected
    document.querySelectorAll('.sentiment-tab').forEach(tab => {
        const isActive = tab.dataset.market === market;
        tab.classList.toggle('active', isActive);
        tab.setAttribute('aria-selected', isActive ? 'true' : 'false');
    });

    // Re-render chart
    renderSentimentChart(market);
}

/**
 * Show the sentiment sidebar
 */
function showSentimentSidebar() {
    const sidebar = document.getElementById('sentiment-sidebar');
    if (sidebar) {
        sidebar.classList.add('show');
        renderSentimentChart(currentMarket);
    }
    // Also show the podcast sidebar
    const podcastSidebar = document.getElementById('podcast-sidebar');
    if (podcastSidebar) {
        podcastSidebar.classList.add('show');
    }
    // Also show the right sidebar
    const rightSidebar = document.getElementById('right-sidebar');
    if (rightSidebar) {
        rightSidebar.classList.add('show');
    }
}

/**
 * Hide the sentiment sidebar
 */
function hideSentimentSidebar() {
    const sidebar = document.getElementById('sentiment-sidebar');
    if (sidebar) {
        sidebar.classList.remove('show');
    }
    // Also hide the podcast sidebar
    const podcastSidebar = document.getElementById('podcast-sidebar');
    if (podcastSidebar) {
        podcastSidebar.classList.remove('show');
    }
    // Also hide the right sidebar
    const rightSidebar = document.getElementById('right-sidebar');
    if (rightSidebar) {
        rightSidebar.classList.remove('show');
    }
}

/**
 * Initialize sentiment chart on page load
 */
function initSentimentChart() {
    // Only initialize if we're on a page with the sentiment chart
    if (!document.getElementById('sentiment-card')) return;

    // Check if result is already visible (e.g., page refresh with cached data)
    const result = document.getElementById('result');
    if (result && result.classList.contains('show')) {
        showSentimentSidebar();
    }

    // Observe the result element for visibility changes
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                const result = mutation.target;
                if (result.classList.contains('show')) {
                    showSentimentSidebar();
                } else {
                    hideSentimentSidebar();
                }
            }
        });
    });

    if (result) {
        observer.observe(result, { attributes: true });
    }
}

/**
 * Handle keyboard navigation for sentiment tabs
 */
function handleSentimentTabKeydown(e) {
    const tabs = Array.from(document.querySelectorAll('.sentiment-tab'));
    const enabledTabs = tabs.filter(tab => tab.style.pointerEvents !== 'none');
    if (enabledTabs.length === 0) return;

    const currentIndex = enabledTabs.findIndex(tab => tab.classList.contains('active'));
    let newIndex = currentIndex;

    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
        e.preventDefault();
        newIndex = (currentIndex + 1) % enabledTabs.length;
    } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        e.preventDefault();
        newIndex = (currentIndex - 1 + enabledTabs.length) % enabledTabs.length;
    } else if (e.key === 'Home') {
        e.preventDefault();
        newIndex = 0;
    } else if (e.key === 'End') {
        e.preventDefault();
        newIndex = enabledTabs.length - 1;
    }

    if (newIndex !== currentIndex) {
        const newTab = enabledTabs[newIndex];
        newTab.focus();
        switchSentimentMarket(newTab.dataset.market);
    }
}

/**
 * Initialize keyboard navigation for sentiment tabs
 */
function initSentimentKeyboard() {
    const tabContainer = document.querySelector('.sentiment-tabs');
    if (tabContainer) {
        tabContainer.addEventListener('keydown', handleSentimentTabKeydown);
    }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initSentimentChart();
        initSentimentKeyboard();
    });
} else {
    initSentimentChart();
    initSentimentKeyboard();
}
