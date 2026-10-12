const API_BASE = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

export type Patient = { id: number; first_name: string; last_name: string; email: string; phone?: string | null; date_of_birth?: string | null }
export type Doctor = { id: number; full_name: string; specialty?: string | null; email?: string | null; phone?: string | null; is_active: boolean; created_at?: string }

function token() { return localStorage.getItem('careflow_token') }
async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers)
  if (!(options.body instanceof FormData) && options.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json')
  if (token()) headers.set('Authorization', `Bearer ${token()}`)
  let response: Response
  try { response = await fetch(`${API_BASE}${path}`, { ...options, headers }) }
  catch { throw new Error(`Cannot reach the API at ${API_BASE}. Start the FastAPI server and check VITE_API_URL.`) }
  if (!response.ok) {
    let message = `Request failed (${response.status})`
    try { const body = await response.json(); message = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail ?? body) } catch { /* keep fallback */ }
    throw new Error(message)
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export const api = {
  baseUrl: API_BASE,
  login: async (email: string, password: string) => {
    // Current FastAPI /auth/login uses OAuth2PasswordRequestForm: username + password form fields.
    const body = new URLSearchParams({ username: email, password })
    return request<{ access_token: string; token_type: string }>('/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body })
  },
  register: (payload: { full_name: string; email: string; password: string }) => request<{ id: number; full_name: string; email: string; is_active: boolean }>('/auth/register', { method: 'POST', body: JSON.stringify(payload) }),
  patients: () => request<Patient[]>('/patients/'),
  createPatient: (payload: Omit<Patient, 'id'>) => request<Patient>('/patients/', { method: 'POST', body: JSON.stringify(payload) }),
  doctors: () => request<Doctor[]>('/doctors/'),
  aiComplete: (prompt: string) => request<{ result: string }>('/ai/complete', { method: 'POST', body: JSON.stringify({ prompt }) }),
  health: () => request<{ status: string }>('/health'),
}
