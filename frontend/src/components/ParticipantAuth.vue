<!-- eslint-disable no-unused-vars -->
<template>
  <div class="participant-auth bg-white rounded-lg p-6 shadow-md">
    <!-- Login/Register Tabs -->
    <div class="flex border-b mb-6">
      <button 
        @click="activeTab = 'login'"
        class="pb-2 px-4 mr-4"
        :class="[
          activeTab === 'login' 
            ? 'border-b-2 border-blue-500 text-blue-600 font-medium' 
            : 'text-gray-500'
        ]"
      >
        Login
      </button>
      <button 
        @click="activeTab = 'register'"
        class="pb-2 px-4"
        :class="[
          activeTab === 'register' 
            ? 'border-b-2 border-blue-500 text-blue-600 font-medium' 
            : 'text-gray-500'
        ]"
      >
        Register
      </button>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="mb-4 p-3 bg-red-100 text-red-700 rounded">
      {{ error }}
    </div>

    <!-- Login Form -->
    <form v-if="activeTab === 'login'" @submit.prevent="handleParticipantLogin" class="space-y-4">
      <div>
        <label class="block text-sm font-medium mb-1">Email</label>
        <input 
          v-model="email" 
          type="email" 
          required
          class="input-field"
          placeholder="Enter your email"
        />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">Password</label>
        <input 
          v-model="password" 
          type="password" 
          required
          class="input-field"
          placeholder="Enter password"
        />
      </div>
      <button 
        type="submit" 
        class="btn btn-primary w-full"
        :disabled="isLoading"
      >
        {{ isLoading ? 'Logging in...' : 'Login' }}
      </button>
    </form>

    <!-- Registration Form -->
    <form v-else @submit.prevent="handleParticipantRegistration" class="space-y-4">
      <div>
        <label class="block text-sm font-medium mb-1">Full Name</label>
        <input 
          v-model="name" 
          type="text" 
          required
          class="input-field"
          placeholder="Enter your full name"
        />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">Email</label>
        <input 
          v-model="email" 
          type="email" 
          required
          class="input-field"
          placeholder="Enter your email"
        />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">Password</label>
        <input 
          v-model="password" 
          type="password" 
          required
          class="input-field"
          placeholder="Create password"
        />
      </div>
      <button 
        type="submit" 
        class="btn btn-primary w-full"
        :disabled="isLoading"
      >
        {{ isLoading ? 'Creating Account...' : 'Create Account' }}
      </button>
    </form>

    <!-- Info Text -->
    <p class="mt-4 text-sm text-gray-600 text-center">
      {{ activeTab === 'login' 
        ? "Don't have an account? Create one to track your quiz results." 
        : 'Already have an account? Login to access your quiz history.' 
      }}
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useParticipantStore } from '../store/participant'
import { useRouter } from 'vue-router'

const props = defineProps({
  quiz: {
    type: Object,
    required: false,
    default: null
  }
})

// eslint-disable-next-line no-unused-vars
const emit = defineEmits(['auth-success'])

const activeTab = ref('login')
const email = ref('')
const password = ref('')
const name = ref('')
const error = ref('')
const isLoading = ref(false)
const router = useRouter()
const participantStore = useParticipantStore()

const handleAuthSuccess = async (participantData) => {
  const participantStore = useParticipantStore()
  
  // Ensure we have the required data
  if (!participantData?.token || !participantData?.participant_id) {
    error.value = 'Invalid response from server'
    return
  }

  try {
    // First set the participant data in store
    await participantStore.setParticipantData(participantData)
    
    // Wait a moment for the store to update
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // Verify token with backend
    await axios.get('/api/participants/me/')
    
    // If we get here, token is valid, proceed with navigation
    if (props.quiz?.id) {
      participantStore.setCurrentQuiz(props.quiz)
      router.push({
        name: 'QuizEvent',
        params: { id: props.quiz.id }
      })
    } else {
      router.push({ 
        name: 'ParticipantPortal',
        replace: true
      })
    }
  } catch (err) {
    console.error('Failed to verify token:', err)
    error.value = 'Authentication failed. Please try again.'
    participantStore.clearParticipantData()
  }
}

const handleParticipantLogin = async () => {
  if (isLoading.value) return
  isLoading.value = true
  error.value = ''

  try {
    console.log('Sending login request:', {
      email: email.value,
      password: password.value,
      quiz_id: props.quiz?.id
    })

    const response = await axios.post('/api/participants/login/', {
      email: email.value,
      password: password.value,
      quiz_id: props.quiz?.id
    })

    console.log('Login response:', response.data)
    await handleAuthSuccess(response.data)
  } catch (err) {
    console.error('Login failed:', err)
    error.value = err.response?.data?.detail || 'Login failed. Please try again.'
    participantStore.clearParticipantData()
  } finally {
    isLoading.value = false
  }
}

const handleParticipantRegistration = async () => {
  if (isLoading.value) return
  isLoading.value = true
  error.value = ''

  try {
    const response = await axios.post('/api/participants/register/', {
      email: email.value,
      password: password.value,
      name: name.value,
      quiz_id: props.quiz?.id
    })

    console.log('Registration response:', response.data)
    await handleAuthSuccess(response.data)
  } catch (err) {
    console.error('Registration failed:', err)
    error.value = err.response?.data?.detail || 'Registration failed. Please try again.'
    participantStore.clearParticipantData()
  } finally {
    isLoading.value = false
  }
}
</script> 