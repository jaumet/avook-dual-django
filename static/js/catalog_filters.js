document.addEventListener('DOMContentLoaded', () => {
    const filters = {
        text: '',
        collection: '',
        levels: [],
        duration: '',
        lang: '',
        ages: ''
    };

    function applyFilters() {
        const cards = document.querySelectorAll('#catalog .custom-title-card');
        const levelContainers = document.querySelectorAll('#catalog .level-container');
        let hasVisibleCards = false;

        const anyFilterActive =
            (filters.text && filters.text.length > 0) ||
            (filters.levels && filters.levels.length > 0) ||
            filters.collection || filters.duration || filters.lang || filters.ages;

        cards.forEach(card => {
            // If no filters are active, the card is not visible.
            // Otherwise, assume it's visible and let the specific filters hide it if it doesn't match.
            let isVisible = anyFilterActive;

            // Apply level filter
            if (isVisible && filters.levels.length > 0) {
                if (!filters.levels.includes(card.dataset.level)) {
                    isVisible = false;
                }
            }

            // Apply text search filter
            if (isVisible && filters.text) {
                if (!card.textContent.toLowerCase().includes(filters.text)) {
                    isVisible = false;
                }
            }

            // Apply collection filter
            if (isVisible && filters.collection) {
                if (card.dataset.collection.toLowerCase() !== filters.collection.toLowerCase()) {
                    isVisible = false;
                }
            }

            // Apply duration filter
            if (isVisible && filters.duration) {
                if (card.dataset.duration !== filters.duration) {
                    isVisible = false;
                }
            }

            // Apply ages filter
            if (isVisible && filters.ages) {
                if (card.dataset.ages !== filters.ages) {
                    isVisible = false;
                }
            }

            // Apply language filter
            if (isVisible && filters.lang) {
                const cardLangs = (card.dataset.languages || '').split(',');
                if (!cardLangs.includes(filters.lang.toUpperCase())) {
                    isVisible = false;
                }
            }

            card.style.display = isVisible ? 'flex' : 'none';
            if (isVisible) {
                hasVisibleCards = true;
            }
        });

        // Hide or show the level containers based on whether they have visible cards
        levelContainers.forEach(container => {
            const containerHasVisibleCard = container.querySelector('.custom-title-card[style*="display: flex"]');
            container.style.display = containerHasVisibleCard ? 'block' : 'none';
        });

        // Show "no results" message if filters are active but no cards are visible
        const noResultsMessage = document.getElementById('noResultsMessage');
        if (noResultsMessage) {
            noResultsMessage.style.display = anyFilterActive && !hasVisibleCards ? 'block' : 'none';
        }
    }

    // --- Event Listeners ---

    // Level buttons
    document.querySelectorAll('#levelSection .levelBtn').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.classList.toggle('active');
            const level = btn.textContent.trim();
            if (btn.classList.contains('active')) {
                if (!filters.levels.includes(level)) {
                    filters.levels.push(level);
                }
            } else {
                filters.levels = filters.levels.filter(l => l !== level);
            }
            applyFilters();
        });
    });

    // Search input
    document.getElementById('searchInput').addEventListener('input', (e) => {
        filters.text = e.target.value.trim().toLowerCase();
        applyFilters();
    });

    // Select dropdowns
    document.querySelectorAll('#filtersBar select').forEach(select => {
        select.addEventListener('change', (e) => {
            const filterKey = e.target.id.replace('filter', '').toLowerCase();
            filters[filterKey] = e.target.value;
            applyFilters();
        });
    });

    // --- Advanced Search Toggle ---
    document.getElementById('toggleFiltersBtn').addEventListener('click', () => {
        const filtersBar = document.getElementById('filtersBar');
        const btn = document.getElementById('toggleFiltersBtn');
        const visible = filtersBar.style.display !== 'none';
        filtersBar.style.display = visible ? 'none' : 'flex';
        btn.textContent = visible ? '🔍 Cerca avançada' : '✖️ Amaga filtres';
    });

    // --- Initial State ---
    applyFilters(); // Call on load to hide everything
});
