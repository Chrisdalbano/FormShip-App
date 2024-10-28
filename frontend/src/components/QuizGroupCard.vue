<template>
  <div
    class="group-card p-4 rounded-lg shadow-md"
    :style="{ backgroundColor: group.color || '#f3f4f6' }"
    draggable="true"
    @dragover.prevent
    @drop="handleGroupDrop"
  >
    <div class="flex justify-between items-center flex-col mb-4">
      <div class="flex items-center">
        <h3 class="font-bold text-xl cursor-pointer" @click="toggleGroupExpand">
          {{ group.name }}
        </h3>
        <button @click="toggleGroupExpand" class="ml-2">
          <span v-if="isExpanded">&#9660;</span>
          <span v-else>&#9658;</span>
        </button>
      </div>
      <div class="flex gap-2">
        <button class="group-options-button" @click="onRenameGroup">
          Rename
        </button>
        <button class="group-options-button" @click="onDeleteGroup">
          Delete
        </button>
        <button class="group-options-button" @click="onUpdateColor">
          Update Color
        </button>
      </div>
    </div>

    <!-- Quiz list displayed only if the group is expanded -->
    <div v-if="isExpanded" class="quiz-grid grid grid-cols-1 gap-4">
      <QuizCard
        v-for="quiz in group.quizzes"
        :key="quiz.id"
        :quiz="quiz"
        :selectedQuizId="selectedQuizId"
        :group="group"
        @drag-start="$emit('drag-start', quiz, group)"
        @navigate-quiz="$emit('navigate-quiz', quiz.id)"
        @share-quiz="$emit('share-quiz', quiz.id)"
        @toggle-options="$emit('toggle-options', quiz.id)"
        @edit-quiz="$emit('edit-quiz', quiz.id)"
        @duplicate-quiz="$emit('duplicate-quiz', quiz.id)"
        @delete-quiz="$emit('delete-quiz', quiz.id)"
        @ungroup-quiz="$emit('ungroup-quiz', quiz, group)"
      />
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import QuizCard from './QuizCard.vue'

const props = defineProps({
  group: Object,
  isExpanded: Boolean,
  selectedQuizId: [Number, String],
})

const emit = defineEmits([
  'rename-group',
  'delete-group',
  'toggle-expand',
  'drag-start',
  'drop',
  'navigate-quiz',
  'share-quiz',
  'edit-quiz',
  'duplicate-quiz',
  'delete-quiz',
  'ungroup-quiz',
  'toggle-options',
  'update-color',
])

const toggleGroupExpand = () => emit('toggle-expand', props.group.id)
const onRenameGroup = () => emit('rename-group', props.group)
const onDeleteGroup = () => emit('delete-group', props.group.id)
const handleGroupDrop = () => emit('drop', props.group)
const onUpdateColor = () => emit('update-color', props.group) 
</script>

<style scoped>
.group-card {
  @apply p-4 rounded-lg shadow-md;
}

.group-options-button {
  font-size: 0.9rem;
  background-color: rgb(145, 145, 145);
  padding-block: 0.5rem;
  padding-inline: 0.25rem;
  border-radius: 0.5rem;
  color:white;
}
</style>
