/* Algoritmi puri, condivisi da interfaccia e test. Nessuna dipendenza dal DOM. */
(function (root) {
  'use strict';
  function search({rows, cols, start, end, walls = [], weights = {}, algorithm = 'bfs'}) {
    const size = rows * cols;
    if (!Number.isInteger(rows) || !Number.isInteger(cols) || rows < 1 || cols < 1 || size > 10000 ||
        !Number.isInteger(start) || !Number.isInteger(end) || start < 0 || end < 0 || start >= size || end >= size ||
        !['bfs', 'dijkstra'].includes(algorithm)) throw new Error('Mappa o algoritmo non valido');
    const blocked = new Set(walls);
    if (blocked.has(start) || blocked.has(end)) throw new Error('Partenza e arrivo devono essere liberi');
    const cost = id => weights[id] ?? 1;
    if (Object.entries(weights).some(([id, value]) => !Number.isInteger(Number(id)) || Number(id) < 0 || Number(id) >= size || !Number.isFinite(value) || value <= 0)) throw new Error('Costo non valido');
    const distances = Array(size).fill(Infinity), previous = Array(size).fill(-1), visited = [];
    distances[start] = 0;
    const frontier = [start], settled = new Set();
    let head = 0;
    while (algorithm === 'bfs' ? head < frontier.length : frontier.length > 0) {
      let node;
      if (algorithm === 'bfs') node = frontier[head++];
      else {
        let best = 0;
        for (let i = 1; i < frontier.length; i++) if (distances[frontier[i]] < distances[frontier[best]]) best = i;
        node = frontier.splice(best, 1)[0];
      }
      settled.add(node);
      visited.push(node);
      if (node === end) break;
      const row = Math.floor(node / cols), col = node % cols;
      const neighbors = [[row - 1, col], [row, col + 1], [row + 1, col], [row, col - 1]];
      for (const [r, c] of neighbors) {
        if (r < 0 || c < 0 || r >= rows || c >= cols) continue;
        const next = r * cols + c;
        if (blocked.has(next) || settled.has(next)) continue;
        const candidate = distances[node] + (algorithm === 'bfs' ? 1 : cost(next));
        if (candidate < distances[next]) {
          const first = distances[next] === Infinity;
          distances[next] = candidate;
          previous[next] = node;
          if (first) frontier.push(next);
        }
      }
    }
    const path = [];
    if (settled.has(end)) {
      for (let node = end; node !== -1; node = previous[node]) path.push(node);
      path.reverse();
    }
    return {visited, path, steps: path.length ? path.length - 1 : null,
      cost: path.length ? path.slice(1).reduce((sum, id) => sum + cost(id), 0) : null};
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = {search};
  else root.PathAlgorithms = {search};
})(typeof globalThis !== 'undefined' ? globalThis : this);
