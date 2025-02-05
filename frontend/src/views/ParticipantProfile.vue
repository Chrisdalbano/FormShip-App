<template>
  <div class="max-w-2xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-6">Profile Settings</h1>

    <div v-if="loading" class="text-center py-8">
      Loading profile...
    </div>

    <div v-else-if="error" class="text-red-600 mb-4">
      {{ error }}
    </div>

    <form v-else @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Name -->
      <div>
        <label class="block text-sm font-medium mb-1">Name</label>
        <input
          v-model="form.name"
          type="text"
          class="w-full px-3 py-2 border rounded-lg"
          required
        />
      </div>

      <!-- Email -->
      <div>
        <label class="block text-sm font-medium mb-1">Email</label>
        <input
          v-model="form.email"
          type="email"
          class="w-full px-3 py-2 border rounded-lg"
          required
        />
      </div>

      <!-- New Password -->
      <div>
        <label class="block text-sm font-medium mb-1">New Password (optional)</label>
        <input
          v-model="form.password"
          type="password"
          class="w-full px-3 py-2 border rounded-lg"
          placeholder="Leave blank to keep current password"
        />
      </div>

      <!-- Submit Button -->
      <div class="flex justify-between">
        <button
          type="submit"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          :disabled="isLoading"
        >
          {{ isLoading ? 'Saving...' : 'Save Changes' }}
        </button>

        <button
          type="button"
          @click="confirmDelete"
          class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          :disabled="isLoading"
        >
          Delete Account
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useParticipantStore } from '@/store/participant'
import axios from 'axios'

const router = useRouter()
const participantStore = useParticipantStore()
const loading = ref(true)
const isLoading = ref(false)
const error = ref(null)

const form = ref({
  name: '',
  email: '',
  password: ''
})

onMounted(async () => {
  try {
    const response = await axios.get('/api/participants/me/')
    form.value.name = response.data.name
    form.value.email = response.data.email
  // eslint-disable-next-line no-unused-vars
  } catch (err) {
    error.value = 'Failed to load profile'
  } finally {
    loading.value = false
  }
})

const handleSubmit = async () => {
  try {
    isLoading.value = true
    error.value = null

    const data = {
      name: form.value.name,
      email: form.value.email
    }

    if (form.value.password) {
      data.password = form.value.password
    }

    const response = await axios.put('/api/participants/me/update/', data)
    participantStore.updateParticipant({
      name: response.data.name,
      email: response.data.email
    })
    
    error.value = 'Profile updated successfully'
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to update profile'
  } finally {
    isLoading.value = false
  }
}

const confirmDelete = async () => {
  if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
    try {
      isLoading.value = true
      await axios.delete('/api/participants/me/delete/')
      participantStore.clearParticipant()
      router.push('/participant/login')
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete account'
    } finally {
      isLoading.value = false
    }
  }
}
</script> 