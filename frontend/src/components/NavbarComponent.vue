<template>
  <nav>
    <router-link to="/">Dashboard</router-link>
    <router-link to="/create-quiz">Create Quiz</router-link>
  </nav>
</template>
<style scoped>
nav a {
  @apply ml-4 text-white hover:text-blue-200;
}
</style>
