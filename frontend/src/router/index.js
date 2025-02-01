// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'
import axios from 'axios'
import { useQuizStore } from '../store/quiz'
import { useParticipantStore } from '../store/participant'

// Views
import QuizDashboard from '../views/QuizDashboard.vue'
import CreateQuiz from '../views/CreateQuiz.vue'
import QuizManagement from '../views/QuizManagement.vue'
import AuthView from '@/views/AuthView.vue'
import MyProfile from '@/views/MyProfile.vue'
import AccountView from '@/views/AccountView.vue'
import UsersView from '@/views/UsersView.vue'
import QuizEventComponent from '@/views/QuizEventComponent.vue'
import CompletedQuiz from '@/components/CompletedQuiz.vue'
import ParticipantDetails from '@/components/ParticipantDetails.vue'
import QuizAccessView from '@/views/QuizAccessView.vue'

const fetchUsers = async (authStore) => {
  if (!authStore.account) return false
  try {
    const response = await axios.get(
      `/api/accounts/${authStore.account.id}/members/`,
      { headers: { Authorization: `Bearer ${authStore.token}` } }
    )
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

async function checkQuizAccess(quizId, isTestMode = false) {
  try {
    const response = await axios.get(`/api/quizzes/${quizId}/`)
    const quiz = response.data
    const authStore = useAuthStore()
    
    // Always allow account owners/admins in test mode
    if (isTestMode && authStore.isAuthenticated) {
      const isOwner = quiz.account === authStore.account?.id
      const isAdmin = authStore.user?.role === 'admin'
      if (isOwner || isAdmin) return { allowed: true, quiz }
    }

    // Handle different access controls
    switch (quiz.access_control) {
      case 'login_required':
        return {
          allowed: authStore.isAuthenticated,
          quiz,
          redirectTo: 'QuizAccess'
        }
      case 'invitation':
        return {
          allowed: false,
          quiz,
          redirectTo: 'QuizAccess'
        }
      case 'public':
        return { allowed: true, quiz }
      default:
        return { allowed: false, quiz, redirectTo: 'QuizAccess' }
    }
  } catch (error) {
    console.error('Error checking quiz access:', error)
    return { allowed: false, error: true }
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
    path: '/quiz/access/:id',
    name: 'QuizAccess',
    component: QuizAccessView,
    meta: { layout: 'blank' },
    beforeEnter: async (to, from, next) => {
      try {
        const quizId = to.params.id
        const response = await axios.get(`/api/quizzes/${quizId}/`)
        const quiz = response.data
        const authStore = useAuthStore()

        // If FormShip user is logged in and is owner/admin, redirect to test mode
        if (authStore.isAuthenticated) {
          const isOwner = quiz.account === authStore.account?.id
          const isAdmin = authStore.user?.role === 'admin'
          if (isOwner || isAdmin) {
            next({ 
              name: 'QuizEvent', 
              params: { id: quizId },
              query: { test: 'true' }
            })
            return
          }
        }

        // For all other cases, proceed to QuizAccess view
        next()
      } catch (error) {
        console.error('Error loading quiz:', error)
        next({ name: 'Error' })
      }
    }
  },
  {
    path: '/quiz/invite/:id',
    redirect: to => ({
      name: 'QuizAccess',
      params: { id: to.params.id }
    })
  },
  {
    path: '/quiz/event/:id',
    name: 'QuizEvent',
    component: QuizEventComponent,
    meta: { layout: 'blank' },
    beforeEnter: async (to, from, next) => {
      const isTestMode = to.query.test === 'true'
      const participantStore = useParticipantStore()
      const authStore = useAuthStore()

      try {
        const response = await axios.get(`/api/quizzes/${to.params.id}/`)
        const quiz = response.data

        // Allow if it's test mode and user is owner/admin
        if (isTestMode && authStore.isAuthenticated) {
          const isOwner = quiz.account === authStore.account?.id
          const isAdmin = authStore.user?.role === 'admin'
          if (isOwner || isAdmin) {
            next()
            return
          }
        }

        // Allow if participant is authenticated for this quiz
        if (participantStore.isAuthenticated && 
            participantStore.currentQuiz?.id === to.params.id) {
          next()
          return
        }

        // Otherwise redirect to quiz access
        next({
          name: 'QuizAccess',
          params: { id: to.params.id }
        })
      } catch (error) {
        console.error('Error checking quiz access:', error)
        next({ name: 'Error' })
      }
    }
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
    path: '/participant/portal',
    name: 'ParticipantPortal',
    component: () => import('@/views/ParticipantPortal.vue'),
    meta: { requiresParticipantAuth: true }
  },
  {
    path: '/participant/profile',
    name: 'ParticipantProfile',
    component: () => import('@/views/ParticipantProfile.vue'),
    meta: { requiresParticipantAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  beforeEach: async (to, from, next) => {
    const participantStore = useParticipantStore()
    const authStore = useAuthStore()

    // Initialize participant store if needed
    if (!participantStore.isInitialized) {
      await participantStore.initializeFromStorage()
    }

    // Handle participant-only routes
    if (to.meta.requiresParticipantAuth) {
      if (!participantStore.isAuthenticated) {
        next({
          name: 'ParticipantLogin',
          query: { redirect: to.fullPath }
        })
        return
      }
    }

    // Handle FormShip-only routes
    if (to.meta.requiresAuth) {
      if (!authStore.isAuthenticated) {
        next({
          name: 'Login',
          query: { redirect: to.fullPath }
        })
        return
      }
    }

    // For quiz access, check both participant and FormShip auth
    if (to.name === 'QuizAccess') {
      const quizId = to.params.id
      try {
        const response = await axios.get(`/api/quizzes/${quizId}/`)
        const quiz = response.data

        // If FormShip user is owner/admin
        if (authStore.isAuthenticated) {
          const isOwner = quiz.account === authStore.account?.id
          const isAdmin = authStore.user?.role === 'admin'
          if (isOwner || isAdmin) {
            next({
              name: 'QuizEvent',
              params: { id: quizId },
              query: { test: 'true' }
            })
            return
          }
        }

        // If participant is already authenticated for this quiz
        if (participantStore.isAuthenticated && 
            participantStore.currentQuiz?.id === quizId) {
          next({
            name: 'QuizEvent',
            params: { id: quizId }
          })
          return
        }
      } catch (error) {
        console.error('Error checking quiz access:', error)
      }
    }

    next()
  }
})

export default router
