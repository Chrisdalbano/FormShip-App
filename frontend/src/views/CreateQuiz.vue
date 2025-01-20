<template>
  <div class="create-quiz-wizard-container flex space-x-8">
    <!-- LEFT: Steps Container -->
    <div class="w-2/3 bg-white p-6 rounded-lg shadow-lg">
      <!-- Step indicators -->
      <div class="mb-4 flex space-x-2 items-center">
        <div
          v-for="n in totalSteps"
          :key="n"
          class="px-3 py-1 rounded-full cursor-pointer"
          :class="{
            'bg-blue-600 text-white': currentStep === n,
            'bg-gray-200 text-gray-800': currentStep !== n,
          }"
          @click="goToStep(n)"
          :disabled="alreadyCreated"
        >
          Step {{ n }}
        </div>
      </div>

      <!-- Dynamic Step Components -->
      <component
        :is="currentStepComponent"
        :quiz="quiz"
        :questions="questions"
        :isLoading="isLoading"
        :aiError="aiError"
        :quizId="quizId"
        :aiGenerationFailed="aiGenerationFailed"
        :alreadyCreated="alreadyCreated"
        @update-quiz="onUpdateQuiz"
        @next="goNext"
        @prev="goPrev"
        @finish="finishAndCreate"
      />
    </div>

    <!-- RIGHT: Live Preview -->
    <div class="w-1/3">
      <h3 class="text-lg font-semibold mb-2">Live Preview</h3>
      <QuizPreviewCard :quiz="quiz" :interactive="true" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/store/auth'

// Step components
import Step1BasicEval from '../components/QuizSteps/Step1BasicEval.vue'
import Step2AIGeneration from '../components/QuizSteps/Step2AIGeneration.vue'
import Step3LayoutToggles from '../components/QuizSteps/Step3LayoutToggles.vue'
import Step4ReviewCreate from '../components/QuizSteps/Step4ReviewCreate.vue'

// Reuse a preview card
import QuizPreviewCard from '@/components/QuizPreviewCard.vue'

// Pinia store
const authStore = useAuthStore()

// Wizard data
const totalSteps = 4
const currentStep = ref(1)

// Quiz object
const quiz = ref({
  title: '',
  topic: '',
  evaluation_type: 'pre', // pre, hybrid, post
  is_testing: false,
  is_published: false,
  access_control: 'public', // public, invitation, login_required

  question_count: 5,
  option_count: 4,
  use_knowledge_base: false,
  knowledge_base_text: '',

  quiz_type: 'standard',
  skippable_questions: true,
  stepwise_time_limit: null,

  is_timed: false,
  quiz_time_limit: null,
  time_per_question: false,
  question_time_limit: null,

  display_results: true,
  require_password: false,
  password: '',
  allow_anonymous: false,
  require_name: false,
})

// AI-generated questions
const questions = ref([])

// States
const isLoading = ref(false)
const aiError = ref('')
const aiGenerationFailed = ref(false)
const alreadyCreated = ref(false)
const quizId = ref(null)

// Current step
const currentStepComponent = computed(() => {
  switch (currentStep.value) {
    case 1:
      return Step1BasicEval
    case 2:
      return Step2AIGeneration
    case 3:
      return Step3LayoutToggles
    case 4:
      return Step4ReviewCreate
    default:
      return Step1BasicEval
  }
})

function onUpdateQuiz(updatedData) {
  quiz.value = { ...quiz.value, ...updatedData }
}

function goNext() {
  if (currentStep.value < totalSteps) {
    currentStep.value++
  }
}

function goPrev() {
  if (currentStep.value > 1 && !alreadyCreated.value) {
    currentStep.value--
  }
}

function goToStep(n) {
  if (n >= 1 && n <= totalSteps && !alreadyCreated.value) {
    currentStep.value = n
  }
}

async function finishAndCreate() {
  currentStep.value = 4 // Ensure we stay on the last step
  aiError.value = ''
  aiGenerationFailed.value = false

  if (alreadyCreated.value) {
    console.log('Quiz already created. Skipping new POST.')
    return
  }

  isLoading.value = true
  questions.value = [] // Reset questions
  try {
    const payload = {
      title: quiz.value.title.trim(),
      topic: quiz.value.topic.trim(),
      evaluation_type: quiz.value.evaluation_type,
      is_testing: quiz.value.is_testing,
      is_published: quiz.value.is_published,
      access_control: quiz.value.access_control,

      question_count: quiz.value.question_count,
      option_count: quiz.value.option_count,
      difficulty: 'easy',
      knowledge_base: quiz.value.use_knowledge_base
        ? quiz.value.knowledge_base_text
        : null,

      display_results: quiz.value.display_results,
      require_password: quiz.value.require_password,
      password: quiz.value.require_password ? quiz.value.password : '',
      allow_anonymous: quiz.value.allow_anonymous,
      require_name: quiz.value.require_name,

      is_timed: quiz.value.is_timed,
      quiz_time_limit: quiz.value.is_timed ? quiz.value.quiz_time_limit : null,
      are_questions_timed:
        quiz.value.quiz_type === 'standard' && quiz.value.time_per_question,
      time_per_question: quiz.value.time_per_question
        ? quiz.value.question_time_limit
        : null,

      quiz_type: quiz.value.quiz_type,
      skippable_questions:
        quiz.value.quiz_type === 'stepwise'
          ? quiz.value.skippable_questions
          : false,
      stepwise_time_limit:
        quiz.value.quiz_type === 'stepwise' && !quiz.value.skippable_questions
          ? quiz.value.stepwise_time_limit
          : null,

      segment_steps: false,
      allow_previous_questions: false,

      account_id: authStore.account?.id,
    }

    console.log('Sending payload to /quizzes/create:', payload)

    const url = `${import.meta.env.VITE_API_BASE_URL}/quizzes/create/`
    const { data } = await axios.post(url, payload, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })

    console.log('Response received from /quizzes/create:', data)

    if (!data?.id) {
      throw new Error('No quiz ID returned from server.')
    }

    alreadyCreated.value = true
    quizId.value = data.id

    if (data.questions && data.questions.length) {
      console.log('AI-generated questions:', data.questions)
      for (const q of data.questions) {
        if (!q.correct_answer) q.correct_answer = 'A'
        questions.value.push(q)
        await new Promise(r => setTimeout(r, 300))
      }
    }
  } catch (err) {
    console.error(
      'Error during quiz creation:',
      err.response || err.message || err,
    )
    aiError.value =
      err.response?.data?.error || err.message || 'Failed to create quiz.'
    aiGenerationFailed.value = true
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.create-quiz-wizard-container {
  margin-top: 2rem;
}
</style>
