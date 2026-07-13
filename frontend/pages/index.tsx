import dynamic from 'next/dynamic'
import Head from 'next/head'
import { useEffect, useState } from 'react'

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
          <h3>Dashboard</h3>
          {metrics ? (
            <div>
              <p><strong>Total municipios:</strong> {metrics.total_municipios}</p>
              <p><strong>IRA medio:</strong> {metrics.average_ira_score?.toFixed(2) ?? 'N/A'}</p>
              <p><strong>Niveles:</strong></p>
              <ul>
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
              <h4>{selected.municipio}</h4>
              <p><strong>DIVIPOLA:</strong> {selected.divipola}</p>
              <p><strong>IRA level:</strong> {selected.ira_level}</p>
              <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12 }}>{JSON.stringify(selected, null, 2)}</pre>
            </div>
          ) : (
            <p>Selecciona un municipio en el mapa o en la lista.</p>
          )}
        </div>
      </div>
      <div style={{ flex: 1 }}>
        <Map onSelect={setSelected} query={search} />
      </div>
    </div>
  )
}
