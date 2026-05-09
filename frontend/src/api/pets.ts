import { get, post, put, del } from './index'

export function createPet(data: { name: string; breed?: string; birthday?: string; gender?: string; weight_kg?: number; color?: string }) {
  return post('/pets', data)
}

export function listPets() {
  return get('/pets')
}

export function getPet(petId: number) {
  return get(`/pets/${petId}`)
}

export function updatePet(petId: number, data: any) {
  return put(`/pets/${petId}`, data)
}

export function deletePet(petId: number) {
  return del(`/pets/${petId}`)
}