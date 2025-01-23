<template>
  <div class="quiz-player-container">
    <!-- Timer -->
    <div v-if="quiz.is_timed" class="timer">
      Time Remaining: {{ formattedQuizTime }}
    </div>

    <!-- Questions -->
    <div class="question-section">
      <p class="question">
        {{ currentQuestionIndex + 1 }}. {{ currentQuestion.question_text }}
      </p>
      <div class="options">
        <label v-for="(option, index) in currentQuestion.options" :key="index">
          <input
            type="radio"
            :name="'question' + currentQuestionIndex"
            :value="option.value"
            v-model="userAnswers[currentQuestionIndex]"
          />
          {{ option.label }}
        </label>
      </div>
    </div>

    <!-- Navigation -->
    <div class="navigation">
      <button
        v-if="currentQuestionIndex > 0"
        @click="prevQuestion"
        class="btn-secondary"
      >
        Previous
      </button>
      <button
        v-if="currentQuestionIndex < quiz.questions.length - 1"
        @click="nextQuestion"
        class="btn-primary"
      >
        Next
      </button>
      <button
        v-if="currentQuestionIndex === quiz.questions.length - 1"
        @click="submitQuiz"
        class="btn-success"
      >
        Submit
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const props = defineProps({
  quiz: Object,
})

const emit = defineEmits(['logEvent'])

const router = useRouter()

const currentQuestionIndex = ref(0)
const userAnswers = ref(Array(props.quiz.questions.length).fill(null))
const quizTimeRemaining = ref(
  props.quiz.is_timed ? props.quiz.quiz_time_limit * 60 : 0,
)

const currentQuestion = computed(
  () => props.quiz.questions[currentQuestionIndex.value],
)

const formattedQuizTime = computed(() => {
  const minutes = Math.floor(quizTimeRemaining.value / 60)
  const seconds = quizTimeRemaining.value % 60
  return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`
})

const startQuizTimer = () => {
  if (props.quiz.is_timed) {
    const timer = setInterval(() => {
      if (quizTimeRemaining.value > 0) {
        quizTimeRemaining.value--
      } else {
        clearInterval(timer)
        submitQuiz()
      }
    }, 1000)
  }
}

const nextQuestion = () => {
  if (currentQuestionIndex.value < props.quiz.questions.length - 1) {
    currentQuestionIndex.value++
    emit('logEvent', {
      type: 'NEXT_QUESTION',
      index: currentQuestionIndex.value,
    })
  }
}

const prevQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
    emit('logEvent', {
      type: 'PREV_QUESTION',
      index: currentQuestionIndex.value,
    })
  }
}

const submitQuiz = async () => {
  const submission = {
    answers: userAnswers.value,
    timeTaken: props.quiz.is_timed
      ? props.quiz.quiz_time_limit * 60 - quizTimeRemaining.value
      : null,
  }

  try {
    const response = await axios.post(
      `/api/quizzes/${props.quiz.id}/submit/`,
      submission,
    )
    console.log('Quiz submitted successfully:', response.data)

    // Redirect to results page or handle post-submit UI
    router.push({ name: 'CompletedQuiz', params: { id: props.quiz.id } })
  } catch (err) {
    console.error('Error submitting quiz:', err)
  }

  emit('logEvent', { type: 'QUIZ_SUBMITTED', submission })
}

onMounted(() => {
  startQuizTimer()
})
</script>

<style scoped>
.quiz-player-container {
  max-width: 600px;
  margin: auto;
  padding: 20px;
}
.timer {
  text-align: right;
  font-weight: bold;
  color: red;
}
.question-section {
  margin-bottom: 20px;
}
.navigation {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}
</style>
