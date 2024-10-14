<template>
  <div
    class="create-quiz-container w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg"
  >
    <h1 class="text-3xl font-bold mb-4">Create a New Quiz</h1>
    <form @submit.prevent="createQuiz">
      <!-- Quiz Information Inputs -->
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
      <!-- Timer Options -->
      <div class="mb-4">
        <label for="isTimed" class="block text-lg font-semibold mb-2"
          >Set Time Limit for Quiz?</label
        >
        <input type="checkbox" v-model="isTimed" id="isTimed" />
        <div v-if="isTimed" class="mt-4">
          <label for="quizTimeLimit" class="block text-lg font-semibold mb-2"
            >Total Time Limit for Quiz (in minutes)</label
          >
          <input
            type="number"
            v-model="quizTimeLimit"
            min="1"
            id="quizTimeLimit"
            class="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300"
          />
        </div>
      </div>
      <div class="mb-4">
        <label for="timePerQuestion" class="block text-lg font-semibold mb-2"
          >Set Time Limit for Each Question (in seconds)</label
        >
        <input type="checkbox" v-model="timePerQuestion" id="timePerQuestion" />
        <div v-if="timePerQuestion" class="mt-4">
          <label
            for="questionTimeLimit"
            class="block text-lg font-semibold mb-2"
            >Time Limit per Question (in seconds)</label
          >
          <input
            type="number"
            v-model="questionTimeLimit"
            min="5"
            id="questionTimeLimit"
            class="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300"
          />
        </div>
      </div>
      <!-- Sharing Customization Options -->
      <div class="mb-4">
        <label for="displayResults" class="block text-lg font-semibold mb-2"
          >Display Results After Quiz?</label
        >
        <input type="checkbox" v-model="displayResults" id="displayResults" />
      </div>
      <div class="mb-4">
        <label for="requirePassword" class="block text-lg font-semibold mb-2"
          >Require Password to Access Quiz?</label
        >
        <input type="checkbox" v-model="requirePassword" id="requirePassword" />
        <input
          v-if="requirePassword"
          type="password"
          v-model="password"
          class="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300 mt-2"
          placeholder="Enter password"
        />
      </div>
      <div class="mb-4">
        <label for="allowAnonymous" class="block text-lg font-semibold mb-2"
          >Allow Anonymous Users?</label
        >
        <input type="checkbox" v-model="allowAnonymous" id="allowAnonymous" />
      </div>
      <div class="mb-4">
        <label for="requireName" class="block text-lg font-semibold mb-2"
          >Require Name/Nickname?</label
        >
        <input type="checkbox" v-model="requireName" id="requireName" />
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
const useKnowledgeBase = ref(false)
const knowledgeBaseText = ref('')
const questions = ref([])
let createdQuizId = null
const loading = ref(false)

const displayResults = ref(true)
const requirePassword = ref(false)
const password = ref('')
const allowAnonymous = ref(false)
const requireName = ref(false)
const isTimed = ref(false)
const quizTimeLimit = ref(null)
const timePerQuestion = ref(false)
const questionTimeLimit = ref(null)

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

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

const createQuiz = async () => {
  loading.value = true
  try {
    const requestData = {
      title: quizTitle.value,
      topic: quizTopic.value,
      question_count: questionCount.value,
      option_count: optionCount.value,
      difficulty: 'medium',
      display_results: displayResults.value,
      require_password: requirePassword.value,
      password: requirePassword.value ? password.value : null,
      allow_anonymous: allowAnonymous.value,
      require_name: requireName.value,
      is_timed: isTimed.value,
      quiz_time_limit: isTimed.value ? quizTimeLimit.value : null,
      time_per_question: timePerQuestion.value,
      question_time_limit: timePerQuestion.value
        ? questionTimeLimit.value
        : null,
    }

    if (useKnowledgeBase.value) {
      requestData.knowledge_base = knowledgeBaseText.value
    }

    const response = await axios.post(
      `${apiBaseUrl}/quizzes/create/`,
      requestData,
    )

    // Check if the response contains the quiz ID
    if (response.data.id) {
      createdQuizId = response.data.id
      questions.value = response.data.questions || []
      alert('Quiz generated successfully! Please review the questions below.')
    } else {
      throw new Error('Quiz ID not returned from backend.')
    }
  } catch (error) {
    console.error('Error generating quiz:', error)
    alert('Failed to generate quiz. Please try again.')
    questions.value = [] // Set to an empty array if quiz creation fails
  } finally {
    loading.value = false
  }
}

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
