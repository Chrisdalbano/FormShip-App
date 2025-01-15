<template>
  <div class="users-container">
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
          class="input-field p-1 rounded"
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
            :key="user.user_id"
            class="border-b"
          >
            <td class="px-4 py-2">{{ user.user_name || 'N/A' }}</td>

            <td class="px-4 py-2">{{ user.user_email || 'N/A' }}</td>
            <td class="px-4 py-2">{{ user.role }}</td>
            <td class="px-4 py-2">
              {{
                user.last_connected
                  ? new Date(user.last_connected).toLocaleString()
                  : 'Never'
              }}
            </td>
            <td class="px-4 py-2">
              <button @click="openEditModal(user)" class="btn-secondary">
                Edit
              </button>
              <button @click="deleteUser(user)" class="btn-danger">
                Remove
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add User Modal -->
    <Modal v-if="showAddUserModal" @close="showAddUserModal = false">
      <h3 class="text-xl font-semibold mb-4">Create New User</h3>
      <form @submit.prevent="createUser">
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
          <label class="block text-gray-700">Password</label>
          <input
            v-model="newUserPassword"
            class="input-field"
            type="password"
            placeholder="Set password"
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
        <div class="mb-4 flex items-center">
          <input
            type="checkbox"
            id="send-invitation"
            v-model="sendInvitation"
            class="mr-2"
          />
          <label for="send-invitation" class="text-gray-700">
            Send Invitation Email
          </label>
        </div>
        <button type="submit" class="btn-primary" :disabled="addingUser">
          <span v-if="addingUser" class="loader mr-2"></span> Create User
        </button>
      </form>
    </Modal>

    <!-- Edit User Modal -->
    <EditUserModal
      v-if="showEditUserModal"
      :visible="showEditUserModal"
      :user="selectedUser"
      @close="closeEditModal"
      @update="updateUser"
      @delete="deleteUser"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../store/auth'
import Modal from '../components/EditPopModal.vue'
import EditUserModal from '../components/EditUserModal.vue'

const authStore = useAuthStore()
const loading = ref(true)
const searchQuery = ref('')
const users = ref([])
const showAddUserModal = ref(false)
const showEditUserModal = ref(false)
const selectedUser = ref(null)

const newUserEmail = ref('')
const newUserPassword = ref('')
const newUserRole = ref('member')
const sendInvitation = ref(false)
const addingUser = ref(false)

const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await axios.get(
      `/api/accounts/${authStore.account.id}/members/`,
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      },
    )
    console.log('Fetched users:', response.data) // Debug log
    users.value = Array.isArray(response.data) ? response.data : []
  } catch (error) {
    console.error(
      'Failed to load users:',
      error.response?.data || error.message,
    )
    users.value = []
  } finally {
    loading.value = false
  }
}

const createUser = async () => {
  try {
    addingUser.value = true
    const newUserData = {
      email: newUserEmail.value,
      password: newUserPassword.value,
      role: newUserRole.value,
      send_invitation: sendInvitation.value,
    }
    await axios.post(
      `/api/accounts/${authStore.account.id}/create-user/`,
      newUserData,
      { headers: { Authorization: `Bearer ${authStore.token}` } },
    )
    alert('User created successfully')
    fetchUsers()
    showAddUserModal.value = false
    newUserEmail.value = ''
    newUserPassword.value = ''
    newUserRole.value = 'member'
    sendInvitation.value = false
  } catch (error) {
    console.error(
      'Failed to create user:',
      error.response?.data || error.message,
    )
    alert('Failed to create user')
  } finally {
    addingUser.value = false
  }
}

const deleteUser = async user => {
  console.log('Deleting user:', user)
  console.log('Account ID:', authStore.account.id)

  if (confirm(`Are you sure you want to remove ${user.user_email}?`)) {
    try {
      await axios.delete(
        `/api/accounts/${authStore.account.id}/users/${user.user_id}/`,
        { headers: { Authorization: `Bearer ${authStore.token}` } },
      )
      alert('User removed successfully')
      fetchUsers()
    } catch (error) {
      console.error(
        'Failed to remove user:',
        error.response?.data || error.message,
      )
      alert(
        `Failed to remove user: ${error.response?.data?.error || error.message}`,
      )
    }
  }
}

const updateUser = async updatedUser => {
  try {
    await axios.patch(
      `/api/accounts/${authStore.account.id}/users/${updatedUser.user_id}/`,
      {
        role: updatedUser.role,
        first_name: updatedUser.first_name,
        last_name: updatedUser.last_name,
        user_email: updatedUser.user_email,
      },
      { headers: { Authorization: `Bearer ${authStore.token}` } },
    )
    alert('User updated successfully')
    fetchUsers()
    closeEditModal()
  } catch (error) {
    console.error(
      'Failed to update user:',
      error.response?.data || error.message,
    )
    alert('Failed to update user. Please check if the user ID is valid.')
  }
}

const openEditModal = user => {
  console.log('User object:', user)

  selectedUser.value = {
    first_name:
      user.first_name ||
      (user.user_name ? user.user_name.split(' ')[0] : 'N/A'),
    last_name:
      user.last_name || (user.user_name ? user.user_name.split(' ')[1] : 'N/A'),
    user_email: user.user_email || '',
    role: user.role || 'member',
    user_id: user.user_id,
  }
  showEditUserModal.value = true
}

const closeEditModal = () => {
  showEditUserModal.value = false
  selectedUser.value = null
}

const filteredUsers = computed(() =>
  users.value.filter(user =>
    (user.user_email || '')
      .toLowerCase()
      .includes(searchQuery.value.toLowerCase()),
  ),
)

onMounted(fetchUsers)
</script>

<style scoped>
.btn-danger {
  @apply bg-red-500 text-white px-2 py-1 rounded hover:bg-red-700 transition duration-150;
}
.btn-secondary {
  @apply bg-gray-300 text-gray-700 px-2 py-1 rounded hover:bg-gray-400 transition duration-150;
}
</style>
