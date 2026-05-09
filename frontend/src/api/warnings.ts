import { get, put } from './index'

export function listWarnings(petId: number, level?: string) {
  return get(`/pets/${petId}/warnings`, level ? { level } : undefined)
}

export function getWarningDashboard(petId: number) {
  return get(`/pets/${petId}/warnings/dashboard`)
}

export function getWarning(petId: number, warningId: number) {
  return get(`/pets/${petId}/warnings/${warningId}`)
}

export function markWarningRead(petId: number, warningId: number) {
  return put(`/pets/${petId}/warnings/${warningId}/read`)
}

export function getDiseaseProbability(petId: number, symptoms: string[]) {
  return get(`/pets/${petId}/warnings/disease-probability`, { symptoms })
}