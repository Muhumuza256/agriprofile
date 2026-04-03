/**
 * Sync engine — uploads pending records to the AgriProfile API
 * when the device comes back online.
 * Called by the service worker's Background Sync event and by the app
 * when it detects a reconnection.
 */
import axios from 'axios'
import { db, addToSyncQueue } from './db'

const API_BASE = '/api'

function getAuthHeader(): Record<string, string> {
  const stored = localStorage.getItem('agriprofile-auth')
  if (!stored) return {}
  try {
    const { state } = JSON.parse(stored)
    return state.accessToken ? { Authorization: `Bearer ${state.accessToken}` } : {}
  } catch {
    return {}
  }
}

async function syncGroups(): Promise<number> {
  const pending = await db.pendingGroups.where('syncStatus').equals('pending').toArray()
  let synced = 0
  for (const group of pending) {
    try {
      await db.pendingGroups.update(group.id!, { syncStatus: 'syncing' })
      await axios.post(`${API_BASE}/groups/`, group.data, { headers: getAuthHeader() })
      await db.pendingGroups.update(group.id!, { syncStatus: 'synced' })
      synced++
    } catch (e) {
      await db.pendingGroups.update(group.id!, { syncStatus: 'error' })
    }
  }
  return synced
}

async function syncFarmers(): Promise<number> {
  const pending = await db.pendingFarmers.where('syncStatus').equals('pending').toArray()
  let synced = 0
  for (const farmer of pending) {
    try {
      await db.pendingFarmers.update(farmer.id!, { syncStatus: 'syncing' })

      const formData = new FormData()
      Object.entries(farmer.data).forEach(([k, v]) => {
        formData.append(k, String(v))
      })
      // Attach photos if any
      farmer.photosBase64.forEach((b64, i) => {
        const arr = Uint8Array.from(atob(b64.split(',')[1] ?? b64), (c) => c.charCodeAt(0))
        formData.append(i === 0 ? 'portrait_photo' : 'national_id_photo', new Blob([arr], { type: 'image/jpeg' }), `photo_${i}.jpg`)
      })

      await axios.post(`${API_BASE}/farmers/`, formData, {
        headers: { ...getAuthHeader(), 'Content-Type': 'multipart/form-data' },
      })
      await db.pendingFarmers.update(farmer.id!, { syncStatus: 'synced' })
      synced++
    } catch {
      await db.pendingFarmers.update(farmer.id!, { syncStatus: 'error' })
    }
  }
  return synced
}

async function syncPlots(): Promise<number> {
  const pending = await db.pendingPlots.where('syncStatus').equals('pending').toArray()
  let synced = 0
  for (const plot of pending) {
    try {
      await db.pendingPlots.update(plot.id!, { syncStatus: 'syncing' })
      await axios.post(`${API_BASE}/plots/`, {
        ...plot.data,
        coordinates: plot.coordinates,
      }, { headers: getAuthHeader() })
      await db.pendingPlots.update(plot.id!, { syncStatus: 'synced' })
      synced++
    } catch {
      await db.pendingPlots.update(plot.id!, { syncStatus: 'error' })
    }
  }
  return synced
}

export async function runSync(): Promise<{ groups: number; farmers: number; plots: number }> {
  const [groups, farmers, plots] = await Promise.all([
    syncGroups(),
    syncFarmers(),
    syncPlots(),
  ])
  return { groups, farmers, plots }
}

export function listenForOnline() {
  window.addEventListener('online', async () => {
    console.log('[AgriProfile PWA] Back online — running sync…')
    const result = await runSync()
    console.log('[AgriProfile PWA] Synced:', result)
  })
}
