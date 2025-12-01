document.addEventListener('DOMContentLoaded', () => {
    async function loadCatalog(){
      const res = await fetch('/catalog/json/');
      const data = await res.json();
      const catalog = document.getElementById('catalog');
      catalog.innerHTML = '';
      catalog.style.display = 'none';

      data.titles.forEach(item => {
        const i = item.title;
        const img = resolveImagePath(i.image_url);
        const human = i.human_name || i.machine_name;

        const colection = i.collection && i.collection.trim() !== "" ? `<span class="colection">${i.collection}</span>` : "";
        const levels    = i.levels && i.levels.trim() !== ""       ? `<span class="level">${i.levels}</span>` : "";
        const ages      = i.ages && i.ages.trim() !== ""           ? `<span class="ages">${i.ages}</span>` : "";
        const duration  = i.duration && i.duration.trim() !== ""   ? `<span class="duration">${i.duration}</span>` : "";
        let langs = '';
        if (i.languages && i.languages.length > 0) {
            langs = `<div class="langList">${i.languages.join(', ')}</div>`;
        }
        const desc      = i.description && i.description.trim() !== "" ? `<div class="description">${i.description}</div>` : "";

        const metaTop = (levels || ages)
          ? `<div class="meta-top">${levels}${ages}</div>`
          : "";

        const meta = (colection || duration)
          ? `<div class="meta">${colection}${duration}</div>`
          : "";

        const card = document.createElement('div');
        card.className = 'titleCard';
        card.innerHTML = `
          <img src="${img}" alt="${human}">
          ${metaTop}
          <div class="cardText">
            <h3>${human}</h3>
            ${meta}
            ${langs}
            ${desc}
          </div>
        `;
        card.onclick = () => {
          window.location.href = `/products/player/${i.machine_name}/`;
        };
        catalog.appendChild(card);
      });

      initFilters(data);
    }

    const filters = { text:'', colection:'', levels:[], duration:'', lang:'', ages:'' };

    function fillSelect(id,set){
      const sel=document.querySelector(id);
      if(!sel)return;
      const opt0=document.createElement('option');
      opt0.value=''; opt0.textContent='—';
      sel.appendChild(opt0);
      [...set].sort().forEach(v=>{
        const opt=document.createElement('option');
        opt.value=v; opt.textContent=v;
        sel.appendChild(opt);
      });
    }

    async function initFilters(data){
        const colSet = new Set(data.collections);
        const levSet = new Set(data.levels);
        const durSet = new Set(data.durations);
        const langSet = new Set(data.languages);
        const ageSet = new Set(data.ages_list);

        fillSelect('#filterColection', colSet);
        fillSelect('#filterDuration', durSet);
        fillSelect('#filterLang', langSet);
        fillSelect('#filterAges', ageSet);

        const levelSection = document.getElementById('levelSection');
        levelSection.innerHTML = '';
        [...levSet].sort().forEach(l => {
            const btn = document.createElement('button');
            btn.className = 'levelBtn';
            btn.textContent = l;
            btn.onclick = () => {
                btn.classList.toggle('active');
                if (btn.classList.contains('active')) {
                    if (!filters.levels.includes(l)) filters.levels.push(l);
                } else {
                    filters.levels = filters.levels.filter(x => x !== l);
                }
                applyFilters();
            };
            levelSection.appendChild(btn);
        });
        setupFakeSelects();
    }

    function applyFilters(){
      const cards = document.querySelectorAll('#catalog .titleCard');
      let anyVisible = false;

      const anyFilterActive =
        (filters.text && filters.text.length > 0) ||
        (filters.levels && filters.levels.length > 0) ||
        filters.colection || filters.duration || filters.lang || filters.ages;

      cards.forEach(card => {
        const txt = card.textContent.toLowerCase();
        const cardLevel = card.querySelector('.level')?.textContent.trim().toLowerCase() || '';
        const cardLangs = (card.querySelector('.langList')?.textContent || '')
          .split(/[,\s]+/)
          .map(l => l.trim().toUpperCase())
          .filter(Boolean);

        let visible = true;
        if (!anyFilterActive) visible = false;
        if (visible && filters.text && !txt.includes(filters.text)) visible = false;
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

        card.style.display = visible ? 'flex' : 'none';
        if (visible) anyVisible = true;
      });

      const catalog = document.getElementById('catalog');
      const help = document.getElementById('helpNote');
      const helpIcon = document.getElementById('helpIcon');

      catalog.style.display = anyVisible ? 'flex' : 'none';
      help.style.display = anyVisible ? 'none' : 'block';
      helpIcon.style.display = anyVisible ? 'flex' : 'none';
    }

    function resolveImagePath(imgPath){
        if (!imgPath) return '';
        if (imgPath.startsWith('/static')) {
            return imgPath;
        }
        return `/static/${imgPath}`;
    }

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
      const filters = document.getElementById('filtersBar');
      const btn = document.getElementById('toggleFiltersBtn');
      const visible = filters.style.display !== 'none';
      filters.style.display = visible ? 'none' : 'flex';
      btn.textContent = visible ? '🔍 Cerca avançada' : '✖️ Amaga filtres';
    });

    loadCatalog();
});
