import { createRouter, createWebHistory } from 'vue-router';
import QuizDashboard from '../views/QuizDashboard.vue';
import CreateQuiz from '../views/CreateQuiz.vue';
import TestQuiz from '../views/TestQuiz.vue';

const routes = [
  {
    path: '/',
    name: 'QuizDashboard',
    component: QuizDashboard,
  },
  {
    path: '/create-quiz',
    name: 'CreateQuiz',
    component: CreateQuiz,
  },
  {
    path: '/quiz/:id',
    name: 'TestQuiz',
    component: TestQuiz,
    props: true,
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;