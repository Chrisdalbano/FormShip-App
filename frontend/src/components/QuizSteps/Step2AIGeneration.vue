<template>
  <div>
    <h2 class="text-xl font-bold mb-2">Step 2: AI Generation</h2>

    <div v-if="aiError" class="text-red-600 mb-2">
      AI/Server Error: {{ aiError }}
    </div>

    <div class="mb-4">
      <label class="block font-semibold mb-1">Number of Questions</label>
      <input
        v-model.number="localQuiz.question_count"
        type="number"
        class="border p-2 w-full"
        min="1"
        max="25"
      />
    </div>

    <div class="mb-4">
      <label class="block font-semibold mb-1">Options per Question</label>
      <input
        v-model.number="localQuiz.option_count"
        type="number"
        class="border p-2 w-full"
        min="2"
        max="5"
      />
    </div>

    <div class="mb-4 flex items-center">
      <input
        id="useKnowledgeBase"
        type="checkbox"
        v-model="localQuiz.use_knowledge_base"
        class="mr-2"
      />
      <label for="useKnowledgeBase" class="text-gray-700">
        Use my custom knowledge base
      </label>
    </div>

    <div v-if="localQuiz.use_knowledge_base" class="mb-4">
      <label class="block font-semibold mb-1">Knowledge Base Text</label>
      <textarea
        v-model="localQuiz.knowledge_base_text"
        rows="3"
        class="border p-2 w-full"
      ></textarea>
    </div>

    <div class="mt-6 flex justify-between">
      <button
        class="bg-gray-300 text-gray-700 px-4 py-2 rounded"
        @click="goPrevStep"
      >
        Back
      </button>
      <button
        class="bg-blue-500 text-white px-4 py-2 rounded"
        @click="goNextStep"
        :disabled="isLoading"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  quiz: { type: Object, required: true },
  questions: { type: Array, default: () => [] },
  isLoading: { type: Boolean, default: false },
  aiError: { type: String, default: '' },
})

const emit = defineEmits(['update-quiz', 'next', 'prev', 'finish'])

const localQuiz = ref({ ...props.quiz })

watch(
  localQuiz,
  newVal => {
    emit('update-quiz', newVal)
  },
  { deep: true },
)

function goPrevStep() {
  emit('prev')
}
function goNextStep() {
  // Possibly do local validation
  emit('next')
}
</script>
