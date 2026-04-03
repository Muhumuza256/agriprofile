import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import { analyticsApi } from '@/api/endpoints'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Fix leaflet default icon paths broken by bundlers
delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl:       'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl:     'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

interface GroupFeature {
  type: string
  geometry: { type: string; coordinates: [number, number] }
  properties: {
    id: string
    name: string
    district: string
    member_count: number
    gacs: number | null
  }
}

export default function MapPage() {
  const { data: geojson } = useQuery({
    queryKey: ['analytics', 'map'],
    queryFn: () => analyticsApi.groupMap().then((r) => r.data),
  })

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold font-display">Group Map</h1>
      <p className="text-sm text-neutral-500">
        Showing {geojson?.features?.length ?? 0} approved groups with GPS coordinates.
      </p>

      <div className="card overflow-hidden" style={{ height: 520 }}>
        <MapContainer
          center={[1.3733, 32.2903]}  // Uganda centre
          zoom={7}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {geojson?.features?.map((feature: GroupFeature) => {
            const [lon, lat] = feature.geometry.coordinates
            return (
              <Marker key={feature.properties.id} position={[lat, lon]}>
                <Popup>
                  <strong>{feature.properties.name}</strong><br />
                  District: {feature.properties.district}<br />
                  Members: {feature.properties.member_count}<br />
                  GACS: {feature.properties.gacs?.toFixed(1) ?? '—'}
                </Popup>
              </Marker>
            )
          })}
        </MapContainer>
      </div>
    </div>
  )
}
