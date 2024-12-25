<template>
  <div class="max-w-md mx-auto mt-8 p-6 bg-white rounded-lg shadow-lg">
    <h2 class="text-2xl font-semibold mb-4 text-center">Create an Account</h2>
    <form @submit.prevent="register">
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
      <div class="mb-4">
        <label class="block text-gray-700">Password</label>
        <input
          type="password"
          v-model="password"
          placeholder="Password"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <div class="mb-6">
        <label class="block text-gray-700">Confirm Password</label>
        <input
          type="password"
          v-model="confirmPassword"
          placeholder="Confirm Password"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <p v-if="passwordMismatch" class="text-red-500 text-sm mt-2">
          Passwords do not match
        </p>
      </div>
      <button
        type="submit"
        :disabled="passwordMismatch"
        class="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
      >
        Register
      </button>
    </form>
  </div>
</template>

<script>
import axios from 'axios'
import { useAuthStore } from '../store/auth'

export default {
  data() {
    return {
      email: '',
      password: '',
      confirmPassword: '',
    }
  },
  computed: {
    passwordMismatch() {
      return (
        this.password &&
        this.confirmPassword &&
        this.password !== this.confirmPassword
      )
    },
  },
  methods: {
    async register() {
      if (this.passwordMismatch) {
        alert('Passwords do not match')
        return
      }
      try {
        await axios.post('http://localhost:8000/api/users/register/', {
          email: this.email,
          password: this.password,
        })

        const loginResponse = await axios.post(
          'http://localhost:8000/api/users/login/',
          {
            email: this.email,
            password: this.password,
          },
        )
        const authStore = useAuthStore()
        authStore.setToken(loginResponse.data.access)
        this.$emit('register-success')
      } catch (error) {
        console.error('Registration error:', error.response?.data || error)
        alert('Registration failed')
      }
    },
  },
}
</script>
