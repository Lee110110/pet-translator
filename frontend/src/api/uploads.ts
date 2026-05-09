import { uploadImage, post } from './index'

export function uploadPetImage(petId: number, filePath: string) {
  return uploadImage(`/pets/${petId}/uploads/image`, filePath)
}

export function analyzeImage(petId: number, data: { image_url: string; analysis_type: string }) {
  return post(`/pets/${petId}/uploads/analyze-image`, data)
}