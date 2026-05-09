import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as petsApi from '../api/pets'

export const usePetStore = defineStore('pet', () => {
  const petList = ref<any[]>([])
  const currentPetId = ref<number>(0)
  const currentPet = computed(() => petList.value.find(p => p.id === currentPetId.value))

  async function fetchPets() {
    petList.value = await petsApi.listPets()
    if (petList.value.length > 0 && !currentPetId.value) {
      currentPetId.value = petList.value[0].id
    }
  }

  function setCurrentPet(petId: number) {
    currentPetId.value = petId
    uni.setStorageSync('currentPetId', petId)
  }

  async function createPet(data: any) {
    const pet = await petsApi.createPet(data)
    petList.value.push(pet)
    if (!currentPetId.value) {
      setCurrentPet(pet.id)
    }
    return pet
  }

  async function deletePet(petId: number) {
    await petsApi.deletePet(petId)
    petList.value = petList.value.filter(p => p.id !== petId)
    if (currentPetId.value === petId) {
      currentPetId.value = petList.value.length > 0 ? petList.value[0].id : 0
    }
  }

  // Restore saved pet selection
  const savedPetId = uni.getStorageSync('currentPetId')
  if (savedPetId) currentPetId.value = savedPetId

  return { petList, currentPetId, currentPet, fetchPets, setCurrentPet, createPet, deletePet }
})