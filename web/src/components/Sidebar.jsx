import { useState, useMemo } from 'react'

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

const s = {
  panel: {
    position: 'absolute', top: 0, right: 0,
    width: 300, height: '100vh',
    background: '#0f172acc',
    backdropFilter: 'blur(12px)',
    borderLeft: '1px solid #1e293b',
    display: 'flex', flexDirection: 'column',
    zIndex: 10, overflow: 'hidden',
  },
  header: {
    padding: '16px 16px 12px',
    borderBottom: '1px solid #1e293b',
  },
  title: { fontSize: 13, fontWeight: 700, color: '#e2e8f0', marginBottom: 2 },
  subtitle: { fontSize: 11, color: '#64748b' },
  section: { padding: '12px 16px', borderBottom: '1px solid #1e293b' },
  label: { fontSize: 10, color: '#64748b', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 6 },
  input: {
    width: '100%', background: '#1e293b', border: '1px solid #334155',
    borderRadius: 6, padding: '7px 10px', color: '#e2e8f0', fontSize: 12,
    outline: 'none',
  },
  dropdown: {
    position: 'absolute', top: '100%', left: 0, right: 0,
    background: '#1e293b', border: '1px solid #334155', borderRadius: 6,
    maxHeight: 200, overflowY: 'auto', zIndex: 20,
  },
  dropItem: {
    padding: '7px 10px', fontSize: 12, cursor: 'pointer', color: '#cbd5e1',
  },
  btn: {
    padding: '7px 12px', borderRadius: 6, border: 'none',
    cursor: 'pointer', fontSize: 11, fontWeight: 600,
  },
  catDot: { width: 8, height: 8, borderRadius: '50%', flexShrink: 0 },
  nodeCard: {
    margin: '8px 16px', background: '#1e293b',
    borderRadius: 8, padding: '10px 12px',
    border: '1px solid #334155',
  },
}

