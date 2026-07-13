import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

type Props = {
  onSelect?: (data: any) => void
  query?: string
}

const AnyMapContainer = MapContainer as any
const AnyTileLayer = TileLayer as any

const getFillColor = (level: string) => {
  switch (level) {
    case 'Bajo':
      return '#2DC4B2'
    case 'Medio':
      return '#F1C40F'
    case 'Alto':
      return '#E67E22'
    case 'Crítico':
      return '#C0392B'
    default:
      return '#888888'
  }
}

function GeojsonLayer({ data, onSelect }: { data: any; onSelect?: (data: any) => void }) {
  const map = useMap()

  useEffect(() => {
    if (!data?.features?.length) return
    const bounds = L.geoJSON(data).getBounds()
    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [24, 24] })
    }

    const geojsonLayer = L.geoJSON(data, {
      style: (feature) => ({
        fillColor: getFillColor(feature.properties?.ira_level),
        weight: 1,
        opacity: 1,
        color: '#222222',
        fillOpacity: 0.55,
      }),
      onEachFeature: (feature, layer) => {
        layer.on('click', () => {
          if (onSelect) onSelect(feature.properties)
        })

        if (feature.properties?.municipio) {
          layer.bindPopup(`
            <strong>${feature.properties.municipio}</strong><br />
            Nivel IRA: ${feature.properties.ira_level || 'N/A'}
          `)
        }
      },
    }).addTo(map)

    return () => {
      geojsonLayer.remove()
    }
  }, [data, map, onSelect])

  return null
}

export default function Map({ onSelect, query }: Props) {
  const [geojson, setGeojson] = useState<any>(null)
  const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000'

  useEffect(() => {
    const loadGeojson = async () => {
      try {
        const url = new URL(`${apiBase}/municipios/geojson`)
        if (query) url.searchParams.set('q', query)
        const res = await fetch(url.toString())
        const data = await res.json()
        setGeojson(data)
      } catch (error) {
        console.error('Error loading geojson', error)
      }
    }

    loadGeojson()
  }, [apiBase, query])

  return (
    <AnyMapContainer center={[4.0, -74.5]} zoom={5} style={{ width: '100%', height: '100%' }}>
      <AnyTileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
      />
      {geojson && <GeojsonLayer data={geojson} onSelect={onSelect} />}
    </AnyMapContainer>
  )
}
