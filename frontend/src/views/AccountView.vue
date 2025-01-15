<template>
  <div
    class="account-container max-w-lg mx-auto mt-12 p-6 bg-white rounded-lg shadow-lg"
  >
    <h2 class="text-2xl font-semibold mb-4 text-center">Account Settings</h2>
    <div v-if="loading" class="text-center text-gray-600">Loading...</div>
    <div v-else-if="!account">
      <p class="text-red-500 text-center">
        User or account information is missing
      </p>
    </div>
    <div v-else>
      <p class="mb-4">
        <strong>Owner:</strong> {{ account.owner_email || 'N/A' }}
      </p>
      <p class="mb-4">
        <strong>Subscription Plan:</strong>
        {{ account.subscription_plan || 'N/A' }}
      </p>
      <p class="mb-4">
        <strong>Member Count:</strong> {{ account.member_count || '0' }}
      </p>
      <div class="flex justify-between mt-6">
        <button class="btn-secondary" @click="navigateToUsers">
          Manage Users
        </button>
        <button class="btn-secondary" @click="upgradePlan">Upgrade Plan</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

const authStore = useAuthStore()
const router = useRouter()
const loading = ref(true)
const account = ref(null)
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

const fetchAccount = async () => {
  try {
    if (!authStore.user || !authStore.user.id) {
      console.error('User or account information is missing')
      loading.value = false
      return
    }

    const response = await axios.get(
      `${apiBaseUrl}/accounts/${authStore.user.id}/`,
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      },
    )
    account.value = response.data
  } catch (error) {
    console.error('Failed to load account data:', error.response?.data || error)
  } finally {
    loading.value = false
  }
}

const navigateToUsers = () => {
  router.push('/users')
}

const upgradePlan = () => {
  alert('Plan upgrade functionality coming soon!')
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    fetchAccount()
  } else {
    console.error('User is not authenticated')
  }
})
</script>

<style scoped>
.btn-secondary {
  @apply bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400 transition duration-150;
}
</style>
