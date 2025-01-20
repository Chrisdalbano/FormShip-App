<template>
  <div
    class="edit-quiz-container w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg"
  >
    <h1 class="text-3xl font-bold mb-4">Edit Quiz</h1>

    <div v-if="loading" class="text-center text-gray-600">Loading quiz...</div>

    <form v-else @submit.prevent="updateQuiz">
      <!-- Basic Info -->
      <div class="mb-4">
        <label class="block text-lg font-semibold mb-2">Quiz Title</label>
        <input v-model="quiz.title" type="text" class="input-field" required />
      </div>

      <div class="mb-4">
        <label class="block text-lg font-semibold mb-2"
          >Topic/Description</label
        >
        <input v-model="quiz.topic" type="text" class="input-field" required />
      </div>

      <!-- Evaluation Type & Testing -->
      <div class="mb-4">
        <label class="block text-lg font-semibold mb-2">Evaluation Type</label>
        <select v-model="quiz.evaluation_type" class="input-field">
          <option value="pre">Pre-Evaluated</option>
          <option value="hybrid">Hybrid</option>
          <option value="post">Post-Evaluated</option>
        </select>
      </div>

      <div class="flex items-center mb-4">
        <input
          id="isTesting"
          type="checkbox"
          v-model="quiz.is_testing"
          class="mr-2"
        />
        <label for="isTesting" class="text-gray-700"> Test-Only Mode </label>
      </div>

      <!-- Publish & Access Control -->
      <div class="flex items-center mb-4">
        <input
          id="isPublished"
          type="checkbox"
          v-model="quiz.is_published"
          class="mr-2"
        />
        <label for="isPublished" class="text-gray-700">
          Publish This Quiz?
        </label>
      </div>

      <div class="mb-4">
        <label class="block text-lg font-semibold mb-2">Access Control</label>
        <select v-model="quiz.access_control" class="input-field">
          <option value="public">Public</option>
          <option value="invitation">Invitation Only</option>
          <option value="login_required">Login Required</option>
        </select>
      </div>

      <!-- Quiz Layout (quiz_type) -->
      <div class="mb-4">
        <label class="block text-lg font-semibold mb-2">Quiz Layout</label>
        <select v-model="quiz.quiz_type" class="input-field">
          <option value="standard">All-at-Once (Standard)</option>
          <option value="stepwise">Stepwise (One at a Time)</option>
        </select>
      </div>

      <!-- Stepwise fields -->
      <div
        v-if="quiz.quiz_type === 'stepwise'"
        class="pl-4 border-l-2 border-blue-300 mb-4"
      >
        <div class="mb-2">
          <label class="inline-flex items-center">
            <input
              type="checkbox"
              v-model="quiz.skippable_questions"
              class="mr-2"
            />
            Allow Skipping Questions?
          </label>
        </div>
        <div class="mb-2">
          <label class="inline-flex items-center">
            <input
              type="checkbox"
              v-model="quiz.allow_previous_questions"
              class="mr-2"
            />
            Allow Going Back to Previous Questions?
          </label>
        </div>
        <div class="mb-2">
          <label class="inline-flex items-center">
            <input
              type="checkbox"
              v-model="quiz.are_questions_timed"
              class="mr-2"
            />
            Time Limit per Question?
          </label>
          <div v-if="quiz.are_questions_timed" class="ml-4 mt-2">
            <label class="block text-sm mb-1">Seconds per Question</label>
            <input
              type="number"
              v-model.number="quiz.time_per_question"
              min="5"
              class="input-field"
            />
          </div>
        </div>
      </div>

      <!-- Standard Quiz Timers -->
      <div
        v-if="quiz.quiz_type === 'standard'"
        class="mb-4 pl-4 border-l-2 border-blue-300"
      >
        <div class="mb-2">
          <label class="inline-flex items-center">
            <input type="checkbox" v-model="quiz.is_timed" class="mr-2" />
            Overall Time Limit (minutes)?
          </label>
        </div>
        <div v-if="quiz.is_timed" class="ml-4 mt-2">
          <label class="block text-sm mb-1">Total Time (minutes)</label>
          <input
            type="number"
            v-model.number="quiz.quiz_time_limit"
            min="1"
            class="input-field"
          />
        </div>
      </div>

      <!-- Display Results, Password, Anonymous, etc. -->
      <div class="mb-4">
        <label class="inline-flex items-center mb-1">
          <input type="checkbox" v-model="quiz.display_results" class="mr-2" />
          Display Results to Participant After Finishing?
        </label>
      </div>

      <div class="mb-4">
        <label class="inline-flex items-center mb-1">
          <input type="checkbox" v-model="quiz.require_password" class="mr-2" />
          Require Password?
        </label>
        <input
          v-if="quiz.require_password"
          type="password"
          v-model="quiz.password"
          class="input-field mt-2"
          placeholder="Quiz password"
        />
      </div>

      <div class="mb-4">
        <label class="inline-flex items-center mb-1">
          <input type="checkbox" v-model="quiz.allow_anonymous" class="mr-2" />
          Allow Anonymous Access?
        </label>
      </div>

      <div class="mb-6">
        <label class="inline-flex items-center mb-1">
          <input type="checkbox" v-model="quiz.require_name" class="mr-2" />
          Require Participant Name/Nickname?
        </label>
      </div>

      <!-- Question Editing -->
      <div
        v-for="(question, index) in quiz.questions"
        :key="question.id || index"
        class="mb-6 p-4 border rounded-lg"
      >
        <h3 class="text-lg font-semibold mb-2">Question {{ index + 1 }}</h3>
        <div class="mb-2">
          <label class="block font-medium">Question Text</label>
          <input
            v-model="question.question_text"
            type="text"
            class="input-field"
            required
          />
        </div>
        <div class="mb-2">
          <label class="block font-medium">Number of Options (2 - 5)</label>
          <select
            v-model="question.option_count"
            @change="adjustOptions(question)"
            class="input-field"
          >
            <option v-for="n in 5" :key="n" :value="n">{{ n }}</option>
          </select>
        </div>
        <!-- Options -->
        <div
          v-for="opt in visibleOptions(question)"
          :key="opt.field"
          class="mb-2 pl-4"
        >
          <label class="block font-medium">{{ opt.label }}</label>
          <input
            v-model="question[opt.field]"
            type="text"
            class="input-field"
          />
        </div>

        <div class="mb-2">
          <label class="block font-medium">Correct Answer</label>
          <select v-model="question.correct_answer" class="input-field">
            <option value="A">A</option>
            <option value="B">B</option>
            <option v-if="question.option_c" value="C">C</option>
            <option v-if="question.option_d" value="D">D</option>
            <option v-if="question.option_e" value="E">E</option>
          </select>
        </div>

        <button
          type="button"
          class="mt-2 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-700"
          @click="deleteQuestion(index)"
        >
          Delete This Question
        </button>
      </div>

      <button
        type="button"
        class="mb-6 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-700"
        @click="addQuestion"
      >
        Add Another Question
      </button>

      <button
        type="submit"
        class="w-full bg-blue-600 hover:bg-blue-800 text-white px-4 py-2 rounded font-semibold"
      >
        Save Changes
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/store/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()



