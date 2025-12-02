document.addEventListener('DOMContentLoaded', () => {
    const filters = { text:'', colection:'', levels:[], duration:'', lang:'', ages:'' };

    function applyFilters(){
      const cards = document.querySelectorAll('#catalog .titleCard');
      let anyVisible = false;

      const anyFilterActive =
        (filters.text && filters.text.length > 0) ||
        (filters.levels && filters.levels.length > 0) ||
        filters.colection || filters.duration || filters.lang || filters.ages;

      cards.forEach(card => {
        let visible = true;

        if (anyFilterActive) {
          const txt = card.textContent.toLowerCase();
          const cardLevel = card.querySelector('.level')?.textContent.trim().toLowerCase() || '';
          const cardLangs = (card.querySelector('.langList')?.dataset.codes || '')
            .split(/[,\s]+/)
            .map(l => l.trim().toUpperCase())
            .filter(Boolean);

          if (filters.text && !txt.includes(filters.text)) visible = false;
          if (visible && filters.levels.length > 0) {
            const wanted = filters.levels.map(l => l.toLowerCase());
            if (!wanted.includes(cardLevel)) visible = false;
          }
          if (visible && filters.lang) {
            const wantedLang = filters.lang.trim().toUpperCase();
            if (!cardLangs.includes(wantedLang)) visible = false;
          }
          if (visible && filters.colection && !txt.includes(filters.colection.toLowerCase())) visible = false;
          if (visible && filters.duration && !txt.includes(filters.duration.toLowerCase())) visible = false;
          if (visible && filters.ages && !txt.includes(filters.ages.toLowerCase())) visible = false;
        }

        card.style.display = visible ? 'flex' : 'none';
        if (visible) anyVisible = true;
      });

      const noResultsMessage = document.getElementById('noResultsMessage');
      if (noResultsMessage) {
        noResultsMessage.style.display = anyVisible ? 'none' : 'block';
      }
    }

    document.querySelectorAll('#levelSection .levelBtn').forEach(btn => {
      btn.addEventListener('click', () => {
        btn.classList.toggle('active');
        const level = btn.textContent;
        if (btn.classList.contains('active')) {
          if (!filters.levels.includes(level)) filters.levels.push(level);
        } else {
          filters.levels = filters.levels.filter(x => x !== level);
        }
        applyFilters();
      });
    });

    document.addEventListener('input', (e) => {
      if (e.target.id === 'searchInput') {
        filters.text = e.target.value.trim().toLowerCase();
        applyFilters();
      }
    });

    document.addEventListener('change', (e) => {
      if (e.target.matches('#filterColection, #filterDuration, #filterLang, #filterAges')) {
        const key = e.target.id.replace('filter', '').toLowerCase();
        filters[key] = e.target.value || '';
        applyFilters();
      }
    });

    function setupFakeSelects(){
      document.querySelectorAll('#filtersBar .av-select select').forEach(sel=>{
        const wrap = sel.parentElement;
        const setLabel = () => {
          const idx = sel.selectedIndex;
          const txt = idx >= 0 ? sel.options[idx].text : '';
          wrap.setAttribute('data-value', txt);
          if (idx === 0) sel.style.color = '#999'; else sel.style.color = '';
        };
        sel.addEventListener('change', setLabel);
        setLabel();
      });
    }

    document.getElementById('toggleFiltersBtn').addEventListener('click', () => {
      const filtersBar = document.getElementById('filtersBar');
      const btn = document.getElementById('toggleFiltersBtn');
      const visible = filtersBar.style.display !== 'none';
      filtersBar.style.display = visible ? 'none' : 'flex';
      btn.textContent = visible ? '🔍 Cerca avançada' : '✖️ Amaga filtres';
    });

    setupFakeSelects();
    applyFilters();
});
