<template>
  <div class="container py-4">
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-4 pb-2 border-bottom">
      <div>
        <h2 class="fw-bold text-dark mb-1"><i class="bi bi-building-fill text-primary me-2"></i> Company Recruitment Dashboard</h2>
        <p class="text-muted small mb-0">{{ companyName }} &bull; HR Contact: {{ hrContact || 'Not Set' }}</p>
      </div>
      <button class="btn btn-primary mt-3 mt-md-0" @click="showCreateModal = true" :disabled="approvalStatus !== 'approved' || isBlacklisted">
        <i class="bi bi-plus-lg me-1"></i> Create Placement Drive
      </button>
    </div>

    <div v-if="approvalStatus === 'pending'" class="alert alert-warning border-warning border-2 d-flex align-items-center mb-4">
      <i class="bi bi-clock-history fs-3 me-3 text-warning"></i>
      <div><h5 class="alert-heading fw-bold mb-1">Registration Pending Admin Approval</h5><p class="mb-0 small">Under review by Institute Placement Cell. Drive posting enabled after approval.</p></div>
    </div>
    <div v-else-if="approvalStatus === 'rejected'" class="alert alert-danger border-danger border-2 d-flex align-items-center mb-4">
      <i class="bi bi-x-circle-fill fs-3 me-3 text-danger"></i>
      <div><h5 class="alert-heading fw-bold mb-1">Registration Request Rejected</h5><p class="mb-0 small">Contact placement cell for details.</p></div>
    </div>
    <div v-if="isBlacklisted" class="alert alert-danger border-danger border-2 mb-4">
      <i class="bi bi-slash-circle-fill me-2"></i> <strong>Notice:</strong> Blacklisted by Institute. Drive creation disabled.
    </div>

    <div class="card border-0 shadow-sm mb-4">
      <div class="card-header bg-white fw-bold py-3 border-0 d-flex justify-content-between align-items-center">
        <span><i class="bi bi-card-checklist text-primary me-2"></i> Your Placement Drives</span>
        <span class="badge bg-secondary">{{ drives.length }} Total Drives</span>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr><th>Drive ID</th><th>Job Title</th><th>Eligibility</th><th>Deadline</th><th>Applicants</th><th>Status</th><th class="text-end px-4">Actions</th></tr>
            </thead>
            <tbody>
              <tr v-for="d in drives" :key="d.id">
                <td>#{{ d.id }}</td>
                <td class="fw-semibold">{{ d.job_title }}</td>
                <td><small class="d-block">Branch: {{ d.eligible_branches || 'All' }} | Min CGPA: {{ d.min_cgpa }}</small></td>
                <td><small>{{ new Date(d.application_deadline).toLocaleDateString() }}</small></td>
                <td><span class="badge bg-primary rounded-pill px-3">{{ d.applicant_count }} Applicants</span></td>
                <td><span class="badge" :class="statusClass(d.status)">{{ d.status.toUpperCase() }}</span></td>
                <td class="text-end px-4"><button class="btn btn-sm btn-outline-primary" @click="viewApplications(d)">View Applicants</button></td>
              </tr>
              <tr v-if="!drives.length"><td colspan="7" class="text-center py-5 text-muted">No placement drives created yet.</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="modal fade show d-block" tabindex="-1" v-if="showCreateModal" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header"><h5 class="modal-title fw-bold">Create Placement Drive</h5><button type="button" class="btn-close" @click="showCreateModal = false"></button></div>
          <form @submit.prevent="handleCreateDrive">
            <div class="modal-body">
              <div class="mb-3"><label class="form-label fw-semibold">Job Title *</label><input type="text" class="form-control" v-model="newDrive.job_title" required /></div>
              <div class="mb-3"><label class="form-label fw-semibold">Description</label><textarea class="form-control" rows="3" v-model="newDrive.job_description"></textarea></div>
              <div class="row">
                <div class="col-md-6 mb-3"><label class="form-label fw-semibold">Eligible Branches</label><input type="text" class="form-control" v-model="newDrive.eligible_branches" /></div>
                <div class="col-md-3 mb-3"><label class="form-label fw-semibold">Min CGPA</label><input type="number" step="0.1" min="0" max="10" class="form-control" v-model="newDrive.min_cgpa" /></div>
                <div class="col-md-3 mb-3"><label class="form-label fw-semibold">Eligible Year</label><input type="number" class="form-control" v-model="newDrive.eligible_year" /></div>
              </div>
              <div class="mb-3"><label class="form-label fw-semibold">Deadline *</label><input type="datetime-local" class="form-control" v-model="newDrive.application_deadline" required /></div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="showCreateModal = false">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="submittingDrive">Submit Drive</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <div class="modal fade show d-block" tabindex="-1" v-if="selectedDrive" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-xl modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header"><h5 class="modal-title fw-bold">Applicants for {{ selectedDrive.job_title }}</h5><button type="button" class="btn-close" @click="selectedDrive = null"></button></div>
          <div class="modal-body p-0">
            <div class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                  <tr><th>App ID</th><th>Student</th><th>Email/Phone</th><th>Branch</th><th>CGPA</th><th>Year</th><th>Resume</th><th>Status</th><th class="text-end px-3">Actions</th></tr>
                </thead>
                <tbody>
                  <tr v-for="app in driveApplicants" :key="app.id">
                    <td>#{{ app.id }}</td>
                    <td class="fw-semibold">{{ app.student_name }}</td>
                    <td><small class="d-block">{{ app.student_email }}</small><small class="text-muted">{{ app.student_phone || 'N/A' }}</small></td>
                    <td><span class="badge bg-secondary">{{ app.student_branch }}</span></td>
                    <td class="fw-bold">{{ app.student_cgpa }}</td>
                    <td>{{ app.student_year }}</td>
                    <td><a v-if="app.resume_link" :href="app.resume_link" target="_blank" class="btn btn-sm btn-outline-primary py-0">Resume</a><span v-else class="text-muted small">None</span></td>
                    <td><span class="badge" :class="appStatusClass(app.status)">{{ app.status.toUpperCase() }}</span></td>
                    <td class="text-end px-3">
                      <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-warning" @click="updateStatus(app.id, 'shortlisted')">Shortlist</button>
                        <button class="btn btn-outline-success" @click="updateStatus(app.id, 'selected')">Select</button>
                        <button class="btn btn-outline-danger" @click="updateStatus(app.id, 'rejected')">Reject</button>
                        <button v-if="app.status === 'selected'" class="btn btn-success" @click="openOfferLetterModal(app)">Offer</button>
                      </div>
                    </td>
                  </tr>
                  <tr v-if="!driveApplicants.length"><td colspan="9" class="text-center py-4 text-muted">No student applications received yet.</td></tr>
                </tbody>
              </table>
            </div>
          </div>
          <div class="modal-footer"><button type="button" class="btn btn-secondary" @click="selectedDrive = null">Close</button></div>
        </div>
      </div>
    </div>

    <div class="modal fade show d-block" tabindex="-1" v-if="offerLetterData" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-success border-2">
          <div class="modal-header bg-success text-white"><h5 class="modal-title fw-bold">Official Offer Letter Preview</h5><button type="button" class="btn-close btn-close-white" @click="offerLetterData = null"></button></div>
          <div class="modal-body p-4 bg-light">
            <div class="card p-4 border shadow-sm text-dark bg-white">
              <div class="text-center border-bottom pb-3 mb-3">
                <h4 class="fw-bold text-success">{{ offerLetterData.company_name }}</h4>
                <p class="small text-muted mb-0">Ref No: {{ offerLetterData.reference_no }} &bull; Date: {{ offerLetterData.issue_date }}</p>
              </div>
              <p>Dear <strong>{{ offerLetterData.candidate_name }}</strong>,</p>
              <p>We offer you the position of <strong>{{ offerLetterData.job_title }}</strong> at {{ offerLetterData.company_name }}.</p>
              <table class="table table-bordered small my-3">
                <tr><th>Position</th><td>{{ offerLetterData.job_title }}</td></tr>
                <tr><th>CTC</th><td>{{ offerLetterData.salary }}</td></tr>
                <tr><th>Joining Date</th><td>{{ offerLetterData.joining_date }}</td></tr>
                <tr><th>Location</th><td>{{ offerLetterData.location }}</td></tr>
              </table>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-primary" @click="printOfferLetter">Print / Download</button>
            <button type="button" class="btn btn-secondary" @click="offerLetterData = null">Close</button>
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

