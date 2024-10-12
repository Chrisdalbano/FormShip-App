<template>
  <div class="zen-container">
    <h1>Test Quiz</h1>
    <div v-if="quiz && !showResults">
      <h2>{{ quiz.title }}</h2>
      <p>Topic: {{ quiz.topic }}</p>
      <div
        v-for="(question, index) in quiz.questions"
        :key="index"
        class="question-block"
      >
        <p>{{ index + 1 }}. {{ question.question_text }}</p>
        <div>
          <label>
            <input
              type="radio"
              :name="'question' + index"
              value="A"
              v-model="userAnswers[index]"
            />
            A. {{ question.option_a }}
          </label>
          <label>
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
        </div>
      </div>
      <button @click="submitAnswers">Submit Answers</button>
    </div>
    <p v-else-if="!quiz">Loading quiz...</p>

    <!-- Use the Results Component -->
    <ResultsView
      v-if="showResults"
      :score="score"
      :totalQuestions="totalQuestions"
      :questions="quiz.questions"
      :userAnswers="userAnswers"
      :xpEarned="calculateXPEarned(score)"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import ResultsView from './ResultsView.vue'

const route = useRoute()
const quiz = ref(null)
const userAnswers = ref([])
const score = ref(0)
const showResults = ref(false)

const quizId = route.params.id
console.log('Quiz ID:', quizId)

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

onMounted(async () => {
  try {
    const response = await axios.get(`${apiBaseUrl}/quizzes/${quizId}/`)
    console.log('Quiz Data:', response.data)
    quiz.value = response.data
    userAnswers.value = Array(response.data.questions.length).fill(null) // Initialize user answers
  } catch (error) {
    console.error('Error fetching quiz:', error)
  }
})

const submitAnswers = () => {
  calculateScore()
  showResults.value = true
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

const totalQuestions = ref(quiz.value ? quiz.value.questions.length : 0)

const calculateXPEarned = score => {
  // You can define your logic to calculate XP here
  return score * 10
}
</script>

<style scoped>
.question-block {
  margin-bottom: 1rem;
}

.results {
  margin-top: 2rem;
}
</style>
