const BASE = '/api'

async function handle(res) {
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(text || `Request failed with status ${res.status}`)
  }
  return res.json()
}

export function fetchExampleTopic() {
  return fetch(`${BASE}/example-topic`).then(handle)
}

export function generateLesson(topic) {
  return fetch(`${BASE}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic }),
  }).then(handle)
}

export function fetchMemory() {
  return fetch(`${BASE}/memory`).then(handle)
}

export function fetchHistory() {
  return fetch(`${BASE}/history`).then(handle)
}
