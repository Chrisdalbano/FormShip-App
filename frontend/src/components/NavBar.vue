<template>
  <nav class="bg-gradient-to-r from-blue-600 to-blue-800 text-white shadow-lg">
    <div class="container mx-auto px-4">
      <div class="flex justify-between items-center h-16">
        <!-- Logo -->
        <router-link class="text-xl font-bold text-white hover:text-blue-200" to="/">
          InteQra
        </router-link>

        <!-- Navigation Links -->
        <div class="hidden md:flex items-center space-x-4">
          <template v-if="participantStore.isAuthenticated">
            <router-link 
              to="/participant/quizzes"
              class="text-white hover:text-blue-200 px-3 py-2 rounded-md text-sm font-medium"
            >
              My Quizzes
            </router-link>
          </template>
        </div>

        <!-- User Menu -->
        <div class="relative" v-if="participantStore.isAuthenticated">
          <button 
            @click="toggleDropdown" 
            class="flex items-center space-x-2 text-white hover:text-blue-200 focus:outline-none"
          >
            <span class="text-sm font-medium">{{ participantStore.participant?.name }}</span>
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          <!-- Dropdown Menu -->
          <div 
            v-show="isDropdownOpen"
            class="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5"
          >
            <div class="py-1">
              <router-link 
                to="/participant/profile"
                class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                @click="isDropdownOpen = false"
              >
                Profile Settings
              </router-link>
              <router-link 
                to="/participant/quizzes"
                class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                @click="isDropdownOpen = false"
              >
                My Quizzes
              </router-link>
              <button
                @click="handleLogout"
                class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100"
              >
                Logout
              </button>
            </div>
          </div>
        </div>

        <!-- Login/Register Links -->
        <div v-else class="flex items-center space-x-4">
          <router-link 
            to="/participant/login"
            class="text-white hover:text-blue-200 px-3 py-2 rounded-md text-sm font-medium"
          >
            Login
          </router-link>
          <router-link 
            to="/participant/register"
            class="bg-white text-blue-600 hover:bg-blue-50 px-4 py-2 rounded-md text-sm font-medium"
          >
            Register
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useParticipantStore } from '@/store/participant'
import { useRouter } from 'vue-router'

const participantStore = useParticipantStore()
const router = useRouter()
const isDropdownOpen = ref(false)

const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}

const handleLogout = () => {
  isDropdownOpen.value = false
  participantStore.clearParticipant()
  router.push('/participant/login')
}

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (isDropdownOpen.value && !event.target.closest('.relative')) {
    isDropdownOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.router-link-active {
  @apply bg-blue-700;
}
</style> 