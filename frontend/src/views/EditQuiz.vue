<template>
  <div
    class="edit-quiz-container w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg"
  >
    <h1 class="text-3xl font-bold mb-4">Edit Quiz</h1>
    <form @submit.prevent="updateQuiz">
      <div class="mb-4">
        <label for="title" class="block text-lg font-semibold mb-2"
          >Quiz Title</label
        >
        <input
          v-model="quiz.title"
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
          v-model="quiz.topic"
          type="text"
          id="topic"
          class="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300"
          required
        />
      </div>

      <!-- Timer Settings -->
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

      <div class="mb-4">
        <label for="timePerQuestion" class="block text-lg font-semibold mb-2"
          >Set Time Limit for Each Question?</label
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

      <!-- Sharing Settings -->
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

      <div
        v-for="(question, index) in quiz.questions"
        :key="question.id || index"
        class="mb-6"
      >
        <h3 class="text-xl font-semibold mb-2">Question {{ index + 1 }}</h3>
        <div class="mb-4">
          <label class="block text-md font-semibold mb-1">Question Text</label>
          <input
            v-model="question.question_text"
            type="text"
            class="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300"
            required
          />
        </div>
        <div class="mb-4">
          <label class="block text-md font-semibold mb-1"
            >Number of Options</label
          >
          <select
            v-model="question.option_count"
            @change="adjustOptions(question)"
            class="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300"
          >
            <option v-for="n in 5" :key="n" :value="n">{{ n }}</option>
          </select>
        </div>
        <div
          v-for="option in visibleOptions(question)"
          :key="option.field"
          class="mb-4"
        >
          <label class="block text-md font-semibold mb-1">{{
            option.label
          }}</label>
          <input
            v-model="question[option.field]"
            type="text"
            class="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300"
          />
        </div>
        <div class="mb-4">
          <label class="block text-md font-semibold mb-1">Correct Answer</label>
          <select
            v-model="question.correct_answer"
            class="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300"
          >
            <option value="A">A</option>
            <option value="B">B</option>
            <option v-if="question.option_c" value="C">C</option>
            <option v-if="question.option_d" value="D">D</option>
            <option v-if="question.option_e" value="E">E</option>
          </select>
        </div>
        <button
          @click="deleteQuestion(index)"
          type="button"
          class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-700"
        >
          Delete Question
        </button>
      </div>
      <button
        @click="addQuestion"
        type="button"
        class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-700 mb-6"
      >
        Add New Question
      </button>
      <button
        type="submit"
        class="bg-blue-500 text-white px-6 py-3 rounded hover:bg-blue-700 w-full font-semibold"
      >
        Update Quiz
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const quizId = route.params.id
const quiz = ref({
  title: '',
  topic: '',
  questions: [],
  display_results: true,
  require_password: false,
  password: '',
  allow_anonymous: false,
  require_name: false,
  is_timed: false,
  quiz_time_limit: null,
  time_per_question: false,
  question_time_limit: null,
})

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

// Option configuration
const optionsConfig = [
  { label: 'Option A', field: 'option_a' },
  { label: 'Option B', field: 'option_b' },
  { label: 'Option C', field: 'option_c' },
  { label: 'Option D', field: 'option_d' },
  { label: 'Option E', field: 'option_e' },
]

onMounted(async () => {
  try {
    const response = await axios.get(`${apiBaseUrl}/quizzes/${quizId}/`)
    quiz.value = response.data
  } catch (error) {
    console.error('Error fetching quiz:', error)
  }
})

const updateQuiz = async () => {
  try {
    // Update quiz details
    const {
      title,
      topic,
      questions,
      display_results,
      require_password,
      password,
      allow_anonymous,
      require_name,
      is_timed,
      quiz_time_limit,
      time_per_question,
      question_time_limit,
    } = quiz.value

    await axios.put(`${apiBaseUrl}/quizzes/${quizId}/`, {
      title,
      topic,
      difficulty: quiz.value.difficulty, // Ensure all necessary fields are passed
      question_count: questions.length,
      quiz_type: quiz.value.quiz_type, // Add any additional properties needed by backend
      display_results,
      require_password,
      password,
      allow_anonymous,
      require_name,
      is_timed,
      quiz_time_limit,
      time_per_question,
      question_time_limit,
    })

    for (const question of questions) {
      const questionData = {
        question_text: question.question_text,
        option_a: question.option_a || null,
        option_b: question.option_b || null,
        option_c: question.option_c || null,
        option_d: question.option_d || null,
        option_e: question.option_e || null,
        correct_answer: question.correct_answer,
      }
      if (question.id) {
        // Update existing question
        await axios.put(`${apiBaseUrl}/questions/${question.id}/`, questionData)
      } else {
        // Create new question
        questionData.quiz = quizId
        await axios.post(
          `${apiBaseUrl}/quizzes/${quizId}/questions/`,
          questionData,
        )
      }
    }

    alert('Quiz updated successfully!')
    router.push({ name: 'QuizDashboard' })
  } catch (error) {
    console.error('Error updating quiz:', error.response?.data || error)
    alert('Failed to update quiz. Please check your inputs and try again.')
  }
}

const addQuestion = () => {
  quiz.value.questions.push({
    question_text: '',
    option_a: '',
    option_b: '',
    option_c: '',
    option_d: '',
    option_e: '',
    correct_answer: 'A',
    option_count: 2,
  })
}

// Adjust number of options displayed based on user selection
const adjustOptions = question => {
  question.option_count = Math.max(2, Math.min(question.option_count, 5)) // Clamp between 2 and 5
}

// Compute visible options based on user's selection
const visibleOptions = question => {
  return optionsConfig.slice(0, question.option_count)
}

const deleteQuestion = async index => {
  const question = quiz.value.questions[index]
  if (question.id) {
    try {
      await axios.delete(`${apiBaseUrl}/questions/${question.id}/`)
    } catch (error) {
      console.error('Error deleting question:', error)
    }
  }
  quiz.value.questions.splice(index, 1)
}
</script>

<style scoped>
.edit-quiz-container {
  @apply mt-10;
}
</style>
