<template>
  <div
    class="participant-details max-w-6xl mx-auto p-6 bg-white rounded shadow"
  >
    <h1 class="text-2xl font-bold mb-4">
      Participant Details - {{ participant.name || 'Anonymous' }}
    </h1>
    <div v-if="loading" class="text-center">Loading...</div>
    <div v-else>
      <div class="mb-6">
        <h2 class="text-xl font-semibold">General Info</h2>
        <p><strong>Quiz:</strong> {{ participant.quiz_title }}</p>
        <p><strong>Email:</strong> {{ participant.email || 'N/A' }}</p>
        <p>
          <strong>Status:</strong>
          {{ participant.has_completed ? 'Completed' : 'Pending' }}
        </p>
        <p>
          <strong>Responded At:</strong> {{ participant.responded_at || 'N/A' }}
        </p>
      </div>

      <div class="mb-6">
        <h2 class="text-xl font-semibold">Performance Summary</h2>
        <p><strong>Final Score:</strong> {{ participant.final_score }}%</p>
        <p><strong>Total Attempts:</strong> {{ attempts.length }}</p>
      </div>

      <div class="mb-6">
        <h2 class="text-xl font-semibold">Attempt Details</h2>
        <table class="table-auto w-full">
          <thead>
            <tr class="bg-gray-200">
              <th class="py-2 px-4">Attempt #</th>
              <th class="py-2 px-4">Completion Time</th>
              <th class="py-2 px-4">Score</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(attempt, index) in attempts"
              :key="attempt.id"
              class="border-b"
            >
              <td class="py-2 px-4">{{ index + 1 }}</td>
              <td class="py-2 px-4">{{ attempt.completed_at }}</td>
              <td class="py-2 px-4">{{ attempt.score }}%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAxios } from '@/composables/useAxios'

const route = useRoute()
const participantId = route.params.id
const loading = ref(true)
const participant = ref({})
const attempts = ref([])

// Get axiosInstance from the composable
const { axiosInstance } = useAxios()

onMounted(async () => {
  try {
    // Use axiosInstance for API requests
    const { data } = await axiosInstance.get(`/participants/${participantId}/`)
    participant.value = data
    attempts.value = data.attempts || []
  } catch (error) {
    console.error('Error fetching participant data:', error)
  } finally {
    loading.value = false
  }
})
</script>
