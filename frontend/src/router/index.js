// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'
import axios from 'axios'
import QuizDashboard from '../views/QuizDashboard.vue'
import CreateQuiz from '../views/CreateQuiz.vue'
import TestQuiz from '@/views/TestQuiz.vue'
import EditQuiz from '@/views/EditQuiz.vue'
import AuthView from '@/views/AuthView.vue'
import MyProfile from '@/views/MyProfile.vue'
import AccountView from '@/views/AccountView.vue'
import UsersView from '@/views/UsersView.vue'
import QuizAdministration from '@/components/QuizAdministration.vue'
import QuizAnalysis from '@/components/QuizAnalysis.vue'

const fetchUsers = async (authStore) => {
  if (!authStore.account) return false

  try {
    const response = await axios.get(
      `/api/accounts/${authStore.account.id}/members/`,
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    )
    return Array.isArray(response.data) ? response.data : []
  } catch (error) {
    console.error('Failed to fetch users:', error)
    return []
  }
}

const beforeEnterRoutesHandler = async (to, from, next) => {
  const authStore = useAuthStore();
  if (authStore.isAuthenticated) {
    // Ensure user and account details are loaded
    if (!authStore.user || !authStore.account) {
      await authStore.fetchUser();
    }

    // For the Users route, prefetch users only if the account is loaded
    if (to.name === 'Users' && authStore.account) {
      const users = await fetchUsers(authStore);
      to.params.prefetchedUsers = users;
    }
    next();
  } else {
    next('/auth');
  }
};


const routes = [
  {
    path: '/',
    name: 'QuizDashboard',
    component: QuizDashboard,
    meta: { requiresAuth: true },
    beforeEnter: beforeEnterRoutesHandler
  },
  {
    path: '/create-quiz',
    name: 'CreateQuiz',
    component: CreateQuiz,
    meta: { requiresAuth: true },
    beforeEnter: beforeEnterRoutesHandler
  },
  {
    path: '/quiz/:id',
    name: 'TestQuiz',
    component: TestQuiz,
    props: true,
    meta: { requiresAuth: true },
    beforeEnter: beforeEnterRoutesHandler
  },
  {
    path: '/edit-quiz/:id',
    name: 'EditQuiz',
    component: EditQuiz,
    props: true,
    meta: { requiresAuth: true },
    beforeEnter: beforeEnterRoutesHandler
  },
  {
    path: '/auth',
    name: 'Auth',
    component: AuthView
  },
  {
    path: '/profile',
    name: 'MyProfile',
    component: MyProfile,
    meta: { requiresAuth: true },
    beforeEnter: beforeEnterRoutesHandler
  },
  {
    path: '/account',
    name: 'Account',
    component: AccountView,
    meta: { requiresAuth: true },
    beforeEnter: beforeEnterRoutesHandler
  },
  {
    path: '/users',
    name: 'Users',
    component: UsersView,
    meta: { requiresAuth: true },
    beforeEnter: beforeEnterRoutesHandler
  },
  {
    path: '/quiz/:id/admin',
    name: 'QuizAdministration',
    component: QuizAdministration,
    meta: { requiresAuth: true },
    beforeEnter: beforeEnterRoutesHandler
  },
  {
    path: '/quiz/:id/analysis',
    name: 'QuizAnalysis',
    component: QuizAnalysis,
    meta: { requiresAuth: true },
    beforeEnter: beforeEnterRoutesHandler
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
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