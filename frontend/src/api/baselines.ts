import { get } from './index'

export function getBaselines(petId: number) {
  return get(`/pets/${petId}/baselines`)
}

export function getBaselineChart(petId: number) {
  return get(`/pets/${petId}/baselines/chart`)
}

export function recalculateBaselines(petId: number) {
  return get(`/pets/${petId}/baselines/recalculate`)
}