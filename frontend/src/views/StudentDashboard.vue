<template>
  <div class="container py-4">
    <div class="card border-0 shadow-sm mb-4 bg-primary text-white">
      <div class="card-body p-4 d-flex flex-column flex-md-row justify-content-between align-items-md-center">
        <div>
          <h2 class="fw-bold mb-1"><i class="bi bi-mortarboard-fill me-2"></i> Welcome, {{ studentName }}</h2>
          <p class="mb-0 opacity-75">
            <span class="badge bg-white text-primary me-2">Branch: {{ branch || 'N/A' }}</span>
            <span class="badge bg-white text-primary me-2">CGPA: {{ cgpa ? cgpa.toFixed(2) : 'N/A' }}</span>
            <span class="badge bg-white text-primary me-2">Year: {{ year || 'N/A' }}</span>
          </p>
        </div>
        <button class="btn btn-light text-primary fw-semibold mt-3 mt-md-0" @click="showProfileModal = true">
          <i class="bi bi-pencil-square me-1"></i> Edit Profile & Resume
        </button>
      </div>
    </div>

    <div v-if="alertMessage" class="alert alert-info alert-dismissible fade show shadow-sm" role="alert">
      <i class="bi bi-info-circle-fill me-2"></i> {{ alertMessage }}
      <a v-if="exportDownloadUrl" :href="exportDownloadUrl" target="_blank" class="fw-bold ms-2 text-decoration-underline">Download CSV File</a>
      <button type="button" class="btn-close" @click="alertMessage = ''; exportDownloadUrl = ''"></button>
    </div>

    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white py-3 border-0">
        <ul class="nav nav-tabs card-header-tabs" role="tablist">
          <li class="nav-item">
            <button class="nav-link fw-semibold" :class="{ active: currentTab === 'drives' }" @click="currentTab = 'drives'">
              <i class="bi bi-briefcase me-1"></i> Approved Placement Drives
            </button>
          </li>
          <li class="nav-item">
            <button class="nav-link fw-semibold" :class="{ active: currentTab === 'applications' }" @click="currentTab = 'applications'">
              <i class="bi bi-journal-check me-1"></i> My Placement History <span class="badge bg-primary ms-1">{{ applications.length }}</span>
            </button>
          </li>
          <li class="nav-item">
            <button class="nav-link fw-semibold" :class="{ active: currentTab === 'ats' }" @click="currentTab = 'ats'">
              <i class="bi bi-magic me-1"></i> ATS Keyword Matcher
            </button>
          </li>
        </ul>
      </div>

      <div class="card-body p-4">
        <div v-if="currentTab === 'drives'">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h5 class="fw-bold mb-0">Active Recruitment Drives</h5>
            <input type="text" class="form-control form-control-sm w-auto" placeholder="Search job title/company..." v-model="searchQuery" @input="fetchApprovedDrives" />
          </div>

          <div class="row g-4">
            <div class="col-md-6 col-lg-4" v-for="drive in drives" :key="drive.id">
              <div class="card h-100 border-0 shadow-sm border-top border-4" :class="drive.is_eligible ? 'border-success' : 'border-secondary'">
                <div class="card-body d-flex flex-column">
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <h5 class="fw-bold card-title text-dark mb-0">{{ drive.job_title }}</h5>
                    <span class="badge bg-light text-dark border">{{ drive.company_name }}</span>
                  </div>
                  <p class="card-text text-muted small flex-grow-1">{{ drive.job_description ? drive.job_description.substring(0, 80) + '...' : 'No description' }}</p>
                  <div class="bg-light p-2 rounded mb-3 small">
                    <div><strong>Min CGPA:</strong> {{ drive.min_cgpa }} | <strong>Year:</strong> {{ drive.eligible_year || 'Any' }}</div>
                    <div><strong>Deadline:</strong> {{ new Date(drive.application_deadline).toLocaleDateString() }}</div>
                  </div>

                  <div class="mb-3">
                    <span class="badge bg-success py-2 px-3 w-100" v-if="drive.is_eligible"><i class="bi bi-check-circle me-1"></i> You are Eligible</span>
                    <div v-else>
                      <span class="badge bg-warning text-dark py-2 px-3 w-100"><i class="bi bi-exclamation-triangle me-1"></i> Ineligible</span>
                      <small class="text-danger d-block mt-1 small" v-for="(reason, rIdx) in drive.eligibility_reasons" :key="rIdx">&bull; {{ reason }}</small>
                    </div>
                  </div>

                  <button v-if="drive.has_applied" class="btn btn-outline-secondary w-100" disabled>Already Applied</button>
                  <button v-else class="btn btn-primary w-100" :disabled="!drive.is_eligible || applyingDriveId === drive.id" @click="applyDrive(drive.id)">
                    <span v-if="applyingDriveId === drive.id" class="spinner-border spinner-border-sm me-1"></span>Apply Now
                  </button>
                </div>
              </div>
            </div>
            <div v-if="!drives.length" class="col-12 text-center py-5 text-muted">No approved placement drives found.</div>
          </div>
        </div>

        <div v-if="currentTab === 'applications'">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="fw-bold mb-0">Your Submissions</h5>
            <button class="btn btn-outline-primary btn-sm" @click="exportCSV" :disabled="exporting">
              <span v-if="exporting" class="spinner-border spinner-border-sm me-1"></span>Export History CSV
            </button>
          </div>

          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead class="table-light">
                <tr><th>App ID</th><th>Company</th><th>Job Title</th><th>Date</th><th>Status</th></tr>
              </thead>
              <tbody>
                <tr v-for="app in applications" :key="app.id">
                  <td>#{{ app.id }}</td>
                  <td class="fw-semibold">{{ app.company_name }}</td>
                  <td>{{ app.job_title }}</td>
                  <td><small>{{ new Date(app.application_date).toLocaleDateString() }}</small></td>
                  <td><span class="badge px-3 py-2" :class="appStatusClass(app.status)">{{ app.status.toUpperCase() }}</span></td>
                </tr>
                <tr v-if="!applications.length"><td colspan="5" class="text-center py-5 text-muted">No applications submitted yet.</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="currentTab === 'ats'">
          <div class="card border-0 shadow-sm p-4 text-center max-w-600 mx-auto">
            <h4 class="fw-bold mb-2"><i class="bi bi-magic text-primary me-2"></i> ATS Resume Keyword Matcher</h4>
            <p class="text-muted small mb-4">Static preview showing simulated ATS compatibility metrics.</p>
            <button class="btn btn-primary py-2 fw-semibold w-50 mx-auto mb-4" @click="runAtsCheck" :disabled="analyzingAts">View Static ATS Analysis</button>

            <div v-if="atsResult" class="card p-4 border shadow-sm bg-light text-start">
              <h4 class="fw-bold text-success text-center mb-3">ATS Score Preview: {{ atsResult.ats_score }}%</h4>
              <div class="row g-3 mb-3">
                <div class="col-md-6"><h6 class="fw-bold text-success">Matched Keywords</h6><span class="badge bg-success-subtle text-success border me-1" v-for="kw in atsResult.matched_keywords" :key="kw">{{ kw }}</span></div>
                <div class="col-md-6"><h6 class="fw-bold text-danger">Missing Keywords</h6><span class="badge bg-danger-subtle text-danger border me-1" v-for="kw in atsResult.missing_keywords" :key="kw">{{ kw }}</span></div>
              </div>
              <p class="mb-0 small text-muted text-center">{{ atsResult.message }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade show d-block" tabindex="-1" v-if="showProfileModal" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-md modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header"><h5 class="modal-title fw-bold">Update Profile & Resume</h5><button type="button" class="btn-close" @click="showProfileModal = false"></button></div>
          <div class="modal-body">
            <form @submit.prevent="updateProfile">
              <div class="mb-3"><label class="form-label fw-semibold">Branch</label><select class="form-select" v-model="profileForm.branch" required><option value="CSE">CSE</option><option value="ECE">ECE</option><option value="MECH">MECH</option><option value="CIVIL">CIVIL</option><option value="EEE">EEE</option></select></div>
              <div class="row mb-3">
                <div class="col-6"><label class="form-label fw-semibold">CGPA</label><input type="number" step="0.01" min="0" max="10" class="form-control" v-model="profileForm.cgpa" required /></div>
                <div class="col-6"><label class="form-label fw-semibold">Graduation Year</label><input type="number" class="form-control" v-model="profileForm.graduation_year" required /></div>
              </div>
              <div class="mb-3"><label class="form-label fw-semibold">Phone</label><input type="tel" class="form-control" v-model="profileForm.phone" /></div>
              <button type="submit" class="btn btn-primary w-100 mb-3" :disabled="savingProfile">Save Profile</button>
            </form>
            <hr />
            <div class="mb-3">
              <label class="form-label fw-semibold">Upload PDF / DOC Resume</label>
              <input type="file" class="form-control" @change="onFileSelected" accept=".pdf,.doc,.docx" />
              <button class="btn btn-outline-primary w-100 mt-2" @click="uploadResume" :disabled="!selectedFile || uploading">Upload Resume</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { authStore } from '../store/auth.js'

const studentName = computed(() => authStore.user?.name || '')
const branch = computed(() => authStore.profile?.branch || '')
const cgpa = computed(() => authStore.profile?.cgpa || 0)
const year = computed(() => authStore.profile?.graduation_year || 0)

const currentTab = ref('drives')
const alertMessage = ref('')
const exportDownloadUrl = ref('')
const exporting = ref(false)
const drives = ref([])
const applications = ref([])
const searchQuery = ref('')
const applyingDriveId = ref(null)
const showProfileModal = ref(false)
const savingProfile = ref(false)
const uploading = ref(false)
const selectedFile = ref(null)

const profileForm = ref({
  branch: authStore.profile?.branch || 'CSE',
  cgpa: authStore.profile?.cgpa || 8.0,
  graduation_year: authStore.profile?.graduation_year || 2026,
  phone: authStore.profile?.phone || ''
})

const atsResult = ref(null)
const analyzingAts = ref(false)

const appStatusClass = (status) => ({ 'bg-primary': status === 'applied', 'bg-warning text-dark': status === 'shortlisted', 'bg-success': status === 'selected', 'bg-danger': status === 'rejected' })

const fetchApprovedDrives = async () => {
  try { drives.value = (await axios.get('/api/student/drives', { params: { search: searchQuery.value } })).data.drives } catch (err) {}
}

const fetchStudentApplications = async () => {
  try {
    const res = await axios.get('/api/student/applications')
    applications.value = res.data.applications
    if (res.data.student) authStore.updateProfile(res.data.student)
  } catch (err) {}
}

const applyDrive = async (driveId) => {
  applyingDriveId.value = driveId
  try {
    const res = await axios.post(`/api/student/drives/${driveId}/apply`)
    alertMessage.value = res.data.message
    fetchApprovedDrives()
    fetchStudentApplications()
  } catch (err) { alert(err.response?.data?.error || 'Application failed') }
  finally { applyingDriveId.value = null }
}

const exportCSV = async () => {
  exporting.value = true; alertMessage.value = ''; exportDownloadUrl.value = ''
  try {
    const res = await axios.post('/api/student/export-csv')
    let result = res.data.result
    if (!result && res.data.task_id) {
      try { result = (await axios.get(`/api/jobs/status/${res.data.task_id}`)).data.result } catch (e) {}
    }
    if (result && result.download_url) {
      alertMessage.value = 'CSV Export completed successfully!'
      exportDownloadUrl.value = result.download_url
    } else { alertMessage.value = 'CSV Export job submitted in background.' }
  } catch (err) { alertMessage.value = err.response?.data?.error || 'Failed to export CSV' }
  finally { exporting.value = false }
}

const onFileSelected = (e) => { selectedFile.value = e.target.files[0] }

const updateProfile = async () => {
  savingProfile.value = true
  try {
    const res = await axios.put('/api/auth/profile', profileForm.value)
    authStore.updateProfile(res.data.profile)
    showProfileModal.value = false
    fetchApprovedDrives()
  } catch (err) { alert('Failed to update profile') }
  finally { savingProfile.value = false }
}

const uploadResume = async () => {
  if (!selectedFile.value) return
  uploading.value = true
  const formData = new FormData()
  formData.append('resume', selectedFile.value)
  try {
    await axios.post('/api/auth/upload-resume', formData)
    alert('Resume uploaded successfully!')
    showProfileModal.value = false
    fetchStudentApplications()
  } catch (err) { alert(err.response?.data?.error || 'Resume upload failed') }
  finally { uploading.value = false }
}

const runAtsCheck = async () => {
  analyzingAts.value = true
  try { atsResult.value = (await axios.post('/api/student/ats-check')).data }
  catch (err) {
    atsResult.value = { ats_score: 85, matched_keywords: ['python', 'sql', 'communication'], missing_keywords: ['docker'], message: 'ATS Feature Preview: Static dummy evaluation complete.' }
  } finally { analyzingAts.value = false }
}

onMounted(() => { fetchApprovedDrives(); fetchStudentApplications() })
</script>
