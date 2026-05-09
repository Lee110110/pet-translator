import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as authApi from '../api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(uni.getStorageSync('token') || '')
  const userInfo = ref<any>(null)
  const isLoggedIn = ref(!!token.value)

  async function login(username: string, password: string) {
    const res = await authApi.login({ username, password })
    token.value = res.access_token
    isLoggedIn.value = true
    uni.setStorageSync('token', token.value)
    await fetchProfile()
  }

  async function register(username: string, password: string, email?: string, display_name?: string) {
    const res = await authApi.register({ username, password, email, display_name })
    token.value = res.access_token
    isLoggedIn.value = true
    uni.setStorageSync('token', token.value)
    await fetchProfile()
  }

  async function fetchProfile() {
    if (!token.value) return
    try {
      userInfo.value = await authApi.getProfile()
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    isLoggedIn.value = false
    uni.removeStorageSync('token')
    uni.reLaunch({ url: '/pages/login/login' })
  }

  return { token, userInfo, isLoggedIn, login, register, fetchProfile, logout }
})