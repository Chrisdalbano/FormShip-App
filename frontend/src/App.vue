<template>
  <div id="app">
    <NavbarComponent />

    <main>
      <router-view />
    </main>
    <FooterComponent />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './store/auth'
import NavbarComponent from './components/NavbarComponent.vue'
import FooterComponent from './components/FooterComponent.vue'

const authStore = useAuthStore()

onMounted(() => {
  authStore.initializeAuth() // Restore authentication state on app load
})
</script>

<style scoped>
#app {
  @apply min-h-screen flex flex-col;
}

.app-header {
  @apply bg-blue-600 text-white p-4 flex justify-between items-center;
}

main {
  @apply flex-1 p-6 bg-gray-100;
}
</style>
