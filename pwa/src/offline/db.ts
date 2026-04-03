import Dexie, { type Table } from 'dexie'

export interface PendingGroup {
  id?: number
  localId: string
  groupName: string
  groupType: string
  district: string
  village: string
  parish: string
  subCounty: string
  chairpersonName: string
  chairpersonPhone: string
  data: Record<string, unknown>
  syncStatus: 'pending' | 'syncing' | 'synced' | 'error'
  createdAt: number
}

export interface PendingFarmer {
  id?: number
  localId: string
  groupId: string
  nationalId: string
  fullName: string
  data: Record<string, unknown>
  photosBase64: string[]   // base64 encoded photos waiting for upload
  syncStatus: 'pending' | 'syncing' | 'synced' | 'error'
  createdAt: number
}

export interface PendingPlot {
  id?: number
  localId: string
  farmerId: string
  plotName: string
  coordinates: Array<{ lat: number; lon: number; accuracy: number }>
  calculatedAcres: number
  landTenure: string
  data: Record<string, unknown>
  syncStatus: 'pending' | 'syncing' | 'synced' | 'error'
  createdAt: number
}

export interface SyncQueueItem {
  id?: number
  entityType: 'group' | 'farmer' | 'plot'
  localId: string
  priority: number
  createdAt: number
  attempts: number
  lastError?: string
}

export class AgriProfileDB extends Dexie {
  pendingGroups!:  Table<PendingGroup,    number>
  pendingFarmers!: Table<PendingFarmer,   number>
  pendingPlots!:   Table<PendingPlot,     number>
  syncQueue!:      Table<SyncQueueItem,   number>

  constructor() {
    super('AgriProfilePWA')
    this.version(1).stores({
      pendingGroups:  '++id, localId, district, syncStatus, createdAt',
      pendingFarmers: '++id, localId, groupId, nationalId, syncStatus, createdAt',
      pendingPlots:   '++id, localId, farmerId, syncStatus, createdAt',
      syncQueue:      '++id, entityType, localId, priority, createdAt',
    })
  }
}

export const db = new AgriProfileDB()

// Convenience helpers
export async function addToSyncQueue(
  entityType: SyncQueueItem['entityType'],
  localId: string,
  priority = 1,
) {
  await db.syncQueue.add({
    entityType,
    localId,
    priority,
    createdAt: Date.now(),
    attempts: 0,
  })
}

export async function getPendingCount() {
  const [groups, farmers, plots] = await Promise.all([
    db.pendingGroups.where('syncStatus').equals('pending').count(),
    db.pendingFarmers.where('syncStatus').equals('pending').count(),
    db.pendingPlots.where('syncStatus').equals('pending').count(),
  ])
  return { groups, farmers, plots, total: groups + farmers + plots }
}
