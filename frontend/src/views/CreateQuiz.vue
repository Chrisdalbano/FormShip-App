<template>
  <div class="zen-container">
    <h1>Create a New Quiz</h1>
    <p>Enter the quiz details to generate questions.</p>
    <input v-model="quizTitle" placeholder="Enter quiz title..." />
    <input v-model="quizTopic" placeholder="Enter quiz topic..." />
    <input
      type="number"
      v-model="questionCount"
      placeholder="Enter number of questions..."
    />
    <select v-model="difficulty">
      <option value="easy">Easy</option>
      <option value="medium">Medium</option>
      <option value="hard">Hard</option>
    </select>
    <button @click="handleGenerateQuiz">Generate Quiz</button>
    <p v-if="apiMessage">API Response: {{ apiMessage }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import router from '@/router'

const quizTitle = ref('')
const quizTopic = ref('')
const questionCount = ref(5)
const difficulty = ref('easy')
const apiMessage = ref(null)

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

const handleGenerateQuiz = async () => {
  try {
    // Call the backend to generate the quiz
    const response = await axios.post(`${apiBaseUrl}/create-quiz/`, {
      title: quizTitle.value,
      topic: quizTopic.value,
      question_count: questionCount.value,
      difficulty: difficulty.value,
      quiz_type: 'multiple-choice',
    })
    const createdQuiz = response.data

    // Store the created quiz ID to use later
    console.log('Created Quiz ID:', createdQuiz.id)
    // You may want to navigate directly to play the quiz after it's created
    router.push({ name: 'TestQuiz', params: { id: createdQuiz.id } })
  } catch (error) {
    console.error('Error generating quiz:', error)
    apiMessage.value = 'Error generating quiz. Please try again.'
  }
}
</script>
