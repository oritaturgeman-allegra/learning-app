// Shared filter logic — loaded on both landing page and newsletter page
// Page-specific behavior (e.g. handleGetNewsletter) stays in main.js / newsletter.js

// Filter State
function getSelectedCategories() {
    const checkboxes = document.querySelectorAll('.filter-toggle input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

function updateFilterState() {
    const checkboxes = document.querySelectorAll('.filter-toggle input[type="checkbox"]');
    if (checkboxes.length === 0) return;

    const selected = getSelectedCategories();
    const btn = document.getElementById('get-newsletter-btn');
    if (btn) btn.disabled = selected.length === 0;
    localStorage.setItem('selectedCategories', JSON.stringify(selected));
}

function loadSavedFilters() {
    const saved = localStorage.getItem('selectedCategories');
    if (saved) {
        try {
            JSON.parse(saved).forEach(cat => {
                const checkbox = document.getElementById(`filter-${cat}`);
                if (checkbox) checkbox.checked = true;
            });
        } catch {
            checkAllCategories();
        }
    } else {
        checkAllCategories();
    }
    updateFilterState();
}

function checkAllCategories() {
    document.querySelectorAll('.filter-toggle input[type="checkbox"]').forEach(checkbox => {
        checkbox.checked = true;
    });
}

// ============================================
// Chip Overflow — Horizontal Slide
// ============================================

function updateChipOverflow() {
    const container = document.querySelector('.filter-toggles');
    const trigger = document.getElementById('chip-overflow-trigger');
    if (!container || !trigger) return;

    const hasOverflow = container.scrollWidth > container.clientWidth + 2;

    if (hasOverflow) {
        const hiddenCount = countHiddenChips(container);
        trigger.innerHTML = '+<span id="overflow-count">' + Math.max(hiddenCount, 1) + '</span> more';
        trigger.style.display = 'inline-flex';
    } else {
        trigger.style.display = 'none';
    }
}

function countHiddenChips(container) {
    const toggles = container.querySelectorAll('.filter-toggle');
    const containerRect = container.getBoundingClientRect();
    let hidden = 0;
    toggles.forEach(t => {
        const r = t.getBoundingClientRect();
        if (r.right > containerRect.right + 2) hidden++;
    });
    return hidden;
}

function scrollChips() {
    const container = document.querySelector('.filter-toggles');
    if (!container) return;

    const atEnd = container.scrollLeft + container.clientWidth >= container.scrollWidth - 2;

    if (atEnd) {
        container.scrollTo({ left: 0, behavior: 'smooth' });
    } else {
        container.scrollTo({ left: container.scrollLeft + container.clientWidth * 0.7, behavior: 'smooth' });
    }
}

// Resize handler for chip overflow
let _chipResizeTimer;
window.addEventListener('resize', () => {
    clearTimeout(_chipResizeTimer);
    _chipResizeTimer = setTimeout(updateChipOverflow, 150);
});

// Update "+N more" count in real-time during trackpad scroll
document.addEventListener('DOMContentLoaded', () => {
    const filterToggles = document.querySelector('.filter-toggles');
    if (filterToggles) {
        filterToggles.addEventListener('scroll', () => updateChipOverflow());
    }
});
