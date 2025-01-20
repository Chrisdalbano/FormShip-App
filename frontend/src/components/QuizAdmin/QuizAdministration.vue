<template>
  <div
    class="quiz-admin w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg"
  >
    <h1 class="text-2xl font-bold mb-6">
      Quiz Administration: {{ quiz.title }}
    </h1>

    <!-- Loading Indicator -->
    <div v-if="loading" class="text-center text-gray-500 mb-4">
      Loading administration panel...
    </div>

    <!-- Main Content -->
    <div v-else>
      <!-- User Invitation and Management -->
      <section class="mb-6">
        <h2 class="text-xl font-semibold mb-4">Invited Users</h2>
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
          <label class="block font-semibold text-gray-700 mb-2">
            Invite More Users (comma-separated)
          </label>
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
            Send Invitations
          </button>
        </div>
      </section>

      <!-- Administration Settings -->
      <section class="mb-6">
        <h2 class="text-xl font-semibold mb-4">Administration Settings</h2>
        <div class="flex flex-col space-y-3">
          <div>
            <input
              type="checkbox"
              id="isPublished"
              v-model="quiz.is_published"
            />
            <label for="isPublished" class="ml-2">Publish Quiz?</label>
          </div>
          <div>
            <input type="checkbox" id="isTesting" v-model="quiz.is_testing" />
            <label for="isTesting" class="ml-2">Enable Testing Mode</label>
          </div>
          <div>
            <label class="block font-semibold text-gray-700 mb-2"
              >Access Control</label
            >
            <select v-model="quiz.access_control" class="input-field w-full">
              <option value="public">Public</option>
              <option value="invitation">Invitation Only</option>
              <option value="login_required">Login Required</option>
            </select>
          </div>
        </div>
      </section>

      <!-- Actions -->
      <section>
        <button
          @click="saveSettings"
          class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Save Changes
        </button>
        <button
          v-if="!quiz.is_published"
          @click="publishQuiz"
          class="ml-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Publish Quiz
        </button>
      </section>
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

const quiz = ref({})
const invitedUsers = ref([])
const inviteEmails = ref('')
const loading = ref(true)

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

const fetchInvitedUsers = async () => {
  try {
    const res = await axios.get(`/api/quizzes/${quizId}/invited-users/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    invitedUsers.value = res.data
  } catch (err) {
    console.error('Error fetching invited users:', err)
  }
}

const inviteUsers = async () => {
  try {
    const emails = inviteEmails.value
      .split(',')
      .map(email => email.trim())
      .filter(email => email)

    const res = await axios.post(
      `/api/quizzes/${quizId}/invite-users/`,
      { emails },
      { headers: { Authorization: `Bearer ${authStore.token}` } },
    )
    invitedUsers.value.push(...res.data)
    inviteEmails.value = ''
    alert('Invitations sent successfully!')
  } catch (err) {
    console.error('Error inviting users:', err)
    alert('Failed to send invitations.')
  }
}

const saveSettings = async () => {
  try {
    await axios.patch(
      `/api/quizzes/${quizId}/`,
      {
        is_published: quiz.value.is_published,
        is_testing: quiz.value.is_testing,
        access_control: quiz.value.access_control,
      },
      { headers: { Authorization: `Bearer ${authStore.token}` } },
    )
    alert('Quiz settings updated successfully!')
  } catch (err) {
    console.error('Error saving settings:', err)
    alert('Failed to save settings.')
  }
}

const publishQuiz = async () => {
  try {
    quiz.value.is_published = true
    await saveSettings()
  } catch (err) {
    console.error('Error publishing quiz:', err)
    alert('Failed to publish quiz.')
  }
}

onMounted(async () => {
  await fetchQuiz()
  await fetchInvitedUsers()
  loading.value = false
})
</script>

<style scoped>
.input-field {
  @apply border border-gray-300 px-3 py-2 rounded focus:outline-none focus:ring;
}
</style>
