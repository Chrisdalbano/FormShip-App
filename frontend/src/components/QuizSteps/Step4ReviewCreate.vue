<template>
  <div>
    <h2 class="text-xl font-bold mb-2">Step 4: Review & Create</h2>
    <p class="text-gray-700">
      Final step. We attempt quiz creation on the parent. If AI generates
      questions, they appear below.
    </p>

    <!-- If there's any server or AI error -->
    <div v-if="aiError" class="text-red-600 my-2">Error: {{ aiError }}</div>

    <!-- If still loading, show a spinner or message -->
    <div v-if="isLoading" class="my-2 text-blue-600">
      Creating quiz (AI generation)...
    </div>

    <!-- Quiz Summary -->
    <div class="border p-4 mt-4 bg-gray-50 rounded">
      <h3 class="font-semibold mb-2">Quiz Summary</h3>
      <ul class="mt-2 text-sm text-gray-700 space-y-1">
        <li><strong>Title:</strong> {{ quiz.title }}</li>
        <li><strong>Topic:</strong> {{ quiz.topic }}</li>
        <li><strong>Evaluation:</strong> {{ quiz.evaluation_type }}</li>
        <li><strong>Access:</strong> {{ quiz.access_control }}</li>
        <li><strong># Questions:</strong> {{ quiz.question_count }}</li>
        <li><strong># Options:</strong> {{ quiz.option_count }}</li>
      </ul>
      <!-- If we already got a quizId from the backend, show it for reference -->
      <div v-if="quizId" class="mt-2 text-xs text-gray-500">
        <strong>Quiz ID:</strong> {{ quizId }}
      </div>
    </div>

    <!-- AI questions (if successfully generated) -->
    <div v-if="!isLoading && questions.length" class="mt-6">
      <h3 class="font-semibold mb-2">AI-Generated Questions</h3>
      <div v-for="(q, i) in questions" :key="i" class="border-b py-2 text-sm">
        <p>Q{{ i + 1 }}: {{ q.question_text }}</p>
        <ul class="ml-4 text-xs text-gray-600">
          <li v-if="q.option_a">A: {{ q.option_a }}</li>
          <li v-if="q.option_b">B: {{ q.option_b }}</li>
          <li v-if="q.option_c">C: {{ q.option_c }}</li>
          <li v-if="q.option_d">D: {{ q.option_d }}</li>
          <li v-if="q.option_e">E: {{ q.option_e }}</li>
        </ul>
        <p class="text-green-600">Correct: {{ q.correct_answer }}</p>
      </div>
    </div>

    <!-- Navigation / Action Buttons -->
    <div class="flex justify-between mt-6">
      <!-- Step Wizard 'Back' -->
      <button
        class="bg-gray-300 text-gray-700 px-4 py-2 rounded"
        @click="goBack"
        :disabled="isLoading"
      >
        Back
      </button>

      <div class="flex space-x-2">
        <!-- Edit / Test only if quizId is known (already created) -->
        <button
          v-if="quizId"
          class="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded"
          @click="goEdit"
        >
          Edit Quiz
        </button>
        <button
          v-if="quizId"
          class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded"
          @click="goTest"
        >
          Test Quiz
        </button>

        <!-- Final "Finish" (close wizard) -->
        <button
          class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
          @click="finish"
          :disabled="isLoading"
        >
          Finish
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  quiz: {
    type: Object,
    required: true,
  },
  questions: {
    type: Array,
    default: () => [],
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
  aiError: {
    type: String,
    default: '',
  },
  quizId: {
    type: Number,
    default: null,
  },
})

const emit = defineEmits(['prev', 'finish'])

const router = useRouter()

function goBack() {
  // Return to Step 3
  emit('prev')
}

function goEdit() {
  // If no quizId, we can't navigate
  if (!props.quizId) {
    alert('No quiz ID to edit. Please confirm creation first.')
    return
  }
  router.push({ name: 'EditQuiz', params: { id: props.quizId } })
}

function goTest() {
  // If no quizId, we can't navigate
  if (!props.quizId) {
    alert('No quiz ID to test. Please confirm creation first.')
    return
  }
  router.push({ name: 'TestQuiz', params: { id: props.quizId } })
}

function finish() {
  // Possibly close or hide the wizard, or let the parent do final logic
  emit('finish')
}
</script>
