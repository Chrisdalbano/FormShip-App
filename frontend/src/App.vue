<template>
  <div class="app min-h-screen flex flex-col">
    <DynamicNavbar />
    <main class="flex-grow">
      <router-view></router-view>
    </main>
    <FooterComponent />
  </div>
</template>

<script setup>
import DynamicNavbar from './components/DynamicNavbar.vue'
import FooterComponent from './components/FooterComponent.vue'
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
