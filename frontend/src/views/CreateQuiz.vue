<template>
  <div
    class="create-quiz-container w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg"
  >
    <h1 class="text-3xl font-bold mb-4">Create a New Quiz</h1>

    <form @submit.prevent="createQuiz">
      <!-- 1. Basic Info -->
      <div class="mb-4">
        <label class="block text-lg font-semibold mb-2">Quiz Title</label>
        <input
          v-model="quiz.title"
          type="text"
          placeholder="Give your quiz a name"
          class="input-field"
          required
        />
      </div>

      <div class="mb-4">
        <label class="block text-lg font-semibold mb-2"
          >Quiz Topic/Description</label
        >
        <input
          v-model="quiz.topic"
          type="text"
          placeholder="Short description or topic"
          class="input-field"
          required
        />
      </div>

      <!-- 2. Evaluation Type & Testing Mode -->
      <div class="mb-4">
        <label class="block text-lg font-semibold mb-2">Evaluation Type</label>
        <select v-model="quiz.evaluation_type" class="input-field">
          <option value="pre">Pre-Evaluated</option>
          <option value="hybrid">Hybrid</option>
          <option value="post">Post-Evaluated</option>
        </select>
        <p class="text-sm text-gray-600 mt-1">
          <strong>Pre-Evaluated:</strong> fully auto-graded;
          <strong>Hybrid:</strong> partial auto-grade & free-text;
          <strong>Post-Evaluated:</strong> manual grading needed.
        </p>
      </div>

      <div class="flex items-center mb-4">
        <input
          id="isTesting"
          type="checkbox"
          v-model="quiz.is_testing"
          class="mr-2"
        />
        <label for="isTesting" class="text-gray-700">
          **Testing Mode** (No real results recorded)
        </label>
      </div>

      <!-- 3. Publish & Access Control -->
      <div class="flex items-center mb-4">
        <input
          id="isPublished"
          type="checkbox"
          v-model="quiz.is_published"
          class="mr-2"
        />
        <label for="isPublished" class="text-gray-700">
          Publish This Quiz Immediately?
        </label>
      </div>

      <div class="mb-4">
        <label class="block text-lg font-semibold mb-2">Access Control</label>
        <select v-model="quiz.access_control" class="input-field">
          <option value="public">Public</option>
          <option value="invitation">Invitation Only</option>
          <option value="login_required">Login Required</option>
        </select>
        <p class="text-sm text-gray-600 mt-1">
          <strong>Public:</strong> anyone with link can attempt;
          <strong>Invitation Only:</strong> must be invited;
          <strong>Login Required:</strong> user must be authenticated.
        </p>
      </div>

      <!-- 4. AI Generation & Knowledge Base -->
      <div class="mb-4">
        <label class="block text-lg font-semibold mb-2"
          >Number of Questions</label
        >
        <input
          v-model.number="quiz.question_count"
          type="number"
          min="1"
          max="25"
          class="input-field"
          required
        />
      </div>

      <div class="mb-4">
        <label class="block text-lg font-semibold mb-2"
          >Options per Question</label
        >
        <input
          v-model.number="quiz.option_count"
          type="number"
          min="2"
          max="5"
          class="input-field"
          required
        />
      </div>

      <div class="flex items-center mb-4">
        <input
          id="useKnowledgeBase"
          type="checkbox"
          v-model="quiz.use_knowledge_base"
          class="mr-2"
        />
        <label for="useKnowledgeBase" class="text-gray-700">
          Use My Own Knowledge Base for AI Generation
        </label>
      </div>

      <div v-if="quiz.use_knowledge_base" class="mb-4">
        <label class="block text-lg font-semibold mb-2">
          Knowledge Base Input (Text or File)
        </label>
        <textarea
          v-model="quiz.knowledge_base_text"
          rows="4"
          class="input-field mb-2"
          placeholder="Paste your knowledge base text here..."
        ></textarea>
        <input type="file" @change="handleFileUpload" class="input-field" />
      </div>

      <!-- 5. Quiz Layout & Timers -->
      <div class="mb-4">
        <label class="block text-lg font-semibold mb-2">Quiz Layout Type</label>
        <select v-model="quiz.quiz_type" class="input-field">
          <option value="standard">All-at-Once (Standard)</option>
          <option value="stepwise">Stepwise (One Question at a Time)</option>
        </select>
      </div>

      <!-- Stepwise fields -->
      <div
        v-if="quiz.quiz_type === 'stepwise'"
        class="mb-4 pl-4 border-l-2 border-blue-300"
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
        <div v-if="!quiz.skippable_questions" class="mb-2 ml-4">
          <label class="block text-sm">Time Limit per Step (seconds)</label>
          <input
            type="number"
            v-model.number="quiz.stepwise_time_limit"
            min="5"
            class="input-field"
          />
        </div>
      </div>

      <!-- Timer settings -->
      <div class="mb-4">
        <label class="inline-flex items-center mb-1">
          <input type="checkbox" v-model="quiz.is_timed" class="mr-2" />
          Overall Time Limit (minutes)?
        </label>
        <div v-if="quiz.is_timed" class="ml-4 mt-2">
          <input
            type="number"
            v-model.number="quiz.quiz_time_limit"
            min="1"
            class="input-field"
            placeholder="Time limit in minutes"
          />
        </div>
      </div>

      <div v-if="quiz.quiz_type === 'standard'" class="mb-4">
        <label class="inline-flex items-center mb-1">
          <input
            type="checkbox"
            v-model="quiz.time_per_question"
            class="mr-2"
          />
          Time Limit per Question (seconds)?
        </label>
        <div v-if="quiz.time_per_question" class="ml-4 mt-2">
          <input
            type="number"
            v-model.number="quiz.question_time_limit"
            min="5"
            class="input-field"
            placeholder="Time limit per question"
          />
        </div>
      </div>

      <!-- 6. Misc Options -->
      <div class="mb-4">
        <label class="inline-flex items-center mb-1">
          <input type="checkbox" v-model="quiz.display_results" class="mr-2" />
          Display Results Immediately After Quiz?
        </label>
      </div>

      <div class="mb-4">
        <label class="inline-flex items-center mb-1">
          <input type="checkbox" v-model="quiz.require_password" class="mr-2" />
          Password Protect This Quiz?
        </label>
        <input
          v-if="quiz.require_password"
          type="password"
          v-model="quiz.password"
          class="input-field mt-2"
          placeholder="Enter quiz password"
        />
      </div>

      <div class="mb-4">
        <label class="inline-flex items-center mb-1">
          <input type="checkbox" v-model="quiz.allow_anonymous" class="mr-2" />
          Allow Anonymous Users?
        </label>
      </div>

      <div class="mb-6">
        <label class="inline-flex items-center mb-1">
          <input type="checkbox" v-model="quiz.require_name" class="mr-2" />
          Require Participant Name/Nickname?
        </label>
      </div>

      <button
        type="submit"
        class="w-full bg-blue-500 hover:bg-blue-700 text-white px-4 py-2 rounded font-semibold"
        :disabled="loading"
      >
        <span v-if="!loading">Create Quiz</span>
        <span v-else>Creating...</span>
      </button>
    </form>

    <!-- Show spinner while AI is generating questions, if desired -->
    <div v-if="loading" class="mt-4 text-center">
      <div class="spinner mx-auto"></div>
      <p class="mt-2">Generating your quiz with AI, please wait...</p>
    </div>

    <!-- Generated questions preview -->
    <div v-if="questions.length" class="generated-questions mt-6">
      <h2 class="text-xl font-semibold mb-2">Generated Questions</h2>
      <div
        v-for="(question, index) in questions"
        :key="index"
        class="border-b border-gray-300 py-2"
      >
        <h3 class="font-semibold">Question {{ index + 1 }}</h3>
        <p class="mt-1">{{ question.question_text }}</p>
        <!-- If you want, list the options here: option_a, etc. -->
      </div>
      <!-- Buttons to go to Edit or Test the newly created quiz -->
      <div class="mt-4 space-y-2">
        <button
          @click="goToEditPage"
          class="w-full bg-yellow-500 text-white py-2 rounded hover:bg-yellow-700"
        >
          Edit Quiz
        </button>
        <button
          @click="goToTestQuiz"
          class="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700"
        >
          Test Quiz
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

