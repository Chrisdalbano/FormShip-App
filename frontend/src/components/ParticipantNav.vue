<template>
  <nav class="bg-white shadow">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex">
          <div class="flex-shrink-0 flex items-center">
            <router-link to="/" class="text-xl font-bold text-blue-600">
              FormShip
            </router-link>
          </div>
        </div>
        
        <div class="flex items-center">
          <router-link 
            to="/participant/portal" 
            class="text-gray-600 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
          >
            My Portal
          </router-link>
          <button 
            @click="logout" 
            class="text-gray-600 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useParticipantStore } from '../store/participant'

const router = useRouter()
const participantStore = useParticipantStore()

const logout = () => {
  participantStore.clearParticipant()
  router.push('/participant/login')
}
</script> 