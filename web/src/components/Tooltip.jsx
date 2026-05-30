export default function Tooltip({ node, x, y }) {
  if (!node) return null
  return (
    <div style={{
      position: 'fixed',
      left: x + 14,
      top: y - 10,
      background: '#1e293b',
      border: '1px solid #334155',
      borderRadius: 8,
      padding: '8px 12px',
      fontSize: 12,
      color: '#e2e8f0',
      pointerEvents: 'none',
      zIndex: 100,
      maxWidth: 220,
      boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
    }}>
      <div style={{ fontWeight: 700, marginBottom: 4 }}>{node.label}</div>
      <div style={{ color: '#94a3b8', fontSize: 11 }}>
        <span>Grau de saída: <b style={{ color: '#e2e8f0' }}>{node.degree}</b></span>
        <br />
        <span>Categoria: <b style={{ color: '#e2e8f0' }}>{node.cat}</b></span>
      </div>
    </div>
  )
}
