(() => {
  'use strict';
  const rows = 8, cols = 12, grid = document.querySelector('#path-grid');
  const status = document.querySelector('#path-status');
  const algorithm = document.querySelector('#algorithm');
  const mode = document.querySelector('#paint-mode');
  const startButton = document.querySelector('#path-start'), pauseButton = document.querySelector('#path-pause');
  let start = 25, end = 34, walls = new Set([5, 17, 29, 41, 65, 77]), weights = {};
  let result = null, position = 0, timer = null, running = false, focusId = 0;
  const cells = [];
  function paint() {
    const explored = new Set(result ? result.visited.slice(0, position) : []);
    const finished = result && position === result.visited.length;
    const path = new Set(finished ? result.path : []);
    cells.forEach((cell, id) => {
      const kind = id === start ? 'start' : id === end ? 'end' : walls.has(id) ? 'wall' : path.has(id) ? 'route' : explored.has(id) ? 'visited' : weights[id] ? 'weighted' : 'empty';
      cell.className = 'grid-cell ' + kind;
      cell.textContent = ({start: 'S', end: 'A', wall: '#', route: '*', visited: '·', weighted: '5', empty: ''})[kind];
      const name = ({start: 'partenza', end: 'arrivo', wall: 'ostacolo', route: 'percorso', visited: 'esplorata', weighted: 'terreno lento', empty: 'libera'})[kind];
      cell.setAttribute('aria-label', `Riga ${Math.floor(id / cols) + 1}, colonna ${id % cols + 1}: ${name}, costo ${weights[id] || 1}`);
      cell.tabIndex = id === focusId ? 0 : -1;
    });
    document.querySelector('#path-visited').textContent = position;
    document.querySelector('#path-length').textContent = finished && result.steps !== null ? result.steps : '—';
    document.querySelector('#path-cost').textContent = finished && result.cost !== null ? result.cost : '—';
    startButton.disabled = running || Boolean(finished);
    pauseButton.disabled = !running;
    document.querySelector('#path-step').disabled = running || Boolean(finished);
    startButton.textContent = position && !finished ? 'Riprendi' : 'Avvia';
  }
  function stop() { clearTimeout(timer); timer = null; running = false; }
  function reset(message = 'Ricerca azzerata. La mappa è conservata.') {
    stop(); result = null; position = 0; paint(); status.textContent = message;
  }
  function edit(id) {
    if (mode.value === 'start' && id !== end) { start = id; walls.delete(id); delete weights[id]; }
    else if (mode.value === 'end' && id !== start) { end = id; walls.delete(id); delete weights[id]; }
    else if (id === start || id === end) { status.textContent = 'Partenza e arrivo devono restare liberi e distinti. Scegli un’altra cella.'; return; }
    else if (mode.value === 'wall') { if (walls.has(id)) walls.delete(id); else walls.add(id); delete weights[id]; }
    else if (mode.value === 'weight') { walls.delete(id); if (weights[id]) delete weights[id]; else weights[id] = 5; }
    reset('Mappa modificata. La ricerca precedente è stata azzerata.');
  }
  for (let row = 0; row < rows; row++) {
    const line = document.createElement('div'); line.setAttribute('role', 'row');
    for (let col = 0; col < cols; col++) {
      const id = row * cols + col, holder = document.createElement('div'), cell = document.createElement('button');
      holder.setAttribute('role', 'gridcell'); cell.type = 'button'; cell.dataset.cell = id;
      cell.addEventListener('focus', () => { focusId = id; cells.forEach((c, n) => { c.tabIndex = n === id ? 0 : -1; }); });
      cell.addEventListener('click', () => edit(id));
      cell.addEventListener('keydown', event => {
        const offsets = {ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1]};
        if (!offsets[event.key]) return;
        event.preventDefault();
        const [dr, dc] = offsets[event.key];
        cells[Math.max(0, Math.min(rows - 1, row + dr)) * cols + Math.max(0, Math.min(cols - 1, col + dc))].focus();
      });
      cells.push(cell); holder.append(cell); line.append(holder);
    }
    grid.append(line);
  }
  function step() {
    if (!result) result = PathAlgorithms.search({rows, cols, start, end, walls: [...walls], weights, algorithm: algorithm.value});
    if (position < result.visited.length) position++;
    if (position === result.visited.length) {
      stop();
      status.textContent = result.path.length ? `Percorso trovato: ${result.steps} passi, costo ${result.cost}.` : 'Nessun percorso: prova a rimuovere un ostacolo.';
    } else status.textContent = `Ricerca ${running ? 'in corso' : 'passo passo'}: ${position} celle esplorate.`;
    paint();
  }
  function tick() { step(); if (running) timer = setTimeout(tick, 100); }
  startButton.addEventListener('click', () => {
    if (running) return;
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
      if (!result) result = PathAlgorithms.search({rows, cols, start, end, walls: [...walls], weights, algorithm: algorithm.value});
      position = result.visited.length - 1; step();
    } else { running = true; tick(); }
  });
  pauseButton.addEventListener('click', () => { stop(); paint(); status.textContent = 'In pausa. Puoi riprendere, avanzare di un passo o modificare la mappa.'; });
  document.querySelector('#path-step').addEventListener('click', step);
  document.querySelector('#path-reset').addEventListener('click', () => reset());
  document.querySelector('#path-clear').addEventListener('click', () => { walls = new Set(); weights = {}; start = 25; end = 34; reset('Mappa svuotata. Partenza e arrivo ripristinati.'); });
  algorithm.addEventListener('change', () => {
    reset('Algoritmo cambiato. Avvia una nuova ricerca.');
    document.querySelector('#algorithm-explanation').textContent = algorithm.value === 'bfs' ? 'BFS esplora i vicini a livelli: prima le celle a un passo, poi quelle a due. Sulla griglia trova il percorso con meno passi, ma ignora i costi del terreno.' : 'Dijkstra sceglie ogni volta la cella raggiungibile con il costo accumulato più basso. Con costi positivi trova il percorso meno costoso, anche quando richiede più passi.';
  });
  window.addEventListener('pagehide', stop);
  paint();
})();
