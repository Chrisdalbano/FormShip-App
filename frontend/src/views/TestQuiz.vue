<template>
  <div class="zen-container">
    <h1>{{ quiz_type === 'stepwise' ? 'Stepwise Quiz' : 'Test Quiz' }}</h1>

    <!-- Password Prompt -->
    <div
      v-if="quiz && quiz.require_password && !passwordValidated && !showResults"
    >
      <h2>Enter Password to Access Quiz</h2>
      <input
        type="password"
        v-model="enteredPassword"
        placeholder="Enter password"
        class="input-field"
      />
      <button @click="validatePassword" class="action-button">
        Submit Password
      </button>
      <p v-if="passwordError" class="error-text">
        Incorrect password. Please try again.
      </p>
    </div>

    <!-- Name Prompt -->
    <div
      v-else-if="quiz && quiz.require_name && !userNameProvided && !showResults"
    >
      <h2>Enter Your Name or Nickname</h2>
      <input
        type="text"
        v-model="userName"
        placeholder="Enter your name"
        class="input-field"
      />
      <button @click="submitName" class="action-button">Submit Name</button>
    </div>

    <!-- Quiz Content -->
    <div
      v-else-if="quiz && !showResults && passwordValidated && userNameProvided"
    >
      <h2>{{ quiz.title }}</h2>
      <p>Topic: {{ quiz.topic }}</p>

      <div v-if="quiz.is_timed && quizTimeRemaining > 0">
        <p class="timer-text">Time Remaining: {{ formattedQuizTime }}</p>
      </div>

      <!-- Stepwise Mode -->
      <div v-if="quiz_type === 'stepwise'" class="stepwise-quiz">
        <div class="question-block">
          <p>
            {{ currentQuestionIndex + 1 }}. {{ currentQuestion.question_text }}
          </p>
          <div>
            <label v-if="currentQuestion.option_a">
              <input
                type="radio"
                :name="'question' + currentQuestionIndex"
                value="A"
                v-model="userAnswers[currentQuestionIndex]"
              />
              A. {{ currentQuestion.option_a }}
            </label>
            <label v-if="currentQuestion.option_b">
              <input
                type="radio"
                :name="'question' + currentQuestionIndex"
                value="B"
                v-model="userAnswers[currentQuestionIndex]"
              />
              B. {{ currentQuestion.option_b }}
            </label>
            <label v-if="currentQuestion.option_c">
              <input
                type="radio"
                :name="'question' + currentQuestionIndex"
                value="C"
                v-model="userAnswers[currentQuestionIndex]"
              />
              C. {{ currentQuestion.option_c }}
            </label>
            <label v-if="currentQuestion.option_d">
              <input
                type="radio"
                :name="'question' + currentQuestionIndex"
                value="D"
                v-model="userAnswers[currentQuestionIndex]"
              />
              D. {{ currentQuestion.option_d }}
            </label>
            <label v-if="currentQuestion.option_e">
              <input
                type="radio"
                :name="'question' + currentQuestionIndex"
                value="E"
                v-model="userAnswers[currentQuestionIndex]"
              />
              E. {{ currentQuestion.option_e }}
            </label>
          </div>
          <div v-if="quiz.time_per_question && questionTimer > 0" class="mt-2">
            <p class="text-red-600">
              Time Remaining for Question: {{ formattedQuestionTime }}
            </p>
          </div>
        </div>

        <!-- Navigation Buttons -->
        <div class="navigation-buttons mt-4">
          <button
            @click="goToNextQuestion"
            class="bg-blue-500 text-white px-4 py-2 rounded"
            :disabled="!canAdvanceToNext"
          >
            Next
          </button>
          <button
            v-if="currentQuestionIndex > 0 && !quiz.time_per_question"
            @click="goToPreviousQuestion"
            class="bg-gray-500 text-white px-4 py-2 rounded ml-2"
          >
            Previous
          </button>
          <button
            v-if="isLastQuestion"
            @click="submitAnswers"
            class="bg-green-500 text-white px-4 py-2 rounded ml-2"
          >
            Submit Answers
          </button>
        </div>
      </div>

      <!-- All-at-Once Mode -->
      <div v-else class="all-at-once-quiz">
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
        </div>
        <button
          @click="submitAnswers"
          class="bg-blue-500 text-white px-4 py-2 rounded mt-4"
        >
          Submit Answers
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <p v-else-if="!quiz && !showResults">Loading quiz...</p>

    <!-- Results Section -->
    <div v-if="showResults">
      <ResultsView
        :score="score"
        :totalQuestions="totalQuestions"
        :questions="quiz.questions"
        :userAnswers="userAnswers"
        :xpEarned="calculateXPEarned(score)"
      />
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
const quiz_type = ref('all-at-once')

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// Password and Name State
const passwordValidated = ref(false)
const enteredPassword = ref('')
const passwordError = ref(false)
const userName = ref('')
const userNameProvided = ref(false)

