// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'
import axios from 'axios'

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
    path: '/quiz/:id',
    name: 'QuizEvent',
    component: QuizEventComponent,
    props: true,
    meta: { requiresAuth: false }, // Allows public access for live quizzes
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
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Auth' })
  } else {
    next()
  }
})

export default router
