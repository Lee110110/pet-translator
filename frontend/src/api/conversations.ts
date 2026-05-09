import { get, post } from './index'

export function startConversation(petId: number, data: { initial_symptoms: string; checkin_id?: number; warning_level?: string }) {
  return post(`/pets/${petId}/conversations`, data)
}

export function replyConversation(petId: number, conversationId: number, data: { content: string }) {
  return post(`/pets/${petId}/conversations/${conversationId}/reply`, data)
}

export function getConversation(petId: number, conversationId: number) {
  return get(`/pets/${petId}/conversations/${conversationId}`)
}

export function listConversations(petId: number) {
  return get(`/pets/${petId}/conversations`)
}