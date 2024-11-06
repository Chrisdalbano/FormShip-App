<template>
  <div v-if="loading" class="text-center mt-8 text-gray-600">Loading...</div>
  <div v-else class="max-w-lg mx-auto mt-8 p-6 bg-white rounded-lg shadow-lg">
    <h2 class="text-2xl font-semibold mb-6 text-center">My Profile</h2>

    <form @submit.prevent="updateProfile">
      <div class="mb-4">
        <label class="block text-gray-700">First Name</label>
        <input v-model="first_name" class="input-field" type="text" required />
      </div>

      <div class="mb-4">
        <label class="block text-gray-700">Last Name</label>
        <input v-model="last_name" class="input-field" type="text" required />
      </div>

      <div class="mb-4">
        <label class="block text-gray-700">Email</label>
        <input v-model="email" class="input-field" type="email" required />
      </div>

      <div class="mb-4">
        <label class="block text-gray-700">New Password</label>
        <input v-model="password" class="input-field" type="password" placeholder="Leave blank to keep current password" />
      </div>

      <div class="mb-4">
        <label class="block text-gray-700">Confirm Password</label>
        <input v-model="confirmPassword" class="input-field" type="password" />
        <p v-if="passwordMismatch" class="text-red-500 text-sm mt-2">Passwords do not match</p>
      </div>

      <button type="submit" class="btn-primary" :disabled="passwordMismatch">Update Profile</button>
    </form>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../store/auth'

export default {
  setup() {
    const authStore = useAuthStore()
    const loading = ref(true)
    const email = ref('')
    const first_name = ref('')
    const last_name = ref('')
    const password = ref('')
    const confirmPassword = ref('')

    const passwordMismatch = computed(() => password.value && confirmPassword.value && password.value !== confirmPassword.value)

    const fetchUserProfile = () => {
      if (authStore.user) {
        email.value = authStore.user.email
        first_name.value = authStore.user.first_name || ''
        last_name.value = authStore.user.last_name || ''
        loading.value = false
      } else {
        authStore.fetchUser().then(() => {
          email.value = authStore.user.email
          first_name.value = authStore.user.first_name || ''
          last_name.value = authStore.user.last_name || ''
          loading.value = false
        }).catch(error => {
          console.error('Failed to fetch user data:', error)
          loading.value = false
        })
      }
    }

    const updateProfile = async () => {
      if (passwordMismatch.value) {
        alert('Passwords do not match')
        return
      }
      try {
        await axios.put(
          'http://localhost:8000/api/users/me/',
          {
            email: email.value,
            first_name: first_name.value,
            last_name: last_name.value,
            password: password.value || undefined,
          },
          { headers: { Authorization: `Bearer ${authStore.token}` } }
        )
        alert('Profile updated successfully')
        authStore.fetchUser() // Refresh user data
      } catch (error) {
        console.error(error)
        alert('Failed to update profile')
      }
    }

    onMounted(() => {
      fetchUserProfile()
    })

    return {
      email,
      first_name,
      last_name,
      password,
      confirmPassword,
      passwordMismatch,
      updateProfile,
      loading,
    }
  },
}
</script>

<style scoped>
.input-field {
  @apply w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500;
}
.btn-primary {
  @apply w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-md;
}
</style>
