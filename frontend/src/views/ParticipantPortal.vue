<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-6xl mx-auto px-4">
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold">My Quizzes</h1>
        <router-link
          to="/participant/profile"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
        >
          Profile Settings
        </router-link>
      </div>

      <div v-if="loading" class="text-center py-8">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading your quizzes...</p>
      </div>

      <div v-else-if="error" class="text-center text-red-600 py-8">
        {{ error }}
      </div>

      <div v-else>
        <!-- No quizzes message -->
        <div v-if="!quizStore.linkedQuizzes.length" class="text-center py-8">
          <p class="text-gray-600">You haven't participated in any quizzes yet.</p>
        </div>

        <!-- Quiz List -->
        <div v-else class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <div 
            v-for="quiz in quizStore.linkedQuizzes" 
            :key="quiz.id"
            class="bg-white rounded-lg shadow-md overflow-hidden"
          >
            <div class="p-6">
              <h3 class="text-xl font-semibold mb-2">{{ quiz.title }}</h3>
              
              <div class="mb-4 text-sm text-gray-600">
                <p v-if="quiz.completed">
                  <span class="font-medium">Score:</span> {{ quiz.final_score }}%
                </p>
                <p>
                  <span class="font-medium">Status:</span>
                  {{ quiz.completed ? 'Completed' : 'In Progress' }}
                </p>
                <p v-if="quiz.completed_at">
                  <span class="font-medium">Completed:</span>
                  {{ new Date(quiz.completed_at).toLocaleDateString() }}
                </p>
              </div>

              <button
                @click="viewQuiz(quiz)"
                class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                {{ quiz.completed ? 'View Results' : 'Continue Quiz' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuizStore } from '@/store/quiz'

const router = useRouter()
const quizStore = useQuizStore()

const loading = ref(true)
const error = ref(null)

const loadQuizzes = async () => {
  if (!quizStore.isAuthenticated) {
    router.push('/quiz/access')
    return
  }

  loading.value = true
  error.value = null

  try {
    await quizStore.loadLinkedQuizzes()
  } catch (err) {
    console.error('Failed to load quizzes:', err)
    error.value = err.response?.data?.detail || 'Failed to load your quizzes'
  } finally {
    loading.value = false
  }
}

const viewQuiz = (quiz) => {
  if (quiz.completed) {
    router.push({
      name: 'QuizResults',
      params: { id: quiz.id }
    })
  } else {
    router.push({
      name: 'QuizEvent',
      params: { id: quiz.id }
    })
  }
}

onMounted(async () => {
  if (!quizStore.isInitialized) {
    const isAuthenticated = await quizStore.initializeFromStorage()
    if (!isAuthenticated) {
      router.push('/quiz/access')
      return
    }
  }
  await loadQuizzes()
})
</script>

<style scoped>
.btn {
  @apply px-4 py-2 rounded-lg font-medium transition-colors;
}
.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}
.btn-secondary {
  @apply bg-gray-500 text-white hover:bg-gray-600;
}
</style>