const companyName = computed(() => authStore.profile?.company_name || authStore.user?.name || '')
const hrContact = computed(() => authStore.profile?.hr_contact || '')
const approvalStatus = ref(authStore.profile?.approval_status || 'pending')
const isBlacklisted = ref(authStore.profile?.is_blacklisted || false)

const drives = ref([])
const showCreateModal = ref(false)
const submittingDrive = ref(false)
const selectedDrive = ref(null)
const driveApplicants = ref([])
const offerLetterData = ref(null)

const newDrive = ref({ job_title: '', job_description: '', eligible_branches: 'CSE, ECE', min_cgpa: 7.0, eligible_year: 2026, application_deadline: '' })

const statusClass = (status) => ({ 'bg-warning text-dark': status === 'pending', 'bg-success': status === 'approved', 'bg-danger': status === 'rejected', 'bg-secondary': status === 'closed' })
const appStatusClass = (status) => ({ 'bg-primary': status === 'applied', 'bg-warning text-dark': status === 'shortlisted', 'bg-success': status === 'selected', 'bg-danger': status === 'rejected' })

const fetchCompanyDrives = async () => {
  try {
    const res = await axios.get('/api/company/drives')
    drives.value = res.data.drives
    approvalStatus.value = res.data.company_status
    isBlacklisted.value = res.data.is_blacklisted
  } catch (err) {}
}

const handleCreateDrive = async () => {
  submittingDrive.value = true
  try {
    await axios.post('/api/company/drives', newDrive.value)
    showCreateModal.value = false
    fetchCompanyDrives()
  } catch (err) { alert(err.response?.data?.error || 'Failed to create drive') }
  finally { submittingDrive.value = false }
}

const viewApplications = async (drive) => {
  selectedDrive.value = drive
  try { driveApplicants.value = (await axios.get(`/api/company/drives/${drive.id}/applications`)).data.applications } catch (err) {}
}

const updateStatus = async (appId, status) => {
  try {
    await axios.put(`/api/company/applications/${appId}/status`, { status })
    if (selectedDrive.value) viewApplications(selectedDrive.value)
  } catch (err) {}
}

const openOfferLetterModal = async (app) => {
  try { offerLetterData.value = (await axios.post('/api/company/generate-offer-letter', { application_id: app.id })).data.offer_letter } catch (err) {}
}

const printOfferLetter = () => window.print()

onMounted(fetchCompanyDrives)
</script>
