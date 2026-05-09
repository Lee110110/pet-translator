import { get, post, put } from './index'

export function createCheckin(petId: number, data: {
  diet_score: number; diet_note?: string;
  water_score: number; water_note?: string;
  stool_score: number; stool_note?: string;
  spirit_score: number; spirit_note?: string;
  note?: string;
}) {
  return post(`/pets/${petId}/checkins`, data)
}

export function updateCheckin(petId: number, checkinId: number, data: any) {
  return put(`/pets/${petId}/checkins/${checkinId}`, data)
}

export function listCheckins(petId: number) {
  return get(`/pets/${petId}/checkins`)
}

export function getLatestCheckin(petId: number) {
  return get(`/pets/${petId}/checkins/latest`)
}