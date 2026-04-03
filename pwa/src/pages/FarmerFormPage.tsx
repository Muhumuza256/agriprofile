import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { db, addToSyncQueue } from '@/offline/db'
import { fileToBase64 } from '@/camera/capture'

interface FormState {
  groupId: string
  fullName: string
  nationalId: string
  gender: string
  primaryPhone: string
  village: string
  parish: string
  subCounty: string
  district: string
  nextOfKinName: string
  nextOfKinPhone: string
  householdSize: string
  dependants: string
  farmCondition: string
  agentNotes: string
}

const INITIAL: FormState = {
  groupId: '', fullName: '', nationalId: '', gender: 'female',
  primaryPhone: '', village: '', parish: '', subCounty: '', district: '',
  nextOfKinName: '', nextOfKinPhone: '', householdSize: '4', dependants: '2',
  farmCondition: 'good', agentNotes: '',
}

export default function FarmerFormPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState<FormState>(INITIAL)
  const [photos, setPhotos] = useState<string[]>([])
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  const set = (key: keyof FormState, value: string) =>
    setForm((f) => ({ ...f, [key]: value }))

  const handlePhotoSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const b64 = await fileToBase64(file)
    setPhotos((prev) => [...prev, b64].slice(0, 2))  // max 2 photos
  }

  const handleSave = async () => {
    if (!form.fullName || !form.nationalId || !form.primaryPhone || !form.groupId) {
      alert('Name, National ID, Phone, and Group ID are required.')
      return
    }
    setSaving(true)
    const localId = `farmer_${Date.now()}`
    try {
      await db.pendingFarmers.add({
        localId,
        groupId: form.groupId,
        nationalId: form.nationalId,
        fullName: form.fullName,
        data: {
          group: form.groupId,
          full_name: form.fullName,
          national_id: form.nationalId,
          gender: form.gender,
          primary_phone: form.primaryPhone,
          village: form.village,
          parish: form.parish,
          sub_county: form.subCounty,
          district: form.district,
          next_of_kin_name: form.nextOfKinName,
          next_of_kin_phone: form.nextOfKinPhone,
          household_size: parseInt(form.householdSize),
          dependants: parseInt(form.dependants),
          farm_condition: form.farmCondition,
          agent_notes: form.agentNotes,
          visit_date: new Date().toISOString().split('T')[0],
        },
        photosBase64: photos,
        syncStatus: 'pending',
        createdAt: Date.now(),
      })
      await addToSyncQueue('farmer', localId, 2)
      setSaved(true)
      setTimeout(() => navigate('/'), 1500)
    } finally {
      setSaving(false)
    }
  }

  if (saved) {
    return (
      <div className="min-h-screen bg-primary-900 flex items-center justify-center">
        <div className="text-center text-white">
          <p className="text-4xl mb-2">✓</p>
          <p className="font-medium">Farmer saved offline</p>
          <p className="text-sm text-primary-300 mt-1">Will sync when online</p>
        </div>
      </div>
    )
  }

  const field = (label: string, key: keyof FormState, type = 'text', opts?: string[]) => (
    <div>
      <label className="block text-xs text-neutral-500 mb-1">{label}</label>
      {opts ? (
        <select
          value={form[key]}
          onChange={(e) => set(key, e.target.value)}
          className="w-full border border-neutral-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          {opts.map((o) => <option key={o} value={o}>{o}</option>)}
        </select>
      ) : (
        <input
          type={type}
          value={form[key]}
          onChange={(e) => set(key, e.target.value)}
          className="w-full border border-neutral-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      )}
    </div>
  )

  return (
    <div className="min-h-screen bg-neutral-50 pb-24">
      <div className="bg-primary-900 px-4 py-4 flex items-center gap-3">
        <button onClick={() => navigate(-1)} className="text-primary-300 text-sm">← Back</button>
        <h1 className="text-white font-semibold">New Farmer Profile</h1>
      </div>

      <div className="p-4 space-y-4">
        {/* Module A */}
        <section className="bg-white rounded-lg p-4 shadow-sm space-y-3">
          <h2 className="text-sm font-semibold text-neutral-700 border-b pb-2">A · Identity</h2>
          {field('Group UUID', 'groupId')}
          {field('Full Name', 'fullName')}
          {field('National ID (NIN)', 'nationalId')}
          {field('Gender', 'gender', 'text', ['female', 'male', 'other'])}
          {field('Primary Phone', 'primaryPhone', 'tel')}
        </section>

        {/* Location */}
        <section className="bg-white rounded-lg p-4 shadow-sm space-y-3">
          <h2 className="text-sm font-semibold text-neutral-700 border-b pb-2">Location</h2>
          {field('Village', 'village')}
          {field('Parish', 'parish')}
          {field('Sub-County', 'subCounty')}
          {field('District', 'district')}
        </section>

        {/* Next of kin */}
        <section className="bg-white rounded-lg p-4 shadow-sm space-y-3">
          <h2 className="text-sm font-semibold text-neutral-700 border-b pb-2">Next of Kin</h2>
          {field('Name', 'nextOfKinName')}
          {field('Phone', 'nextOfKinPhone', 'tel')}
        </section>

        {/* Household */}
        <section className="bg-white rounded-lg p-4 shadow-sm space-y-3">
          <h2 className="text-sm font-semibold text-neutral-700 border-b pb-2">B · Household</h2>
          {field('Household Size', 'householdSize', 'number')}
          {field('Dependants', 'dependants', 'number')}
        </section>

        {/* Agent observations */}
        <section className="bg-white rounded-lg p-4 shadow-sm space-y-3">
          <h2 className="text-sm font-semibold text-neutral-700 border-b pb-2">H · Agent Observations</h2>
          {field('Farm Condition', 'farmCondition', 'text', ['excellent', 'good', 'fair', 'poor'])}
          <div>
            <label className="block text-xs text-neutral-500 mb-1">Notes</label>
            <textarea
              value={form.agentNotes}
              onChange={(e) => set('agentNotes', e.target.value)}
              rows={3}
              className="w-full border border-neutral-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </section>

        {/* Photos */}
        <section className="bg-white rounded-lg p-4 shadow-sm space-y-3">
          <h2 className="text-sm font-semibold text-neutral-700 border-b pb-2">Photos</h2>
          <div className="flex gap-3 flex-wrap">
            {photos.map((p, i) => (
              <img key={i} src={p} className="w-20 h-20 object-cover rounded border border-neutral-200" />
            ))}
          </div>
          <input
            ref={fileRef}
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={handlePhotoSelect}
          />
          {photos.length < 2 && (
            <button
              onClick={() => fileRef.current?.click()}
              className="text-sm text-primary-700 border border-primary-300 rounded px-3 py-1.5"
            >
              {photos.length === 0 ? '📷 Add Portrait Photo' : '📷 Add ID Photo'}
            </button>
          )}
        </section>

        <button
          onClick={handleSave}
          disabled={saving}
          className="w-full py-4 bg-primary-700 text-white font-semibold rounded-xl active:bg-primary-900 disabled:opacity-50"
        >
          {saving ? 'Saving…' : 'Save Offline'}
        </button>
      </div>
    </div>
  )
}
