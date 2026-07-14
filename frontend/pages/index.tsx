import dynamic from 'next/dynamic'
import Head from 'next/head'
import { useEffect, useState } from 'react'

function RadarChart({ values }: { values: Array<{ label: string; value: number }> }) {
  const size = 180
  const center = size / 2
  const radius = 70
  const points = values.map((item, index) => {
    const angle = (-Math.PI / 2) + (index * (Math.PI * 2)) / values.length
    const x = center + Math.cos(angle) * radius * item.value
    const y = center + Math.sin(angle) * radius * item.value
    return `${x},${y}`
  })

  return (
    <svg viewBox={`0 0 ${size} ${size}`} width="100%" height="180" style={{ maxWidth: 220 }}>
      <circle cx={center} cy={center} r={radius * 0.33} fill="none" stroke="#ddd" />
      <circle cx={center} cy={center} r={radius * 0.66} fill="none" stroke="#ddd" />
      <circle cx={center} cy={center} r={radius} fill="none" stroke="#ddd" />
      {values.map((item, index) => {
        const angle = (-Math.PI / 2) + (index * (Math.PI * 2)) / values.length
        const x = center + Math.cos(angle) * radius
        const y = center + Math.sin(angle) * radius
        return <line key={item.label} x1={center} y1={center} x2={x} y2={y} stroke="#ddd" />
      })}
      <polygon points={points.join(' ')} fill="rgba(192,57,43,0.35)" stroke="#c0392b" strokeWidth="2" />
    </svg>
  )
}

function TrendChart({ data }: { data: Array<{ anio: number; valor: number }> }) {
  if (!data.length) return null
  const max = Math.max(...data.map((item) => item.valor)) || 1
  const min = Math.min(...data.map((item) => item.valor)) || 0
  const width = 240
  const height = 120
  const padding = 20
  const points = data.map((item, index) => {
    const x = padding + (index * (width - padding * 2)) / Math.max(data.length - 1, 1)
    const y = height - padding - ((item.valor - min) / Math.max(max - min, 1)) * (height - padding * 2)
    return `${x},${y}`
  })

  return (
    <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="140" style={{ maxWidth: 280 }}>
      <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="#ddd" />
      <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="#ddd" />
      <polyline fill="none" stroke="#2DC4B2" strokeWidth="3" points={points.join(' ')} />
      {data.map((item, index) => {
        const x = padding + (index * (width - padding * 2)) / Math.max(data.length - 1, 1)
        const y = height - padding - ((item.valor - min) / Math.max(max - min, 1)) * (height - padding * 2)
        return <circle key={`${item.anio}`} cx={x} cy={y} r="3" fill="#c0392b" />
      })}
    </svg>
  )
}

const Map = dynamic(() => import('../components/Map'), { ssr: false })

type Metrics = {
  total_municipios: number
  average_ira_score: number | null
  count_by_level: Record<string, number>
}

