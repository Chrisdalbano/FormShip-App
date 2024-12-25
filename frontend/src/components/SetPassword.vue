<template>
  <div>
    <h2>Set Your Password</h2>
    <form @submit.prevent="setPassword">
      <div>
        <label>Email</label>
        <input v-model="email" type="email" required />
      </div>
      <div>
        <label>Token</label>
        <input v-model="token" type="text" required />
      </div>
      <div>
        <label>New Password</label>
        <input v-model="password" type="password" required />
      </div>
      <button type="submit">Set Password</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const email = ref('')
const token = ref('')
const password = ref('')

const setPassword = async () => {
  try {
    await axios.post('/api/set-password/', { email, token, password })
    alert('Password set successfully')
  } catch (error) {
    console.error('Failed to set password', error)
    alert('Failed to set password')
  }
}
</script>
