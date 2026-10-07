<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-5">
        <div class="card shadow border-0">
          <div class="card-body p-4 p-md-5">
            <div class="text-center mb-4">
              <div class="bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 60px; height: 60px;">
                <i class="bi bi-person-circle fs-2"></i>
              </div>
              <h3 class="fw-bold">Sign In</h3>
              <p class="text-muted small">Placement Portal Application - V2</p>
            </div>

            <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
              <i class="bi bi-exclamation-triangle-fill me-2"></i> {{ error }}
              <button type="button" class="btn-close" @click="error = ''"></button>
            </div>

            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label class="form-label fw-semibold">Email Address</label>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-envelope"></i></span>
                  <input
                    type="email"
                    class="form-control"
                    v-model="email"
                    placeholder="user@example.com"
                    required
                  />
                </div>
              </div>

              <div class="mb-4">
                <label class="form-label fw-semibold">Password</label>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-lock"></i></span>
                  <input
                    type="password"
                    class="form-control"
                    v-model="password"
                    placeholder="••••••••"
                    required
                  />
                </div>
              </div>

              <button type="submit" class="btn btn-primary w-100 py-2 fw-semibold" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                <i v-else class="bi bi-box-arrow-in-right me-1"></i> Sign In
              </button>
            </form>

            <div class="mt-4 pt-3 border-top text-center">
              <p class="text-muted small mb-0">
                New Student or Company?
                <router-link to="/register" class="fw-bold text-decoration-none">Register Here</router-link>
              </p>
              <p class="text-muted small mt-2">
                <i class="bi bi-shield-check text-success me-1"></i> Default Admin: <code>admin@ppa.com</code> / <code>admin123</code>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { authStore } from '../store/auth.js'

const router = useRouter()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const handleLogin = async () => {
  error.value = ''
  loading.value = true

  try {
    const response = await axios.post('/api/auth/login', {
      email: email.value,
      password: password.value
    })

    const { access_token, user, profile } = response.data
    authStore.setAuth(access_token, user, profile)

    if (user.role === 'admin') router.push('/admin/dashboard')
    else if (user.role === 'company') router.push('/company/dashboard')
    else if (user.role === 'student') router.push('/student/dashboard')
    else router.push('/')
  } catch (err) {
    error.value = err.response?.data?.error || 'Login failed. Please check your credentials.'
  } finally {
    loading.value = false
  }
}
</script>
