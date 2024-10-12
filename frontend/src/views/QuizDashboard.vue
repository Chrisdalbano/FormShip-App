<template>
  <div class="zen-container">
    <h1>Your Quiz Dashboard</h1>
    <p>Create a new quiz or view your existing quizzes below.</p>

    <!-- Button to create a new quiz -->
    <button @click="navigateToCreateQuiz" class="create-quiz-btn">
      Create New Quiz
    </button>

    <!-- List of existing quizzes -->
    <div v-if="quizzes.length" class="quiz-list">
      <h2>Your Quizzes:</h2>
      <ul>
        <li v-for="quiz in quizzes" :key="quiz.id" class="quiz-item">
          <h3>{{ quiz.title }}</h3>
          <p>Topic: {{ quiz.topic }}</p>
          <button @click="navigateToQuiz(quiz.id)">Test Quiz</button>
          <button @click="shareQuiz(quiz.id)">Share Quiz</button>
        </li>
      </ul>
    </div>
    <p v-else>No quizzes found. Start by creating a new one!</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const quizzes = ref([])

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

// Fetch quizzes when the component is mounted
onMounted(async () => {
  try {
    const response = await axios.get(`${apiBaseUrl}/quizzes/`)
    quizzes.value = response.data
  } catch (error) {
    console.error('Error fetching quizzes:', error)
  }
})

const navigateToCreateQuiz = () => {
  router.push({ name: 'CreateQuiz' })
}

const navigateToQuiz = quizId => {
  router.push({ name: 'TestQuiz', params: { id: quizId } })
}

const shareQuiz = quizId => {
  // Logic for sharing the quiz link
  alert(
    `Shareable link for quiz ${quizId}: http://localhost:5173/quiz/${quizId}`,
  )
}
</script>

<style scoped>
.create-quiz-btn {
  @apply bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700;
}

.quiz-list {
  margin-top: 2rem;
}

.quiz-item {
  @apply bg-gray-100 p-4 rounded shadow my-4;
}
</style>
