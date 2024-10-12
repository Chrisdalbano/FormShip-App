<template>
  <div
    class="create-quiz-container w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg"
  >
    <h1 class="text-3xl font-bold mb-4">Create a New Quiz</h1>
    <form @submit.prevent="createQuiz">
      <div class="mb-4">
        <label for="title" class="block text-lg font-semibold mb-2"
          >Quiz Title</label
        >
        <input
          v-model="quizTitle"
          type="text"
          id="title"
          class="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300"
          required
        />
      </div>
      <div class="mb-4">
        <label for="topic" class="block text-lg font-semibold mb-2"
          >Topic</label
        >
        <input
          v-model="quizTopic"
          type="text"
          id="topic"
          class="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300"
          required
        />
      </div>
      <div class="mb-4">
        <label for="questionCount" class="block text-lg font-semibold mb-2"
          >Number of Questions</label
        >
        <input
          type="number"
          v-model="questionCount"
          min="2"
          max="5"
          id="questionCount"
          class="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300"
          required
        />
      </div>
      <div class="mb-4">
        <label for="optionCount" class="block text-lg font-semibold mb-2"
          >Number of Options per Question</label
        >
        <input
          type="number"
          v-model="optionCount"
          min="2"
          max="5"
          id="optionCount"
          class="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300"
          required
        />
      </div>
      <button
        type="submit"
        class="bg-blue-500 text-white px-6 py-3 rounded hover:bg-blue-700 w-full font-semibold mb-6"
      >
        Generate Quiz
      </button>
    </form>

    <div v-if="questions.length" class="generated-questions mt-6">
      <h2 class="text-2xl font-bold mb-4">Generated Questions</h2>
      <div v-for="(question, index) in questions" :key="index" class="mb-6">
        <h3 class="text-xl font-semibold mb-2">Question {{ index + 1 }}</h3>
        <p class="mb-4"><strong>Question Text:</strong> {{ question.question_text }}</p>
        <ul class="mb-4">
          <li v-if="question.option_a"><strong>A:</strong> {{ question.option_a }}</li>
          <li v-if="question.option_b"><strong>B:</strong> {{ question.option_b }}</li>
          <li v-if="question.option_c"><strong>C:</strong> {{ question.option_c }}</li>
          <li v-if="question.option_d"><strong>D:</strong> {{ question.option_d }}</li>
          <li v-if="question.option_e"><strong>E:</strong> {{ question.option_e }}</li>
        </ul>
        <p><strong>Correct Answer:</strong> {{ question.correct_answer }}</p>
      </div>
      <button
        @click="goToEditPage"
        type="button"
        class="bg-green-500 text-white px-6 py-3 rounded hover:bg-green-700 w-full font-semibold"
      >
        Edit Quiz
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const quizTitle = ref('')
const quizTopic = ref('')
const questionCount = ref(2) // Default to 2 questions
const optionCount = ref(2) // Default to 2 options per question
const questions = ref([])
let createdQuizId = null // Store the created quiz ID

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

// Function to create quiz and request AI-generated questions
const createQuiz = async () => {
  try {
    const response = await axios.post(`${apiBaseUrl}/create-quiz/`, {
      title: quizTitle.value,
      topic: quizTopic.value,
      question_count: questionCount.value,
      option_count: optionCount.value,
      difficulty: 'medium', // You can add a difficulty selection if needed
    })

    // Assign generated questions to the questions array
    questions.value = response.data.questions
    createdQuizId = response.data.id // Store the created quiz ID
    alert('Quiz generated successfully! Please review the questions below.')
  } catch (error) {
    console.error('Error generating quiz:', error)
    alert('Failed to generate quiz. Please try again.')
  }
}

// Function to navigate to the edit page for the created quiz
const goToEditPage = () => {
  if (createdQuizId) {
    router.push({ name: 'EditQuiz', params: { id: createdQuizId } })
  } else {
    alert('No quiz has been created yet.')
  }
}
</script>

<style scoped>
.create-quiz-container {
  @apply mt-10;
}
</style>