<template>
  <div class="quiz-event min-h-screen bg-gray-50">
    <div v-if="loading" class="flex justify-center items-center min-h-screen">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading quiz...</p>
      </div>
    </div>

    <div v-else-if="error" class="flex justify-center items-center min-h-screen">
      <div class="text-center text-red-600">
        {{ error }}
      </div>
    </div>

    <div v-else>
      <!-- Quiz Content -->
      <div v-if="quiz" class="max-w-4xl mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold mb-6">{{ quiz.title }}</h1>
        <!-- Add your quiz content here -->
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAxios } from '@/composables/useAxios'

const route = useRoute()
const router = useRouter()
const { axiosInstance } = useAxios()
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

const quiz = ref(null)
const loading = ref(true)
const error = ref(null)

const loadQuiz = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await axiosInstance.get(`${apiBaseUrl}/quizzes/${route.params.id}/`)
    quiz.value = response.data
  } catch (err) {
    if (err.response?.status === 403) {
      // If access is denied, redirect to access page
      router.replace({
        name: 'QuizAccess',
        params: { id: route.params.id }
      })
      return
    }
    error.value = err.response?.data?.detail || 'Failed to load quiz'
  } finally {
    loading.value = false
  }
}

onMounted(loadQuiz)
</script> 