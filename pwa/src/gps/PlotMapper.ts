/**
 * PlotMapper — captures GPS coordinates as the field agent walks a farm boundary,
 * calculates area using the Shoelace formula with equirectangular projection,
 * and generates a GeoJSON polygon for submission.
 */
export interface Coordinate {
  lat: number
  lon: number
  accuracy: number
  timestamp: number
}

export class PlotMapper {
  private coordinates: Coordinate[] = []

  addPoint(position: GeolocationPosition): Coordinate {
    const coord: Coordinate = {
      lat:      position.coords.latitude,
      lon:      position.coords.longitude,
      accuracy: position.coords.accuracy,
      timestamp: position.timestamp,
    }
    this.coordinates.push(coord)
    return coord
  }

  getCoordinates(): Coordinate[] {
    return [...this.coordinates]
  }

  get pointCount(): number {
    return this.coordinates.length
  }

  reset(): void {
    this.coordinates = []
  }

  /** Area in acres using the Shoelace formula. */
  calculateAreaAcres(): number {
    const n = this.coordinates.length
    if (n < 3) return 0

    let area = 0
    for (let i = 0; i < n; i++) {
      const j = (i + 1) % n
      const { lat: lat_i, lon: lon_i } = this.coordinates[i]
      const { lat: lat_j, lon: lon_j } = this.coordinates[j]

      // Equirectangular projection to metres
      const xi = lon_i * 111320 * Math.cos((lat_i * Math.PI) / 180)
      const yi = lat_i * 110540
      const xj = lon_j * 111320 * Math.cos((lat_j * Math.PI) / 180)
      const yj = lat_j * 110540

      area += xi * yj - xj * yi
    }

    const areaM2 = Math.abs(area) / 2
    return areaM2 / 4046.86  // 1 acre = 4046.86 m²
  }

  /** Average GPS accuracy across all collected points. */
  get averageAccuracyM(): number {
    if (!this.coordinates.length) return 0
    return this.coordinates.reduce((s, c) => s + c.accuracy, 0) / this.coordinates.length
  }

  /** GeoJSON Polygon (auto-closes). */
  toGeoJSON(): GeoJSONPolygon {
    const coords = this.coordinates.map((c) => [c.lon, c.lat] as [number, number])
    if (coords.length > 0) coords.push(coords[0])  // close polygon
    return { type: 'Polygon', coordinates: [coords] }
  }

  /** Simple API payload: list of {lat, lon} dicts expected by PlotCreateSerializer. */
  toAPIPayload(): Array<{ lat: number; lon: number }> {
    return this.coordinates.map(({ lat, lon }) => ({ lat, lon }))
  }
}

export interface GeoJSONPolygon {
  type: 'Polygon'
  coordinates: Array<Array<[number, number]>>
}

/** Singleton mapper for the current plot-mapping session. */
export const plotMapper = new PlotMapper()
