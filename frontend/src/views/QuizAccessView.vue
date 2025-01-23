<template>
  <div class="quiz-access-container">
    <div v-if="loading" class="text-center">Loading quiz info...</div>
    <div v-else-if="errorMessage" class="text-center text-red-500">
      {{ errorMessage }}
    </div>
    <div v-else-if="quiz">
      <div v-if="quiz.access_control === 'login_required' && !isUserLoggedIn">
        <p>You must be logged in to access this quiz.</p>
      </div>

      <div v-if="quiz.access_control === 'invitation'">
        <label class="block mt-2">Enter your invitation email:</label>
        <input
          type="email"
          v-model="invitationEmail"
          placeholder="john@example.com"
          class="border p-2 rounded"
        />
      </div>

      <div v-if="quiz.require_password">
        <label class="block mt-2">Quiz Password:</label>
        <input
          type="password"
          v-model="quizPassword"
          placeholder="Enter quiz password"
          class="border p-2 rounded"
        />
      </div>

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
const invitationEmail = ref('')
const quizPassword = ref('')
const participantName = ref('')

const isUserLoggedIn = computed(() => !!authStore.token)

onMounted(async () => {
  try {
    const res = await axios.get(`/api/quizzes/${quizId}/`)
    quiz.value = res.data
  } catch (err) {
    console.error('Error fetching quiz:', err)
    errorMessage.value =
      'Could not load quiz. It may be invalid or unpublished.'
  } finally {
    loading.value = false
  }
})

async function onSubmitAccess() {
  if (!quiz.value) return

  try {
    const payload = {
      email: invitationEmail.value || null,
      password: quizPassword.value || null,
      name: participantName.value || null,
    }

    const participantRes = await axios.post(
      `/api/participants/quiz/${quizId}/`,
      payload,
    )

    const participantData = participantRes.data
    localStorage.setItem(`quiz_${quizId}_participant_id`, participantData.id)
    router.push({ name: 'QuizEvent', params: { id: quizId } })
  } catch (err) {
    console.error('Error creating participant:', err)
    errorMessage.value =
      err.response?.data?.error || 'Failed to validate participant.'
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
