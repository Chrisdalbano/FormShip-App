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
          <label class="block text-md font-semibold mb-1">Option A</label>
          <input
            v-model="question.option_a"
            type="text"
            class="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300"
            required
          />
        </div>
        <div class="mb-4">
          <label class="block text-md font-semibold mb-1">Option B</label>
          <input
            v-model="question.option_b"
            type="text"
            class="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring focus:border-blue-300"
            required
          />
        </div>
        <div class="mb-4">
          <label class="block text-md font-semibold mb-1">Option C</label>
          <input
            v-model="question.option_c"
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
            <option value="C" v-if="question.option_c">C</option>
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

// Route and Router instances
const route = useRoute()
const router = useRouter()
const quizId = route.params.id

// State for the quiz object
const quiz = ref({
  title: '',
  topic: '',
  questions: [],
})

const originalQuiz = ref(null) // To keep track of original state for comparisons

// Base API URL
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

// Fetch quiz data when the component mounts
onMounted(async () => {
  try {
    const response = await axios.get(`${apiBaseUrl}/quizzes/${quizId}/`)
    quiz.value = response.data
    originalQuiz.value = JSON.parse(JSON.stringify(response.data)) // Deep clone to track changes
  } catch (error) {
    console.error('Error fetching quiz:', error)
    alert('Failed to fetch quiz. Please try again later.')
  }
})

// Function to update the quiz and questions
const updateQuiz = async () => {
  try {
    // Update only if title or topic has changed
    if (
      quiz.value.title !== originalQuiz.value.title ||
      quiz.value.topic !== originalQuiz.value.topic
    ) {
      await axios.put(`${apiBaseUrl}/quizzes/${quizId}/`, {
        title: quiz.value.title,
        topic: quiz.value.topic,
        question_count: quiz.value.questions.length,
      })
    }

    // Track changes for each question and send requests accordingly
    for (const question of quiz.value.questions) {
      const originalQuestion = originalQuiz.value.questions.find(
        q => q.id === question.id,
      )

      if (question.id) {
        // Only update if question fields have changed
        if (
          !originalQuestion ||
          JSON.stringify(originalQuestion) !== JSON.stringify(question)
        ) {
          const questionData = {
            question_text: question.question_text,
            option_a: question.option_a,
            option_b: question.option_b,
            option_c: question.option_c,
            correct_answer: question.correct_answer,
          }
          await axios.put(
            `${apiBaseUrl}/questions/${question.id}/`,
            questionData,
          )
        }
      } else {
        // Create new question
        const newQuestionData = {
          ...question,
          quiz: quizId,
        }
        await axios.post(
          `${apiBaseUrl}/quizzes/${quizId}/questions/`,
          newQuestionData,
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

// Function to add a new question to the quiz
const addQuestion = () => {
  quiz.value.questions.push({
    question_text: '',
    option_a: '',
    option_b: '',
    option_c: '',
    correct_answer: 'A',
  })
}

// Function to delete a question from the quiz
const deleteQuestion = async index => {
  const question = quiz.value.questions[index]
  if (question.id) {
    try {
      await axios.delete(`${apiBaseUrl}/questions/${question.id}/`)
    } catch (error) {
      console.error('Error deleting question:', error)
      alert('Failed to delete question. Please try again.')
      return
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