const quizId = route.params.id
const loading = ref(true)

// The quiz object from the backend
const quiz = ref({
  title: '',
  topic: '',
  evaluation_type: 'pre',
  is_testing: false,
  is_published: false,
  access_control: 'public',

  questions: [],

  quiz_type: 'standard',
  skippable_questions: false,
  allow_previous_questions: false,
  are_questions_timed: false,
  time_per_question: null,

  is_timed: false,
  quiz_time_limit: null,

  display_results: true,
  require_password: false,
  password: '',
  allow_anonymous: false,
  require_name: false,
})

// For controlling how many option fields to show
const optionsConfig = [
  { label: 'Option A', field: 'option_a' },
  { label: 'Option B', field: 'option_b' },
  { label: 'Option C', field: 'option_c' },
  { label: 'Option D', field: 'option_d' },
  { label: 'Option E', field: 'option_e' },
]

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

onMounted(async () => {
  try {
    const res = await axios.get(`${apiBaseUrl}/quizzes/${quizId}/`)
    quiz.value = res.data
    // For each question, figure out how many options are actually used
    quiz.value.questions.forEach(q => {
      q.option_count = calculateOptionCount(q)
    })
  } catch (err) {
    console.error('Error fetching quiz data:', err)
  } finally {
    loading.value = false
  }
})

/**
 * Submits updated quiz info to the backend (PUT /quizzes/:id/).
 * Then updates each question individually (PUT /questions/:id/) or creates new ones if needed.
 */
