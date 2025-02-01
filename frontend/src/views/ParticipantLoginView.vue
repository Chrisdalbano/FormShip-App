<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <h2 class="text-center text-3xl font-extrabold text-gray-900">
        Participant Portal
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        Access your quiz history and results
      </p>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
        <ParticipantAuth 
          :quiz="null"
          @auth-success="handleAuthSuccess"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import ParticipantAuth from '@/components/ParticipantAuth.vue'

const router = useRouter()

const handleAuthSuccess = () => {
  router.push({ name: 'ParticipantPortal' })
}
</script> 