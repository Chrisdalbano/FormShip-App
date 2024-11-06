<template>
  <div
    class="auth-container max-w-lg mx-auto mt-12 p-6 bg-white rounded-lg shadow-lg"
  >
    <div v-if="isLogin">
      <LoginComponent @login-success="handleLoginSuccess" />
      <p class="text-center mt-4">
        Don't have an account?
        <button @click="toggleAuthMode" class="text-blue-500 hover:underline">
          Register
        </button>
      </p>
    </div>
    <div v-else>
      <RegisterComponent @register-success="handleRegisterSuccess" />
      <p class="text-center mt-4">
        Already have an account?
        <button @click="toggleAuthMode" class="text-blue-500 hover:underline">
          Login
        </button>
      </p>
    </div>
  </div>
</template>

<script>
import LoginComponent from '../components/LoginComponent.vue'
import RegisterComponent from '../components/RegisterComponent.vue'
import { useRouter } from 'vue-router'

export default {
  components: { LoginComponent, RegisterComponent },
  data() {
    return {
      isLogin: true,
    }
  },
  setup() {
    const router = useRouter()

    const handleLoginSuccess = () => {
      router.push({ name: 'QuizDashboard' })
    }

    const handleRegisterSuccess = () => {
      router.push({ name: 'QuizDashboard' })
    }

    return { handleLoginSuccess, handleRegisterSuccess }
  },
  methods: {
    toggleAuthMode() {
      this.isLogin = !this.isLogin
    },
  },
}
</script>

<style scoped>
.auth-container {
  @apply max-w-md mx-auto mt-12 p-4 bg-white shadow-md rounded-lg;
}
</style>
