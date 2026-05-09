import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as checkinsApi from '../api/checkins'

export const useCheckinStore = defineStore('checkin', () => {
  const todayCheckin = ref<any>(null)
  const checkinHistory = ref<any[]>([])

  async function fetchLatest(petId: number) {
    try {
      todayCheckin.value = await checkinsApi.getLatestCheckin(petId)
    } catch {
      todayCheckin.value = null
    }
  }

  async function fetchHistory(petId: number) {
    checkinHistory.value = await checkinsApi.listCheckins(petId)
  }

  async function submitCheckin(petId: number, data: any) {
    todayCheckin.value = await checkinsApi.createCheckin(petId, data)
    await fetchHistory(petId)
    return todayCheckin.value
  }

  async function updateCheckin(petId: number, checkinId: number, data: any) {
    todayCheckin.value = await checkinsApi.updateCheckin(petId, checkinId, data)
    await fetchHistory(petId)
    return todayCheckin.value
  }

  return { todayCheckin, checkinHistory, fetchLatest, fetchHistory, submitCheckin, updateCheckin }
})