// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useQuizStore } from '@/store/quiz'
import apiService from '@/services/api'

// Views
import QuizDashboard from '../views/QuizDashboard.vue'
import CreateQuiz from '../views/CreateQuiz.vue'
import QuizManagement from '../views/QuizManagement.vue'
import AuthView from '@/views/AuthView.vue'
import MyProfile from '@/views/MyProfile.vue'
import AccountView from '@/views/AccountView.vue'
import UsersView from '@/views/UsersView.vue'
import CompletedQuiz from '@/components/CompletedQuiz.vue'
import ParticipantDetails from '@/components/ParticipantDetails.vue'

const fetchUsers = async (authStore) => {
  if (!authStore.account) return false
  try {
    const response = await apiService.get(`/accounts/${authStore.account.id}/members/`)
    return Array.isArray(response.data) ? response.data : []
  } catch (error) {
    console.error('Failed to fetch users:', error)
    return []
  }
}

const beforeEnterRoutesHandler = async (to, from, next) => {
  const authStore = useAuthStore()
  if (authStore.isAuthenticated) {
    if (!authStore.user || !authStore.account) {
      await authStore.fetchUser()
    }

    if (to.name === 'Users' && authStore.account) {
      const users = await fetchUsers(authStore)
      to.params.prefetchedUsers = users
    }
    next()
  } else {
    next('/auth')
  }
}

const routes = [
  {
    path: '/',
    name: 'QuizDashboard',
    component: QuizDashboard,
    meta: { requiresAuth: true },
    beforeEnter: beforeEnterRoutesHandler,
  },
  {
    path: '/quiz/access/:id',
    name: 'QuizAccess',
    component: () => import('@/components/QuizAccess.vue'),
    props: true
  },
  {
    path: '/quiz/:id',
    name: 'QuizView',
    component: () => import('@/components/QuizAccess.vue'),
    props: true
  },
  {
    path: '/create-quiz',
    name: 'CreateQuiz',
    component: CreateQuiz,
    meta: { requiresAuth: true },
    beforeEnter: beforeEnterRoutesHandler,
  },
  {
    path: '/quiz/:id/manage',
    name: 'QuizManagement',
    component: QuizManagement,
    props: true,
    meta: { requiresAuth: true },
    beforeEnter: beforeEnterRoutesHandler,
  },
  {
    path: '/quiz/:id/event',
    name: 'QuizEvent',
    component: () => import('@/views/QuizEvent.vue'),
    props: true,
    meta: { requiresAccess: true }
  },
  {
    path: '/quiz/:id/results',
    name: 'QuizResults',
    component: () => import('@/views/QuizResults.vue'),
    props: true,
    meta: { requiresAccess: true }
  },
  {
    path: '/quiz-results/:id',
    name: 'CompletedQuiz',
    component: CompletedQuiz,
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: '/auth',
    name: 'Auth',
    component: AuthView,
  },
  {
    path: '/auth/login',
    name: 'Login',
    component: AuthView,
    props: route => ({ 
      initialTab: 'login',
      redirect: route.query.redirect,
      message: route.query.message 
    })
  },
  {
    path: '/error',
    name: 'Error',
    component: () => import('@/views/ErrorView.vue')
  },
  {
    path: '/participant/:id',
    name: 'ParticipantDetails',
    component: ParticipantDetails,
    meta: { requiresAuth: true },
    beforeEnter: beforeEnterRoutesHandler,
  },
  {
    path: '/profile',
    name: 'MyProfile',
    component: MyProfile,
    meta: { requiresAuth: true },
    beforeEnter: beforeEnterRoutesHandler,
  },
  {
    path: '/account',
    name: 'Account',
    component: AccountView,
    meta: { requiresAuth: true },
    beforeEnter: beforeEnterRoutesHandler,
  },
  {
    path: '/users',
    name: 'Users',
    component: UsersView,
    meta: { requiresAuth: true },
    beforeEnter: beforeEnterRoutesHandler,
  },
  {
    path: '/participant/login',
    name: 'ParticipantLogin',
    component: () => import('@/views/ParticipantLoginView.vue'),
    meta: { layout: 'blank' }
  },
  {
    path: '/participant',
    name: 'ParticipantPortal',
    component: () => import('@/views/ParticipantPortal.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/participant/profile',
    name: 'ParticipantProfile',
    component: () => import('@/views/ParticipantProfile.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const quizStore = useQuizStore()
  const authStore = useAuthStore()

  // Initialize store if needed
  if (!quizStore.isInitialized) {
    await quizStore.initializeFromStorage()
  }

  // Handle routes requiring authentication
  if (to.meta.requiresAuth) {
    // Check for FormShip user authentication first
    if (authStore.isAuthenticated) {
      next()
      return
    }
    // Then check for quiz participant authentication
    if (!quizStore.isAuthenticated) {
      next({ name: 'Auth', query: { redirect: to.fullPath } })
      return
    }
  }

  // Handle routes requiring quiz access
  if (to.meta.requiresAccess) {
    const quizId = to.params.id
    try {
      const result = await quizStore.verifyQuizAccess(quizId)
      if (!result.success) {
        next({ 
          name: 'QuizAccess', 
          params: { id: quizId },
          replace: true 
        })
        return
      }
    } catch {
      next({ 
        name: 'QuizAccess', 
        params: { id: quizId },
        replace: true 
      })
      return
    }
  }

  next()
})

export default router
