<template>
  <div class="min-h-screen flex flex-col">
    <div class="zen-container">
      <h1>{{ quiz_type === 'stepwise' ? 'Stepwise Quiz' : 'Quiz' }}</h1>

      <!-- Loading State -->
      <p v-if="loading">Loading quiz...</p>

      <!-- Error Message -->
      <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

      <!-- Quiz Content -->
      <div
        v-else-if="quiz && quiz.questions.length > 0 && !showResults"
        class="quiz-container"
      >
        <h2 class="quiz-title">{{ quiz.title }}</h2>
        <p class="quiz-topic">Topic: {{ quiz.topic }}</p>

        <!-- Stepwise Mode -->
        <div v-if="quiz_type === 'stepwise'" class="stepwise-quiz">
          <div class="question-block">
            <p class="question-text">
              {{ currentQuestionIndex + 1 }}.
              {{
                currentQuestion
                  ? currentQuestion.question_text
                  : 'Loading question...'
              }}
            </p>

            <!-- Options -->
            <div class="option-group">
              <template
                v-if="currentQuestion.options && currentQuestion.options.length"
              >
                <label
                  v-for="(option, index) in currentQuestion.options"
                  :key="index"
                >
                  <input
                    type="radio"
                    :name="'question' + currentQuestionIndex"
                    :value="option.value"
                    :checked="
                      userAnswers[currentQuestionIndex] === option.value
                    "
                    @change="updateAnswer(currentQuestionIndex, option.value)"
                  />
                  {{ option.label }}
                </label>
              </template>

              <!-- Fallback for old format -->
              <template v-else>
                <label v-if="currentQuestion.option_a">
                  <input
                    type="radio"
                    :name="'question' + currentQuestionIndex"
                    value="A"
                    :checked="userAnswers[currentQuestionIndex] === 'A'"
                    @change="updateAnswer(currentQuestionIndex, 'A')"
                  />
                  A. {{ currentQuestion.option_a }}
                </label>
                <label v-if="currentQuestion.option_b">
                  <input
                    type="radio"
                    :name="'question' + currentQuestionIndex"
                    value="B"
                    :checked="userAnswers[currentQuestionIndex] === 'B'"
                    @change="updateAnswer(currentQuestionIndex, 'B')"
                  />
                  B. {{ currentQuestion.option_b }}
                </label>
                <label v-if="currentQuestion.option_c">
                  <input
                    type="radio"
                    :name="'question' + currentQuestionIndex"
                    value="C"
                    :checked="userAnswers[currentQuestionIndex] === 'C'"
                    @change="updateAnswer(currentQuestionIndex, 'C')"
                  />
                  C. {{ currentQuestion.option_c }}
                </label>
                <label v-if="currentQuestion.option_d">
                  <input
                    type="radio"
                    :name="'question' + currentQuestionIndex"
                    value="D"
                    :checked="userAnswers[currentQuestionIndex] === 'D'"
                    @change="updateAnswer(currentQuestionIndex, 'D')"
                  />
                  D. {{ currentQuestion.option_d }}
                </label>
                <label v-if="currentQuestion.option_e">
                  <input
                    type="radio"
                    :name="'question' + currentQuestionIndex"
                    value="E"
                    :checked="userAnswers[currentQuestionIndex] === 'E'"
                    @change="updateAnswer(currentQuestionIndex, 'E')"
                  />
                  E. {{ currentQuestion.option_e }}
                </label>
              </template>
            </div>
          </div>

          <!-- Navigation Buttons -->
          <div class="navigation-buttons">
            <button
              @click="goToPreviousQuestion"
              :disabled="currentQuestionIndex === 0"
              class="btn btn-secondary"
            >
              Previous
            </button>
            <button
              @click="goToNextQuestion"
              :disabled="!canAdvanceToNext"
              class="btn btn-primary"
            >
              Next
            </button>
            <button
              v-if="isLastQuestion"
              @click="submitQuiz"
              class="btn btn-success"
              :disabled="submitting"
            >
              {{ submitting ? 'Submitting...' : 'Submit' }}
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
            <div class="option-group">
              <template v-if="question.options && question.options.length">
                <label v-for="(option, idx) in question.options" :key="idx">
                  <input
                    type="radio"
                    :name="'question' + index"
                    :value="option.value"
                    :checked="userAnswers[index] === option.value"
                    @change="updateAnswer(index, option.value)"
                  />
                  {{ option.label }}
                </label>
              </template>

              <template v-else>
                <label v-if="question.option_a">
                  <input
                    type="radio"
                    :name="'question' + index"
                    value="A"
                    :checked="userAnswers[index] === 'A'"
                    @change="updateAnswer(index, 'A')"
                  />
                  A. {{ question.option_a }}
                </label>
                <label v-if="question.option_b">
                  <input
                    type="radio"
                    :name="'question' + index"
                    value="B"
                    :checked="userAnswers[index] === 'B'"
                    @change="updateAnswer(index, 'B')"
                  />
                  B. {{ question.option_b }}
                </label>
                <label v-if="question.option_c">
                  <input
                    type="radio"
                    :name="'question' + index"
                    value="C"
                    :checked="userAnswers[index] === 'C'"
                    @change="updateAnswer(index, 'C')"
                  />
                  C. {{ question.option_c }}
                </label>
                <label v-if="question.option_d">
                  <input
                    type="radio"
                    :name="'question' + index"
                    value="D"
                    :checked="userAnswers[index] === 'D'"
                    @change="updateAnswer(index, 'D')"
                  />
                  D. {{ question.option_d }}
                </label>
                <label v-if="question.option_e">
                  <input
                    type="radio"
                    :name="'question' + index"
                    value="E"
                    :checked="userAnswers[index] === 'E'"
                    @change="updateAnswer(index, 'E')"
                  />
                  E. {{ question.option_e }}
                </label>
              </template>
            </div>
          </div>
          <button
            @click="submitQuiz"
            class="btn btn-primary"
            :disabled="submitting"
          >
            {{ submitting ? 'Submitting...' : 'Submit' }}
          </button>
        </div>
      </div>

      <!-- Completed/Results Section -->
      <CompletedQuiz
        v-if="showResults"
        :quiz="quiz"
        :score="score"
        :totalQuestions="totalQuestions"
        :questions="quiz.questions"
        :userAnswers="userAnswers"
      >
        <span class="total-score text-5xl font-bold">
          {{ score }} / {{ totalQuestions }}
        </span>
      </CompletedQuiz>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useQuizStore } from '@/store/quiz'
