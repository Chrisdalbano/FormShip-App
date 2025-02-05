<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4">
      <div v-if="loading" class="text-center py-8">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading quiz results...</p>
      </div>

      <div v-else-if="error" class="text-center text-red-600 py-8">
        {{ error }}
      </div>

      <div v-else class="bg-white rounded-lg shadow-lg overflow-hidden">
        <!-- Quiz Header -->
        <div class="p-6 border-b">
          <h1 class="text-2xl font-bold mb-2">{{ quiz?.title }}</h1>
          <p class="text-gray-600">Completed on {{ formatDate(quiz?.completed_at) }}</p>
        </div>

        <!-- Score Summary -->
        <div class="p-6 bg-blue-50">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-xl font-semibold mb-1">Final Score</h2>
              <p class="text-gray-600">Your performance summary</p>
            </div>
            <div class="text-right">
              <p class="text-3xl font-bold text-blue-600">{{ quiz?.final_score }}%</p>
              <p class="text-sm text-gray-600">
                {{ quiz?.correct_answers }} / {{ quiz?.total_questions }} correct
              </p>
            </div>
          </div>
        </div>

        <!-- Question Review -->
        <div class="p-6">
          <h2 class="text-xl font-semibold mb-4">Question Review</h2>
          
          <div v-for="(question, index) in quiz?.questions" :key="question.id" 
               class="mb-8 p-4 rounded-lg" 
               :class="getQuestionStatusClass(question)">
            <div class="flex items-start justify-between mb-2">
              <h3 class="text-lg font-medium">Question {{ index + 1 }}</h3>
              <span class="px-2 py-1 rounded text-sm" :class="getStatusBadgeClass(question)">
                {{ question.is_correct ? 'Correct' : 'Incorrect' }}
              </span>
            </div>

            <div class="prose max-w-none mb-4" v-html="question.text"></div>

            <div class="space-y-2">
              <div v-for="answer in question.answers" :key="answer.id"
                   class="p-3 rounded-lg border"
                   :class="getAnswerClass(answer)">
                <div class="flex items-start">
                  <div class="flex-grow">
                    <p class="font-medium" v-html="answer.text"></p>
                  </div>
                  <div v-if="shouldShowAnswerIcon(answer)"
                       class="ml-3 flex-shrink-0">
                    <i class="fas" :class="getAnswerIconClass(answer)"></i>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="question.explanation" class="mt-4 p-4 bg-gray-50 rounded-lg">
              <h4 class="font-medium mb-2">Explanation</h4>
              <div class="text-gray-600" v-html="question.explanation"></div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="p-6 border-t bg-gray-50">
          <div class="flex justify-between">
            <router-link 
              to="/participant"
              class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              Back to My Quizzes
            </router-link>
            <button
              v-if="quiz?.can_retake"
              @click="retakeQuiz"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Retake Quiz
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useParticipantStore } from '@/store/participant'
import { useAxios } from '@/composables/useAxios'

const props = defineProps({
  id: {
    type: String,
    required: true
  }
})

const router = useRouter()
const participantStore = useParticipantStore()
const { axiosInstance } = useAxios()
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

const loading = ref(true)
const error = ref(null)
const quiz = ref(null)

const loadQuizResults = async () => {
  try {
    const response = await axiosInstance.get(`${apiBaseUrl}/quizzes/${props.id}/results/`, {
      headers: participantStore.getAuthHeader
    })
    quiz.value = response.data
  } catch (err) {
    console.error('Failed to load quiz results:', err)
    error.value = err.response?.data?.detail || 'Failed to load quiz results'
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getQuestionStatusClass = (question) => {
  return {
    'bg-green-50 border border-green-200': question.is_correct,
    'bg-red-50 border border-red-200': !question.is_correct
  }
}

const getStatusBadgeClass = (question) => {
  return {
    'bg-green-100 text-green-800': question.is_correct,
    'bg-red-100 text-red-800': !question.is_correct
  }
}

const getAnswerClass = (answer) => {
  if (answer.is_selected && answer.is_correct) {
    return 'bg-green-50 border-green-200'
  }
  if (answer.is_selected && !answer.is_correct) {
    return 'bg-red-50 border-red-200'
  }
  if (!answer.is_selected && answer.is_correct) {
    return 'bg-blue-50 border-blue-200'
  }
  return 'bg-white border-gray-200'
}

const shouldShowAnswerIcon = (answer) => {
  return answer.is_selected || answer.is_correct
}

const getAnswerIconClass = (answer) => {
  if (answer.is_selected && answer.is_correct) {
    return 'fa-check text-green-600'
  }
  if (answer.is_selected && !answer.is_correct) {
    return 'fa-times text-red-600'
  }
  if (!answer.is_selected && answer.is_correct) {
    return 'fa-check text-blue-600'
  }
  return ''
}

const retakeQuiz = () => {
  router.push({
    name: 'QuizEvent',
    params: { id: props.id }
  })
}

onMounted(loadQuizResults)
</script> 