// Timer States
const quizTimeRemaining = ref(0)
let questionTimer = ref(0)
const currentQuestionIndex = ref(0)
const currentQuestion = computed(
  () => quiz.value.questions[currentQuestionIndex.value],
)

onMounted(async () => {
  try {
    const response = await axios.get(`${apiBaseUrl}/quizzes/${quizId}/`)
    quiz.value = response.data
    userAnswers.value = Array(response.data.questions.length).fill(null)
    passwordValidated.value = !quiz.value.require_password
    userNameProvided.value = !quiz.value.require_name
    quiz_type.value =
      quiz.value.quiz_type === 'stepwise' ? 'stepwise' : 'all-at-once'

    if (quiz.value.is_timed) {
      quizTimeRemaining.value = quiz.value.quiz_time_limit * 60
      startQuizTimer()
    }
    if (quiz.value.time_per_question) {
      questionTimer.value = quiz.value.time_per_question
      startQuestionTimer()
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

const startQuestionTimer = () => {
  const timer = setInterval(() => {
    if (questionTimer.value > 0) {
      questionTimer.value--
    } else {
      clearInterval(timer)
      if (!isLastQuestion.value) {
        goToNextQuestion()
      } else {
        submitAnswers()
      }
    }
  }, 1000)
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
  if (userName.value.trim()) {
    userNameProvided.value = true
  }
}

const goToNextQuestion = () => {
  if (currentQuestionIndex.value < quiz.value.questions.length - 1) {
    currentQuestionIndex.value++
    if (quiz.value.time_per_question) {
      questionTimer.value = quiz.value.time_per_question
      startQuestionTimer()
    }
  }
}

// Updated: Prevent going back if the questions are timed
const goToPreviousQuestion = () => {
  if (currentQuestionIndex.value > 0 && !quiz.value.time_per_question) {
    currentQuestionIndex.value--
  }
}

const submitAnswers = () => {
  calculateScore()
  showResults.value = true
}

const calculateScore = () => {
  score.value = userAnswers.value.filter(
    (answer, index) => answer === quiz.value.questions[index].correct_answer,
  ).length
}

const calculateXPEarned = score => score * 10 // Adjust XP logic as needed

const formattedQuizTime = computed(() => {
  const minutes = Math.floor(quizTimeRemaining.value / 60)
  const seconds = quizTimeRemaining.value % 60
  return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`
})

const formattedQuestionTime = computed(() => {
  const minutes = Math.floor(questionTimer.value / 60)
  const seconds = questionTimer.value % 60
  return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`
})

const isLastQuestion = computed(() => {
  return currentQuestionIndex.value === quiz.value.questions.length - 1
})

const canAdvanceToNext = computed(() => {
  return userAnswers[currentQuestionIndex.value] !== null
})
</script>

<style scoped>
.zen-container {
  max-width: 800px;
  margin: auto;
}
.input-field {
  border: 1px solid #ddd;
  padding: 10px;
  border-radius: 5px;
  width: 100%;
  margin-bottom: 10px;
}
.action-button {
  background-color: #3490dc;
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
  border: none;
  cursor: pointer;
}
.action-button:hover {
  background-color: #2779bd;
}
.timer-text {
  font-weight: bold;
  color: red;
}
.question-block {
  margin-bottom: 20px;
}
.error-text {
  color: red;
  font-size: 14px;
}
</style>
