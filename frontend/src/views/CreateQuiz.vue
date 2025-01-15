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
          v-model="quiz.title"
          type="text"
          id="title"
          placeholder="Name your quiz"
          class="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300"
          required
        />
      </div>
      <div class="mb-4">
        <label for="topic" class="block text-lg font-semibold mb-2"
          >About the quiz</label
        >
        <input
          v-model="quiz.topic"
          type="text"
          id="topic"
          placeholder="Provide details about the quiz for faster generation (AI)"
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
          v-model="quiz.question_count"
          min="2"
          max="5"
          id="questionCount"
          class="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300"
          required
        />
      </div>
      <div class="mb-4">
        <label for="optionCount" class="block text-lg font-semibold mb-2"
          >Number of Answer Options per Question</label
        >
        <input
          type="number"
          v-model="quiz.option_count"
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
          v-model="quiz.use_knowledge_base"
          id="useKnowledgeBase"
          class="mr-2"
        />
        <span>Yes, use my provided information to generate the quiz.</span>
      </div>
      <div v-if="quiz.use_knowledge_base" class="mb-4">
        <label for="knowledgeBaseInput" class="block text-lg font-semibold mb-2"
          >Knowledge Base Input (Text or Upload File)</label
        >
        <textarea
          v-model="quiz.knowledge_base_text"
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
      <!-- Quiz Type Selection -->
      <div class="mb-4">
        <label for="quizType" class="block text-lg font-semibold mb-2"
          >Select Quiz Type</label
        >
        <select
          v-model="quiz.quiz_type"
          id="quizType"
          class="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300"
        >
          <option value="standard">
            Standard Quiz (All Questions at Once)
          </option>
          <option value="stepwise">
            Stepwise Quiz (One Question at a Time)
          </option>
        </select>
      </div>
      <!-- Stepwise Quiz Options -->
      <div v-if="quiz.quiz_type === 'stepwise'" class="mb-4">
        <label for="allowSkipping" class="block text-lg font-semibold mb-2"
          >Allow Skipping Questions?</label
        >
        <input
          type="checkbox"
          v-model="quiz.allow_skipping"
          id="allowSkipping"
        />
        <div v-if="!quiz.allow_skipping" class="mt-4">
          <label
            for="stepwiseTimeLimit"
            class="block text-lg font-semibold mb-2"
            >Set Time Limit for Each Step (in seconds)</label
          >
          <input
            type="number"
            v-model="quiz.stepwise_time_limit"
            min="5"
            id="stepwiseTimeLimit"
            class="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300"
          />
        </div>
      </div>
      <!-- Timer Options -->
      <div class="mb-4">
        <label for="isTimed" class="block text-lg font-semibold mb-2"
          >Set Time Limit for Quiz?</label
        >
        <input type="checkbox" v-model="quiz.is_timed" id="isTimed" />
        <div v-if="quiz.is_timed" class="mt-4">
          <label for="quizTimeLimit" class="block text-lg font-semibold mb-2"
            >Total Time Limit for Quiz (in minutes)</label
          >
          <input
            type="number"
            v-model="quiz.quiz_time_limit"
            min="1"
            id="quizTimeLimit"
            class="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300"
          />
        </div>
      </div>
      <div class="mb-4" v-if="quiz.quiz_type === 'standard'">
        <label for="timePerQuestion" class="block text-lg font-semibold mb-2"
          >Set Time Limit for Each Question (in seconds)</label
        >
        <input
          type="checkbox"
          v-model="quiz.time_per_question"
          id="timePerQuestion"
        />
        <div v-if="quiz.time_per_question" class="mt-4">
          <label
            for="questionTimeLimit"
            class="block text-lg font-semibold mb-2"
            >Time Limit per Question (in seconds)</label
          >
          <input
            type="number"
            v-model="quiz.question_time_limit"
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
        <input
          type="checkbox"
          v-model="quiz.display_results"
          id="displayResults"
        />
      </div>
      <div class="mb-4">
        <label for="requirePassword" class="block text-lg font-semibold mb-2"
          >Require Password to Access Quiz?</label
        >
        <input
          type="checkbox"
          v-model="quiz.require_password"
          id="requirePassword"
        />
        <input
          v-if="quiz.require_password"
          type="password"
          v-model="quiz.password"
          class="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300 mt-2"
          placeholder="Enter password"
        />
      </div>
      <div class="mb-4">
        <label for="allowAnonymous" class="block text-lg font-semibold mb-2"
          >Allow Anonymous Users?</label
        >
        <input
          type="checkbox"
          v-model="quiz.allow_anonymous"
          id="allowAnonymous"
        />
      </div>
      <div class="mb-4">
        <label for="requireName" class="block text-lg font-semibold mb-2"
          >Require Name/Nickname?</label
        >
        <input type="checkbox" v-model="quiz.require_name" id="requireName" />
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
      <div class="space-y-2">
        <button
          @click="goToEditPage"
          type="button"
          class="bg-yellow-500 text-white px-6 py-3 rounded hover:bg-green-700 w-full font-semibold"
        >
          Edit Quiz
        </button>
        <button
          @click="goToTestQuiz"
          type="button"
          class="bg-green-500 text-white px-6 py-3 rounded hover:bg-green-700 w-full font-semibold"
        >
          Test Quiz
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const questions = ref([])
let createdQuizId = null

