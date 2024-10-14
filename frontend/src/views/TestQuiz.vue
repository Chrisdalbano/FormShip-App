<!-- eslint-disable no-undef -->
<template>
  <div class="zen-container">
    <h1>Test Quiz</h1>

    <!-- Password Prompt if Required -->
    <div
      v-if="quiz && quiz.require_password && !passwordValidated && !showResults"
    >
      <h2>Enter Password to Access Quiz</h2>
      <input
        type="password"
        v-model="enteredPassword"
        placeholder="Enter password"
        class="border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300"
      />
      <button
        @click="validatePassword"
        class="bg-blue-500 text-white px-4 py-2 rounded mt-4"
      >
        Submit Password
      </button>
      <p v-if="passwordError" class="text-red-500 mt-2">
        Incorrect password. Please try again.
      </p>
    </div>

    <!-- Name/Nickname Prompt if Required -->
    <div
      v-else-if="quiz && quiz.require_name && !userNameProvided && !showResults"
    >
      <h2>Enter Your Name or Nickname</h2>
      <input
        type="text"
        v-model="userName"
        placeholder="Enter your name"
        class="border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300"
      />
      <button
        @click="submitName"
        class="bg-blue-500 text-white px-4 py-2 rounded mt-4"
      >
        Submit Name
      </button>
    </div>

    <!-- Quiz Content -->
    <div
      v-if="
        quiz &&
        (!quiz.require_password || passwordValidated) &&
        (!quiz.require_name || userNameProvided) &&
        !showResults
      "
    >
      <h2>{{ quiz.title }}</h2>
      <p>Topic: {{ quiz.topic }}</p>
      <div v-if="quiz.is_timed && quizTimeRemaining > 0">
        <p class="font-semibold text-red-500">
          Time Remaining: {{ formattedQuizTime }}
        </p>
      </div>
      <div
        v-for="(question, index) in quiz.questions"
        :key="index"
        class="question-block"
      >
        <p>{{ index + 1 }}. {{ question.question_text }}</p>
        <div>
          <label v-if="question.option_a">
            <input
              type="radio"
              :name="'question' + index"
              value="A"
              v-model="userAnswers[index]"
            />
            A. {{ question.option_a }}
          </label>
          <label v-if="question.option_b">
            <input
              type="radio"
              :name="'question' + index"
              value="B"
              v-model="userAnswers[index]"
            />
            B. {{ question.option_b }}
          </label>
          <label v-if="question.option_c">
            <input
              type="radio"
              :name="'question' + index"
              value="C"
              v-model="userAnswers[index]"
            />
            C. {{ question.option_c }}
          </label>
          <label v-if="question.option_d">
            <input
              type="radio"
              :name="'question' + index"
              value="D"
              v-model="userAnswers[index]"
            />
            D. {{ question.option_d }}
          </label>
          <label v-if="question.option_e">
            <input
              type="radio"
              :name="'question' + index"
              value="E"
              v-model="userAnswers[index]"
            />
            E. {{ question.option_e }}
          </label>
        </div>
        <div
          v-if="quiz.time_per_question && questionTimers[index] > 0"
          class="mt-2"
        >
          <p class="text-red-600">
            Time Remaining for Question: {{ formattedQuestionTime(index) }}
          </p>
        </div>
      </div>
      <button
        @click="submitAnswers"
        class="bg-blue-500 text-white px-4 py-2 rounded mt-4"
      >
        Submit Answers
      </button>
    </div>

    <!-- Loading State -->
    <p v-else-if="!quiz && !showResults">Loading quiz...</p>

    <!-- Results Section -->
    <div v-if="showResults">
      <h2>Quiz Completed!</h2>
      <div v-if="quiz.display_results">
        <p>Your Score: {{ score }} / {{ totalQuestions }}</p>
        <ResultsView
          :score="score"
          :totalQuestions="totalQuestions"
          :questions="quiz.questions"
          :userAnswers="userAnswers"
          :xpEarned="calculateXPEarned(score)"
        />
      </div>
      <div v-else>
        <p>Thank you for completing the quiz!</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import ResultsView from './ResultsView.vue'

const route = useRoute()
const quiz = ref(null)
const userAnswers = ref([])
const score = ref(0)
const showResults = ref(false)

