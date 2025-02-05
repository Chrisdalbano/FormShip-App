<template>
  <div
    class="quiz-analysis-container w-full max-w-5xl mx-auto p-6 bg-white rounded-lg shadow-lg"
  >
    <h1 class="text-2xl font-bold mb-6">Quiz Analysis: {{ quiz.title }}</h1>

    <div v-if="loading" class="text-center text-gray-500">
      Loading analysis data...
    </div>

    <div v-else>
      <!-- Attempt Summary -->
      <section class="mb-6">
        <h2 class="text-xl font-semibold mb-4">Attempts Summary</h2>
        <p>Total Attempts: {{ attempts.length }}</p>
        <p>
          Average Score:
          {{
            attempts.length > 0
              ? (
                  attempts.reduce((sum, a) => sum + (a.final_score || 0), 0) /
                  attempts.length
                ).toFixed(2)
              : 'N/A'
          }}
        </p>
      </section>

      <!-- Awaiting Grading -->
      <section v-if="awaitingGrading.length" class="mb-6">
        <h2 class="text-xl font-semibold mb-4">Awaiting Manual Grading</h2>
        <div
          v-for="attempt in awaitingGrading"
          :key="attempt.id"
          class="mb-4 p-4 border rounded"
        >
          <p>Participant: {{ attempt.participant_name || 'Anonymous' }}</p>
          <button
            @click="gradeAttempt(attempt)"
            class="mt-2 bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-700"
          >
            Grade Attempt
          </button>
        </div>
      </section>

      <!-- All Attempts Table -->
      <section>
        <h2 class="text-xl font-semibold mb-4">All Attempts</h2>
        <table class="w-full border">
          <thead>
            <tr class="bg-gray-200">
              <th class="py-2 px-4">Participant</th>
              <th class="py-2 px-4">Email</th>
              <th class="py-2 px-4">Score</th>
              <th class="py-2 px-4">Duration</th>
              <th class="py-2 px-4">Started At</th>
              <th class="py-2 px-4">Completed At</th>
              <th class="py-2 px-4">Status</th>
              <th class="py-2 px-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="attempt in attempts" :key="attempt.id" class="border-t hover:bg-gray-50">
              <td class="py-2 px-4">{{ attempt.participant_name || 'Anonymous' }}</td>
              <td class="py-2 px-4">{{ attempt.participant_email || 'N/A' }}</td>
              <td class="py-2 px-4">
                <span :class="getScoreClass(attempt.final_score)">
                  {{ attempt.final_score !== null ? `${attempt.final_score}%` : 'N/A' }}
                </span>
              </td>
              <td class="py-2 px-4">{{ formatDuration(attempt.duration) }}</td>
              <td class="py-2 px-4">{{ formatDate(attempt.started_at) }}</td>
              <td class="py-2 px-4">{{ formatDate(attempt.completed_at) }}</td>
              <td class="py-2 px-4">
                <span :class="getStatusClass(attempt)">
                  {{ getStatusText(attempt) }}
                </span>
              </td>
              <td class="py-2 px-4">
                <button
                  v-if="attempt.needs_manual_grading"
                  @click="gradeAttempt(attempt)"
                  class="text-sm bg-yellow-500 text-white px-3 py-1 rounded hover:bg-yellow-600"
                >
                  Grade
                </button>
                <button
                  v-else
                  @click="viewAttemptDetails(attempt)"
                  class="text-sm bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600"
                >
                  View
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/store/auth'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const quizId = route.params.id
const authStore = useAuthStore()

const quiz = ref({})
const attempts = ref([])
const loading = ref(true)

const awaitingGrading = computed(() =>
  attempts.value.filter(a => a.needs_manual_grading),
)

const getScoreClass = (score) => {
  if (score === null) return ''
  if (score >= 80) return 'text-green-600 font-semibold'
  if (score >= 60) return 'text-yellow-600 font-semibold'
  return 'text-red-600 font-semibold'
}

const getStatusClass = (attempt) => {
  if (attempt.needs_manual_grading) return 'text-yellow-600 font-semibold'
  if (!attempt.completed_at) return 'text-gray-600'
  return 'text-green-600 font-semibold'
}

const getStatusText = (attempt) => {
  if (attempt.needs_manual_grading) return 'Needs Grading'
  if (!attempt.completed_at) return 'In Progress'
  return 'Completed'
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const formatDuration = (seconds) => {
  if (!seconds) return 'N/A'
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}m ${remainingSeconds}s`
}

const viewAttemptDetails = (attempt) => {
  router.push(`/quiz/${quizId}/attempt/${attempt.id}`)
}

const fetchQuiz = async () => {
  try {
    const res = await axios.get(`/api/quizzes/${quizId}/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    quiz.value = res.data
  } catch (err) {
    console.error('Error fetching quiz:', err)
  }
}

const fetchAttempts = async () => {
  try {
    const res = await axios.get(`/api/quizzes/${quizId}/attempts/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    attempts.value = res.data
  } catch (err) {
    console.error('Error fetching attempts:', err)
  }
}

const gradeAttempt = async attempt => {
  alert(`Grading attempt #${attempt.id}...`)
  // TODO: Open a grading modal or redirect to a grading view
}

onMounted(async () => {
  await fetchQuiz()
  await fetchAttempts()
  loading.value = false
})
</script>

<style scoped>
.table {
  border-collapse: collapse;
}
.table th,
.table td {
  border: 1px solid #ddd;
  padding: 8px;
}
.table th {
  background-color: #f9f9f9;
  font-weight: bold;
}
</style>
