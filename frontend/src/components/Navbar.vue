<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
    <div class="container-fluid px-4">
      <router-link class="navbar-brand d-flex align-items-center fw-bold" to="/">
        <i class="bi bi-briefcase-fill text-primary me-2 fs-4"></i>
        <span>Placement Portal <span class="badge bg-primary fs-6 ms-1">V2</span></span>
      </router-link>

      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarMain"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarMain">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0" v-if="authStore.isAuthenticated()">
          <li class="nav-item" v-if="role === 'admin'">
            <router-link class="nav-link" to="/admin/dashboard">
              <i class="bi bi-speedometer2 me-1"></i> Admin Dashboard
            </router-link>
          </li>
          <li class="nav-item" v-if="role === 'company'">
            <router-link class="nav-link" to="/company/dashboard">
              <i class="bi bi-building me-1"></i> Company Dashboard
            </router-link>
          </li>
          <li class="nav-item" v-if="role === 'student'">
            <router-link class="nav-link" to="/student/dashboard">
              <i class="bi bi-person-badge me-1"></i> Student Dashboard
            </router-link>
          </li>
        </ul>

        <div class="d-flex align-items-center ms-auto" v-if="authStore.isAuthenticated()">
          <span class="badge bg-outline-light text-light me-3 border border-secondary px-3 py-2">
            <i class="bi bi-shield-lock-fill text-warning me-1"></i>
            <span class="text-uppercase fw-semibold">{{ role }}</span>
          </span>
          <span class="text-light me-3 d-none d-md-inline fw-medium">
            {{ authStore.user?.name }}
          </span>
          <button class="btn btn-outline-danger btn-sm px-3" @click="handleLogout">
            <i class="bi bi-box-arrow-right me-1"></i> Logout
          </button>
        </div>

        <div class="d-flex align-items-center ms-auto" v-else>
          <router-link to="/login" class="btn btn-outline-light me-2">Login</router-link>
          <router-link to="/register" class="btn btn-primary">Register</router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { authStore } from '../store/auth.js'

const router = useRouter()
const role = computed(() => authStore.getRole())

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.navbar-brand {
  letter-spacing: -0.5px;
}
</style>
