<template>
  <nav>
    <router-link v-if="isAuthenticated" to="/">Dashboard</router-link>
    <router-link v-if="isAuthenticated" to="/create-quiz"
      >Create Quiz</router-link
    >
    <button v-if="isAuthenticated" @click="logout">Logout</button>
    <router-link v-else to="/auth">Login/Register</router-link>
  </nav>
</template>

<script>
export default {
  computed: {
    isAuthenticated() {
      return !!localStorage.getItem('jwt')
    },
  },
  methods: {
    logout() {
      localStorage.removeItem('jwt')
      this.$router.push({ name: 'Auth' })
    },
  },
}
</script>

<style scoped>
nav a {
  @apply ml-4 text-white hover:text-blue-200;
}
</style>