const updateQuiz = async () => {
  try {
    const payload = {
      title: quiz.value.title.trim(),
      topic: quiz.value.topic.trim(),
      evaluation_type: quiz.value.evaluation_type,
      is_testing: quiz.value.is_testing,
      is_published: quiz.value.is_published,
      access_control: quiz.value.access_control,

      quiz_type: quiz.value.quiz_type,
      skippable_questions: quiz.value.skippable_questions,
      allow_previous_questions: quiz.value.allow_previous_questions,
      are_questions_timed: quiz.value.are_questions_timed,
      time_per_question: quiz.value.are_questions_timed
        ? quiz.value.time_per_question
        : null,

      is_timed: quiz.value.is_timed,
      quiz_time_limit: quiz.value.is_timed ? quiz.value.quiz_time_limit : null,

      display_results: quiz.value.display_results,
      require_password: quiz.value.require_password,
      password: quiz.value.require_password ? quiz.value.password : '',
      allow_anonymous: quiz.value.allow_anonymous,
      require_name: quiz.value.require_name,

      // You might also need question_count or difficulty if your backend requires them
      question_count: quiz.value.questions.length,
      difficulty: quiz.value.difficulty || 'medium',

      account_id: authStore.account?.id,
    }

    // 1. Update the main quiz
    await axios.put(`${apiBaseUrl}/quizzes/${quizId}/`, payload, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })

    // 2. Update or create each question
    for (const question of quiz.value.questions) {
      const questionData = {
        question_text: question.question_text || '',
        option_a: question.option_a || null,
        option_b: question.option_b || null,
        option_c: question.option_c || null,
        option_d: question.option_d || null,
        option_e: question.option_e || null,
        correct_answer: question.correct_answer || 'A',
      }

      if (question.id) {
        // Existing question => PUT
        await axios.put(
          `${apiBaseUrl}/questions/${question.id}/`,
          questionData,
          {
            headers: { Authorization: `Bearer ${authStore.token}` },
          },
        )
      } else {
        // New question => POST
        questionData.quiz = quizId
        await axios.post(
          `${apiBaseUrl}/quizzes/${quizId}/questions/`,
          questionData,
          {
            headers: { Authorization: `Bearer ${authStore.token}` },
          },
        )
      }
    }

    alert('Quiz updated successfully!')
    router.push({ name: 'QuizDashboard' })
  } catch (error) {
    console.error('Error updating quiz:', error.response?.data || error)
    alert('Failed to update quiz. Check console for details.')
  }
}

/**
 * Add a new blank question to local state
 */
const addQuestion = () => {
  quiz.value.questions.push({
    question_text: '',
    option_a: '',
    option_b: '',
    option_c: '',
    option_d: '',
    option_e: '',
    correct_answer: 'A',
    option_count: 2, // default to 2
  })
}

/**
 * Adjust the 'option_count' if the user picks e.g. 4 => we show 4 option fields
 */
const adjustOptions = question => {
  question.option_count = Math.max(2, Math.min(question.option_count, 5))
  // If the user decreased from 5 to 3, you might want to clear the extra fields, etc.
}

/**
 * Return only the relevant option fields for the chosen 'option_count'
 */
const visibleOptions = question => {
  return optionsConfig.slice(0, question.option_count)
}

/**
 * Remove a question from the local array and optionally delete from backend if it has an id
 */
const deleteQuestion = async index => {
  const q = quiz.value.questions[index]
  if (q.id) {
    try {
      await axios.delete(`${apiBaseUrl}/questions/${q.id}/`, {
        headers: { Authorization: `Bearer ${authStore.token}` },
      })
    } catch (err) {
      console.error('Error deleting question:', err)
      alert('Failed to delete question from server.')
    }
  }
  quiz.value.questions.splice(index, 1)
}

/**
 * Count how many option fields are actually used (A-E) so we can set "option_count"
 */
const calculateOptionCount = q => {
  let count = 0
  if (q.option_a) count++
  if (q.option_b) count++
  if (q.option_c) count++
  if (q.option_d) count++
  if (q.option_e) count++
  return Math.max(count, 2)
}
</script>

<style scoped>
.edit-quiz-container {
  margin-top: 2rem;
}

.input-field {
  @apply w-full border border-gray-300 px-3 py-2 rounded focus:outline-none focus:ring;
  margin-bottom: 0.5rem;
}
</style>