// If your app auto-loads from .env
const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const router = useRouter()
const authStore = useAuthStore()

// Spinner/loading state
const loading = ref(false)
// Holds the AI-generated question previews
const questions = ref([])
let createdQuizId = null

// Our big reactive object for quiz creation
const quiz = ref({
  // Basic
  title: '',
  topic: '',

  // New fields
  evaluation_type: 'pre', // pre, hybrid, post
  is_testing: false, // toggles "test-only" mode
  is_published: false, // published or draft
  access_control: 'public', // public, invitation, login_required

  // AI generation
  question_count: 5,
  option_count: 4,
  use_knowledge_base: false,
  knowledge_base_text: '',

  // Layout type
  quiz_type: 'standard', // standard or stepwise
  skippable_questions: true, // relevant if stepwise
  stepwise_time_limit: null, // if !skippable

  // Timers
  is_timed: false,
  quiz_time_limit: null,
  time_per_question: false,
  question_time_limit: null,

  // Additional toggles
  display_results: true,
  require_password: false,
  password: '',
  allow_anonymous: false,
  require_name: false,
})

/**
 * If the user picks a file for knowledge base, read it into quiz.knowledge_base_text
 */
function handleFileUpload(evt) {
  const file = evt.target.files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = e => {
    quiz.value.knowledge_base_text = e.target?.result || ''
  }
  reader.readAsText(file)
}