export default function Sidebar({
  graphData, filteredCat, setFilteredCat,
  onSearch, onFindPath, highlightPath,
  hoveredNode, selectedNode, onReset, egoStats,
}) {
  const [searchTerm, setSearchTerm] = useState('')
  const [showSearchDrop, setShowSearchDrop] = useState(false)
  const [pathFrom, setPathFrom] = useState('')
  const [pathTo, setPathTo] = useState('')
  const [showFromDrop, setShowFromDrop] = useState(false)
  const [showToDrop, setShowToDrop] = useState(false)

  const categories = graphData?.meta?.categories || []
  const colorMap = CATEGORY_COLORS

  const allLabels = useMemo(() =>
    graphData?.nodes?.map(n => n.label) || [], [graphData])

  const searchSuggestions = allLabels
    .filter(l => l.toLowerCase().includes(searchTerm.toLowerCase()) && searchTerm.length > 1)
    .slice(0, 8)

  const fromSuggestions = allLabels
    .filter(l => l.toLowerCase().includes(pathFrom.toLowerCase()) && pathFrom.length > 1)
    .slice(0, 8)

  const toSuggestions = allLabels
    .filter(l => l.toLowerCase().includes(pathTo.toLowerCase()) && pathTo.length > 1)
    .slice(0, 8)

  const selectSearch = (label) => {
    setSearchTerm(label)
    setShowSearchDrop(false)
    const node = graphData?.nodes?.find(n => n.label === label)
    onSearch(node || null)
  }

  const handleSearchInput = (val) => {
    setSearchTerm(val)
    setShowSearchDrop(true)
    const node = graphData?.nodes?.find(n =>
      n.label.toLowerCase().includes(val.toLowerCase()))
    onSearch(val.length > 1 ? node || null : null)
  }

  const handleFindPath = () => {
    if (!pathFrom || !pathTo) return
    const src = graphData?.nodes?.find(n => n.label === pathFrom)
    const tgt = graphData?.nodes?.find(n => n.label === pathTo)
    if (src && tgt) onFindPath(src, tgt)
  }

  const displayNode = hoveredNode || selectedNode

  return (
    <div style={s.panel}>
      <div style={s.header}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={s.title}>🌐 Wikispeedia Graph</div>
            <div style={s.subtitle}>
              {graphData
                ? `${graphData.meta.num_nodes.toLocaleString()} artigos · ${graphData.meta.num_edges.toLocaleString()} links`
                : 'Carregando...'}
            </div>
          </div>
          {egoStats?.nodes > 0 && (
            <button
              style={{ ...s.btn, background: '#1e293b', color: '#64748b', fontSize: 10, padding: '4px 8px' }}
              onClick={onReset}
              title="Limpar grafo">
              ↺ Reset
            </button>
          )}
        </div>
        {egoStats?.nodes > 0 && (
          <div style={{ marginTop: 6, fontSize: 10, color: '#334155' }}>
            Explorando: <span style={{ color: '#2dd4bf' }}>{egoStats.nodes} artigos</span> · <span style={{ color: '#475569' }}>{egoStats.edges} conexões</span>
          </div>
        )}
      </div>

      {/* Busca de artigo com picklist */}
      <div style={s.section}>
        <div style={s.label}>Buscar artigo</div>
        <div style={{ position: 'relative' }}>
          <input
            style={s.input}
            placeholder="Digite o nome..."
            value={searchTerm}
            onChange={e => handleSearchInput(e.target.value)}
            onFocus={() => setShowSearchDrop(true)}
            onBlur={() => setTimeout(() => setShowSearchDrop(false), 150)}
          />
          {showSearchDrop && searchSuggestions.length > 0 && (
            <div style={s.dropdown}>
              {searchSuggestions.map(l => (
                <div
                  key={l}
                  style={s.dropItem}
                  onMouseEnter={e => e.currentTarget.style.background = '#334155'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                  onMouseDown={() => selectSearch(l)}
                >
                  {l}
                </div>
              ))}
            </div>
          )}
        </div>
        {searchTerm && (
          <button
            style={{ ...s.btn, background: 'transparent', color: '#64748b', padding: '4px 0', fontSize: 10, marginTop: 4 }}
            onClick={() => { setSearchTerm(''); onSearch(null) }}>
            ✕ Limpar busca
          </button>
        )}
      </div>

      {/* Caminho mínimo */}
      <div style={s.section}>
        <div style={s.label}>Caminho mínimo (Dijkstra)</div>
        <div style={{ position: 'relative', marginBottom: 6 }}>
          <input
            style={s.input}
            placeholder="De..."
            value={pathFrom}
            onChange={e => { setPathFrom(e.target.value); setShowFromDrop(true) }}
            onBlur={() => setTimeout(() => setShowFromDrop(false), 150)}
          />
          {showFromDrop && fromSuggestions.length > 0 && (
            <div style={s.dropdown}>
              {fromSuggestions.map(l => (
                <div key={l} style={s.dropItem}
                  onMouseEnter={e => e.currentTarget.style.background = '#334155'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                  onMouseDown={() => { setPathFrom(l); setShowFromDrop(false) }}>
                  {l}
                </div>
              ))}
            </div>
          )}
        </div>
        <div style={{ position: 'relative', marginBottom: 8 }}>
          <input
            style={s.input}
            placeholder="Para..."
            value={pathTo}
            onChange={e => { setPathTo(e.target.value); setShowToDrop(true) }}
            onBlur={() => setTimeout(() => setShowToDrop(false), 150)}
          />
          {showToDrop && toSuggestions.length > 0 && (
            <div style={s.dropdown}>
              {toSuggestions.map(l => (
                <div key={l} style={s.dropItem}
                  onMouseEnter={e => e.currentTarget.style.background = '#334155'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                  onMouseDown={() => { setPathTo(l); setShowToDrop(false) }}>
                  {l}
                </div>
              ))}
            </div>
          )}
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          <button
            style={{ ...s.btn, background: '#0ea5e9', color: '#fff', flex: 1 }}
            onClick={handleFindPath}>
            Calcular caminho
          </button>
          {highlightPath?.length > 0 && (
            <button
              style={{ ...s.btn, background: '#334155', color: '#94a3b8' }}
              onClick={() => { onFindPath(null, null); setPathFrom(''); setPathTo('') }}>
              ✕
            </button>
          )}
        </div>
        {highlightPath?.length > 0 && (
          <div style={{ marginTop: 8, fontSize: 11, color: '#f59e0b' }}>
            {highlightPath.length} artigos · {highlightPath.length - 1} saltos
          </div>
        )}
      </div>

      {/* Info do nó */}
      {displayNode && (
        <div style={s.section}>
          <div style={s.label}>Artigo selecionado</div>
          <div style={s.nodeCard}>
            <div style={{ fontSize: 12, fontWeight: 600, color: '#e2e8f0', marginBottom: 4 }}>
              {displayNode.label}
            </div>
            <div style={{ fontSize: 11, color: '#94a3b8', display: 'flex', gap: 8 }}>
              <span>Grau: <b style={{ color: '#e2e8f0' }}>{displayNode.degree}</b></span>
              <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <span style={{ ...s.catDot, background: colorMap[displayNode.cat] }} />
                {displayNode.cat}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Dica de exploração */}
      <div style={{ ...s.section, flex: 1, overflowY: 'auto' }}>
        <div style={s.label}>Como explorar</div>
        <div style={{ fontSize: 11, color: '#475569', lineHeight: 1.7 }}>
          <div style={{ marginBottom: 6 }}>🔍 <b style={{ color: '#64748b' }}>Busque</b> qualquer artigo para começar</div>
          <div style={{ marginBottom: 6 }}>🖱 <b style={{ color: '#64748b' }}>Clique</b> num nó para ver suas conexões em destaque</div>
          <div style={{ marginBottom: 6 }}>🖱 <b style={{ color: '#64748b' }}>Duplo clique</b> para expandir os vizinhos do nó</div>
          <div style={{ marginBottom: 6 }}>🛤 <b style={{ color: '#64748b' }}>Caminho mínimo</b> revela a rota entre dois artigos</div>
          <div>↺ <b style={{ color: '#64748b' }}>Reset</b> limpa e começa uma nova exploração</div>
        </div>
        {graphData && (
          <div style={{ marginTop: 16 }}>
            <div style={s.label}>Categorias</div>
            {graphData.meta.categories.map(cat => (
              <div key={cat} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '3px 0' }}>
                <div style={{ ...s.catDot, background: CATEGORY_COLORS[cat] || '#94a3b8' }} />
                <span style={{ fontSize: 11, color: '#475569' }}>{cat}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
