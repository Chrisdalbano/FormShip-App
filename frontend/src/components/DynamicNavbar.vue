<template>
  <nav class="flex items-center justify-between p-4 bg-blue-500">
    <!-- Logo -->
    <div class="flex items-center">
      <router-link class="font-bold text-xl text-white" to="/">
        FormShip
      </router-link>
    </div>

    <!-- Navigation Links -->
    <div class="flex items-center space-x-4">
      <!-- FormShip User Navigation -->
      <template v-if="authStore.isAuthenticated">
        <router-link class="text-white hover:text-blue-100" to="/create-quiz">
          Create Quiz
        </router-link>
        
        <!-- User Dropdown -->
        <div class="relative">
          <button
            @click="toggleDropdown"
            class="flex items-center text-white hover:text-blue-100"
          >
            {{ displayUser }}
            <span class="ml-1">▼</span>
          </button>

          <div
            v-if="showDropdown"
            class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg"
          >
            <router-link
              v-for="item in formshipMenuItems"
              :key="item.path"
              :to="item.path"
              class="block px-4 py-2 text-gray-800 hover:bg-gray-100"
              @click="closeDropdown"
            >
              {{ item.label }}
            </router-link>
            <button
              @click="handleFormshipLogout"
              class="w-full text-left block px-4 py-2 text-gray-800 hover:bg-gray-100"
            >
              Logout
            </button>
          </div>
        </div>
      </template>

      <!-- Participant Navigation -->
      <template v-else-if="quizStore.isAuthenticated">
        <router-link 
          to="/participant/portal" 
          class="text-white hover:text-blue-100"
        >
          My Quizzes
        </router-link>
        <router-link 
          to="/participant/profile" 
          class="text-white hover:text-blue-100"
        >
          Profile
        </router-link>
        <div class="flex items-center">
          <span class="text-white mr-4">
            {{ displayParticipantName }}
          </span>
          <button 
            @click="handleParticipantLogout"
            class="text-white hover:text-blue-100"
          >
            Logout
          </button>
        </div>
      </template>

      <!-- Guest Navigation -->
      <template v-else>
        <router-link class="text-white hover:text-blue-100" to="/auth">
          Login/Register
        </router-link>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useQuizStore } from '@/store/quiz'

const router = useRouter()
const authStore = useAuthStore()
const quizStore = useQuizStore()
const showDropdown = ref(false)

const formshipMenuItems = [
  { path: '/profile', label: 'My Profile' },
  { path: '/account', label: 'Account' },
  { path: '/billing', label: 'Billing' },
  { path: '/users', label: 'Users' }
]

const displayUser = computed(() => {
  if (authStore.user?.first_name) {
    return authStore.user.first_name
  } else if (authStore.user?.email) {
    return authStore.user.email
  }
  return 'Account'
})

const displayParticipantName = computed(() => {
  return quizStore.participant?.name || 'Guest'
})

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
}

const closeDropdown = () => {
  showDropdown.value = false
}

const handleFormshipLogout = () => {
  authStore.logout(router)
  closeDropdown()
}

const handleParticipantLogout = async () => {
  await quizStore.clearParticipantData()
  router.push('/participant/login')
}
</script> 