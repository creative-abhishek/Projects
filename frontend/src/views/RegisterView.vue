<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-md-8 col-lg-7">
        <div class="card shadow border-0">
          <div class="card-body p-4 p-md-5">
            <div class="text-center mb-4">
              <h3 class="fw-bold">Create AN Account</h3>
              <p class="text-muted small">Select your role to register on the Placement Portal</p>

              <ul class="nav nav-pills nav-justified mt-3 bg-light p-1 rounded border" role="tablist">
                <li class="nav-item" role="presentation">
                  <button
                    class="nav-link fw-semibold"
                    :class="{ active: activeRole === 'student' }"
                    @click="activeRole = 'student'"
                  >
                    <i class="bi bi-mortarboard-fill me-1"></i> Student Registration
                  </button>
                </li>
                <li class="nav-item" role="presentation">
                  <button
                    class="nav-link fw-semibold"
                    :class="{ active: activeRole === 'company' }"
                    @click="activeRole = 'company'"
                  >
                    <i class="bi bi-building me-1"></i> Company Registration
                  </button>
                </li>
              </ul>
            </div>

            <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
              <i class="bi bi-exclamation-triangle-fill me-2"></i> {{ error }}
              <button type="button" class="btn-close" @click="error = ''"></button>
            </div>

            <div v-if="success" class="alert alert-success alert-dismissible fade show" role="alert">
              <i class="bi bi-check-circle-fill me-2"></i> {{ success }}
            </div>

            <form v-if="activeRole === 'student'" @submit.prevent="handleStudentRegister">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label fw-semibold">Full Name *</label>
                  <input type="text" class="form-control" v-model="studentForm.name" placeholder="John Doe" required />
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label fw-semibold">Email Address *</label>
                  <input type="email" class="form-control" v-model="studentForm.email" placeholder="john@student.edu" required />
                </div>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label fw-semibold">Password *</label>
                  <input type="password" class="form-control" v-model="studentForm.password" placeholder="••••••••" required />
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label fw-semibold">Phone Number</label>
                  <input type="tel" class="form-control" v-model="studentForm.phone" placeholder="+91 9876543210" />
                </div>
              </div>

              <div class="row">
                <div class="col-md-4 mb-3">
                  <label class="form-label fw-semibold">Branch *</label>
                  <select class="form-select" v-model="studentForm.branch" required>
                    <option value="" disabled>Select Branch</option>
                    <option value="CSE">Computer Science (CSE)</option>
                    <option value="ECE">Electronics (ECE)</option>
                    <option value="MECH">Mechanical (MECH)</option>
                    <option value="CIVIL">Civil Engg (CIVIL)</option>
                    <option value="EEE">Electrical (EEE)</option>
                  </select>
                </div>
                <div class="col-md-4 mb-3">
                  <label class="form-label fw-semibold">CGPA *</label>
                  <input type="number" step="0.01" min="0" max="10" class="form-control" v-model="studentForm.cgpa" placeholder="e.g. 8.5" required />
                </div>
                <div class="col-md-4 mb-3">
                  <label class="form-label fw-semibold">Passout Year *</label>
                  <input type="number" min="2020" max="2030" class="form-control" v-model="studentForm.graduation_year" placeholder="e.g. 2026" required />
                </div>
              </div>

              <button type="submit" class="btn btn-primary w-100 py-2 mt-2 fw-semibold" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                Register as Student
              </button>
            </form>

            <form v-else @submit.prevent="handleCompanyRegister">
              <div class="mb-3">
                <label class="form-label fw-semibold">Company Name *</label>
                <input type="text" class="form-control" v-model="companyForm.company_name" placeholder="Acme Technologies" required />
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label fw-semibold">HR Email Address *</label>
                  <input type="email" class="form-control" v-model="companyForm.email" placeholder="hr@acme.com" required />
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label fw-semibold">Password *</label>
                  <input type="password" class="form-control" v-model="companyForm.password" placeholder="••••••••" required />
                </div>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label fw-semibold">HR Contact Person / Phone</label>
                  <input type="text" class="form-control" v-model="companyForm.hr_contact" placeholder="Jane Smith (+91 9876543210)" />
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label fw-semibold">Company Website</label>
                  <input type="url" class="form-control" v-model="companyForm.website" placeholder="https://acme.com" />
                </div>
              </div>

              <div class="alert alert-info py-2 small">
                <i class="bi bi-info-circle me-1"></i> Company accounts require Institute Admin approval before creating placement drives.
              </div>

              <button type="submit" class="btn btn-primary w-100 py-2 mt-2 fw-semibold" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                Register Company Profile
              </button>
            </form>

            <div class="mt-4 text-center">
              <p class="text-muted small mb-0">
                Already have an account?
                <router-link to="/login" class="fw-bold text-decoration-none">Sign In</router-link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { authStore } from '../store/auth.js'

const router = useRouter()
const activeRole = ref('student')
const loading = ref(false)
const error = ref('')
const success = ref('')

const studentForm = reactive({
  name: '',
  email: '',
  password: '',
  phone: '',
  branch: 'CSE',
  cgpa: 8.0,
  graduation_year: 2026
})

const companyForm = reactive({
  company_name: '',
  email: '',
  password: '',
  hr_contact: '',
  website: ''
})

const handleStudentRegister = async () => {
  error.value = ''
  success.value = ''
  loading.value = true

  try {
    const res = await axios.post('/api/auth/register/student', studentForm)
    authStore.setAuth(res.data.access_token, res.data.user, res.data.profile)
    router.push('/student/dashboard')
  } catch (err) {
    error.value = err.response?.data?.error || 'Student registration failed'
  } finally {
    loading.value = false
  }
}

const handleCompanyRegister = async () => {
  error.value = ''
  success.value = ''
  loading.value = true

  try {
    const res = await axios.post('/api/auth/register/company', companyForm)
    authStore.setAuth(res.data.access_token, res.data.user, res.data.profile)
    router.push('/company/dashboard')
  } catch (err) {
    error.value = err.response?.data?.error || 'Company registration failed'
  } finally {
    loading.value = false
  }
}
</script>