// Define a single reactive object to store all quiz details
const quiz = ref({
  title: '',
  topic: '',
  question_count: 2, // Default to 2 questions
  option_count: 2, // Default to 2 options per question
  use_knowledge_base: false,
  knowledge_base_text: '',
  display_results: true,
  require_password: false,
  password: '',
  allow_anonymous: false,
  require_name: false,
  is_timed: false,
  quiz_time_limit: null,
  time_per_question: false,
  question_time_limit: null,
  quiz_type: 'standard', // Default quiz type is standard
  skippable_questions: false,
  stepwise_time_limit: null,
})

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

// Handle file upload
const handleFileUpload = event => {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = e => {
      quiz.value.knowledge_base_text = e.target.result
    }
    reader.readAsText(file)
  }
}

const createQuiz = async () => {
  loading.value = true
  try {
    const requestData = {
      title: quiz.value.title,
      topic: quiz.value.topic,
      question_count: quiz.value.question_count,
      option_count: quiz.value.option_count,
      difficulty: 'medium',
      display_results: quiz.value.display_results,
      require_password: quiz.value.require_password,
      password: quiz.value.require_password ? quiz.value.password : null,
      allow_anonymous: quiz.value.allow_anonymous,
      require_name: quiz.value.require_name,
      is_timed: quiz.value.is_timed,
      quiz_time_limit: quiz.value.is_timed ? quiz.value.quiz_time_limit : null,
      time_per_question: quiz.value.time_per_question,
      question_time_limit: quiz.value.time_per_question
        ? quiz.value.question_time_limit
        : null,
      quiz_type: quiz.value.quiz_type,
      allow_skipping:
        quiz.value.quiz_type === 'stepwise'
          ? quiz.value.skippable_questions
          : null,
      stepwise_time_limit:
        quiz.value.quiz_type === 'stepwise' && !quiz.value.skippable_questions
          ? quiz.value.stepwise_time_limit
          : null,
      account_id: authStore.account.id, // Include the account_id
    }

    if (quiz.value.use_knowledge_base) {
      requestData.knowledge_base = quiz.value.knowledge_base_text
    }

    const response = await axios.post(
      `${apiBaseUrl}/quizzes/create/`,
      requestData,
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      },
    )

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
    questions.value = []
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

const goToTestQuiz = () => {
  if (createdQuizId) {
    router.push({ name: 'TestQuiz', params: { id: createdQuizId } })
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
