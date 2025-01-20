<!-- eslint-disable no-undef -->
<template>
  <div
    class="completed-quiz flex flex-col items-center justify-center w-full max-w-lg mx-auto p-4"
  >
    <!-- Results Section -->
    <div v-if="quiz.display_results" class="results w-full">
      <div
        class="score bg-blue-600 text-white rounded-lg p-6 mb-6 w-full text-center shadow-md"
      >
        <p class="text-lg font-semibold">Your Results</p>
        <span class="total-score text-5xl font-bold">
          {{ score }} / {{ totalQuestions }}
        </span>
        <p class="text-lg mt-2">Thanks for completing the quiz!</p>
      </div>

      <!-- Detailed question-by-question results -->
      <ol class="answers list-none w-full">
        <li
          v-for="(question, index) in questions"
          :key="question.id || index"
          class="question-result flex flex-col gap-2 mb-6 p-4 bg-white rounded-lg shadow-md"
        >
          <h3 class="font-medium text-xl">
            {{ index + 1 }}. {{ question.question_text }}
          </h3>
          <p>
            <strong>Your Answer:</strong>
            <span v-if="userAnswers[index]" class="text-blue-500">
              {{ getAnswerContent(question, userAnswers[index]) }}
            </span>
            <span v-else class="text-gray-500">N/A</span>
          </p>

          <span
            v-if="isAnswerCorrect(question, userAnswers[index])"
            class="text-green-600 font-semibold"
          >
            Correct!
          </span>
          <span v-else class="text-red-600 font-semibold">
            Incorrect. Correct answer:
            {{ getAnswerContent(question, question.correct_answer) }}
          </span>
        </li>
      </ol>
    </div>

    <!-- Thank You Section -->
    <div v-else class="hidden-results w-full">
      <div
        class="bg-blue-100 text-gray-800 rounded-lg p-6 mb-6 w-full text-center shadow-md"
      >
        <p class="text-lg font-semibold mb-2">Quiz Completed</p>
        <p>Thank you for taking the quiz!</p>
        <p>Results will be shared later or reviewed by the instructor.</p>
      </div>
    </div>

    <!-- Retake button (if allowed) -->
    <button
      v-if="quiz.is_testing"
      class="bg-gray-400 text-white px-4 py-2 rounded mt-4"
      @click="onRetake"
    >
      Retake Quiz
    </button>

    <!-- Back to Dashboard -->
    <button
      class="bg-blue-600 text-white px-4 py-2 rounded mt-4"
      @click="goToDashboard"
    >
      Back to Dashboard
    </button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { defineProps } from 'vue'

// Props
defineProps({
  quiz: {
    type: Object,
    required: true,
  },
  score: {
    type: Number,
    required: true,
  },
  totalQuestions: {
    type: Number,
    required: true,
  },
  questions: {
    type: Array,
    required: true,
    default: () => [],
  },
  userAnswers: {
    type: Array,
    required: true,
    default: () => [],
  },
})

// Router
const router = useRouter()

// Methods
function isAnswerCorrect(question, userAnswer) {
  return userAnswer === question.correct_answer
}

function getAnswerContent(question, answerKey) {
  if (!answerKey) return 'N/A'
  switch (answerKey) {
    case 'A':
      return question.option_a || 'N/A'
    case 'B':
      return question.option_b || 'N/A'
    case 'C':
      return question.option_c || 'N/A'
    case 'D':
      return question.option_d || 'N/A'
    case 'E':
      return question.option_e || 'N/A'
    default:
      return 'N/A'
  }
}

function onRetake() {
  // eslint-disable-next-line no-undef
  router.push({ name: 'QuizEvent', params: { id: quiz.id } })
}

function goToDashboard() {
  router.push({ name: 'QuizDashboard' })
}
</script>
<style scoped>
.completed-quiz {
  margin-top: 1rem;
}

.score {
  animation: fadeInDown 0.5s;
}

.answers {
  animation: fadeInUp 0.5s;
}

.question-result {
  border-left: 4px solid #ddd;
  padding-left: 1rem;
}

/* Optional animations */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}
</style>
