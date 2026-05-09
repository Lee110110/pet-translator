import { get, post, put, del } from './index'

export function createVaccine(petId: number, data: { type: string; name: string; scheduled_date: string; notes?: string }) {
  return post(`/pets/${petId}/vaccines`, data)
}

export function listVaccines(petId: number) {
  return get(`/pets/${petId}/vaccines`)
}

export function getVaccineSchedule(petId: number) {
  return get(`/pets/${petId}/vaccines/schedule`)
}

export function updateVaccine(petId: number, vaccineId: number, data: any) {
  return put(`/pets/${petId}/vaccines/${vaccineId}`, data)
}

export function deleteVaccine(petId: number, vaccineId: number) {
  return del(`/pets/${petId}/vaccines/${vaccineId}`)
}