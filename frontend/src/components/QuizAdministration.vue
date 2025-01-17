<template>
    <div class="quiz-admin w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow">
      <h1 class="text-2xl font-bold mb-4">Quiz Administration: {{ quiz?.title }}</h1>
  
      <div v-if="loading" class="text-center text-gray-600 mb-4">Loading...</div>
      <div v-else>
        <div class="mb-6">
          <h2 class="text-xl font-semibold">Invited Users</h2>
          <ul>
            <li
              v-for="invite in invitedUsers"
              :key="invite.id"
              class="flex justify-between items-center my-2"
            >
              <span>{{ invite.email }}</span>
              <span class="text-sm text-gray-500">{{ invite.invited_at }}</span>
            </li>
          </ul>
  
          <div class="mt-4">
            <label class="block text-gray-700 mb-2">Invite more users (comma-separated)</label>
            <input
              v-model="inviteEmails"
              type="text"
              placeholder="user1@example.com, user2@example.com"
              class="input-field w-full"
            />
            <button
              @click="inviteUsers"
              class="mt-2 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Send Invites
            </button>
          </div>
        </div>
  
        <!-- Additional Administration, e.g. toggles for publish, testing, advanced... -->
        <div>
          <h2 class="text-xl font-semibold mb-2">Administration Settings</h2>
          <div class="mb-2">
            <input type="checkbox" v-model="quiz.is_published" id="isPublished" />
            <label for="isPublished" class="ml-2">Is Published?</label>
          </div>
          <div class="mb-2">
            <input type="checkbox" v-model="quiz.is_testing" id="isTesting" />
            <label for="isTesting" class="ml-2">Is Testing?</label>
          </div>
  
          <button
            @click="updateQuizAdminSettings"
            class="mt-2 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            Save Admin Changes
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import axios from 'axios'
  import { useAuthStore } from '@/store/auth'
  import { useRoute } from 'vue-router'
  
  const route = useRoute()
  const quizId = route.params.id
  const authStore = useAuthStore()
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL
  
  const quiz = ref(null)
  const invitedUsers = ref([])
  const inviteEmails = ref('')
  const loading = ref(true)
  
  onMounted(async () => {
    await fetchQuiz()
    await fetchInvitedUsers()
    loading.value = false
  })
  
  const fetchQuiz = async () => {
    try {
      const res = await axios.get(`${apiBaseUrl}/quizzes/${quizId}/`, {
        headers: { Authorization: `Bearer ${authStore.token}` },
      })
      quiz.value = res.data
    } catch (err) {
      console.error('Error fetching quiz:', err)
    }
  }
  
  const fetchInvitedUsers = async () => {
    try {
      const res = await axios.get(`${apiBaseUrl}/quizzes/${quizId}/invited-users/`, {
        headers: { Authorization: `Bearer ${authStore.token}` },
      })
      invitedUsers.value = res.data
    } catch (err) {
      console.error('Error fetching invited users:', err)
    }
  }
  
  const inviteUsers = async () => {
    try {
      // Convert comma-separated to array
      const emailsArr = inviteEmails.value
        .split(',')
        .map(e => e.trim())
        .filter(e => e.length > 0)
  
      const res = await axios.post(
        `${apiBaseUrl}/quizzes/${quizId}/invite-users/`,
        { emails: emailsArr },
        { headers: { Authorization: `Bearer ${authStore.token}` } }
      )
      invitedUsers.value.push(...res.data)
      inviteEmails.value = ''
      alert('Invites sent successfully')
    } catch (err) {
      console.error('Error inviting users:', err)
      alert('Failed to invite users.')
    }
  }
  
  const updateQuizAdminSettings = async () => {
    if (!quiz.value) return
    try {
      const payload = {
        is_published: quiz.value.is_published,
        is_testing: quiz.value.is_testing,
        // etc. 
      }
      await axios.patch(`${apiBaseUrl}/quizzes/${quizId}/`, payload, {
        headers: { Authorization: `Bearer ${authStore.token}` },
      })
      alert('Quiz admin settings updated successfully!')
    } catch (err) {
      console.error('Error updating quiz admin settings:', err)
      alert('Failed to update admin settings.')
    }
  }
  </script>
  
  <style scoped>
  .input-field {
    @apply border border-gray-300 px-3 py-2 rounded focus:outline-none focus:ring;
  }
  </style>
  