import { useEffect, useRef, useCallback } from 'react'
import * as d3 from 'd3'

const CATEGORY_COLORS = {
  "Science":    "#34d399",
  "History":    "#f59e0b",
  "Geography":  "#38bdf8",
  "Politics":   "#f87171",
  "Arts":       "#c084fc",
  "Religion":   "#fb923c",
  "Sports":     "#4ade80",
  "Philosophy": "#e879f9",
  "Nature":     "#86efac",
  "People":     "#67e8f9",
  "Other":      "#94a3b8",
}

export default function GraphCanvas({
  graphData,
  egoGraph,
  highlightPath,
  onNodeHover,
  onNodeClick,
  onNodeDblClick,
  selectedNode,
}) {
  const canvasRef = useRef(null)
  const simRef = useRef(null)
  const stateRef = useRef({
    nodes: [], edges: [], transform: d3.zoomIdentity,
    hoveredNode: null, highlightPath: new Set(),
    selectedNode: null,
  })

  useEffect(() => {
    stateRef.current.highlightPath = new Set(highlightPath || [])
    stateRef.current.selectedNode = selectedNode
    if (!canvasRef.current) return
    const canvas = canvasRef.current
    draw(canvas.getContext('2d'), canvas.width, canvas.height)
  }, [highlightPath, selectedNode])

  useEffect(() => {
    if (!canvasRef.current) return
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    const W = canvas.width = window.innerWidth
    const H = canvas.height = window.innerHeight

    if (simRef.current) simRef.current.stop()

    if (!egoGraph || egoGraph.nodes.length === 0) {
      stateRef.current.nodes = []
      stateRef.current.edges = []
      draw(ctx, W, H)
      return
    }

    const nodes = egoGraph.nodes.map(n => ({ ...n, fx: null, fy: null }))
    const edges = egoGraph.edges.map(e => ({ ...e }))

    stateRef.current.nodes = nodes
    stateRef.current.edges = edges

    const sim = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(edges).id(d => d.id).distance(d => {
        return 80 + 40 * (1 - (d.target.degree || 0) / 200)
      }).strength(0.5))
      .force('charge', d3.forceManyBody().strength(-200))
      .force('center', d3.forceCenter(W / 2, H / 2).strength(0.05))
      .force('collision', d3.forceCollide(d => d.size + 8))
      .alphaDecay(0.03)
      .on('tick', () => { if (canvasRef.current) draw(ctx, W, H) })

    simRef.current = sim

    const zoom = d3.zoom()
      .scaleExtent([0.1, 10])
      .on('zoom', e => {
        stateRef.current.transform = e.transform
        draw(ctx, W, H)
      })
    d3.select(canvas).call(zoom)

    canvas.onmousemove = (e) => {
      const { nodes, transform } = stateRef.current
      const [mx, my] = transform.invert([e.offsetX, e.offsetY])
      let found = null
      for (const n of nodes) {
        if (!n.x) continue
        const dx = n.x - mx, dy = n.y - my
        if (Math.sqrt(dx * dx + dy * dy) < n.size + 8) { found = n; break }
      }
      stateRef.current.hoveredNode = found
      onNodeHover(found)
      draw(ctx, canvas.width, canvas.height)
    }

    let clickTimer = null
    canvas.onclick = () => {
      const { hoveredNode } = stateRef.current
      if (!hoveredNode) return
      if (clickTimer) {
        clearTimeout(clickTimer)
        clickTimer = null
        onNodeDblClick(hoveredNode)
      } else {
        clickTimer = setTimeout(() => {
          clickTimer = null
          onNodeClick(hoveredNode)
        }, 220)
      }
    }

    return () => {
      if (simRef.current) simRef.current.stop()
      canvas.onmousemove = null
      canvas.onclick = null
      if (clickTimer) clearTimeout(clickTimer)
    }
  }, [egoGraph])

  useEffect(() => {
    if (!canvasRef.current) return
    const canvas = canvasRef.current
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
    draw(canvas.getContext('2d'), canvas.width, canvas.height)
  }, [])

  const draw = useCallback((ctx, W, H) => {
    const { nodes, edges, transform, hoveredNode, highlightPath: hlSet, selectedNode: selNode } = stateRef.current
    const k = transform.k
    const hasPath = hlSet.size > 0
    const hasSelected = !!selNode && !hasPath

    const selectedNeighbors = new Set()
    if (hasSelected) {
      selectedNeighbors.add(selNode.id)
      for (const e of edges) {
        const s = typeof e.source === 'object' ? e.source.id : e.source
        const t = typeof e.target === 'object' ? e.target.id : e.target
        if (s === selNode.id) selectedNeighbors.add(t)
        if (t === selNode.id) selectedNeighbors.add(s)
      }
    }

    ctx.save()
    ctx.clearRect(0, 0, W, H)

    if (nodes.length === 0) {
      ctx.fillStyle = '#1e293b'
      ctx.fillRect(0, 0, W, H)
      ctx.font = 'bold 18px Segoe UI'
      ctx.fillStyle = '#ffffff'
      ctx.textAlign = 'center'
      ctx.fillText('Busque um artigo para começar a explorar', W / 2, H / 2 - 10)
      ctx.font = '13px Segoe UI'
      ctx.fillStyle = '#e1e1e1'
      ctx.fillText('Digite o nome de qualquer artigo da Wikipedia na barra lateral', W / 2, H / 2 + 20)
      ctx.restore()
      return
    }

    ctx.translate(transform.x, transform.y)
    ctx.scale(k, k)

    const localDegree = {}
    for (const e of edges) {
      const s = typeof e.source === 'object' ? e.source.id : e.source
      const t = typeof e.target === 'object' ? e.target.id : e.target
      localDegree[s] = (localDegree[s] || 0) + 1
      localDegree[t] = (localDegree[t] || 0) + 1
    }
    const isCenterNode = (id) => egoGraph?.centerIds?.has(id)

    for (const e of edges) {
      const src = e.source, tgt = e.target
      if (!src?.x || !tgt?.x) continue
      const srcId = src.id, tgtId = tgt.id
      const inPath = hasPath && hlSet.has(src.raw) && hlSet.has(tgt.raw)
      const dimmedBySelected = hasSelected && !(selectedNeighbors.has(srcId) || selectedNeighbors.has(tgtId))
      const dimmedByPath = hasPath && !inPath

      const srcPeriph = !isCenterNode(srcId) && (localDegree[srcId] || 0) <= 2
      const tgtPeriph = !isCenterNode(tgtId) && (localDegree[tgtId] || 0) <= 2
      if (srcPeriph && tgtPeriph && !inPath) continue

      ctx.beginPath()
      ctx.moveTo(src.x, src.y)
      ctx.lineTo(tgt.x, tgt.y)

      if (inPath) {
        ctx.strokeStyle = '#f59e0b'; ctx.lineWidth = 2.5 / k; ctx.globalAlpha = 1
      } else if (dimmedByPath || dimmedBySelected) {
        ctx.strokeStyle = '#1e293b'; ctx.lineWidth = 0.5 / k; ctx.globalAlpha = 0
      } else if (hasSelected) {
        ctx.strokeStyle = '#94a3b8'; ctx.lineWidth = 1.5 / k; ctx.globalAlpha = 0.85
      } else if (srcPeriph || tgtPeriph) {
        ctx.strokeStyle = '#334155'; ctx.lineWidth = 0.8 / k; ctx.globalAlpha = 0.25
      } else {
        ctx.strokeStyle = '#64748b'; ctx.lineWidth = 1.2 / k; ctx.globalAlpha = 0.55
      }
      ctx.stroke()
      ctx.globalAlpha = 1
    }

    for (const n of nodes) {
      if (!n.x) continue
      const inPath = hasPath && hlSet.has(n.raw)
      const isHovered = hoveredNode?.id === n.id
      const isSelected = hasSelected && selNode?.id === n.id
      const isNeighbor = selectedNeighbors.has(n.id)
      const isCenter = egoGraph?.centerIds?.has(n.id)
      const dimmed = (hasSelected && !selectedNeighbors.has(n.id)) || (hasPath && !inPath)

      const color = CATEGORY_COLORS[n.cat] || '#94a3b8'
      const r = isCenter ? n.size + 4 : n.size
      const isActive = isHovered || inPath || isSelected || isCenter

      ctx.globalAlpha = dimmed ? 0 : 1

      if (isCenter && !dimmed) {
        ctx.shadowColor = color
        ctx.shadowBlur = 14 / k
      }

      ctx.beginPath()
      ctx.arc(n.x, n.y, isActive ? r + 3 : r, 0, Math.PI * 2)
      ctx.fillStyle = inPath ? '#f59e0b' : isSelected ? '#ffffff' : color
      ctx.fill()
      ctx.shadowBlur = 0

      ctx.beginPath()
      ctx.arc(n.x, n.y, isActive ? r + 3 : r, 0, Math.PI * 2)
      ctx.strokeStyle = isActive ? (inPath ? '#f59e0b' : '#ffffff') : '#0f172a'
      ctx.lineWidth = isActive ? 2 / k : 1 / k
      ctx.stroke()

      if (!dimmed && r > 3) {
        const fontSize = Math.max(12, Math.min(16, r * 0.7)) / k
        ctx.font = `${isCenter ? 'bold ' : ''}${fontSize}px Segoe UI`
        ctx.textAlign = 'center'
        ctx.textBaseline = 'top'
        const rEff = isActive ? r + 3 : r
        const label = n.label.substring(0, 18)
        const textW = ctx.measureText(label).width
        const tx = n.x
        const ty = n.y + rEff + 3 / k

        const pad = 3 / k
        ctx.fillStyle = 'rgba(15,23,42,0.75)'
        ctx.beginPath()
        ctx.roundRect(tx - textW / 2 - pad, ty - pad, textW + pad * 2, fontSize + pad * 2, 3 / k)
        ctx.fill()

        ctx.fillStyle = isCenter ? '#ffffff' : '#cbd5e1'
        ctx.globalAlpha = 1
        ctx.fillText(label, tx, ty)
        ctx.textBaseline = 'alphabetic'
      }
      ctx.globalAlpha = 1
    }

    ctx.restore()

    ctx.font = '10px Segoe UI'
    ctx.fillStyle = '#334155'
    ctx.textAlign = 'left'
    if (nodes.length > 0) {
      ctx.fillText(
        `${nodes.length} artigos · ${edges.length} conexões visíveis — clique num nó para expandir`,
        12, H - 16
      )
    }
  }, [egoGraph])

  return (
    <canvas
      ref={canvasRef}
      style={{ position: 'absolute', top: 0, left: 0, background: '#0f172a', cursor: 'crosshair' }}
    />
  )
}
