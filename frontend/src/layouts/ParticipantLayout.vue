<template>
  <div class="min-h-screen flex flex-col">
    <!-- Participant Navigation -->
    <nav class="bg-blue-600 text-white">
      <div class="max-w-7xl mx-auto px-4 py-3">
        <div class="flex justify-between items-center">
          <router-link to="/participant/portal" class="text-xl font-bold">
            FormShip Participant
          </router-link>
          <div class="flex items-center space-x-4">
            <router-link 
              to="/participant/portal" 
              class="hover:text-blue-200"
            >
              My Quizzes
            </router-link>
            <button 
              @click="logout" 
              class="hover:text-blue-200"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="flex-grow">
      <slot />
    </main>

    <!-- Participant Footer -->
    <footer class="bg-gray-100 border-t">
      <div class="max-w-7xl mx-auto px-4 py-6">
        <div class="flex justify-between items-center">
          <div class="text-sm text-gray-600">
            © {{ new Date().getFullYear() }} FormShip
          </div>
          <div class="flex items-center space-x-6">
            <a 
              href="https://formship.com/help" 
              class="text-sm text-gray-600 hover:text-blue-600"
            >
              Help Center
            </a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useParticipantStore } from '@/store/participant'

const router = useRouter()
const participantStore = useParticipantStore()

const logout = () => {
  participantStore.clearParticipant()
  router.push('/participant/login')
}
</script> 