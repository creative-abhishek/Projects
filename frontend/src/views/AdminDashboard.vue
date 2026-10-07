<template>
  <div class="container-fluid px-4 py-3">
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-4 pb-2 border-bottom">
      <div>
        <h2 class="fw-bold text-dark mb-1"><i class="bi bi-shield-lock-fill text-primary me-2"></i> Admin Control Center</h2>
        <p class="text-muted small mb-0">Institute Placement Cell Management & System Analytics</p>
      </div>
      <div class="mt-3 mt-md-0 d-flex gap-2">
        <button class="btn btn-outline-primary btn-sm" @click="triggerMonthlyReport" :disabled="triggeringReport">
          <span v-if="triggeringReport" class="spinner-border spinner-border-sm me-1"></span>
          <i v-else class="bi bi-file-earmark-pdf me-1"></i> Generate Report
        </button>
        <button class="btn btn-outline-secondary btn-sm" @click="triggerDailyReminders" :disabled="triggeringReminders">
          <span v-if="triggeringReminders" class="spinner-border spinner-border-sm me-1"></span>
          <i v-else class="bi bi-bell-fill me-1"></i> Trigger Reminders
        </button>
        <button class="btn btn-sm btn-primary" @click="fetchData"><i class="bi bi-arrow-clockwise me-1"></i> Refresh</button>
      </div>
    </div>

    <div v-if="alertMessage" class="alert alert-info alert-dismissible fade show" role="alert">
      <i class="bi bi-info-circle-fill me-2"></i> {{ alertMessage }}
      <a v-if="reportUrl" :href="reportUrl" target="_blank" class="fw-bold ms-2 text-decoration-underline">View HTML Report</a>
      <button type="button" class="btn-close" @click="alertMessage = ''; reportUrl = ''"></button>
    </div>

    <div class="row g-3 mb-4">
      <div class="col-6 col-md-3" v-for="(card, i) in statCards" :key="i">
        <div class="card border-0 shadow-sm bg-white h-100 p-3 border-start border-4" :class="'border-' + card.color">
          <div class="d-flex align-items-center">
            <div class="rounded-circle p-3 me-3" :class="`bg-${card.color}-subtle text-${card.color}`">
              <i :class="`bi ${card.icon} fs-3`"></i>
            </div>
            <div>
              <div class="text-muted small fw-semibold">{{ card.title }}</div>
              <div class="fs-3 fw-bold text-dark">
                {{ card.value }}
                <span v-if="card.sub" class="badge text-dark fs-6 ms-1" :class="'bg-' + card.color">{{ card.sub }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4 mb-4" v-if="stats.charts">
      <div class="col-md-6 col-lg-4">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-white fw-bold py-3 border-0"><i class="bi bi-pie-chart-fill text-primary me-2"></i> Drives Status</div>
          <div class="card-body"><Doughnut :data="driveChartData" :options="chartOptions" /></div>
        </div>
      </div>

      <div class="col-md-6 col-lg-4">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-white fw-bold py-3 border-0"><i class="bi bi-bar-chart-line-fill text-success me-2"></i> Application Outcomes</div>
          <div class="card-body"><Bar :data="appChartData" :options="chartOptions" /></div>
        </div>
      </div>

      <div class="col-md-12 col-lg-4">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-white fw-bold py-3 border-0"><i class="bi bi-trophy-fill text-warning me-2"></i> Top Recruiters</div>
          <div class="card-body">
            <ul class="list-group list-group-flush" v-if="stats.charts.top_companies.length">
              <li v-for="(comp, idx) in stats.charts.top_companies" :key="idx" class="list-group-item d-flex justify-content-between align-items-center py-3">
                <div class="fw-semibold text-dark"><span class="badge bg-secondary me-2">#{{ idx + 1 }}</span>{{ comp.name }}</div>
                <span class="badge bg-primary rounded-pill">{{ comp.drives }} Drives</span>
              </li>
            </ul>
            <p v-else class="text-muted text-center py-4 mb-0">No companies data available</p>
          </div>
        </div>
      </div>
    </div>

    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white py-3 border-0">
        <ul class="nav nav-tabs card-header-tabs" role="tablist">
          <li class="nav-item">
            <button class="nav-link fw-semibold" :class="{ active: currentTab === 'companies' }" @click="currentTab = 'companies'; fetchCompanies()">
              <i class="bi bi-building me-1"></i> Company Approvals
              <span class="badge bg-danger ms-1" v-if="pendingCompaniesCount">{{ pendingCompaniesCount }}</span>
            </button>
          </li>
          <li class="nav-item">
            <button class="nav-link fw-semibold" :class="{ active: currentTab === 'drives' }" @click="currentTab = 'drives'; fetchDrives()">
              <i class="bi bi-briefcase me-1"></i> Drive Approvals
              <span class="badge bg-danger ms-1" v-if="pendingDrivesCount">{{ pendingDrivesCount }}</span>
            </button>
          </li>
          <li class="nav-item">
            <button class="nav-link fw-semibold" :class="{ active: currentTab === 'students' }" @click="currentTab = 'students'; fetchStudents()">
              <i class="bi bi-people me-1"></i> Students Directory
            </button>
          </li>
        </ul>
      </div>

      <div class="card-body p-4">
        <div v-if="currentTab === 'companies'">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="fw-bold mb-0">Registered Companies</h5>
            <input type="text" class="form-control form-control-sm w-auto" placeholder="Search company/email..." v-model="companySearch" @input="fetchCompanies" />
          </div>

          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead class="table-light">
                <tr><th>ID</th><th>Company Name</th><th>HR Contact</th><th>Website</th><th>Approval</th><th>Blacklist</th><th>Status</th><th class="text-end">Actions</th></tr>
              </thead>
              <tbody>
                <tr v-for="comp in companies" :key="comp.id">
                  <td>#{{ comp.id }}</td>
                  <td class="fw-semibold">{{ comp.company_name }}</td>
                  <td>{{ comp.hr_contact || 'N/A' }}</td>
                  <td><a v-if="comp.website" :href="comp.website" target="_blank" class="small text-truncate d-inline-block" style="max-width: 150px;">{{ comp.website }}</a><span v-else class="text-muted small">N/A</span></td>
                  <td><span class="badge" :class="statusClass(comp.approval_status)">{{ comp.approval_status.toUpperCase() }}</span></td>
                  <td><span class="badge bg-danger" v-if="comp.is_blacklisted">BLACKLISTED</span><span class="badge bg-secondary" v-else>Active</span></td>
                  <td><span class="badge" :class="comp.is_active ? 'bg-success' : 'bg-danger'">{{ comp.is_active ? 'ACTIVE' : 'DEACTIVATED' }}</span></td>
                  <td class="text-end">
                    <div class="btn-group btn-group-sm">
                      <button v-if="comp.approval_status !== 'approved'" class="btn btn-outline-success" @click="approveCompany(comp.id)">Approve</button>
                      <button v-if="comp.approval_status !== 'rejected'" class="btn btn-outline-danger" @click="rejectCompany(comp.id)">Reject</button>
                      <button class="btn btn-outline-dark" @click="toggleBlacklistCompany(comp.id)">{{ comp.is_blacklisted ? 'Whitelist' : 'Blacklist' }}</button>
                      <button class="btn btn-outline-secondary" @click="toggleUserActive(comp.user_id)">{{ comp.is_active ? 'Deactivate' : 'Activate' }}</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="currentTab === 'drives'">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="fw-bold mb-0">Placement Drives Queue</h5>
            <input type="text" class="form-control form-control-sm w-auto" placeholder="Search drive/company..." v-model="driveSearch" @input="fetchDrives" />
          </div>

          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead class="table-light">
                <tr><th>ID</th><th>Company</th><th>Job Title</th><th>Eligibility</th><th>Deadline</th><th>Applicants</th><th>Status</th><th class="text-end">Actions</th></tr>
              </thead>
              <tbody>
                <tr v-for="d in drives" :key="d.id">
                  <td>#{{ d.id }}</td>
                  <td class="fw-semibold">{{ d.company_name }}</td>
                  <td>{{ d.job_title }}</td>
                  <td><small class="d-block">Branch: {{ d.eligible_branches || 'All' }} | Min CGPA: {{ d.min_cgpa }}</small></td>
                  <td><small>{{ new Date(d.application_deadline).toLocaleDateString() }}</small></td>
                  <td><span class="badge bg-info text-dark">{{ d.applicant_count }}</span></td>
                  <td><span class="badge" :class="statusClass(d.status)">{{ d.status.toUpperCase() }}</span></td>
                  <td class="text-end">
                    <div class="btn-group btn-group-sm">
                      <button v-if="d.status !== 'approved'" class="btn btn-outline-success" @click="approveDrive(d.id)">Approve</button>
                      <button v-if="d.status !== 'rejected'" class="btn btn-outline-danger" @click="rejectDrive(d.id)">Reject</button>
                      <button v-if="d.status !== 'closed'" class="btn btn-outline-secondary" @click="closeDrive(d.id)">Close</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="currentTab === 'students'">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="fw-bold mb-0">Student Directory</h5>
            <input type="text" class="form-control form-control-sm w-auto" placeholder="Search student/branch..." v-model="studentSearch" @input="fetchStudents" />
          </div>

          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead class="table-light">
                <tr><th>ID</th><th>Name</th><th>Email</th><th>Branch</th><th>CGPA</th><th>Grad Year</th><th>Resume</th><th>Account</th><th class="text-end">Actions</th></tr>
              </thead>
              <tbody>
                <tr v-for="s in students" :key="s.id">
                  <td>#{{ s.id }}</td>
                  <td class="fw-semibold">{{ s.name }}</td>
                  <td>{{ s.email }}</td>
                  <td><span class="badge bg-secondary">{{ s.branch || 'N/A' }}</span></td>
                  <td>{{ s.cgpa ? s.cgpa.toFixed(2) : 'N/A' }}</td>
                  <td>{{ s.graduation_year || 'N/A' }}</td>
                  <td><a v-if="s.resume_link" :href="s.resume_link" target="_blank" class="btn btn-sm btn-outline-primary py-0">View</a><span v-else class="text-muted small">None</span></td>
                  <td><span class="badge" :class="s.is_active ? 'bg-success' : 'bg-danger'">{{ s.is_active ? 'Active' : 'Deactivated' }}</span></td>
                  <td class="text-end">
                    <button class="btn btn-sm" :class="s.is_active ? 'btn-outline-danger' : 'btn-outline-success'" @click="toggleUserActive(s.user_id)">
                      {{ s.is_active ? 'Deactivate' : 'Activate' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement, BarElement, CategoryScale, LinearScale } from 'chart.js'
import { Doughnut, Bar } from 'vue-chartjs'

ChartJS.register(Title, Tooltip, Legend, ArcElement, BarElement, CategoryScale, LinearScale)

const currentTab = ref('companies')
const alertMessage = ref('')
const reportUrl = ref('')
const triggeringReport = ref(false)
const triggeringReminders = ref(false)

const stats = ref({ summary: {}, charts: { drives_distribution: {}, applications_distribution: {}, top_companies: [] } })
const companies = ref([])
const drives = ref([])
const students = ref([])
const companySearch = ref('')
const driveSearch = ref('')
const studentSearch = ref('')

const pendingCompaniesCount = computed(() => companies.value.filter(c => c.approval_status === 'pending').length)
const pendingDrivesCount = computed(() => drives.value.filter(d => d.status === 'pending').length)

const statCards = computed(() => [
  { title: 'Total Students', value: stats.value.summary.total_students || 0, color: 'primary', icon: 'bi-people-fill' },
  { title: 'Companies', value: stats.value.summary.total_companies || 0, sub: `${stats.value.summary.pending_companies || 0} Pending`, color: 'warning', icon: 'bi-building' },
  { title: 'Placement Drives', value: stats.value.summary.total_drives || 0, sub: `${stats.value.summary.pending_drives || 0} Pending`, color: 'info', icon: 'bi-briefcase-fill' },
  { title: 'Students Placed', value: stats.value.summary.selected_applications || 0, color: 'success', icon: 'bi-check-circle-fill' }
])

const chartOptions = { responsive: true, maintainAspectRatio: false }

const driveChartData = computed(() => {
  const dist = stats.value.charts.drives_distribution || {}
  return { labels: Object.keys(dist), datasets: [{ backgroundColor: ['#ffc107', '#198754', '#dc3545', '#6c757d'], data: Object.values(dist) }] }
})

const appChartData = computed(() => {
  const dist = stats.value.charts.applications_distribution || {}
  return { labels: Object.keys(dist), datasets: [{ label: 'Applications', backgroundColor: '#0d6efd', data: Object.values(dist) }] }
})

const statusClass = (status) => ({
  'bg-warning text-dark': status === 'pending',
  'bg-success': status === 'approved',
  'bg-danger': status === 'rejected',
  'bg-secondary': status === 'closed'
})

const fetchData = async () => {
  try { stats.value = (await axios.get('/api/admin/stats')).data } catch (e) {}
  await Promise.allSettled([fetchCompanies(), fetchDrives(), fetchStudents()])
}

const fetchCompanies = async () => { companies.value = (await axios.get('/api/admin/companies', { params: { search: companySearch.value } })).data.companies || [] }
const fetchDrives = async () => { drives.value = (await axios.get('/api/admin/drives', { params: { search: driveSearch.value } })).data.drives || [] }
const fetchStudents = async () => { students.value = (await axios.get('/api/admin/students', { params: { search: studentSearch.value } })).data.students || [] }

const approveCompany = async (id) => { await axios.post(`/api/admin/companies/${id}/approve`); fetchData() }
const rejectCompany = async (id) => { await axios.post(`/api/admin/companies/${id}/reject`); fetchData() }
const toggleBlacklistCompany = async (id) => { await axios.post(`/api/admin/companies/${id}/toggle-blacklist`); fetchData() }
const approveDrive = async (id) => { await axios.post(`/api/admin/drives/${id}/approve`); fetchData() }
const rejectDrive = async (id) => { await axios.post(`/api/admin/drives/${id}/reject`); fetchData() }
const closeDrive = async (id) => { await axios.post(`/api/admin/drives/${id}/close`); fetchData() }
const toggleUserActive = async (id) => { await axios.post(`/api/admin/users/${id}/toggle-active`); fetchData() }

const triggerMonthlyReport = async () => {
  triggeringReport.value = true; alertMessage.value = ''
  try {
    const res = await axios.post('/api/jobs/trigger-monthly-report')
    alertMessage.value = 'Monthly activity report generated successfully!'
    if (res.data.result?.report_url) reportUrl.value = res.data.result.report_url
  } catch (e) { alertMessage.value = 'Failed to trigger report generation' }
  finally { triggeringReport.value = false }
}

const triggerDailyReminders = async () => {
  triggeringReminders.value = true
  try {
    const res = await axios.post('/api/jobs/trigger-daily-reminders')
    alertMessage.value = res.data.message || 'Daily reminders task triggered'
  } catch (e) { alertMessage.value = 'Failed to trigger reminders' }
  finally { triggeringReminders.value = false }
}

onMounted(fetchData)
</script>
