<template>
  <div v-if="loading" class="text-center mt-8 text-gray-600">Loading...</div>
  <div v-else class="max-w-lg mx-auto mt-8 p-6 bg-white rounded-lg shadow-lg">
    <h2 class="text-2xl font-semibold mb-6 text-center">My Profile</h2>

    <form @submit.prevent="updateProfile">
      <div class="mb-4">
        <label class="block text-gray-700">First Name</label>
        <input
          v-model="first_name"
          class="input-field"
          type="text"
          placeholder="Not provided yet"
          required
        />
      </div>

      <div class="mb-4">
        <label class="block text-gray-700">Last Name</label>
        <input
          v-model="last_name"
          class="input-field"
          type="text"
          placeholder="Not provided yet"
          required
        />
      </div>

      <div class="mb-4">
        <label class="block text-gray-700">Email</label>
        <div class="flex items-center">
          <input v-model="email" class="input-field" type="email" readonly />
          <button
            @click="openEmailModal"
            type="button"
            class="btn-secondary ml-2"
            :disabled="emailUpdating"
          >
            Change
          </button>
        </div>
      </div>

      <div class="mb-4">
        <label class="block text-gray-700">Password</label>
        <div class="flex items-center">
          <input
            class="input-field"
            type="password"
            placeholder="********"
            readonly
          />
          <button
            @click="openPasswordModal"
            type="button"
            class="btn-secondary ml-2"
            :disabled="passwordUpdating"
          >
            Change
          </button>
        </div>
      </div>

      <div class="mb-4">
        <label class="block text-gray-700">Organization Type</label>
        <select v-model="organization_type" class="input-field">
          <option value="" disabled>Select your organization type</option>
          <option value="ecommerce">eCommerce</option>
          <option value="education">Education</option>
          <option value="medical">Medical</option>
        </select>
      </div>

      <button type="submit" class="btn-primary" :disabled="isSaving">
        <span v-if="isSaving" class="loader mr-2"></span> Save Changes
      </button>
    </form>

    <!-- Email Change Modal -->
    <Modal v-if="showEmailModal" @close="closeEmailModal">
      <h3 class="text-xl font-semibold mb-4">Update Email</h3>
      <form @submit.prevent="updateEmail">
        <div class="mb-4">
          <label class="block text-gray-700">New Email</label>
          <input v-model="newEmail" class="input-field" type="email" required />
        </div>
        <div class="mb-4">
          <label class="block text-gray-700">Current Password</label>
          <input
            v-model="currentPassword"
            class="input-field"
            type="password"
            required
          />
        </div>
        <button type="submit" class="btn-primary" :disabled="emailUpdating">
          <span v-if="emailUpdating" class="loader mr-2"></span> Update Email
        </button>
      </form>
    </Modal>

    <!-- Password Change Modal -->
    <Modal v-if="showPasswordModal" @close="closePasswordModal">
      <h3 class="text-xl font-semibold mb-4">Update Password</h3>
      <form @submit.prevent="updatePassword">
        <div class="mb-4">
          <label class="block text-gray-700">New Password</label>
          <input
            v-model="newPassword"
            class="input-field"
            type="password"
            required
          />
        </div>
        <div class="mb-4">
          <label class="block text-gray-700">Confirm New Password</label>
          <input
            v-model="confirmNewPassword"
            class="input-field"
            type="password"
            required
          />
        </div>
        <p v-if="passwordMismatch" class="text-red-500 text-sm mt-2">
          Passwords do not match
        </p>
        <button
          type="submit"
          class="btn-primary"
          :disabled="passwordUpdating || passwordMismatch"
        >
          <span v-if="passwordUpdating" class="loader mr-2"></span> Update
          Password
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
const email = ref('')
const first_name = ref('')
const last_name = ref('')
const organization_type = ref('')
const newEmail = ref('')
const currentPassword = ref('')
const newPassword = ref('')
const confirmNewPassword = ref('')
const showEmailModal = ref(false)
const showPasswordModal = ref(false)
const emailUpdating = ref(false)
const passwordUpdating = ref(false)
const isSaving = ref(false)
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

const passwordMismatch = computed(
  () =>
    newPassword.value &&
    confirmNewPassword.value &&
    newPassword.value !== confirmNewPassword.value,
)

const fetchUserProfile = async () => {
  try {
    loading.value = true
    const response = await axios.get(`${apiBaseUrl}/user/profile/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    const userData = response.data
    email.value = userData.email || ''
    first_name.value = userData.first_name || ''
    last_name.value = userData.last_name || ''
    organization_type.value = userData.organization_type || ''
  } catch (error) {
    console.error('Failed to fetch user profile:', error)
  } finally {
    loading.value = false
  }
}

const updateProfile = async () => {
  try {
    isSaving.value = true
    await axios.put(
      `${apiBaseUrl}/users/me/`, // Make sure this matches your updated route
      {
        first_name: first_name.value,
        last_name: last_name.value,
        organization_type: organization_type.value,
      },
      { headers: { Authorization: `Bearer ${authStore.token}` } },
    )
    alert('Profile updated successfully')
  } catch (error) {
    console.error('Failed to update profile:', error)
    alert('Failed to update profile')
  } finally {
    isSaving.value = false
  }
}

const openEmailModal = () => (showEmailModal.value = true)
const closeEmailModal = () => (showEmailModal.value = false)
const openPasswordModal = () => (showPasswordModal.value = true)
const closePasswordModal = () => (showPasswordModal.value = false)

const updateEmail = async () => {
  try {
    emailUpdating.value = true
    await axios.put(
      `${apiBaseUrl}/users/change-email/`,
      {
        new_email: newEmail.value,
        current_password: currentPassword.value,
      },
      { headers: { Authorization: `Bearer ${authStore.token}` } },
    )
    email.value = newEmail.value
    alert('Email updated successfully')
    closeEmailModal()
  } catch (error) {
    console.error('Failed to update email:', error)
    alert('Failed to update email')
  } finally {
    emailUpdating.value = false
  }
}

const updatePassword = async () => {
  try {
    passwordUpdating.value = true
    await axios.put(
      `${apiBaseUrl}/users/change-password/`,
      {
        new_password: newPassword.value,
        confirm_new_password: confirmNewPassword.value,
      },
      { headers: { Authorization: `Bearer ${authStore.token}` } },
    )
    alert('Password updated successfully')
    closePasswordModal()
  } catch (error) {
    console.error('Failed to update password:', error)
    alert('Failed to update password')
  } finally {
    passwordUpdating.value = false
  }
}

onMounted(() => fetchUserProfile())
</script>

<style scoped>
.input-field {
  @apply w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-150;
}
.btn-primary {
  @apply w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-md transition duration-150;
}
.btn-secondary {
  @apply bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400 transition duration-150;
}
.loader {
  border: 2px solid #f3f3f3;
  border-top: 2px solid #3498db;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  animation: spin 0.6s linear infinite;
}
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
