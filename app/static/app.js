const grid = document.querySelector('#planet-grid');
const status = document.querySelector('#status');
const search = document.querySelector('#search');
const region = document.querySelector('#region');
const retry = document.querySelector('#retry');
const regions = {outer: 'Внешнее кольцо', core: 'Ядро', unknown: 'Неизведанные регионы'};
let controller;
let timer;

function element(tag, className, content) {
  const node = document.createElement(tag);
  node.className = className;
  if (content !== undefined) node.textContent = content;
  return node;
}

function card(planet, index) {
  const article = element('article', 'planet-card');
  const art = element('div', `card-art ${planet.color}`);
  art.setAttribute('aria-hidden', 'true');
  art.append(element('span', 'card-number', String(index + 1).padStart(2, '0')),
    element('div', 'orb'), element('span', 'terrain', planet.terrain));
  const body = element('div', 'card-body');
  const top = element('div', 'card-topline');
  top.append(element('h3', '', planet.name), element('span', '', '✦'));
  body.append(top, element('p', 'card-region', regions[planet.region]), element('p', '', planet.description));
  article.append(art, body);
  return article;
}

async function loadPlanets() {
  controller?.abort();
  const request = new AbortController();
  controller = request;
  grid.setAttribute('aria-busy', 'true');
  status.textContent = 'Загружаем координаты…';
  retry.hidden = true;
  const params = new URLSearchParams({q: search.value});
  if (region.value) params.set('region', region.value);
  try {
    const response = await fetch(`/api/planets?${params}`, {signal: request.signal});
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const planets = await response.json();
    if (request.signal.aborted) return;
    grid.replaceChildren(...planets.map(card));
    status.textContent = planets.length ? `Миров найдено: ${planets.length}` : 'Ничего не найдено. Попробуйте другое название или регион.';
  } catch (error) {
    if (request.signal.aborted) return;
    grid.replaceChildren();
    status.textContent = 'Связь с атласом потеряна. Попробуйте ещё раз.';
    retry.hidden = false;
  } finally {
    if (controller === request) grid.setAttribute('aria-busy', 'false');
  }
}

document.querySelector('#filters').addEventListener('submit', event => {
  event.preventDefault();
  clearTimeout(timer);
  loadPlanets();
});
search.addEventListener('input', () => {
  clearTimeout(timer);
  controller?.abort();
  timer = setTimeout(loadPlanets, 200);
});
region.addEventListener('change', () => { clearTimeout(timer); loadPlanets(); });
retry.addEventListener('click', loadPlanets);
loadPlanets();
