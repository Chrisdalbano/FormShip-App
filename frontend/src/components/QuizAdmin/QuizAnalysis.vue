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
              <th class="py-2 px-4">Score</th>
              <th class="py-2 px-4">Completed At</th>
              <th class="py-2 px-4">Needs Grading?</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="attempt in attempts" :key="attempt.id" class="border-t">
              <td class="py-2 px-4">
                {{ attempt.participant_name || 'Anonymous' }}
              </td>
              <td class="py-2 px-4">{{ attempt.final_score ?? 'N/A' }}</td>
              <td class="py-2 px-4">{{ attempt.completed_at }}</td>
              <td class="py-2 px-4">
                {{ attempt.needs_manual_grading ? 'Yes' : 'No' }}
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
import { useRoute } from 'vue-router'

const route = useRoute()
const quizId = route.params.id
const authStore = useAuthStore()

const quiz = ref({})
const attempts = ref([])
const loading = ref(true)

const awaitingGrading = computed(() =>
  attempts.value.filter(a => a.needs_manual_grading),
)

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
