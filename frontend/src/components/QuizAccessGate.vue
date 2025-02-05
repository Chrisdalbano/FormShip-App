<template>
  <div class="quiz-access-gate max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
    <h2 class="text-2xl font-bold mb-4">{{ quiz.title }}</h2>
    
    <!-- Access Denied Message -->
    <div v-if="error" class="mb-4 p-3 bg-red-100 text-red-700 rounded">
      {{ error }}
    </div>

    <!-- Login Required -->
    <div v-if="requiredAction === 'REQUIRE_AUTH'" class="space-y-4">
      <p class="text-gray-600">
        This quiz requires you to log in or register to participate.
      </p>
      <ParticipantAuth 
        :quiz="quiz"
        @auth-success="handleAuthSuccess"
      />
    </div>

    <!-- Email Verification (Invitation) -->
    <div v-else-if="requiredAction === 'REQUIRE_EMAIL'" class="space-y-4">
      <p class="text-gray-600">
        This quiz is invitation-only. Please enter your email to verify your invitation.
      </p>
      <form @submit.prevent="verifyInvitation" class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1">Email</label>
          <input
            v-model="email"
            type="email"
            required
            class="w-full px-3 py-2 border rounded-lg"
          />
        </div>
        <button
          type="submit"
          :disabled="isLoading"
          class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {{ isLoading ? 'Verifying...' : 'Verify Invitation' }}
        </button>
      </form>
    </div>

    <!-- Password Required -->
    <div v-else-if="requiredAction === 'REQUIRE_PASSWORD'" class="space-y-4">
      <p class="text-gray-600">
        This quiz is password protected. Please enter the password to continue.
      </p>
      <form @submit.prevent="verifyPassword" class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1">Password</label>
          <input
            v-model="password"
            type="password"
            required
            class="w-full px-3 py-2 border rounded-lg"
          />
        </div>
        <button
          type="submit"
          :disabled="isLoading"
          class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {{ isLoading ? 'Verifying...' : 'Submit Password' }}
        </button>
      </form>
    </div>

    <!-- Quiz Unavailable -->
    <div v-else-if="requiredAction === 'QUIZ_UNAVAILABLE'" class="text-center py-8">
      <p class="text-gray-600">
        This quiz is not currently available.
      </p>
    </div>

    <!-- Not Invited -->
    <div v-else-if="requiredAction === 'NOT_INVITED'" class="text-center py-8">
      <p class="text-gray-600">
        Sorry, you are not invited to take this quiz.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
// import { useRouter } from 'vue-router'
import { useAxios } from '@/composables/useAxios'
import ParticipantAuth from './ParticipantAuth.vue'

const props = defineProps({
  quiz: {
    type: Object,
    required: true
  },
  requiredAction: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['access-granted'])

// const router = useRouter()
const { axiosInstance } = useAxios()
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

const email = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)

const handleAuthSuccess = () => {
  emit('access-granted')
}

const verifyInvitation = async () => {
  if (isLoading.value) return
  isLoading.value = true
  error.value = ''

  try {
    await axiosInstance.post(`${apiBaseUrl}/quizzes/${props.quiz.id}/verify-access/`, {
      email: email.value
    })
    emit('access-granted')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to verify invitation'
  } finally {
    isLoading.value = false
  }
}

const verifyPassword = async () => {
  if (isLoading.value) return
  isLoading.value = true
  error.value = ''

  try {
    await axiosInstance.post(`${apiBaseUrl}/quizzes/${props.quiz.id}/verify-access/`, {
      password: password.value
    })
    emit('access-granted')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Invalid password'
  } finally {
    isLoading.value = false
  }
}
</script> 