'use strict';
const assert = require('node:assert/strict');
const {search} = require('../lab/percorso/algorithms.js');
const base = {rows: 3, cols: 5, start: 5, end: 9, weights: {6: 5, 7: 5, 8: 5}};
const bfs = search({...base, algorithm: 'bfs'}), dijkstra = search({...base, algorithm: 'dijkstra'});
assert.equal(bfs.steps, 4); assert.equal(bfs.cost, 16);
assert.equal(dijkstra.steps, 6); assert.equal(dijkstra.cost, 6);
assert.equal(search({...base, walls: [4, 8, 14]}).path.length, 0);
assert.deepEqual(search({rows: 1, cols: 1, start: 0, end: 0}).path, [0]);
assert.throws(() => search({...base, weights: {6: -1}}));
// Un oracolo indipendente Bellman-Ford controlla il costo ottimo su mappe deterministiche.
let seed = 771;
function random() { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; }
for (let trial = 0; trial < 80; trial++) {
  const rows = 5, cols = 7, count = rows * cols, walls = [], weights = {};
  for (let i = 1; i < count - 1; i++) { if (random() < .2) walls.push(i); else weights[i] = random() < .3 ? 5 : 1; }
  const blocked = new Set(walls);
  const edges = [];
  for (let u = 0; u < count; u++) for (let v = 0; v < count; v++) {
    if (!blocked.has(u) && !blocked.has(v) && Math.abs(Math.floor(u / cols) - Math.floor(v / cols)) + Math.abs(u % cols - v % cols) === 1) edges.push([u, v]);
  }
  for (const algorithm of ['bfs', 'dijkstra']) {
    const dist = Array(count).fill(Infinity); dist[0] = 0;
    for (let k = 0; k < count - 1; k++) for (const [u, v] of edges) dist[v] = Math.min(dist[v], dist[u] + (algorithm === 'bfs' ? 1 : weights[v] || 1));
    const result = search({rows, cols, start: 0, end: count - 1, walls, weights, algorithm});
    assert.equal(algorithm === 'bfs' ? result.steps ?? Infinity : result.cost ?? Infinity, dist[count - 1]);
    if (result.path.length) {
      assert.equal(result.path[0], 0); assert.equal(result.path.at(-1), count - 1);
      assert.equal(new Set(result.path).size, result.path.length);
      result.path.forEach((v, i) => { assert(!blocked.has(v)); if (i) assert(edges.some(([a, b]) => a === result.path[i - 1] && b === v)); });
    }
  }
}
console.log('PASS: BFS/Dijkstra, terreno pesato, percorso assente, estremi e 160 confronti con oracolo indipendente.');
