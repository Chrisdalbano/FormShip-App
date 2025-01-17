<template>
  <div
    class="quiz-analysis w-full max-w-5xl mx-auto p-6 bg-white rounded shadow"
  >
    <h1 class="text-2xl font-bold mb-4">Quiz Analysis - {{ quiz?.title }}</h1>

    <div v-if="loading" class="text-center">Loading...</div>
    <div v-else>
      <p class="mb-2">Evaluation Type: {{ quiz.evaluation_type }}</p>
      <p class="mb-4">Total Attempts: {{ attempts.length }}</p>

      <!-- If post-evaluated or hybrid, show attempts needing manual grading -->
      <div
        v-if="
          quiz.evaluation_type === 'post' || quiz.evaluation_type === 'hybrid'
        "
      >
        <h2 class="text-xl font-semibold mb-2">Awaiting Manual Grading</h2>
        <div
          v-for="attempt in attempts"
          :key="attempt.id"
          class="border p-2 mb-2"
        >
          <p class="font-bold">
            User: {{ attempt.participant_name || 'Anonymous' }}
          </p>
          <p>Score: {{ attempt.partial_score }} (auto-graded so far)</p>
          <button
            @click="gradeAttempt(attempt)"
            class="mt-2 bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-700"
          >
            Finalize Grade
          </button>
        </div>
      </div>

      <!-- Show summary for all attempts -->
      <h2 class="text-xl font-semibold mt-6 mb-2">All Attempts</h2>
      <table class="w-full border">
        <thead>
          <tr class="bg-gray-200">
            <th class="py-2 px-2 text-left">Participant</th>
            <th class="py-2 px-2 text-left">Score</th>
            <th class="py-2 px-2 text-left">Completed At</th>
            <th class="py-2 px-2 text-left">Needs Grading?</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="attempt in attempts" :key="attempt.id" class="border-b">
            <td class="px-2 py-1">{{ attempt.participant_name || 'Anon' }}</td>
            <td class="px-2 py-1">{{ attempt.final_score ?? 'N/A' }}</td>
            <td class="px-2 py-1">{{ attempt.completed_at }}</td>
            <td class="px-2 py-1">
              {{ attempt.needs_manual_grading ? 'Yes' : 'No' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/store/auth'
import { useRoute } from 'vue-router'

const route = useRoute()
const authStore = useAuthStore()
const quizId = route.params.id
const loading = ref(true)
const quiz = ref({})
const attempts = ref([])

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

onMounted(async () => {
  await fetchQuiz()
  await fetchAttempts()
  loading.value = false
})

const fetchQuiz = async () => {
  try {
    const res = await axios.get(`${apiBaseUrl}/quizzes/${quizId}/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    quiz.value = res.data
  } catch (err) {
    console.error('Error fetching quiz info:', err)
  }
}

const fetchAttempts = async () => {
  try {
    // Assume you have an endpoint like /api/quizzes/:id/attempts/ returning a list
    const res = await axios.get(`${apiBaseUrl}/quizzes/${quizId}/attempts/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    attempts.value = res.data
  } catch (err) {
    console.error('Error fetching quiz attempts:', err)
  }
}

const gradeAttempt = attempt => {
  alert(`Manually grading attempt #${attempt.id}... (not implemented)`)
  // Possibly open a modal or route to a detailed grader component
}
</script>

<style scoped></style>
