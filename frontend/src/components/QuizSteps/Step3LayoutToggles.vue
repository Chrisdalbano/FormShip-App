<template>
  <div>
    <h2 class="text-xl font-bold mb-2">Step 3: Layout & Timer Options</h2>

    <div class="mb-4">
      <label class="block font-semibold mb-1">Quiz Layout</label>
      <select v-model="localQuiz.quiz_type" class="border p-2 w-full">
        <option value="standard">All-at-Once (Standard)</option>
        <option value="stepwise">Stepwise (One Q at a Time)</option>
      </select>
    </div>

    <div
      v-if="localQuiz.quiz_type === 'stepwise'"
      class="mb-4 ml-4 border-l pl-4"
    >
      <label class="flex items-center mb-2">
        <input
          type="checkbox"
          v-model="localQuiz.skippable_questions"
          class="mr-2"
        />
        Allow Skipping Questions?
      </label>

      <div v-if="!localQuiz.skippable_questions">
        <label class="block font-semibold mb-1"
          >Time Limit per Step (sec)</label
        >
        <input
          v-model.number="localQuiz.stepwise_time_limit"
          type="number"
          class="border p-2 w-full"
          min="5"
        />
      </div>
    </div>

    <!-- Overall timed quiz? -->
    <div class="mb-4">
      <label class="flex items-center mb-2">
        <input type="checkbox" v-model="localQuiz.is_timed" class="mr-2" />
        Overall Time Limit (minutes)?
      </label>
      <div v-if="localQuiz.is_timed" class="ml-4">
        <input
          type="number"
          v-model.number="localQuiz.quiz_time_limit"
          min="1"
          class="border p-2 w-full"
          placeholder="Time limit (min)"
        />
      </div>
    </div>

    <div v-if="localQuiz.quiz_type === 'standard'" class="mb-4">
      <label class="flex items-center mb-2">
        <input
          type="checkbox"
          v-model="localQuiz.time_per_question"
          class="mr-2"
        />
        Time Limit per Question (seconds)?
      </label>
      <div v-if="localQuiz.time_per_question" class="ml-4">
        <input
          type="number"
          v-model.number="localQuiz.question_time_limit"
          min="5"
          class="border p-2 w-full"
          placeholder="Seconds per question"
        />
      </div>
    </div>

    <div class="mb-4 flex items-center">
      <input
        id="displayResults"
        type="checkbox"
        v-model="localQuiz.display_results"
        class="mr-2"
      />
      <label for="displayResults">Display Results Immediately?</label>
    </div>

    <div class="mb-4 flex items-center">
      <input
        id="requirePassword"
        type="checkbox"
        v-model="localQuiz.require_password"
        class="mr-2"
      />
      <label for="requirePassword">Require Password?</label>
    </div>
    <div v-if="localQuiz.require_password" class="ml-6 mb-4">
      <input
        type="password"
        v-model="localQuiz.password"
        class="border p-2 w-full"
        placeholder="Quiz Password"
      />
    </div>

    <div class="mb-4 flex items-center">
      <input
        id="allowAnonymous"
        type="checkbox"
        v-model="localQuiz.allow_anonymous"
        class="mr-2"
      />
      <label for="allowAnonymous">Allow Anonymous?</label>
    </div>

    <div class="mb-4 flex items-center">
      <input
        id="requireName"
        type="checkbox"
        v-model="localQuiz.require_name"
        class="mr-2"
      />
      <label for="requireName">Require Participant Name?</label>
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
  quiz: Object,
  questions: Array,
  isLoading: Boolean,
  aiError: String,
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
  emit('next')
}
</script>
