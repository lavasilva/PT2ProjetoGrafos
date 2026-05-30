import { useState, useEffect, useCallback, useRef } from 'react'
import GraphCanvas from './components/GraphCanvas'
import Sidebar from './components/Sidebar'
import Tooltip from './components/Tooltip'
import { dijkstra } from './dijkstra'

export default function App() {
  const [graphData, setGraphData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Ego-graph: subconjunto visível de nós e arestas
  const [egoGraph, setEgoGraph] = useState({ nodes: [], edges: [], centerIds: new Set() })

  // Índices pré-computados para busca rápida de vizinhos
  const adjRef = useRef({})  // id -> [{ id, weight, raw }]
  const nodeByIdRef = useRef({})

  const [highlightPath, setHighlightPath] = useState([])
  const [hoveredNode, setHoveredNode] = useState(null)
  const [selectedNode, setSelectedNode] = useState(null)
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })

  useEffect(() => {
    fetch('./graph_data.json')
      .then(r => { if (!r.ok) throw new Error(`Erro ${r.status}`); return r.json() })
      .then(data => {
        // Pré-computa adjacência
        const adj = {}
        const byId = {}
        for (const n of data.nodes) { adj[n.id] = []; byId[n.id] = n }
        for (const e of data.edges) {
          const s = e.source, t = e.target
          adj[s]?.push({ id: t, weight: e.weight })
          // grafo dirigido — só saída, mas para visualização adicionamos entrada também
          adj[t]?.push({ id: s, weight: e.weight })
        }
        adjRef.current = adj
        nodeByIdRef.current = byId
        setGraphData(data)
        setLoading(false)
      })
      .catch(e => { setError(e.message); setLoading(false) })
  }, [])

  // Expande o ego-graph a partir de um nó — adiciona ele e seus vizinhos
  const expandNode = useCallback((node) => {
    if (!graphData) return

    setEgoGraph(prev => {
      const existingIds = new Set(prev.nodes.map(n => n.id))
      const newCenterIds = new Set(prev.centerIds)
      newCenterIds.add(node.id)

      // Mantém posições dos nós já existentes
      const newNodes = prev.nodes.map(n => ({
        ...n,
        x: n.x ?? 0,
        y: n.y ?? 0,
      }))

      const newEdgesMap = new Map(prev.edges.map(e => {
        const s = typeof e.source === 'object' ? e.source.id : e.source
        const t = typeof e.target === 'object' ? e.target.id : e.target
        return [`${s}-${t}`, e]
      }))

      // Adiciona o nó central se não existir
      if (!existingIds.has(node.id)) {
        newNodes.push({ ...node })
        existingIds.add(node.id)
      }

      // Novos vizinhos aparecem ao redor do nó expandido
      const parentNode = newNodes.find(n => n.id === node.id)
      const px = parentNode?.fx ?? parentNode?.x ?? 0
      const py = parentNode?.fy ?? parentNode?.y ?? 0

      const neighbors = adjRef.current[node.id] || []
      const toAdd = neighbors.slice(0, 30)
      const angleStep = (2 * Math.PI) / Math.max(toAdd.length, 1)

      toAdd.forEach(({ id: nid, weight }, i) => {
        const neighborData = nodeByIdRef.current[nid]
        if (!neighborData) return
        if (!existingIds.has(nid)) {
          // Posição inicial ao redor do nó pai
          const angle = angleStep * i
          const spread = 80 + Math.random() * 40
          newNodes.push({
            ...neighborData,
            x: px + Math.cos(angle) * spread,
            y: py + Math.sin(angle) * spread,
          })
          existingIds.add(nid)
        }
        const key = `${node.id}-${nid}`
        if (!newEdgesMap.has(key)) {
          newEdgesMap.set(key, { source: node.id, target: nid, weight })
        }
      })

      // Adiciona arestas entre nós já existentes no ego-graph
      for (const n of newNodes) {
        for (const { id: nid, weight } of (adjRef.current[n.id] || [])) {
          if (existingIds.has(nid)) {
            const key = `${n.id}-${nid}`
            if (!newEdgesMap.has(key)) {
              newEdgesMap.set(key, { source: n.id, target: nid, weight })
            }
          }
        }
      }

      return {
        nodes: newNodes,
        edges: Array.from(newEdgesMap.values()),
        centerIds: newCenterIds,
      }
    })
  }, [graphData])

  const handleNodeHover = useCallback((node) => setHoveredNode(node), [])

  // Clique simples: só seleciona (dimmed nos outros)
  const handleNodeClick = useCallback((node) => {
    setSelectedNode(prev => prev?.id === node.id ? null : node)
  }, [])

  // Duplo clique: expande vizinhos
  const handleNodeDblClick = useCallback((node) => {
    setSelectedNode(null)
    expandNode(node)
  }, [expandNode])

  const handleSearch = useCallback((node) => {
    if (!node) return
    // Busca reseta o ego-graph e começa do nó buscado
    setEgoGraph({ nodes: [], edges: [], centerIds: new Set() })
    setHighlightPath([])
    setSelectedNode(null)
    setTimeout(() => expandNode(node), 50)
  }, [expandNode])

  const handleFindPath = useCallback((src, tgt) => {
    if (!src || !tgt || !graphData) { setHighlightPath([]); return }

    // Dijkstra nos dados completos
    const result = dijkstra(graphData.nodes, graphData.edges, src.id, tgt.id)
    if (!result) { alert(`Caminho não encontrado entre "${src.label}" e "${tgt.label}".`); return }

    const byId = nodeByIdRef.current
    const pathRaws = result.path.map(id => byId[id]?.raw).filter(Boolean)
    setHighlightPath(pathRaws)

    // Revela todos os nós do caminho no ego-graph
    setEgoGraph({ nodes: [], edges: [], centerIds: new Set() })
    setTimeout(() => {
      for (const id of result.path) {
        const node = byId[id]
        if (node) expandNode(node)
      }
    }, 50)
  }, [graphData, expandNode])

  const handleReset = useCallback(() => {
    setEgoGraph({ nodes: [], edges: [], centerIds: new Set() })
    setHighlightPath([])
    setSelectedNode(null)
    setHoveredNode(null)
  }, [])

  if (loading) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', flexDirection: 'column', gap: 12 }}>
      <div style={{ fontSize: 28 }}>🌐</div>
      <div style={{ color: '#94a3b8', fontSize: 14 }}>Carregando grafo...</div>
    </div>
  )

  if (error) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', flexDirection: 'column', gap: 12 }}>
      <div style={{ color: '#ef4444', fontSize: 14 }}>Erro: {error}</div>
      <div style={{ color: '#475569', fontSize: 11 }}>
        Rode <code style={{ background: '#1e293b', padding: '2px 6px', borderRadius: 4 }}>python -m src.export_graph_json</code> primeiro.
      </div>
    </div>
  )

  return (
    <div style={{ position: 'relative', width: '100vw', height: '100vh' }}
      onMouseMove={e => setMousePos({ x: e.clientX, y: e.clientY })}>

      <GraphCanvas
        graphData={graphData}
        egoGraph={egoGraph}
        highlightPath={highlightPath}
        onNodeHover={handleNodeHover}
        onNodeClick={handleNodeClick}
        onNodeDblClick={handleNodeDblClick}
        selectedNode={selectedNode}
      />

      <Sidebar
        graphData={graphData}
        filteredCat={null}
        setFilteredCat={() => {}}
        onSearch={handleSearch}
        onFindPath={handleFindPath}
        highlightPath={highlightPath}
        hoveredNode={hoveredNode}
        selectedNode={selectedNode}
        onReset={handleReset}
        egoStats={{ nodes: egoGraph.nodes.length, edges: egoGraph.edges.length }}
      />

      <Tooltip node={hoveredNode} x={mousePos.x} y={mousePos.y} />

      <div style={{
        position: 'absolute', bottom: 16, left: 16,
        background: '#0f172acc', backdropFilter: 'blur(8px)',
        border: '1px solid #1e293b', borderRadius: 8,
        padding: '8px 12px', fontSize: 10, color: '#475569', lineHeight: 1.8,
      }}>
        <div>🖱 Scroll — zoom &nbsp;·&nbsp; Arrastar — mover</div>
        <div>🖱 Clique num nó — expande vizinhos</div>
        {highlightPath.length > 0 && (
          <div style={{ color: '#f59e0b', marginTop: 4 }}>
            🟡 Caminho: {highlightPath.length} artigos · {highlightPath.length - 1} saltos
          </div>
        )}
      </div>
    </div>
  )
}
