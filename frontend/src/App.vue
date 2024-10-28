<template>
  <div id="app">
    <header class="app-header">
      <h1 class="font-bold text-white text-3xl">Inteqra</h1>
      <NavbarComponent />
    </header>
    <main>
      <router-view />
    </main>
    <FooterComponent />
  </div>
</template>

<script setup>
import NavbarComponent from './components/NavbarComponent.vue'
import FooterComponent from './components/FooterComponent.vue'

// No additional script for the App component is needed
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
