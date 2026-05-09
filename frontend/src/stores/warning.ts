import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as warningsApi from '../api/warnings'

export const useWarningStore = defineStore('warning', () => {
  const dashboard = ref<any>({ green: 0, yellow: 0, orange: 0, red: 0, total_unread: 0 })
  const warningList = ref<any[]>([])

  async function fetchDashboard(petId: number) {
    dashboard.value = await warningsApi.getWarningDashboard(petId)
  }

  async function fetchWarnings(petId: number, level?: string) {
    warningList.value = await warningsApi.listWarnings(petId, level)
  }

  async function markRead(petId: number, warningId: number) {
    await warningsApi.markWarningRead(petId, warningId)
    await fetchDashboard(petId)
    await fetchWarnings(petId)
  }

  function getMaxLevel(): string {
    if (dashboard.value.red > 0) return 'red'
    if (dashboard.value.orange > 0) return 'orange'
    if (dashboard.value.yellow > 0) return 'yellow'
    return 'green'
  }

  return { dashboard, warningList, fetchDashboard, fetchWarnings, markRead, getMaxLevel }
})