export default function Home() {
  const [selected, setSelected] = useState<any>(null)
  const [search, setSearch] = useState('')
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [results, setResults] = useState<any[]>([])
  const [anio, setAnio] = useState(2024)
  const [escenario, setEscenario] = useState('Base')
  const [detalle, setDetalle] = useState<any>(null)
  const [cultivos, setCultivos] = useState<any[]>([])
  const [historial, setHistorial] = useState<any[]>([])
  const [alerta, setAlerta] = useState<any>(null)
  const [dimensiones, setDimensiones] = useState<Record<string, number | null>>({})
  const [cultivoSeleccionado, setCultivoSeleccionado] = useState('')
  const [tendenciaCultivo, setTendenciaCultivo] = useState<Array<{ anio: number; valor: number }>>([])

  const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000'

  useEffect(() => {
    fetch(`${apiBase}/metrics`)
      .then((r) => r.json())
      .then(setMetrics)
      .catch((e) => console.warn('Could not fetch metrics', e))
  }, [apiBase])

  useEffect(() => {
    const url = new URL(`${apiBase}/municipios`)
    if (search) url.searchParams.set('q', search)
    url.searchParams.set('per_page', '50')
    fetch(url.toString())
      .then((r) => r.json())
      .then((data) => setResults(data))
      .catch((e) => console.warn('Could not fetch municipios', e))
  }, [apiBase, search])

  useEffect(() => {
    if (!selected?.divipola) {
      setDetalle(null)
      setCultivos([])
      setHistorial([])
      setAlerta(null)
      setDimensiones({})
      setCultivoSeleccionado('')
      setTendenciaCultivo([])
      return
    }

    const divipola = selected.divipola
    Promise.all([
      fetch(`${apiBase}/municipios/${divipola}`).then((r) => r.json()),
      fetch(`${apiBase}/municipios/${divipola}/cultivos`).then((r) => r.json()),
      fetch(`${apiBase}/municipios/${divipola}/cultivos/historico`).then((r) => r.json()),
      fetch(`${apiBase}/alertas/municipio/${divipola}`).then((r) => r.json()),
      fetch(`${apiBase}/municipios/${divipola}/dimensiones`).then((r) => r.json()),
    ])
      .then(([detalleData, cultivosData, historialData, alertaData, dimensionesData]) => {
        setDetalle(detalleData)
        setCultivos(cultivosData.cultivos || [])
        setHistorial(historialData.serie || [])
        setAlerta(alertaData)
        setDimensiones(dimensionesData || {})
        const firstCultivo = (cultivosData.cultivos || [])[0]?.cultivo || ''
        setCultivoSeleccionado(firstCultivo)
        setTendenciaCultivo([])
      })
      .catch((e) => console.warn('Could not fetch municipio detail', e))
  }, [apiBase, selected?.divipola])

  useEffect(() => {
    if (!selected?.divipola || !cultivoSeleccionado) return
    fetch(`${apiBase}/municipios/${selected.divipola}/cultivos/historico`)
      .then((r) => r.json())
      .then((data) => {
        const serie = Array.isArray(data?.serie) ? data.serie : []
        setTendenciaCultivo(serie.map((item: any) => ({ anio: Number(item.anio), valor: Number(item.valor || 0) })))
      })
      .catch(() => setTendenciaCultivo([]))
  }, [apiBase, selected?.divipola, cultivoSeleccionado])

  const radarValues = Object.entries(dimensiones)
    .filter(([_, value]) => typeof value === 'number' || (typeof value === 'string' && value))
    .slice(0, 4)
    .map(([label, value]) => ({ label, value: Math.max(0, Math.min(1, Number(value || 0))) }))

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <Head>
        <title>IRA Municipal - Mapa</title>
      </Head>
      <div style={{ width: 360, padding: 16, background: '#fff', overflow: 'auto' }}>
        <h2>IRA Municipal</h2>
        <div style={{ marginBottom: 12 }}>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar municipio..."
            style={{ width: '100%', padding: 8, borderRadius: 8, border: '1px solid #ddd' }}
          />
        </div>
        <div style={{ marginBottom: 16 }}>
          <h3>Dashboard nacional</h3>
          {metrics ? (
            <div style={{ border: '1px solid #eee', borderRadius: 10, padding: 10, background: '#fafafa' }}>
              <p style={{ margin: '2px 0' }}><strong>Colombia — IRA {anio}</strong></p>
              <p style={{ margin: '2px 0' }}><strong>Total municipios:</strong> {metrics.total_municipios}</p>
              <p style={{ margin: '2px 0' }}><strong>IRA medio:</strong> {metrics.average_ira_score?.toFixed(2) ?? 'N/A'}</p>
              <p style={{ margin: '2px 0' }}><strong>Niveles:</strong></p>
              <ul style={{ margin: '4px 0 0 16px' }}>
                {Object.entries(metrics.count_by_level || {}).map(([level, count]) => (
                  <li key={level}>{level}: {count}</li>
                ))}
              </ul>
            </div>
          ) : (
            <p>Cargando métricas...</p>
          )}
        </div>

        <div style={{ marginBottom: 16 }}>
          <label htmlFor="anio" style={{ display: 'block', marginBottom: 4 }}><strong>Año</strong></label>
          <input
            id="anio"
            type="range"
            min="2021"
            max="2029"
            value={anio}
            onChange={(e) => setAnio(Number(e.target.value))}
            style={{ width: '100%' }}
          />
          <div style={{ fontSize: 13, color: '#555' }}>Seleccionado: {anio}</div>
        </div>

        <div style={{ marginBottom: 16 }}>
          <label htmlFor="escenario" style={{ display: 'block', marginBottom: 4 }}><strong>Escenario</strong></label>
          <select
            id="escenario"
            value={escenario}
            onChange={(e) => setEscenario(e.target.value)}
            disabled={anio <= 2024}
            style={{ width: '100%', padding: 8, borderRadius: 8, border: '1px solid #ddd' }}
          >
            <option value="Base">Base</option>
            <option value="Real">Real</option>
            <option value="Optimista">Optimista</option>
            <option value="Pesimista">Pesimista</option>
          </select>
        </div>
        <div style={{ marginBottom: 16 }}>
          <h3>Resultados</h3>
          <div style={{ maxHeight: 220, overflow: 'auto' }}>
            {results.length ? (
              results.map((item) => (
                <button
                  key={item.divipola}
                  onClick={() => setSelected(item)}
                  style={{
                    width: '100%',
                    padding: 10,
                    marginBottom: 4,
                    textAlign: 'left',
                    border: '1px solid #eee',
                    borderRadius: 6,
                    background: '#fafafa',
                    cursor: 'pointer',
                  }}
                >
                  <strong>{item.municipio}</strong> · {item.ira_level}
                </button>
              ))
            ) : (
              <p>No hay municipios en resultados.</p>
            )}
          </div>
        </div>
        <div>
          <h3>Detalle</h3>
          {selected ? (
            <div>
              <h4>{detalle?.municipio || selected.municipio}</h4>
              <p><strong>Departamento:</strong> {detalle?.departamento || 'N/A'}</p>
              <p><strong>DIVIPOLA:</strong> {detalle?.divipola || selected.divipola}</p>
              <p><strong>IRA level:</strong> {detalle?.ira_level || selected.ira_level}</p>
              <p><strong>Score:</strong> {detalle?.ira_score ?? 'N/A'}</p>
              {alerta ? (
                <p><strong>Alerta:</strong> {alerta.color || 'N/A'} · {alerta.nivel_alerta || 'N/A'}</p>
              ) : null}
              {Object.keys(dimensiones).length ? (
                <div style={{ marginTop: 8 }}>
                  <strong>Dimensiones IRA</strong>
                  <ul style={{ paddingLeft: 16, margin: '4px 0' }}>
                    {Object.entries(dimensiones).map(([key, value]) => {
                      const numericValue = typeof value === 'number' ? value : Number(value ?? 0)
                      const safeValue = Number.isFinite(numericValue) ? numericValue : 0
                      const percent = Math.max(0, Math.min(100, safeValue * 100))
                      return (
                        <li key={key} style={{ marginBottom: 6 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>{key}</div>
                          <div style={{ height: 8, background: '#eee', borderRadius: 4, overflow: 'hidden' }}>
                            <div style={{ width: `${percent}%`, height: '100%', background: '#c0392b' }} />
                          </div>
                          <div style={{ fontSize: 12, color: '#666' }}>{safeValue.toFixed(2)}</div>
                        </li>
                      )
                    })}
                  </ul>
                </div>
              ) : null}
              {cultivos.length ? (
                <div style={{ marginTop: 8 }}>
                  <strong>Top cultivos 2024</strong>
                  <ul style={{ paddingLeft: 16, margin: '4px 0' }}>
                    {cultivos.map((item, index) => (
                      <li key={`${item.cultivo}-${index}`}>{item.cultivo}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
              {historial.length ? (
                <div style={{ marginTop: 8 }}>
                  <strong>Historial IRA</strong>
                  <ul style={{ paddingLeft: 16, margin: '4px 0' }}>
                    {historial.map((item) => (
                      <li key={item.anio}>{item.anio}: {item.valor}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
              {radarValues.length ? (
                <div style={{ marginTop: 12 }}>
                  <strong>Radar de dimensiones</strong>
                  <RadarChart values={radarValues} />
                </div>
              ) : null}
              {cultivos.length ? (
                <div style={{ marginTop: 12 }}>
                  <strong>Tendencia de cultivos</strong>
                  <select
                    value={cultivoSeleccionado}
                    onChange={(e) => setCultivoSeleccionado(e.target.value)}
                    style={{ width: '100%', padding: 8, borderRadius: 8, border: '1px solid #ddd', marginTop: 6 }}
                  >
                    {cultivos.map((item, index) => (
                      <option key={`${item.cultivo}-${index}`} value={item.cultivo}>{item.cultivo}</option>
                    ))}
                  </select>
                  <TrendChart data={tendenciaCultivo} />
                </div>
              ) : null}
            </div>
          ) : (
            <p>Selecciona un municipio en el mapa o en la lista.</p>
          )}
        </div>
      </div>
      <div style={{ flex: 1 }}>
        <Map onSelect={setSelected} query={search} anio={anio} escenario={escenario} />
      </div>
    </div>
  )
}
