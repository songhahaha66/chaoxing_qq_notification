import { defineStore } from 'pinia'
import { ref } from 'vue'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))

  const isAuthenticated = ref<boolean>(!!accessToken.value)

  function setTokens(newAccessToken: string, newRefreshToken: string) {
    accessToken.value = newAccessToken
    refreshToken.value = newRefreshToken
    localStorage.setItem('access_token', newAccessToken)
    localStorage.setItem('refresh_token', newRefreshToken)
    isAuthenticated.value = true
  }

  function clearTokens() {
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    isAuthenticated.value = false
  }

  function logout() {
    clearTokens()
    router.push('/login')
  }

  // Potentially, add a function here to handle token refresh logic if needed by other parts of the app
  // For now, the API service will handle its own token refresh internally.

  return { accessToken, refreshToken, isAuthenticated, setTokens, clearTokens, logout }
})

