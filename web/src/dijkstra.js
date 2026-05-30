export function dijkstra(nodes, edges, sourceId, targetId) {
  // Monta lista de adjacência
  const adj = {}
  for (const n of nodes) adj[n.id] = []
  for (const e of edges) {
    const srcId = typeof e.source === 'object' ? e.source.id : e.source
    const tgtId = typeof e.target === 'object' ? e.target.id : e.target
    if (adj[srcId] !== undefined) {
      adj[srcId].push({ to: tgtId, weight: e.weight })
    }
  }

  const dist = {}
  const parent = {}
  const visited = new Set()

  for (const n of nodes) dist[n.id] = Infinity
  dist[sourceId] = 0
  parent[sourceId] = null

  // Min-heap simples (array ordenado — ok para ~4600 nós)
  const heap = [{ id: sourceId, d: 0 }]

  while (heap.length > 0) {
    heap.sort((a, b) => a.d - b.d)
    const { id: u } = heap.shift()

    if (visited.has(u)) continue
    visited.add(u)
    if (u === targetId) break

    for (const { to, weight } of (adj[u] || [])) {
      if (!visited.has(to) && dist[u] + weight < dist[to]) {
        dist[to] = dist[u] + weight
        parent[to] = u
        heap.push({ id: to, d: dist[to] })
      }
    }
  }

  // Reconstrói caminho
  if (dist[targetId] === Infinity) return null

  const path = []
  let cur = targetId
  while (cur !== null) {
    path.unshift(cur)
    cur = parent[cur]
  }

  return { path, distance: dist[targetId] }
}
