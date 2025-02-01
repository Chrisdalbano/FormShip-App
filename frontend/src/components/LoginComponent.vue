<template>
  <div class="max-w-md mx-auto mt-8 p-6 bg-white rounded-lg shadow-lg">
    <h2 class="text-2xl font-semibold mb-4 text-center">Log in to formship</h2>
    <form @submit.prevent="login">
      <div class="mb-4">
        <label class="block text-gray-700">Email</label>
        <input
          type="email"
          v-model="email"
          placeholder="Email"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <div class="mb-6">
        <label class="block text-gray-700">Password</label>
        <input
          type="password"
          v-model="password"
          placeholder="Password"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <button
        type="submit"
        class="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
      >
        Login
      </button>
    </form>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useAuthStore } from '../store/auth'
import axios from 'axios'

export default {
  setup(_, { emit }) {
    const email = ref('')
    const password = ref('')
    const authStore = useAuthStore()

    const login = async () => {
      try {
        const response = await axios.post(
          'http://localhost:8000/api/user/login/',
          {
            email: email.value,
            password: password.value,
          },
        )

        authStore.setToken(response.data.access)
        await authStore.fetchUser() // Fetch user data after setting token
        emit('login-success')
      } catch (error) {
        console.error('Login error:', error.response?.data || error)
        alert('Login failed')
      }
    }

    return {
      email,
      password,
      login,
    }
  },
}
</script>
