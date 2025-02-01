<template>
  <div class="quiz-access-container p-6 max-w-lg mx-auto">
    <h2 class="text-xl font-bold mb-4">{{ quiz?.title }}</h2>

    <div v-if="loading" class="text-center">Loading quiz access...</div>

    <div v-else-if="errorMessage" class="text-red-500">{{ errorMessage }}</div>

    <div v-else>
      <!-- Use ParticipantAuth for authentication -->
      <ParticipantAuth
        v-if="showParticipantAuth"
        :quiz="quiz"
        @auth-success="handleAuthSuccess"
      />

      <!-- Invitation Validation -->
      <div v-else-if="showInvitationPrompt" class="mb-6">
        <p class="text-blue-600 mb-4">This quiz requires an invitation.</p>
        <div class="email-validation">
          <input
            v-model="email"
            type="email"
            placeholder="Enter your email"
            class="input-field mb-2"
          />
          <button @click="validateInvitation" class="btn btn-primary">
            Validate Invitation
          </button>
        </div>
      </div>

      <!-- Public Access -->
      <div v-else>
        <div v-if="quiz?.require_name" class="mb-4">
          <label class="block mb-2">Your Name</label>
          <input
            v-model="participantName"
            type="text"
            class="input-field"
            placeholder="Enter your name"
          />
        </div>

        <button
          @click="proceedToQuiz"
          class="btn btn-primary w-full"
          :disabled="!canProceed"
        >
          Start Quiz
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
// import { useAuthStore } from '../store/auth'
import ParticipantAuth from '../components/ParticipantAuth.vue'
import { useParticipantStore } from '@/store/participant'

const route = useRoute()
const router = useRouter()
const quizId = route.params.id
const quiz = ref(null)
const errorMessage = ref('')
const participantName = ref('')
const email = ref('')
const loading = ref(true)
const isEmailValidated = ref(false)
const showParticipantAuth = ref(false)
const showInvitationPrompt = ref(false)


onMounted(async () => {
  try {
    const participantStore = useParticipantStore()
    
    // First check if participant is already authenticated
    if (participantStore.isAuthenticated) {
      console.log('[QuizAccess] Participant already authenticated')
      
      // Get quiz details first
      const response = await axios.get(`/api/quizzes/${quizId}/`)
      quiz.value = response.data
      
      // Set current quiz in store
      participantStore.setCurrentQuiz(quiz.value)
      
      // Directly proceed to quiz
      router.push({
        name: 'QuizEvent',
        params: { id: quizId }
      })
      return
    }

    // If not authenticated, get quiz details and show appropriate access form
    const response = await axios.get(`/api/quizzes/${quizId}/`)
    quiz.value = response.data
    
    // Handle participant access for non-authenticated users
    switch (quiz.value.access_control) {
      case 'login_required':
        showParticipantAuth.value = true
        break
      case 'invitation':
        showInvitationPrompt.value = true
        break
      case 'public':
        // Allow direct access
        break
    }
  } catch (error) {
    console.error('Failed to load quiz:', error)
    errorMessage.value = 'Failed to load quiz.'
  } finally {
    loading.value = false
  }
})

const canProceed = computed(() => {
  if (quiz.value?.access_control === 'invitation' && !isEmailValidated.value) {
    return false
  }
  if (quiz.value?.require_name && !participantName.value) {
    return false
  }
  return true
})

const validateInvitation = async () => {
  try {
    const response = await axios.post(
      `/api/quizzes/${quizId}/validate-invitation/`,
      {
        email: email.value,
      },
    )
    if (response.data.valid) {
      isEmailValidated.value = true
    } else {
      errorMessage.value = 'Email not found in invitation list'
    }
  // eslint-disable-next-line no-unused-vars
  } catch (error) {
    errorMessage.value = 'Failed to validate invitation'
  }
}

const handleAuthSuccess = async (participantData) => {
  const participantStore = useParticipantStore()
  
  // Set the participant data in the store
  await participantStore.setParticipantData({
    ...participantData,
    currentQuiz: quiz.value
  })
  
  // Navigate to quiz
  router.push({
    name: 'QuizEvent',
    params: { id: quizId },
  })
}
</script>

<style scoped>
.btn {
  @apply px-4 py-2 rounded-lg font-medium transition-colors;
}
.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}
.input-field {
  @apply w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500;
}
</style>
