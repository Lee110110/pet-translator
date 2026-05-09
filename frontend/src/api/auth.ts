import { post, get, put } from './index'

export function register(data: { username: string; password: string; email?: string; display_name?: string }) {
  return post('/auth/register', data)
}

export function login(data: { username: string; password: string }) {
  return post('/auth/login', data)
}

export function getProfile() {
  return get('/auth/me')
}

export function updateProfile(data: { display_name?: string; email?: string; avatar_url?: string }) {
  return put('/auth/me', data)
}