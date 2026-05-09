import { post } from './index'

export function generateMedicalSummary(petId: number, data: { start_date?: string; end_date?: string; visit_reason?: string }) {
  return post(`/pets/${petId}/medical/summary`, data)
}