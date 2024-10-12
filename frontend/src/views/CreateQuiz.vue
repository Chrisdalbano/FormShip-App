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
      <div class="mb-4">
        <label for="useKnowledgeBase" class="block text-lg font-semibold mb-2"
          >Use Your Own Knowledge Base?</label
        >
        <input
          type="checkbox"
          v-model="useKnowledgeBase"
          id="useKnowledgeBase"
          class="mr-2"
        />
        <span>Yes, use my provided information to generate the quiz.</span>
      </div>
      <div v-if="useKnowledgeBase" class="mb-4">
        <label for="knowledgeBaseInput" class="block text-lg font-semibold mb-2"
          >Knowledge Base Input (Text or Upload File)</label
        >
        <textarea
          v-model="knowledgeBaseText"
          id="knowledgeBaseInput"
          class="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300 mb-4"
          rows="5"
          placeholder="You can paste your knowledge base text here..."
        ></textarea>
        <input
          type="file"
          @change="handleFileUpload"
          class="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300"
        />
      </div>
      <button
        type="submit"
        class="bg-blue-500 text-white px-6 py-3 rounded hover:bg-blue-700 w-full font-semibold mb-6"
      >
        Generate Quiz
      </button>
    </form>

    <!-- Loading spinner -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Generating your quiz, please wait...</p>
    </div>

    <div v-if="questions.length" class="generated-questions mt-6">
      <h2 class="text-2xl font-bold mb-4">Generated Questions</h2>
      <div v-for="(question, index) in questions" :key="index" class="mb-6">
        <h3 class="text-xl font-semibold mb-2">Question {{ index + 1 }}</h3>
        <p class="mb-4">
          <strong>Question Text:</strong> {{ question.question_text }}
        </p>
        <ul class="mb-4">
          <li v-if="question.option_a">
            <strong>A:</strong> {{ question.option_a }}
          </li>
          <li v-if="question.option_b">
            <strong>B:</strong> {{ question.option_b }}
          </li>
          <li v-if="question.option_c">
            <strong>C:</strong> {{ question.option_c }}
          </li>
          <li v-if="question.option_d">
            <strong>D:</strong> {{ question.option_d }}
          </li>
          <li v-if="question.option_e">
            <strong>E:</strong> {{ question.option_e }}
          </li>
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
const useKnowledgeBase = ref(false) // Toggle for using custom knowledge base
const knowledgeBaseText = ref('')
const questions = ref([])
let createdQuizId = null // Store the created quiz ID
const loading = ref(false) // Loading state for animation

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

// Handle file upload for knowledge base
const handleFileUpload = event => {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = e => {
      knowledgeBaseText.value = e.target.result
    }
    reader.readAsText(file)
  }
}

// Function to create quiz and request AI-generated questions
const createQuiz = async () => {
  loading.value = true // Start loading
  try {
    const requestData = {
      title: quizTitle.value,
      topic: quizTopic.value,
      question_count: questionCount.value,
      option_count: optionCount.value,
      difficulty: 'medium', // You can add a difficulty selection if needed
    }

    // If the user wants to use their own knowledge base, include it in the request
    if (useKnowledgeBase.value) {
      if (knowledgeBaseText.value.length > 5000) {
        // Split into chunks if too long
        const chunks = splitTextIntoChunks(knowledgeBaseText.value, 4000)
        requestData.knowledge_base_chunks = chunks
      } else {
        requestData.knowledge_base = knowledgeBaseText.value
      }
    }

    const response = await axios.post(`${apiBaseUrl}/create-quiz/`, requestData)

    // Assign generated questions to the questions array
    questions.value = response.data.questions
    createdQuizId = response.data.id // Store the created quiz ID
    alert('Quiz generated successfully! Please review the questions below.')
  } catch (error) {
    console.error('Error generating quiz:', error)
    alert('Failed to generate quiz. Please try again.')
  } finally {
    loading.value = false // Stop loading
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

// Helper function to split large text into smaller chunks
const splitTextIntoChunks = (text, maxLength) => {
  const chunks = []
  let currentIndex = 0
  while (currentIndex < text.length) {
    const chunk = text.slice(currentIndex, currentIndex + maxLength)
    chunks.push(chunk)
    currentIndex += maxLength
  }
  return chunks
}
</script>

<style scoped>
.create-quiz-container {
  @apply mt-10;
}

.loading-container {
  text-align: center;
  margin-top: 20px;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border-left-color: #09f;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
