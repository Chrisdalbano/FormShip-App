<template>
  <div
    class="results flex flex-col items-center justify-center w-full max-w-lg mx-auto p-4"
  >
    <div
      class="score bg-blue-600 text-white rounded-lg p-6 mb-6 w-full text-center shadow-md animate__animated animate__fadeInDown"
    >
      <p class="text-lg font-semibold">Your results</p>
      <span class="total-score text-5xl font-bold">
        {{ score }} / {{ totalQuestions }}
      </span>
      <p class="text-lg mt-2">You earned {{ xpEarned }} points</p>
    </div>

    <ol
      class="answers list-none w-full animate__animated animate__fadeInUp"
      ref="results"
    >
      <li
        v-for="(question, index) in questions"
        :key="question.id"
        class="flex flex-col gap-4 mb-8 p-4 bg-white rounded-lg shadow-md"
      >
        <h3 class="font-medium text-xl">{{ question.question_text }}</h3>
        <p class="font-medium">
          Your answer:
          <span v-if="userAnswers[index]" class="text-blue-500">
            {{ getAnswerContent(question, userAnswers[index]) }}
          </span>
          <span v-else class="text-gray-500">N/A</span>
        </p>
        <span
          role="alert"
          v-if="isAnswerCorrect(question, userAnswers[index])"
          class="correct-answers text-green-600 font-semibold"
        >
          Correct!
        </span>
        <span
          role="alert"
          v-else
          class="incorrect-answers text-red-600 font-semibold"
        >
          Incorrect. The correct answer is:
          {{ getAnswerContent(question, question.correct_answer) }}
        </span>
        <div class="voting flex items-center gap-4">
          <button
            class="bg-transparent border-none cursor-pointer text-2xl transition-transform transform hover:scale-125"
            @click="vote(question.id, 'yes')"
          >
            👍
          </button>
          <button
            class="bg-transparent border-none cursor-pointer text-2xl transition-transform transform hover:scale-125"
            @click="vote(question.id, 'no')"
          >
            👎
          </button>
          <span v-if="votingResults[question.id]" class="text-sm text-gray-600">
            Thanks for your vote: {{ votingResults[question.id] }}
          </span>
        </div>
      </li>
    </ol>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Props
const props = defineProps({
  score: {
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
  xpEarned: {
    type: Number,
    required: true,
  },
})

// Computed property to calculate total number of questions
const totalQuestions = computed(() => props.questions.length)

// Refs and reactive data
const votingResults = ref({})

// Methods
const isAnswerCorrect = (question, userAnswer) => {
  return userAnswer === question.correct_answer
}

const getAnswerContent = (question, answerKey) => {
  switch (answerKey) {
    case 'A':
      return question.option_a
    case 'B':
      return question.option_b
    case 'C':
      return question.option_c || 'N/A'
    default:
      return 'N/A'
  }
}

const vote = (questionId, vote) => {
  // Simple vote handler storing the user's vote in votingResults ref
  votingResults.value = {
    ...votingResults.value,
    [questionId]: vote,
  }
  console.log(`User voted ${vote} for question ID: ${questionId}`)
}
</script>

<style scoped>
@import 'https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css';

.correct-answers {
  color: #16a34a; /* Tailwind green-600 */
}

.incorrect-answers {
  color: #dc2626; /* Tailwind red-600 */
}

.voting button {
  background-color: transparent;
  border: none;
  cursor: pointer;
  font-size: 1.5rem;
  transition: transform 0.3s ease;
}

.voting button:hover {
  transform: scale(1.25);
}
</style>
