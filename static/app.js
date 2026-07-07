let deferredInstallPrompt = null;
let instruments = [];
let activeInstrumentId = 'guzheng';
let activeCategory = '全部';
let searchTerm = '';

const qs = selector => document.querySelector(selector);
const statsEl = qs('#stats');
const gridEl = qs('#instrumentGrid');
const partStackEl = qs('#partStack');
const techniqueChipsEl = qs('#techniqueChips');
const activeNameEl = qs('#activeInstrumentName');
const activeStoryEl = qs('#activeInstrumentStory');
const resultEl = qs('#recognitionResult');
const modelSelect = qs('#modelSelect');
const audioInput = qs('#audioInput');
const searchInput = qs('#instrumentSearch');
const categoryFiltersEl = qs('#categoryFilters');
const emptyStateEl = qs('#emptyState');

function showRecognitionMessage(title, message, isError = false) {
  resultEl.className = `result-card ${isError ? 'error' : ''}`;
  resultEl.innerHTML = `<strong>${title}</strong><small>${message}</small>`;
}

window.addEventListener('beforeinstallprompt', event => {
  event.preventDefault();
  deferredInstallPrompt = event;
});

function installApp() {
  if (!deferredInstallPrompt) {
    alert('如果浏览器未弹出安装，请使用浏览器菜单中的“安装应用”或 iOS 的“添加到主屏幕”。');
    return;
  }
  deferredInstallPrompt.prompt();
  deferredInstallPrompt = null;
}
qs('#installTop').addEventListener('click', installApp);
qs('#installMain').addEventListener('click', installApp);

function assetPath(path) {
  if (!path) return '';
  return path.replace(/^\/static\//, 'static/');
}

async function fetchJson(url) {
  const response = await fetch(url, { cache: 'no-store' });
  if (!response.ok) throw new Error(`${url} returned ${response.status}`);
  return response.json();
}

async function loadInstruments() {
  let data;
  try {
    data = await fetchJson('api/instruments');
  } catch (error) {
    data = await fetchJson('static/data/instruments.json');
  }
  instruments = data.items;
  statsEl.innerHTML = data.stats.map(item => `<div class="stat"><strong>${item.value}</strong><span>${item.label}</span></div>`).join('');
  activeInstrumentId = instruments[0]?.id || activeInstrumentId;
  renderFilters();
  renderGrid();
  renderWorkshop(activeInstrumentId);
}

function getCategories() {
  return ['全部', ...Array.from(new Set(instruments.map(item => item.category)))];
}

function renderFilters() {
  categoryFiltersEl.innerHTML = getCategories().map(category => `
    <button class="filter-chip ${category === activeCategory ? 'active' : ''}" type="button" data-category="${category}">${category}</button>
  `).join('');
  categoryFiltersEl.querySelectorAll('.filter-chip').forEach(button => {
    button.addEventListener('click', () => {
      activeCategory = button.dataset.category;
      renderFilters();
      renderGrid();
    });
  });
}

function filteredInstruments() {
  const normalized = searchTerm.trim().toLowerCase();
  return instruments.filter(item => {
    const inCategory = activeCategory === '全部' || item.category === activeCategory;
    const haystack = [item.name, item.pinyin, item.category, item.tone, item.era, ...item.parts, ...item.techniques].join(' ').toLowerCase();
    return inCategory && (!normalized || haystack.includes(normalized));
  });
}

function renderGrid() {
  const items = filteredInstruments();
  emptyStateEl.classList.toggle('hidden', items.length > 0);
  gridEl.innerHTML = items.map(item => `
    <article class="instrument-card ${item.id === activeInstrumentId ? 'active' : ''}" style="--instrument-gradient:${item.gradient}" data-id="${item.id}">
      <div class="instrument-image-wrap">
        <img class="instrument-image" src="${assetPath(item.image) || `static/photos/${item.id}.jpg`}" alt="${item.name}真实照片" />
      </div>
      <div class="instrument-top">
        <div><p class="eyebrow">${item.pinyin}</p><h3>${item.name}</h3></div>
        <div class="instrument-seal">${item.name.slice(0, 1)}</div>
      </div>
      <p>${item.summary}</p>
      <div class="meta-list">
        <span>${item.category}</span><span>${item.era}</span><span>${item.tone}</span>
      </div>
    </article>
  `).join('');
  gridEl.querySelectorAll('.instrument-card').forEach(card => {
    card.addEventListener('click', () => {
      activeInstrumentId = card.dataset.id;
      renderGrid();
      renderWorkshop(activeInstrumentId);
      qs('#structure').scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
}

function renderWorkshop(id) {
  const item = instruments.find(entry => entry.id === id) || instruments[0];
  if (!item) return;
  activeNameEl.textContent = `${item.name}结构`;
  activeStoryEl.textContent = item.story;
  partStackEl.innerHTML = `
    <img class="workshop-image" src="${assetPath(item.image) || `static/photos/${item.id}.jpg`}" alt="${item.name}结构照片" />
    ${item.parts.map((part, index) => `<div class="part-card" style="--i:${index}"><b>${String(index + 1).padStart(2, '0')}</b> · ${part}</div>`).join('')}
  `;
  techniqueChipsEl.innerHTML = [...item.techniques, ...item.heritage].map(text => `<span>${text}</span>`).join('');
}

searchInput.addEventListener('input', event => {
  searchTerm = event.target.value;
  renderGrid();
});

audioInput.addEventListener('change', event => {
  const file = event.target.files?.[0];
  qs('#fileName').textContent = file ? `${file.name} · ${(file.size / 1024 / 1024).toFixed(2)} MB` : '建议 3–10 秒，环境噪声越低越准确';
  if (file) {
    resultEl.className = 'result-card hidden';
    resultEl.innerHTML = '';
  }
});

qs('#recognizeForm').addEventListener('submit', async event => {
  event.preventDefault();
  const form = event.currentTarget;
  const submitButton = form.querySelector('button[type="submit"]');
  const file = audioInput.files?.[0];
  if (!file) {
    showRecognitionMessage('请先选择音频', '点击上方上传区域，选择一段 3–10 秒的传统乐器录音后再开始识别。', true);
    return;
  }
  const formData = new FormData(form);
  showRecognitionMessage('正在识别…', '正在生成频谱并调用智能识别模型，请稍候。');
  submitButton.disabled = true;
  submitButton.textContent = '识别中…';
  try {
    const response = await fetch('api/recognize', { method: 'POST', body: formData });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || '识别失败');
    resultEl.className = `result-card ${data.ok ? '' : 'error'}`;
    resultEl.innerHTML = `<strong>${data.instrument || '未识别'}</strong><small>${data.status} · 文件：${data.filename} · 模型：${data.model}</small>`;
  } catch (error) {
    showRecognitionMessage('识别暂不可用', error.message, true);
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = '开始识别';
  }
});

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('service-worker.js').catch(console.warn);
}

loadInstruments();
loadModels();

async function loadModels() {
  try {
    const data = await fetchJson('api/models');
    modelSelect.innerHTML = data.models.map((model, index) => `<option value="${model}" ${index === 0 ? 'selected' : ''}>${model}</option>`).join('');
  } catch (error) {
    modelSelect.innerHTML = '<option value="">静态展示版：识别需本地启动</option>';
    console.warn(error);
  }
}