const quizId = route.params.id

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// State for Password Requirement
const passwordValidated = ref(!quiz.value?.require_password)
const enteredPassword = ref('')
const passwordError = ref(false)

// State for Name Requirement
const userName = ref('')
const userNameProvided = ref(!quiz.value?.require_name)

// Timer States
const quizTimeRemaining = ref(null)
const questionTimers = ref([])

let quizStartTime = null

onMounted(async () => {
  try {
    const response = await axios.get(`${apiBaseUrl}/quizzes/${quizId}/`)
    quiz.value = response.data
    userAnswers.value = Array(response.data.questions.length).fill(null)
    passwordValidated.value = !quiz.value.require_password
    userNameProvided.value = !quiz.value.require_name

    if (quiz.value.is_timed && quiz.value.quiz_time_limit) {
      quizTimeRemaining.value = quiz.value.quiz_time_limit * 60
      quizStartTime = new Date()
      startQuizTimer()
    }
    if (quiz.value.time_per_question && quiz.value.question_time_limit) {
      questionTimers.value = Array(response.data.questions.length).fill(
        quiz.value.question_time_limit,
      )
      startQuestionTimers()
    }
  } catch (error) {
    console.error('Error fetching quiz:', error)
  }
})

const startQuizTimer = () => {
  const timer = setInterval(() => {
    if (quizTimeRemaining.value > 0) {
      quizTimeRemaining.value--
    } else {
      clearInterval(timer)
      submitAnswers()
    }
  }, 1000)
}

const startQuestionTimers = () => {
  questionTimers.value.forEach((_, index) => {
    const timer = setInterval(() => {
      if (questionTimers.value[index] > 0) {
        questionTimers.value[index]--
      } else {
        clearInterval(timer)
        nextQuestion(index)
      }
    }, 1000)
  })
}

const nextQuestion = currentIndex => {
  if (currentIndex < quiz.value.questions.length - 1) {
    document
      .querySelector(`[name='question${currentIndex + 1}']`)
      .scrollIntoView({ behavior: 'smooth' })
  }
}

const validatePassword = () => {
  if (enteredPassword.value === quiz.value.password) {
    passwordValidated.value = true
    passwordError.value = false
  } else {
    passwordError.value = true
  }
}

const submitName = () => {
  if (userName.value.trim() !== '') {
    userNameProvided.value = true
  }
}
const submitAnswers = async () => {
  calculateScore()
  showResults.value = true

  const userAnswersDict = {}
  quiz.value.questions.forEach((question, index) => {
    userAnswersDict[question.id] = userAnswers.value[index]
  })

  const requestData = {
    quiz_id: quiz.value.id,
    user_name: userName.value.trim() ? userName.value : 'Anonymous',
    user_answers: userAnswersDict,
    quiz_start_time: quizStartTime?.toISOString(),
  }

  console.log('Submitting request data:', requestData)

  try {
    const response = await axios.post(
      `${apiBaseUrl}/submit-quiz-results/`,
      requestData,
    )
    if (response.status === 201) {
      console.log('Quiz results successfully submitted')
    }
  } catch (error) {
    console.error('Error submitting quiz results:', error)
  }
}

const calculateScore = () => {
  let calculatedScore = 0
  quiz.value.questions.forEach((question, index) => {
    if (userAnswers.value[index] === question.correct_answer) {
      calculatedScore++
    }
  })
  score.value = calculatedScore
}

const calculateXPEarned = score => {
  // Assuming XP earned is proportional to the score
  return score * 10 // You can adjust this logic as needed
}

// eslint-disable-next-line no-undef
const formattedQuizTime = computed(() => {
  const minutes = Math.floor(quizTimeRemaining.value / 60)
  const seconds = quizTimeRemaining.value % 60
  return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`
})

const formattedQuestionTime = index => {
  const seconds = questionTimers.value[index]
  return `${Math.floor(seconds / 60)}:${seconds % 60 < 10 ? '0' : ''}${
    seconds % 60
  }`
}
</script>

<style scoped>
.question-block {
  margin-bottom: 1rem;
}

.results {
  margin-top: 2rem;
}

.zen-container {
  max-width: 800px;
  margin: auto;
}

.button {
  margin-top: 10px;
}
</style>