import { useAuthStore } from '@/store/auth'
import CompletedQuiz from '@/components/CompletedQuiz.vue'

defineProps({
  id: {
    type: String,
    required: true,
  },
})

const route = useRoute()
// const router = useRouter()
const quizStore = useQuizStore()
const authStore = useAuthStore()

const loading = ref(true)
const submitting = ref(false)
const showResults = ref(false)
const errorMessage = ref('')
const currentQuestionIndex = ref(0)
const userAnswers = computed(() => quizStore.userAnswers)

const quiz = computed(() => quizStore.quiz)
const quiz_type = computed(() => {
  return quiz.value?.quiz_type || 'all_at_once'
})
const currentQuestion = computed(
  () => quiz.value?.questions?.[currentQuestionIndex.value] || null,
)

// Calculate the score
const score = computed(() => {
  return quiz.value.questions.reduce((acc, question, index) => {
    return (
      acc + (quizStore.userAnswers[index] === question.correct_answer ? 1 : 0)
    )
  }, 0)
})

const totalQuestions = computed(() => quiz.value?.questions?.length || 0)

onMounted(async () => {
  try {
    await quizStore.loadQuiz(route.params.id)

    // Check access permissions
    if (!authStore.isAuthenticated && !quiz.value.is_published) {
      errorMessage.value = 'This quiz is not available.'
      loading.value = false
      return
    }

    // Set current quiz in store if participant is authenticated
    if (quizStore.isAuthenticated && !quizStore.currentQuiz) {
      await quizStore.setCurrentQuiz(quiz.value)
    }

    loading.value = false

    if (!quiz.value.questions || quiz.value.questions.length === 0) {
      errorMessage.value = 'This quiz has no questions.'
      return
    }

    // Ensure userAnswers is initialized with the correct length
    if (userAnswers.value.length !== quiz.value.questions.length) {
      userAnswers.value = Array(quiz.value.questions.length).fill(null)
    }
  } catch (err) {
    console.error('Failed to load quiz:', err)
    errorMessage.value = 'Failed to load the quiz. Please try again later.'
  }
})

const goToNextQuestion = () => {
  if (currentQuestionIndex.value < quiz.value.questions.length - 1) {
    currentQuestionIndex.value++
  }
}

const goToPreviousQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
  }
}

const submitQuiz = async () => {
  if (submitting.value) return
  submitting.value = true

  try {
    // If in testing mode (FormShip user), just show results without submitting to backend
    if (authStore.isAuthenticated && route.query.test === 'true') {
      showResults.value = true
      submitting.value = false
      return
    }

    // For participants, submit to backend
    await quizStore.submitAnswers(userAnswers.value)
    showResults.value = true
  } catch (err) {
    console.error('Failed to submit quiz:', err)
    errorMessage.value = 'Failed to submit the quiz. Please try again.'
  } finally {
    submitting.value = false
  }
}

const isLastQuestion = computed(
  () => currentQuestionIndex.value === quiz.value.questions.length - 1,
)
const canAdvanceToNext = computed(
  () => userAnswers.value[currentQuestionIndex.value] !== null,
)

const updateAnswer = (index, value) => {
  quizStore.userAnswers[index] = value
  console.log('Updated userAnswers:', quizStore.userAnswers)
}
</script>

<style scoped>
.error-text {
  color: red;
  margin: 1rem 0;
}

.zen-container {
  max-width: 800px;
  margin: auto;
  padding: 1rem;
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
</style>
