<template>
  <div
    class="users-container max-w-full mx-auto mt-12 p-6 bg-white rounded-lg shadow-lg"
  >
    <h2 class="text-2xl font-semibold mb-4 text-center">Manage Users</h2>
    <div v-if="loading" class="text-center text-gray-600">Loading...</div>
    <div v-else-if="!authStore.account">
      <p class="text-red-500 text-center">Account data is not available</p>
    </div>
    <div v-else>
      <div class="flex justify-between mb-4">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Search users..."
          class="input-field"
        />
        <button @click="showAddUserModal = true" class="btn-primary">
          Add User
        </button>
      </div>

      <table class="w-full table-auto">
        <thead>
          <tr class="bg-gray-200">
            <th class="px-4 py-2">Name</th>
            <th class="px-4 py-2">Email</th>
            <th class="px-4 py-2">Role</th>
            <th class="px-4 py-2">Last Connected</th>
            <th class="px-4 py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="user in filteredUsers"
            :key="user.user_email"
            class="border-b"
          >
            <td class="px-4 py-2">{{ user.user_name || 'N/A' }}</td>
            <td class="px-4 py-2">{{ user.user_email }}</td>
            <td class="px-4 py-2">{{ user.role }}</td>
            <td class="px-4 py-2">{{ user.last_connected || 'Never' }}</td>
            <td class="px-4 py-2">
              <button
                v-if="canModifyUser(user)"
                @click="removeUser(user.user_email)"
                class="btn-danger"
              >
                Remove
              </button>
              <button
                v-if="canModifyUser(user)"
                @click="editUser(user)"
                class="btn-secondary"
              >
                Edit
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add User Modal -->
    <Modal v-if="showAddUserModal" @close="showAddUserModal = false">
      <h3 class="text-xl font-semibold mb-4">Invite New User</h3>
      <form @submit.prevent="addUser">
        <div class="mb-4">
          <label class="block text-gray-700">Email</label>
          <input
            v-model="newUserEmail"
            class="input-field"
            type="email"
            placeholder="Enter email"
            required
          />
        </div>
        <div class="mb-4">
          <label class="block text-gray-700">Role</label>
          <select v-model="newUserRole" class="input-field">
            <option value="member">Member</option>
            <option value="admin">Admin</option>
          </select>
        </div>
        <button type="submit" class="btn-primary" :disabled="addingUser">
          <span v-if="addingUser" class="loader mr-2"></span> Invite User
        </button>
      </form>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../store/auth'
import Modal from '../components/EditPopModal.vue'

const authStore = useAuthStore()
const loading = ref(true)
const searchQuery = ref('')
const users = ref([])
const showAddUserModal = ref(false)
const newUserEmail = ref('')
const newUserRole = ref('member')
const addingUser = ref(false)

const fetchUsers = async () => {
  if (!authStore.account) {
    console.error('Account data is not available')
    loading.value = false
    return
  }

  try {
    const response = await axios.get(
      `/api/accounts/${authStore.account.id}/members/`,
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      },
    )

    if (Array.isArray(response.data)) {
      users.value = response.data
    } else {
      console.error(
        'Invalid response format. Expected an array but received:',
        response.data,
      )
      users.value = []
    }
  } catch (error) {
    console.error(
      'Failed to load users:',
      error.response?.data || error.message,
    )
    users.value = [] // Reset users to prevent further issues
  } finally {
    loading.value = false
  }
}

const addUser = async () => {
  try {
    addingUser.value = true
    const response = await axios.post(
      `/api/accounts/${authStore.account.id}/invite/`,
      {
        email: newUserEmail.value,
        role: newUserRole.value,
      },
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      },
    )

    users.value.push(response.data) // Add the new user to the table
    alert('User invited successfully')
    showAddUserModal.value = false
  } catch (error) {
    console.error(
      'Failed to invite user:',
      error.response?.data || error.message,
    )
    alert('Failed to invite user')
  } finally {
    addingUser.value = false
  }
}

const filteredUsers = computed(() =>
  Array.isArray(users.value)
    ? users.value.filter(user =>
        user.user_email.toLowerCase().includes(searchQuery.value.toLowerCase()),
      )
    : [],
)

const canModifyUser = user => {
  return (
    authStore.user.role === 'owner' ||
    (authStore.user.role === 'admin' && user.role !== 'owner')
  )
}

const removeUser = async userEmail => {
  try {
    await axios.delete(
      `/api/accounts/${authStore.account.id}/members/${userEmail}/`,
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      },
    )
    users.value = users.value.filter(user => user.user_email !== userEmail)
    alert('User removed successfully')
  } catch (error) {
    console.error('Failed to remove user:', error.message)
    alert('Failed to remove user')
  }
}

const editUser = user => {
  console.log('Edit user:', user)
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    fetchUsers()
  } else {
    console.error('User is not authenticated')
  }
})
</script>

<style scoped>
.btn-danger {
  @apply bg-red-500 text-white px-2 py-1 rounded hover:bg-red-700 transition duration-150;
}
.btn-secondary {
  @apply bg-gray-300 text-gray-700 px-2 py-1 rounded hover:bg-gray-400 transition duration-150;
}
</style>
