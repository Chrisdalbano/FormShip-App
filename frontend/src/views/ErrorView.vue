<template>
  <div class="error-container p-6 max-w-lg mx-auto text-center">
    <h1 class="text-2xl font-bold text-red-600 mb-4">Error</h1>
    <p class="text-gray-700 mb-4">{{ message || 'Something went wrong' }}</p>
    <button @click="goBack" class="btn btn-primary">Go Back</button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { defineProps } from 'vue'

defineProps({
  message: String,
})

const router = useRouter()

const goBack = () => {
  router.back()
}
</script>
