function loadCatalog(base){
  const catalog = document.getElementById('catalog');
  catalog.innerHTML = '';
  catalog.style.display = 'none';

  for (const title in base) {
    const i = base[title];
    const img = resolveImagePath(i.image, title);
    const human = i["title-human"] || title;

    const collection = i.collection && i.collection.trim() !== "" ? `<span class="collection">${i.collection}</span>` : "";
    const levels    = i.levels && i.levels.trim() !== ""       ? `<span class="level">${i.levels}</span>` : "";
    const ages      = i.ages && i.ages.trim() !== ""           ? `<span class="ages">${i.ages}</span>` : "";
    const duration  = i.duration && i.duration.trim() !== ""   ? `<span class="duration">${i.duration}</span>` : "";
    const langs     = i.langs && i.langs.trim() !== ""         ? `<div class="langList">${i.langs}</div>` : "";
    const desc      = i.description && i.description.trim() !== "" ? `<div class="description">${i.description}</div>` : "";

    const metaTop = (levels || ages)
      ? `<div class="meta-top">${levels}${ages}</div>`
      : "";

    const meta = (collection || duration)
      ? `<div class="meta">${collection}${duration}</div>`
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
    };
    catalog.appendChild(card);
  }

  initFilters(base);
}

const filters = { text:'', collection:'', levels:[], duration:'', lang:'', ages:'' };

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

function initFilters(base){
  const colSet = new Set();
  const levSet = new Set();
  const durSet = new Set();
  const langSet = new Set();
  const ageSet = new Set();

  for(const t in base){
    const i = base[t];
    if(i.collection) colSet.add(i.collection.trim());
    if(i.levels) levSet.add(i.levels.trim());
    if(i.duration) durSet.add(i.duration.trim());
    if(i.ages) ageSet.add(i.ages.trim());
    if(i.langs) i.langs.split(',').map(x=>x.trim().toUpperCase()).forEach(l=>langSet.add(l));
  }

  fillSelect('#filterCollection', colSet);
  fillSelect('#filterDuration',  durSet);
  fillSelect('#filterLang',      langSet);
  fillSelect('#filterAges',      ageSet);

  const levelSection = document.getElementById('levelSection');
  levelSection.innerHTML = '';
  [...levSet].sort().forEach(l=>{
    const btn = document.createElement('button');
    btn.className = 'levelBtn';
    btn.textContent = l;
    btn.onclick = () => {
      btn.classList.toggle('active');
      if (btn.classList.contains('active')) {
        if (!filters.levels.includes(l)) filters.levels.push(l);
      } else {
        filters.levels = filters.levels.filter(x=>x!==l);
      }
      applyFilters();
    };
    levelSection.appendChild(btn);
  });
}

function applyFilters(){
  const cards = document.querySelectorAll('#catalog .titleCard');
  let anyVisible = false;

  const anyFilterActive =
    (filters.text && filters.text.length > 0) ||
    (filters.levels && filters.levels.length > 0) ||
    filters.collection || filters.duration || filters.lang || filters.ages;

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

    if (visible && filters.collection && !txt.includes(filters.collection.toLowerCase())) visible = false;
    if (visible && filters.duration && !txt.includes(filters.duration.toLowerCase())) visible = false;
    if (visible && filters.ages && !txt.includes(filters.ages.toLowerCase())) visible = false;

    card.style.display = visible ? 'flex' : 'none';
    if (visible) anyVisible = true;
  });

  const catalog = document.getElementById('catalog');
  const help = document.getElementById('helpNote');

  catalog.style.display = anyVisible ? 'flex' : 'none';
  if (help) {
      help.style.display = anyVisible ? 'none' : 'block';
  }
}

function resolveImagePath(imgPath,title){
  return "https://via.placeholder.com/80";
}

document.addEventListener('input', (e) => {
  if (e.target.id === 'searchInput') {
    filters.text = e.target.value.trim().toLowerCase();
    applyFilters();
  }
});

document.addEventListener('change', (e) => {
  if (e.target.matches('#filterCollection, #filterDuration, #filterLang, #filterAges')) {
    const key = e.target.id.replace('filter', '').toLowerCase();
    filters[key] = e.target.value || '';
    applyFilters();
  }
});

document.getElementById('toggleFiltersBtn').addEventListener('click', () => {
  const filters = document.getElementById('filtersBar');
  const btn = document.getElementById('toggleFiltersBtn');
  const visible = filters.style.display !== 'none';
  filters.style.display = visible ? 'none' : 'flex';
  btn.textContent = visible ? '🔍 Cerca avançada' : '✖️ Amaga filtres';
});

const titlesDataElement = document.getElementById('titles-data');
if (titlesDataElement) {
    const titlesData = JSON.parse(titlesDataElement.textContent);

    const base = {};
    titlesData.forEach(title => {
        // Robust language processing
        const languages = Array.isArray(title.languages) ? title.languages.map(l => l.language).join(', ') : '';

        base[title.machine_name] = {
            "title-human": title.human_name,
            "description": title.description,
            "levels": title.levels,
            "langs": languages,
            "ages": title.ages,
            "collection": title.collection,
            "duration": title.duration,
            "id": title.id,
            "image": null
        };
    });
    loadCatalog(base);
} else {
}
