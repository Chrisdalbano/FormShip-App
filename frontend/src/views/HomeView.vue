<template>
  <div class="zen-container">
    <h1>Welcome to the Zen-Like Webapp</h1>
    <p>This is the home page of our minimalistic webapp.</p>
    <button class="bg-red-500 p-1 border rounded" @click="fetchMessage">Fetch Welcome Message</button>
    <p v-if="apiMessage">{{ apiMessage }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const apiMessage = ref(null)

const fetchMessage = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/welcome/')
    apiMessage.value = response.data.message
  } catch (error) {
    console.error('Error fetching the API message:', error)
  }
}
</script>
