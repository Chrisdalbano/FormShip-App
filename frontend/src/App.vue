<template>
  <div id="app">
    <header class="app-header">
      <h1 class="font-bold text-white text-3xl">Inteqra</h1>
      <nav>
        <router-link to="/">Dashboard</router-link>
        <router-link to="/create-quiz">Create Quiz</router-link>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
    <footer class="app-footer">
      <p>Made by <a href="https://chrisdalbano.com" target="_blank" class="text-white">Chrisdalbano</a></p>
    </footer>
  </div>
</template>

<script setup>
// No additional script for the App component is needed
</script>

<style scoped>
#app {
  @apply min-h-screen flex flex-col;
}

.app-header {
  @apply bg-blue-600 text-white p-4 flex justify-between items-center;
}

nav a {
  @apply ml-4 text-white hover:text-blue-200;
}

main {
  @apply flex-1 p-6 bg-gray-100;
}

.app-footer {
  @apply bg-blue-600 text-white p-4 text-center;
}
</style>
