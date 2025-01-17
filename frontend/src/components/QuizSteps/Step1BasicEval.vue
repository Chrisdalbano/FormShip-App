<template>
  <div>
    <h2 class="text-xl font-bold mb-2">Step 1: Basic Quiz Settings</h2>

    <div class="mb-4">
      <label class="block font-semibold mb-1">Quiz Title</label>
      <input
        v-model="localQuiz.title"
        class="border p-2 w-full"
        type="text"
        placeholder="Enter a quiz title"
      />
    </div>

    <div class="mb-4">
      <label class="block font-semibold mb-1">Quiz Topic</label>
      <input
        v-model="localQuiz.topic"
        class="border p-2 w-full"
        type="text"
        placeholder="Topic/Description"
      />
    </div>

    <div class="mb-4">
      <label class="block font-semibold mb-1">Evaluation Type</label>
      <select v-model="localQuiz.evaluation_type" class="border p-2 w-full">
        <option value="pre">Pre-Evaluated</option>
        <option value="hybrid">Hybrid</option>
        <option value="post">Post-Evaluated</option>
      </select>
    </div>

    <div class="mb-4 flex items-center">
      <input
        id="isTesting"
        type="checkbox"
        v-model="localQuiz.is_testing"
        class="mr-2"
      />
      <label for="isTesting" class="text-gray-700">
        Testing Mode (no real results)
      </label>
    </div>

    <div class="mb-4 flex items-center">
      <input
        id="isPublished"
        type="checkbox"
        v-model="localQuiz.is_published"
        class="mr-2"
      />
      <label for="isPublished" class="text-gray-700">
        Publish Immediately?
      </label>
    </div>

    <div class="mb-4">
      <label class="block font-semibold mb-1">Access Control</label>
      <select v-model="localQuiz.access_control" class="border p-2 w-full">
        <option value="public">Public</option>
        <option value="invitation">Invitation Only</option>
        <option value="login_required">Login Required</option>
      </select>
    </div>

    <div class="mt-6 flex justify-end space-x-4">
      <button
        class="bg-blue-500 text-white px-4 py-2 rounded"
        @click="goNextStep"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

// Props from wizard
const props = defineProps({
  quiz: { type: Object, required: true },
  questions: { type: Array, default: () => [] },
  isLoading: { type: Boolean, default: false },
  aiError: { type: String, default: '' },
})

const emit = defineEmits(['update-quiz', 'next', 'prev', 'finish'])

// Create a local copy
const localQuiz = ref({ ...props.quiz })

// Whenever localQuiz changes, bubble up
watch(
  localQuiz,
  newVal => {
    emit('update-quiz', newVal)
  },
  { deep: true },
)

function goNextStep() {
  // (Optional) validation logic here
  emit('next')
}
</script>
