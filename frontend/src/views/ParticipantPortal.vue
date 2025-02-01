<template>
  <div class="max-w-7xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-6">My Quizzes</h1>

    <div v-if="loading" class="text-center py-8">Loading your quizzes...</div>

    <div v-else-if="error" class="text-red-600">
      {{ error }}
    </div>

    <div v-else class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="quiz in quizzes"
        :key="quiz.id"
        class="bg-white rounded-lg shadow p-6"
      >
        <h3 class="text-lg font-semibold mb-2">{{ quiz.title }}</h3>
        <p class="text-gray-600 mb-4">
          Score: {{ quiz.final_score || 'Not completed' }}
        </p>
        <div class="flex justify-between items-center">
          <span class="text-sm text-gray-500">
            {{ new Date(quiz.completed_at).toLocaleDateString() }}
          </span>
          <button
            v-if="!quiz.completed"
            @click="continueQuiz(quiz)"
            class="btn btn-primary"
          >
            Continue Quiz
          </button>
          <button v-else @click="viewResults(quiz)" class="btn btn-secondary">
            View Results
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useParticipantStore } from '@/store/participant'
import axios from 'axios'

const router = useRouter()
const participantStore = useParticipantStore()
const quizzes = ref([])
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    loading.value = true
    error.value = null

    // Ensure we have a valid token
    if (!participantStore.token) {
      console.log('No token found, redirecting to login')
      router.push('/participant/login')
      return
    }

    console.log('Fetching quizzes with token:', participantStore.token.substring(0, 20) + '...')
    const response = await axios.get('/api/participants/my-quizzes/', {
      headers: {
        Authorization: `Bearer ${participantStore.token}`
      }
    })
    quizzes.value = response.data
  } catch (err) {
    console.error('Failed to fetch quizzes:', err)
    error.value = 'Failed to load your quizzes'
    if (err.response?.status === 401) {
      participantStore.clearParticipant()
      router.push('/participant/login')
    }
  } finally {
    loading.value = false
  }
})

const continueQuiz = quiz => {
  router.push({
    name: 'QuizEvent',
    params: { id: quiz.id },
  })
}

const viewResults = quiz => {
  router.push({
    name: 'QuizResults',
    params: { id: quiz.id },
  })
}
</script>
