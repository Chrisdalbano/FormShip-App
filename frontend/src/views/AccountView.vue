<template>
  <div>
    <h1>Account Settings</h1>
    <form @submit.prevent="updateAccount">
      <input type="email" v-model="user.email" placeholder="Email" />
      <input type="text" v-model="user.first_name" placeholder="First Name" />
      <input type="text" v-model="user.last_name" placeholder="Last Name" />
      <input
        type="text"
        v-model="user.organization"
        placeholder="Organization"
      />
      <select v-model="user.organization_type">
        <option>eCommerce</option>
        <option>Education</option>
        <option>Medical</option>
        <!-- Add other organization types here -->
      </select>
      <button type="submit">Update</button>
    </form>
  </div>
</template>

<script>
import { useAuthStore } from '../store/auth'
import axios from 'axios'

export default {
  setup() {
    const authStore = useAuthStore()
    const user = authStore.user

    const updateAccount = async () => {
      try {
        await axios.put('http://localhost:8000/api/users/me/', user, {
          headers: { Authorization: `Bearer ${authStore.token}` },
        })
        alert('Account updated')
      } catch (error) {
        console.error('Failed to update account', error)
        alert('Failed to update account')
      }
    }

    return { user, updateAccount }
  },
}
</script>
