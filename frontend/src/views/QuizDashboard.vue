<template>
  <div class="zen-container">
    <h1 class="text-3xl font-bold mb-4">Your Quiz Dashboard</h1>
    <p class="text-lg mb-6">
      Create a new quiz or manage your existing quizzes below.
    </p>

    <!-- Button to create a new quiz -->
    <button @click="navigateToCreateQuiz" class="create-quiz-btn mb-6">
      Create New Quiz
    </button>

    <!-- List of existing quizzes -->
    <div v-if="quizzes.length" class="quiz-list">
      <h2 class="text-2xl font-semibold mb-4">Your Quizzes:</h2>
      <ul>
        <li
          v-for="quiz in quizzes"
          :key="quiz.id"
          class="quiz-item flex flex-col gap-4 mb-6 p-4 bg-white rounded-lg shadow-md"
        >
          <div class="flex justify-between items-center">
            <div>
              <h3 class="font-semibold text-xl">{{ quiz.title }}</h3>
              <p class="text-sm text-gray-600">Topic: {{ quiz.topic }}</p>
            </div>
            <div class="flex gap-4">
              <button
                class="sub-quiz-button bg-green-500 text-white px-4 py-2 rounded hover:bg-green-700"
                @click="navigateToQuiz(quiz.id)"
              >
                Test Quiz
              </button>
              <button
                class="sub-quiz-button bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700"
                @click="shareQuiz(quiz.id)"
              >
                Share Quiz
              </button>
              <button
                class="sub-quiz-button bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-700"
                @click="duplicateQuiz(quiz.id)"
              >
                Duplicate
              </button>
              <button
                class="sub-quiz-button bg-red-500 text-white px-4 py-2 rounded hover:bg-red-700"
                @click="deleteQuiz(quiz.id)"
              >
                Delete
              </button>
              <button
                class="sub-quiz-button bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-700"
                @click="editQuiz(quiz.id)"
              >
                Edit
              </button>
            </div>
          </div>
        </li>
      </ul>
    </div>
    <p v-else class="text-gray-600 mt-6">
      No quizzes found. Start by creating a new one!
    </p>
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
  alert(
    `Shareable link for quiz ${quizId}: http://localhost:5173/quiz/${quizId}`,
  )
}

const duplicateQuiz = async quizId => {
  try {
    const response = await axios.post(
      `${apiBaseUrl}/quizzes/${quizId}/duplicate/`,
    )
    quizzes.value.push(response.data)
    alert('Quiz duplicated successfully!')
  } catch (error) {
    console.error('Error duplicating quiz:', error)
  }
}

const deleteQuiz = async quizId => {
  try {
    await axios.delete(`${apiBaseUrl}/quizzes/${quizId}/`)
    quizzes.value = quizzes.value.filter(quiz => quiz.id !== quizId)
    alert('Quiz deleted successfully!')
  } catch (error) {
    console.error('Error deleting quiz:', error)
    alert('Failed to delete quiz. Please try again.')
  }
}


const editQuiz = quizId => {
  // Navigate to the quiz editing page
  router.push({ name: 'EditQuiz', params: { id: quizId } })
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

.sub-quiz-button {
  @apply text-white px-4 py-2 rounded;
}
</style>
