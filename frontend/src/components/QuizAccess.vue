<template>
  <div class="max-w-md mx-auto p-6 bg-white rounded-lg shadow-lg">
    <div v-if="loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      <p class="mt-4 text-gray-600">Checking quiz access...</p>
    </div>

    <div v-else>
      <h2 class="text-2xl font-bold mb-6">{{ quiz?.title || 'Access Quiz' }}</h2>

      <!-- Error Message -->
      <div v-if="error" class="mb-6 p-4 bg-red-100 text-red-700 rounded-lg">
        {{ error }}
      </div>

      <!-- Quiz Not Available -->
      <div v-if="requiredAction === 'QUIZ_UNAVAILABLE'" class="text-center py-4">
        <p class="text-gray-700">This quiz is not currently available.</p>
      </div>

      <!-- Authentication Form -->
      <form v-else-if="!quizStore.isAuthenticated && ['REQUIRE_AUTH', 'NOT_INVITED'].includes(requiredAction)"
            @submit.prevent="handleAuth" class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1">Email</label>
          <input
            v-model="form.email"
            type="email"
            required
            class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div v-if="isRegistering">
          <label class="block text-sm font-medium mb-1">Name</label>
          <input
            v-model="form.name"
            type="text"
            required
            class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Password</label>
          <input
            v-model="form.password"
            type="password"
            required
            class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div class="flex justify-between items-center">
          <button
            type="submit"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            :disabled="isLoading"
          >
            {{ isRegistering ? 'Register' : 'Login' }}
          </button>

          <button
            type="button"
            @click="toggleAuthMode"
            class="text-blue-600 hover:underline"
          >
            {{ isRegistering ? 'Already have an account?' : 'Need to register?' }}
          </button>
        </div>
      </form>

      <!-- Email Verification -->
      <form v-else-if="requiredAction === 'REQUIRE_EMAIL'" @submit.prevent="verifyEmail" class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1">Email</label>
          <input
            v-model="form.email"
            type="email"
            required
            class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <button
          type="submit"
          class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          :disabled="isLoading"
        >
          Verify Email
        </button>
      </form>

      <!-- Password Verification -->
      <form v-else-if="requiredAction === 'REQUIRE_PASSWORD'" @submit.prevent="verifyPassword" class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1">Quiz Password</label>
          <input
            v-model="form.quizPassword"
            type="password"
            required
            class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <button
          type="submit"
          class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          :disabled="isLoading"
        >
          Submit Password
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useQuizStore } from '@/store/quiz'

const props = defineProps({
  id: {
    type: String,
    required: true
  }
})

const router = useRouter()
const quizStore = useQuizStore()

const loading = ref(true)
const isLoading = ref(false)
const error = ref(null)
const quiz = ref(null)
const requiredAction = ref(null)
const isRegistering = ref(false)

const form = ref({
  email: '',
  password: '',
  name: '',
  quizPassword: ''
})

const checkAccess = async () => {
  loading.value = true
  error.value = null

  try {
    if (!props.id) {
      error.value = 'Invalid quiz ID'
      return
    }

    const result = await quizStore.verifyQuizAccess(props.id)
    if (result.success) {
      // Access granted, redirect to quiz
      router.push({ name: 'QuizEvent', params: { id: props.id }})
      return
    }

    // Access denied, show appropriate form
    quiz.value = result.quizData
    requiredAction.value = result.requiredAction
  } catch (err) {
    console.error('Quiz access error:', err)
    error.value = 'Failed to check quiz access. Please try again.'
  } finally {
    loading.value = false
  }
}

const handleAuth = async () => {
  isLoading.value = true
  error.value = null

  try {
    const endpoint = isRegistering.value ? 'register' : 'login'
    const response = await quizStore.authenticateParticipant({
      endpoint,
      email: form.value.email,
      password: form.value.password,
      name: form.value.name
    })

    if (response && response.token) {
      await quizStore.setParticipantData(response)
      await checkAccess()
    } else {
      error.value = 'Invalid response from server'
    }
  } catch (err) {
    console.error('Authentication error:', err)
    error.value = err.response?.data?.detail || 'Authentication failed'
  } finally {
    isLoading.value = false
  }
}

const verifyEmail = async () => {
  isLoading.value = true
  error.value = null

  try {
    await quizStore.verifyQuizInvitation(props.id, form.value.email)
    await checkAccess()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Email verification failed'
  } finally {
    isLoading.value = false
  }
}

const verifyPassword = async () => {
  isLoading.value = true
  error.value = null

  try {
    await quizStore.verifyQuizPassword(props.id, form.value.quizPassword)
    await checkAccess()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Invalid password'
  } finally {
    isLoading.value = false
  }
}

const toggleAuthMode = () => {
  isRegistering.value = !isRegistering.value
  form.value = {
    email: '',
    password: '',
    name: '',
    quizPassword: ''
  }
  error.value = null
}

// Watch for changes in authentication state
watch(() => quizStore.isAuthenticated, async (isAuthenticated) => {
  if (isAuthenticated) {
    await checkAccess()
  }
})

onMounted(async () => {
  if (!quizStore.isInitialized) {
    await quizStore.initializeFromStorage()
  }
  await checkAccess()
})
</script> 