/**
 * Actually call your Django backend to create the quiz.
 * This merges your new fields + old AI generation logic.
 */
async function createQuiz() {
  loading.value = true
  try {
    const payload = {
      title: quiz.value.title.trim(),
      topic: quiz.value.topic.trim(),

      // new fields
      evaluation_type: quiz.value.evaluation_type,
      is_testing: quiz.value.is_testing,
      is_published: quiz.value.is_published,
      access_control: quiz.value.access_control,

      // AI question gen fields
      question_count: quiz.value.question_count,
      option_count: quiz.value.option_count,
      difficulty: 'medium', // or let user pick
      knowledge_base: quiz.value.use_knowledge_base
        ? quiz.value.knowledge_base_text
        : null,

      // Layout & timers
      quiz_type: quiz.value.quiz_type,
      skippable_questions:
        quiz.value.quiz_type === 'stepwise'
          ? quiz.value.skippable_questions
          : false,
      stepwise_time_limit:
        quiz.value.quiz_type === 'stepwise' && !quiz.value.skippable_questions
          ? quiz.value.stepwise_time_limit
          : null,

      is_timed: quiz.value.is_timed,
      quiz_time_limit: quiz.value.is_timed ? quiz.value.quiz_time_limit : null,
      are_questions_timed:
        quiz.value.quiz_type === 'standard'
          ? quiz.value.time_per_question
          : false,
      time_per_question: quiz.value.time_per_question
        ? quiz.value.question_time_limit
        : null,

      // Additional toggles
      display_results: quiz.value.display_results,
      require_password: quiz.value.require_password,
      password: quiz.value.require_password ? quiz.value.password : '',
      allow_anonymous: quiz.value.allow_anonymous,
      require_name: quiz.value.require_name,

      // Make sure your backend can handle account_id
      account_id: authStore.account?.id,
    }

    // POST to /quizzes/create/ with token
    const res = await axios.post(`${apiBaseUrl}/quizzes/create/`, payload, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })

    // If successful, we get the new quiz ID plus any AI-generated questions
    if (!res.data.id) {
      throw new Error('No quiz ID returned from backend.')
    }

    createdQuizId = res.data.id
    questions.value = res.data.questions || []
    alert('Quiz created successfully, see below for generated questions.')
  } catch (err) {
    console.error('Error creating quiz:', err)
    alert('Failed to create quiz. See console for details.')
    questions.value = []
  } finally {
    loading.value = false
  }
}

/**
 * After creation, let user jump to Edit
 */
function goToEditPage() {
  if (!createdQuizId) {
    alert('No quiz has been created yet!')
    return
  }
  router.push({ name: 'EditQuiz', params: { id: createdQuizId } })
}

/**
 * Or go to the "TestQuiz" route
 */
function goToTestQuiz() {
  if (!createdQuizId) {
    alert('No quiz has been created yet!')
    return
  }
  router.push({ name: 'TestQuiz', params: { id: createdQuizId } })
}
</script>

<style scoped>
.create-quiz-container {
  margin-top: 2rem;
}

/* Reuse your .input-field, .spinner, etc. as before */
.input-field {
  @apply w-full border border-gray-300 px-3 py-2 rounded focus:outline-none focus:ring;
  margin-bottom: 0.5rem;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border-left-color: #09f;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
