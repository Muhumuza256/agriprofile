/**
 * Camera capture utilities.
 * Uses the MediaDevices API (rear camera preferred).
 * Returns base64-encoded JPEG strings for offline storage in Dexie.
 */

export async function capturePhoto(): Promise<string> {
  // Prefer rear camera on mobile
  const stream = await navigator.mediaDevices.getUserMedia({
    video: {
      facingMode: { ideal: 'environment' },
      width: { ideal: 1280 },
      height: { ideal: 720 },
    },
  })

  const video = document.createElement('video')
  video.srcObject = stream
  video.autoplay = true
  await new Promise<void>((resolve) => { video.onloadedmetadata = () => resolve() })

  const canvas = document.createElement('canvas')
  canvas.width  = video.videoWidth
  canvas.height = video.videoHeight
  canvas.getContext('2d')!.drawImage(video, 0, 0)

  stream.getTracks().forEach((t) => t.stop())

  return canvas.toDataURL('image/jpeg', 0.8)
}

export async function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload  = () => resolve(reader.result as string)
    reader.onerror = () => reject(reader.error)
    reader.readAsDataURL(file)
  })
}
