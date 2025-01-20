<template>
  <div class="zen-container">
    <!-- Quiz Title -->
    <h1>{{ quiz_type === 'stepwise' ? 'Stepwise Quiz' : 'Quiz' }}</h1>

    <!-- Loading State -->
    <p v-if="!quiz && !showResults">Loading quiz...</p>

    <!-- Quiz Content (only if we have quiz data & haven't submitted yet) -->
    <div v-else-if="quiz && !showResults" class="quiz-container">
      <h2 class="quiz-title">{{ quiz.title }}</h2>
      <p class="quiz-topic">Topic: {{ quiz.topic }}</p>

      <!-- Overall Timer for Timed Quiz -->
      <div v-if="quiz.is_timed && quizTimeRemaining > 0" class="quiz-timer">
        <p class="timer-text">Time Remaining: {{ formattedQuizTime }}</p>
      </div>

      <!-- Stepwise Mode -->
      <div v-if="quiz_type === 'stepwise'" class="stepwise-quiz">
        <div class="question-block">
          <p class="question-text">
            {{ currentQuestionIndex + 1 }}. {{ currentQuestion.question_text }}
          </p>
          <div class="option-group">
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

          <!-- Per-Question Timer -->
          <div
            v-if="quiz.time_per_question && questionTimer > 0"
            class="question-timer"
          >
            <p class="text-red-600">
              Time Remaining for Question: {{ formattedQuestionTime }}
            </p>
          </div>
        </div>

        <!-- Navigation Buttons -->
        <div class="navigation-buttons mt-4">
          <button
            @click="goToNextQuestion"
            class="btn btn-primary"
            :disabled="!canAdvanceToNext"
          >
            Next
          </button>
          <button
            v-if="
              currentQuestionIndex > 0 &&
              !quiz.time_per_question &&
              quiz.allow_previous_questions
            "
            @click="goToPreviousQuestion"
            class="btn btn-secondary ml-2"
          >
            Previous
          </button>
          <button
            v-if="isLastQuestion"
            @click="submitAnswers"
            class="btn btn-success ml-2"
          >
            Submit
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
          <p class="question-text">
            {{ index + 1 }}. {{ question.question_text }}
          </p>
          <div class="option-group">
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
        <button @click="submitAnswers" class="btn btn-primary mt-4">
          Submit
        </button>
      </div>
    </div>

    <!-- Completed/Results Section -->
    <CompletedQuiz
      v-if="showResults && quiz"
      :quiz="quiz"
      :score="score"
      :totalQuestions="totalQuestions"
      :questions="quiz.questions"
      :userAnswers="userAnswers"
      @retakeQuiz="retakeQuiz"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

// The new or renamed results component:
import CompletedQuiz from '../components/CompletedQuiz.vue'

const route = useRoute()
const quiz = ref(null)

// Participant or attempt info (optional)
const participantId = ref(null)

// Array for storing user’s chosen answers
const userAnswers = ref([])

// Quiz meta
const showResults = ref(false)
const score = ref(0)
const quizId = route.params.id
const quiz_type = ref('all-at-once')

// Stepwise
const currentQuestionIndex = ref(0)
const currentQuestion = computed(() =>
  quiz.value && quiz.value.questions
    ? quiz.value.questions[currentQuestionIndex.value]
    : {},
)

// Timers
const quizTimeRemaining = ref(0)
const questionTimer = ref(0)

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// Lifecycle
onMounted(async () => {
  // 1) Optionally load participant ID from localStorage or another source
  participantId.value =
    localStorage.getItem(`quiz_${quizId}_participant_id`) || null

  // 2) Fetch the quiz data
  try {
    const response = await axios.get(`${apiBaseUrl}/quizzes/${quizId}/`)
    quiz.value = response.data
    userAnswers.value = Array(response.data.questions.length).fill(null)
    quiz_type.value =
      quiz.value.quiz_type === 'stepwise' ? 'stepwise' : 'all-at-once'

    // If the quiz is timed
    if (quiz.value.is_timed && quiz.value.quiz_time_limit) {
      quizTimeRemaining.value = quiz.value.quiz_time_limit * 60 // convert min -> sec
      startQuizTimer()
    }

    // If each question is timed
    if (quiz.value.time_per_question) {
      questionTimer.value = quiz.value.time_per_question
      startQuestionTimer()
    }
  } catch (error) {
    console.error('Error fetching quiz:', error)
  }
})

// Timer functions
function startQuizTimer() {
  const timer = setInterval(() => {
    if (quizTimeRemaining.value > 0) {
      quizTimeRemaining.value--
    } else {
      clearInterval(timer)
      submitAnswers()
    }
  }, 1000)
}

function startQuestionTimer() {
  const timer = setInterval(() => {
    if (questionTimer.value > 0) {
      questionTimer.value--
    } else {
      clearInterval(timer)
      // Move on automatically or submit, depending on logic
      if (!isLastQuestion.value) {
        goToNextQuestion()
      } else {
        submitAnswers()
      }
    }
  }, 1000)
}

// Navigation
function goToNextQuestion() {
  if (currentQuestionIndex.value < quiz.value.questions.length - 1) {
    currentQuestionIndex.value++
    // Reset question timer if needed
    if (quiz.value.time_per_question) {
      questionTimer.value = quiz.value.time_per_question
      startQuestionTimer()
    }
  }
}

function goToPreviousQuestion() {
  // Only allowed if quiz.allow_previous_questions = true and not timed per question
  if (currentQuestionIndex.value > 0 && !quiz.value.time_per_question) {
    currentQuestionIndex.value--
  }
}

// Submitting
function submitAnswers() {
  calculateScore()
  // Optionally push attempt/score to the backend
  sendAttemptToBackend()

  // Show results or “completed” screen
  showResults.value = true
}

// Example method to post the attempt/score
async function sendAttemptToBackend() {
  if (!participantId.value) return
  try {
    await axios.post(`${apiBaseUrl}/attempts/submit/`, {
      participant_id: participantId.value,
      quiz_id: quizId,
      score: score.value,
      answers: userAnswers.value,
    })
  } catch (err) {
    console.error('Error sending attempt data:', err)
  }
}

function calculateScore() {
  if (!quiz.value) return
  score.value = userAnswers.value.filter(
    (answer, index) => answer === quiz.value.questions[index].correct_answer,
  ).length
}

function retakeQuiz() {
  // If you want a “retake” button in CompletedQuiz.vue
  showResults.value = false
  score.value = 0
  currentQuestionIndex.value = 0
  userAnswers.value = Array(quiz.value.questions.length).fill(null)
  if (quiz.value.time_per_question) {
    questionTimer.value = quiz.value.time_per_question
    startQuestionTimer()
  }
  if (quiz.value.is_timed && quiz.value.quiz_time_limit) {
    quizTimeRemaining.value = quiz.value.quiz_time_limit * 60
    startQuizTimer()
  }
}

// Computed
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
  return quiz.value
    ? currentQuestionIndex.value === quiz.value.questions.length - 1
    : false
})

const canAdvanceToNext = computed(() => {
  return userAnswers.value[currentQuestionIndex.value] !== null
})

const totalQuestions = computed(() => quiz.value?.questions?.length || 0)
</script>

<style scoped>
.zen-container {
  max-width: 800px;
  margin: auto;
  padding: 1rem;
}

.quiz-container {
  margin-top: 1rem;
}

.question-block {
  margin-bottom: 20px;
}

.question-text {
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.option-group label {
  display: block;
  margin: 0.4rem 0;
}

.btn {
  display: inline-block;
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
}

.btn-primary {
  background-color: #3490dc;
  color: #fff;
}

.btn-primary:hover {
  background-color: #2779bd;
}

.btn-secondary {
  background-color: #6c757d;
  color: #fff;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.btn-success {
  background-color: #38c172;
  color: white;
}

.btn-success:hover {
  background-color: #2fa360;
}

.timer-text {
  font-weight: bold;
  color: #b91c1c;
  margin: 0.5rem 0;
}
</style>
