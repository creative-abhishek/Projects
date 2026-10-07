import { createRouter, createWebHistory } from 'vue-router'
import { authStore } from '../store/auth.js'

import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import CompanyDashboard from '../views/CompanyDashboard.vue'
import StudentDashboard from '../views/StudentDashboard.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    redirect: () => {
      if (!authStore.isAuthenticated()) return '/login'
      const role = authStore.getRole()
      if (role === 'admin') return '/admin/dashboard'
      if (role === 'company') return '/company/dashboard'
      if (role === 'student') return '/student/dashboard'
      return '/login'
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { guestOnly: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: { guestOnly: true }
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/company/dashboard',
    name: 'CompanyDashboard',
    component: CompanyDashboard,
    meta: { requiresAuth: true, role: 'company' }
  },
  {
    path: '/student/dashboard',
    name: 'StudentDashboard',
    component: StudentDashboard,
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const isAuth = authStore.isAuthenticated()
  const userRole = authStore.getRole()

  if (to.meta.requiresAuth && !isAuth) {
    return next({ name: 'Login' })
  }

  if (to.meta.guestOnly && isAuth) {
    return next({ name: 'Home' })
  }

  if (to.meta.role && userRole !== to.meta.role) {
    return next({ name: 'Home' })
  }

  next()
})

export default router
