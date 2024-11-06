import { createRouter, createWebHistory } from 'vue-router'
import QuizDashboard from '../views/QuizDashboard.vue'
import CreateQuiz from '../views/CreateQuiz.vue'
import TestQuiz from '@/views/TestQuiz.vue'
import EditQuiz from '@/views/EditQuiz.vue'
import AuthView from '@/views/AuthView.vue'
import MyProfile from '@/views/MyProfile.vue'  // Import MyProfile

const isAuthenticated = () => !!localStorage.getItem('jwt')

const routes = [
  { path: '/', name: 'QuizDashboard', component: QuizDashboard, meta: { requiresAuth: true } },
  { path: '/create-quiz', name: 'CreateQuiz', component: CreateQuiz, meta: { requiresAuth: true } },
  { path: '/quiz/:id', name: 'TestQuiz', component: TestQuiz, props: true, meta: { requiresAuth: true } },
  { path: '/edit-quiz/:id', name: 'EditQuiz', component: EditQuiz, props: true, meta: { requiresAuth: true } },
  { path: '/auth', name: 'Auth', component: AuthView },
  { path: '/profile', name: 'MyProfile', component: MyProfile, meta: { requiresAuth: true } },  // New profile route

]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    next({ name: 'Auth' })
  } else {
    next()
  }
})

export default router
