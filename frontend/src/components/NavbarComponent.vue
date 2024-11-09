<template>
  <nav class="flex items-center justify-between p-4 bg-blue-500">
    <!-- Logo and Navigation Links -->
    <div>
      <router-link class="font-bold text-xl text-white" to="/"
        >Inteqra</router-link
      >
      <router-link
        v-if="authStore.isAuthenticated"
        class="ml-4 text-white"
        to="/create-quiz"
        >Create Quiz</router-link
      >
    </div>

    <!-- Authentication Links and Account Dropdown -->
    <div>
      <template v-if="authStore.isAuthenticated">
        <div class="relative inline-block text-left">
          <button
            ref="displayUser"
            @click="toggleDropdown"
            class="focus:outline-none text-white"
          >
            {{ displayUser }}
          </button>

          <!-- Dropdown Menu -->
          <div
            v-if="showDropdown"
            class="absolute right-0 mt-2 w-48 bg-white [&>*]:text-gray-800 rounded-lg shadow-lg"
          >
            <router-link
              @click="closeDropdown"
              to="/profile"
              class="block px-4 py-2 hover:bg-gray-100"
              >My Profile</router-link
            >
            <router-link
              @click="closeDropdown"
              to="/account"
              class="block px-4 py-2 hover:bg-gray-100"
              >Account</router-link
            >
            <router-link
              @click="closeDropdown"
              to="/billing"
              class="block px-4 py-2 hover:bg-gray-100"
              >Billing</router-link
            >
            <router-link
              @click="closeDropdown"
              to="/users"
              class="block px-4 py-2 hover:bg-gray-100"
              >Users</router-link
            >
            <button
              @click="logout"
              class="w-full text-left block px-4 py-2 hover:bg-gray-100"
            >
              Logout
            </button>
          </div>
        </div>
      </template>
      <template v-else>
        <router-link class="ml-4" to="/auth">Login/Register</router-link>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '../store/auth'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const showDropdown = ref(false)

const displayUser = computed(() => {
  if (authStore.user?.first_name) {
    return authStore.user.first_name
  } else if (authStore.user?.email) {
    return authStore.user.email
  } else {
    return 'Account'
  }
})

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
}

const closeDropdown = () => {
  showDropdown.value = false
}

const logout = () => {
  authStore.logout(router)
  closeDropdown()
}
</script>

<style scoped></style>
