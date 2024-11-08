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
      <button class="primary-button bg-green-500" @click="navigateToQuiz">
        Test
      </button>
      <button class="primary-button bg-blue-500" @click="shareQuiz">
        Share
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
      <button @click="editQuiz" class="option-item">Edit</button>
      <button @click="duplicateQuiz" class="option-item">Duplicate</button>
      <button @click="deleteQuiz" class="option-item">Delete</button>
      <button v-if="group" @click="ungroupQuiz" class="option-item">
        Ungroup
      </button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  quiz: Object,
  selectedQuizId: [Number, String],
  group: Object, // Optional, only for grouped quizzes
})

// Define Emits
const emit = defineEmits([
  'drag-start',
  'navigate-quiz',
  'share-quiz',
  'toggle-options',
  'edit-quiz',
  'duplicate-quiz',
  'delete-quiz',
  'ungroup-quiz',
])

// Methods for quiz actions
const handleDragStart = () => emit('drag-start', props.quiz, props.group)
const navigateToQuiz = () => emit('navigate-quiz', props.quiz.id)
const shareQuiz = () => emit('share-quiz', props.quiz.id)
const editQuiz = () => emit('edit-quiz', props.quiz.id)
const duplicateQuiz = () => emit('duplicate-quiz', props.quiz.id)
const deleteQuiz = () => emit('delete-quiz', props.quiz.id)
const toggleMoreOptions = () => emit('toggle-options', props.quiz.id)
const ungroupQuiz = () => emit('ungroup-quiz', props.quiz, props.group)
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
  gap: 1rem;
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.25rem;
  background-color: #f3f4f6;
  padding: 1rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.options-dropdown > * {
  border-bottom: 2px solid black
}
</style>
