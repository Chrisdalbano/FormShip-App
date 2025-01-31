<template>
  <div
    class="quiz-card p-4 rounded-lg shadow-md relative"
    :style="{ backgroundColor: quiz.color || '#ffffff' }"
    draggable="true"
    @dragstart="handleDragStart"
  >
    <h3 class="font-semibold text-lg">{{ quiz.title }}</h3>
    <p class="text-sm text-gray-600 mb-4">Topic: {{ quiz.topic }}</p>
    <div class="flex justify-between">
      <button class="primary-button bg-blue-500" @click="goToManagement">
        Manage
      </button>
      <button class="primary-button bg-green-500" @click="navigateToQuiz">
        Take Quiz
      </button>
      <button @click="toggleMoreOptions" class="more-options-button">
        &#x22EE;
      </button>
    </div>

    <!-- More options dropdown -->
    <div
      v-if="selectedQuizId === quiz.id"
      class="options-dropdown bg-gray-200 absolute top-full left-0 mt-2 p-4 rounded-lg shadow-md z-10"
    >
      <button @click="renameQuiz" class="option-item">Rename</button>
      <button @click="duplicateQuiz" class="option-item">Duplicate</button>
      <button @click="deleteQuiz" class="option-item">Delete</button>
    </div>
    
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const props = defineProps({
  quiz: Object,
  selectedQuizId: [Number, String],
})

const emit = defineEmits([
  'drag-start',
  'navigate-quiz',
  'toggle-options',
  'rename-quiz',
  'duplicate-quiz',
  'delete-quiz',
])

const handleDragStart = () => emit('drag-start', props.quiz)
const navigateToQuiz = () => {
  if (props.quiz.is_published || props.quiz.is_testing) {
    router.push({ name: 'QuizEvent', params: { id: props.quiz.id } })
  } else {
    alert('This quiz is not published or available for testing.')
  }
}

const goToManagement = () =>
  router.push({ name: 'QuizManagement', params: { id: props.quiz.id } })
const toggleMoreOptions = () => emit('toggle-options', props.quiz.id)
const renameQuiz = () => emit('rename-quiz', props.quiz.id)
const duplicateQuiz = () => emit('duplicate-quiz', props.quiz.id)
const deleteQuiz = () => emit('delete-quiz', props.quiz.id)
</script>

<style scoped>
.quiz-card {
  @apply p-4 rounded-lg shadow-md relative;
}
.primary-button {
  @apply text-white px-3 py-2 rounded-lg;
}
.more-options-button {
  @apply text-gray-700;
  position: relative;
}
.options-dropdown {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  position: absolute;
  top: 100%;
  right: 0;
  background-color: #f3f4f6;
  padding: 0.75rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
</style>
