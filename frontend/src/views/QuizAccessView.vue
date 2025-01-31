<template>
  <div class="quiz-access-container">
    <h2 v-if="quiz.isCreator" class="text-xl font-bold">
      Test Mode Available for Quiz: {{ quiz.title }}
    </h2>
    <div v-if="loading">Loading quiz...</div>
    <div v-else-if="errorMessage" class="text-red-500">{{ errorMessage }}</div>
    <div v-else>
      <div v-if="quiz.access_control === 'login_required' && !isUserLoggedIn">
        <p class="text-yellow-600">
          You must be logged in to access this quiz.
        </p>
      </div>
      <div v-if="quiz.require_password">
        <label>Quiz Password:</label>
        <input v-model="quizPassword" type="password" placeholder="Password" />
      </div>
      <div v-if="quiz.require_name || !quiz.allow_anonymous">
        <label>Your Name:</label>
        <input v-model="participantName" type="text" placeholder="Name" />
      </div>
      <button @click="validateAccess" class="btn btn-primary">Access Quiz</button>
      <button
        v-if="quiz.isCreator"
        @click="launchTestMode"
        class="btn btn-secondary"
      >
        Test Quiz
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const quizId = route.params.id
const quiz = ref(null)
const errorMessage = ref('')
const participantName = ref('')
const quizPassword = ref('')
const loading = ref(true)
const isUserLoggedIn = ref(false) // Assume a method to check login status

onMounted(async () => {
  try {
    const response = await axios.get(`/api/quizzes/${quizId}/`)
    quiz.value = response.data
    
    // Check if quiz requires login and user is not logged in
    if (quiz.value.access_control === 'login_required' && !checkUserLoginStatus()) {
      router.push({ 
        name: 'Login', 
        query: { 
          redirect: `/quiz/${quizId}`,
          message: 'Please login to access this quiz'
        }
      })
      return
    }
    
    isUserLoggedIn.value = checkUserLoginStatus()
  } catch (error) {
    if (error.response?.status === 401) {
      router.push({ 
        name: 'Login', 
        query: { 
          redirect: `/quiz/${quizId}`,
          message: 'Please login to access this quiz'
        }
      })
      return
    }
    console.error('Failed to load quiz:', error)
    errorMessage.value = 'Failed to load quiz.'
  } finally {
    loading.value = false
  }
})

const validateAccess = async () => {
  try {
    if (quiz.value.access_control === 'login_required' && !isUserLoggedIn.value) {
      router.push({ 
        name: 'Login',
        query: { 
          redirect: `/quiz/${quizId}`,
          message: 'Please login to access this quiz'
        }
      })
      return
    }

    const payload = {
      name: participantName.value || 'Guest',
      password: quizPassword.value || null,
    }
    const response = await axios.post(
      `/api/participants/quiz/${quizId}/`,
      payload,
    )

    if (response.data.id) {
      localStorage.setItem(`participant_${quizId}`, response.data.id)
      router.push({ name: 'QuizEvent', params: { id: quizId } })
    } else {
      console.error('Participant ID is missing in response.')
      errorMessage.value = 'Failed to validate participant.'
    }
  } catch (error) {
    if (error.response?.status === 401) {
      router.push({ 
        name: 'Login',
        query: { 
          redirect: `/quiz/${quizId}`,
          message: 'Please login to access this quiz'
        }
      })
      return
    }
    console.error('Failed to validate participant:', error)
    errorMessage.value = 'Failed to validate participant.'
  }
}

const launchTestMode = () => {
  window.open(`/quiz/${quizId}?test=true`, '_blank')
}

function checkUserLoginStatus() {
  // Implement actual login check, for example:
  return localStorage.getItem('token') !== null
}
</script>
