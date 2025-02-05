<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div v-if="loading" class="flex justify-center items-center min-h-[50vh]">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading quiz...</p>
      </div>
    </div>

    <div v-else-if="error" class="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <div class="text-center text-red-600">
        {{ error }}
      </div>
    </div>

    <div v-else>
      <!-- Show QuizAccessGate when access control is required -->
      <QuizAccessGate
        v-if="quiz && requiredAction"
        :quiz="quiz"
        :required-action="requiredAction"
        @access-granted="handleAccessGranted"
      />

      <!-- Show loading state while redirecting -->
      <div v-else-if="redirecting" class="text-center py-8">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Redirecting to quiz...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAxios } from '@/composables/useAxios'
import QuizAccessGate from '@/components/QuizAccessGate.vue'

const route = useRoute()
const router = useRouter()
const { axiosInstance } = useAxios()
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

const quiz = ref(null)
const loading = ref(true)
const error = ref(null)
const requiredAction = ref(null)
const redirecting = ref(false)

const loadQuiz = async () => {
  loading.value = true
  error.value = null
  requiredAction.value = null

  try {
    const response = await axiosInstance.get(`${apiBaseUrl}/quizzes/${route.params.id}/`)
    quiz.value = response.data
    // If we get here, we have access - redirect to quiz
    redirectToQuiz()
  } catch (err) {
    if (err.response?.status === 403) {
      const data = err.response.data
      requiredAction.value = data.required_action
      quiz.value = {
        id: route.params.id,
        title: data.quiz_title,
        access_control: data.access_control,
        is_published: data.is_published
      }
    } else {
      error.value = err.response?.data?.detail || 'Failed to load quiz'
    }
  } finally {
    loading.value = false
  }
}

const handleAccessGranted = async () => {
  // Reload quiz to verify access and get full quiz data
  await loadQuiz()
}

const redirectToQuiz = () => {
  redirecting.value = true
  // Redirect to the actual quiz page
  router.replace({
    name: 'QuizEvent',
    params: { id: route.params.id }
  })
}

onMounted(loadQuiz)
</script>
