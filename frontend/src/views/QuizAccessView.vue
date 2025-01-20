<template>
  <div class="quiz-access-container">
    <!-- Loading / Error States -->
    <div v-if="loading" class="text-center">Loading quiz info...</div>
    <div v-else-if="errorMessage" class="text-center text-red-500">
      {{ errorMessage }}
    </div>
    <!-- QUIZ ACCESS LOGIC -->
    <div v-else-if="quiz">
      <!-- If the user must be logged in but is not, prompt or show message -->
      <div v-if="quiz.access_control === 'login_required' && !isUserLoggedIn">
        <p>You must be logged in to access this quiz.</p>
        <!-- Link to your login page or show login component inline -->
      </div>

      <!-- If invitation, ask for email unless user is already logged in with an email? -->
      <div v-if="quiz.access_control === 'invitation'">
        <label class="block mt-2">Enter your invitation email:</label>
        <input
          type="email"
          v-model="invitationEmail"
          placeholder="john@example.com"
          class="border p-2 rounded"
        />
      </div>

      <!-- If quiz requires password -->
      <div v-if="quiz.require_password">
        <label class="block mt-2">Quiz Password:</label>
        <input
          type="password"
          v-model="quizPassword"
          placeholder="Enter quiz password"
          class="border p-2 rounded"
        />
      </div>

      <!-- If quiz require_name or does NOT allow_anonymous -->
      <div v-if="quiz.require_name || !quiz.allow_anonymous">
        <label class="block mt-2">Your Name/Nickname:</label>
        <input
          type="text"
          v-model="participantName"
          placeholder="Your name"
          class="border p-2 rounded"
        />
      </div>

      <button
        class="bg-blue-500 text-white px-4 py-2 rounded mt-4"
        @click="onSubmitAccess"
      >
        Continue to Quiz
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

const quizId = route.params.id
const quiz = ref(null)
const loading = ref(true)
const errorMessage = ref('')

// Fields for participant creation
const invitationEmail = ref('')
const quizPassword = ref('')
const participantName = ref('')

const isUserLoggedIn = computed(() => !!authStore.token)

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// 1) On mount, fetch minimal quiz info
onMounted(async () => {
  try {
    const res = await axios.get(`${apiBaseUrl}/quizzes/${quizId}/`)
    quiz.value = res.data
  } catch (err) {
    console.error('Error fetching quiz:', err)
    errorMessage.value =
      'Could not load quiz. It may be invalid or unpublished.'
  } finally {
    loading.value = false
  }
})

// 2) Attempt to create participant. If success, proceed to CompletedQuiz
async function onSubmitAccess() {
  if (!quiz.value) return

  try {
    const payload = {
      email: invitationEmail.value || null,
      password: quizPassword.value || null,
      name: participantName.value || null,
    }

    const participantRes = await axios.post(
      `${apiBaseUrl}/participants/quiz/${quizId}/`,
      payload,
    )

    // If we get here, participant was created successfully
    const participantData = participantRes.data

    // Option A: store participant ID in local storage or in a global store
    localStorage.setItem(`quiz_${quizId}_participant_id`, participantData.id)

    // Now route to the actual quiz-taking page:
    router.push({ name: 'QuizEventComponent', params: { id: quizId } })
  } catch (err) {
    console.error('Error creating participant:', err)
    errorMessage.value =
      err.response?.data?.error ||
      err.response?.data?.detail ||
      'Failed to validate participant.'
  }
}
</script>

<style scoped>
.quiz-access-container {
  max-width: 600px;
  margin: 2rem auto;
  padding: 1rem;
  background-color: #fff;
  border-radius: 8px;
}
</style>
