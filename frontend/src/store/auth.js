import { reactive } from 'vue'
import axios from 'axios'

const savedToken = localStorage.getItem('ppa_token') || ''
const savedUser = JSON.parse(localStorage.getItem('ppa_user') || 'null')
const savedProfile = JSON.parse(localStorage.getItem('ppa_profile') || 'null')

if (savedToken) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`
}

axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('ppa_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

export const authStore = reactive({
  token: savedToken,
  user: savedUser,
  profile: savedProfile,

  isAuthenticated() {
    return !!this.token && !!this.user
  },

  getRole() {
    return this.user ? this.user.role : null
  },

  setAuth(token, user, profile) {
    this.token = token
    this.user = user
    this.profile = profile

    localStorage.setItem('ppa_token', token)
    localStorage.setItem('ppa_user', JSON.stringify(user))
    localStorage.setItem('ppa_profile', JSON.stringify(profile))

    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
  },

  updateProfile(profile) {
    this.profile = profile
    localStorage.setItem('ppa_profile', JSON.stringify(profile))
  },

  logout() {
    this.token = ''
    this.user = null
    this.profile = null

    localStorage.removeItem('ppa_token')
    localStorage.removeItem('ppa_user')
    localStorage.removeItem('ppa_profile')

    delete axios.defaults.headers.common['Authorization']
  }
})
