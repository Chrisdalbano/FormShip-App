<template>
  <div class="preview-container">
    <!-- If there's no quiz or no questions yet, show placeholders -->
    <div v-if="!quiz?.title">
      <p class="italic text-gray-500 mb-2">No quiz data yet.</p>
      <p class="text-xs text-gray-400">
        Fill out steps in the wizard on the left...
      </p>
    </div>
    <div v-else>
      <!-- Title, topic, basic info -->
      <h4 class="font-bold text-base mb-1">
        Preview: {{ quiz.title || 'Untitled' }}
      </h4>
      <p class="text-xs text-gray-500 mb-2">
        Topic: {{ quiz.topic || 'N/A' }} | Eval:
        {{ quiz.evaluation_type || 'pre' }}<br />
        Access: {{ quiz.access_control }} | Published:
        {{ quiz.is_published ? 'Yes' : 'No' }}
      </p>

      <!-- If the quiz requires a password, show a local password prompt simulation -->
      <div
        v-if="quiz.require_password && !localPasswordValidated && !finished"
        class="mb-2 border p-2 bg-gray-50"
      >
        <label class="block text-sm font-semibold mb-1">Enter Password</label>
        <input
          v-model="enteredPassword"
          type="password"
          class="border p-1 w-full text-xs"
        />
        <button
          class="bg-blue-500 text-white text-xs px-2 py-1 mt-2 rounded"
          @click="validatePassword"
        >
          Validate
        </button>
        <p v-if="wrongPassword" class="text-red-600 text-xs mt-1">
          Incorrect password.
        </p>
      </div>

      <!-- If the quiz requires name, show a local name prompt simulation -->
      <div
        v-else-if="quiz.require_name && !localNameProvided && !finished"
        class="mb-2 border p-2 bg-gray-50"
      >
        <label class="block text-sm font-semibold mb-1">Enter Your Name</label>
        <input
          v-model="enteredName"
          type="text"
          class="border p-1 w-full text-xs"
          placeholder="e.g. JohnDoe42"
        />
        <button
          class="bg-blue-500 text-white text-xs px-2 py-1 mt-2 rounded"
          @click="submitName"
        >
          Confirm
        </button>
      </div>

      <!-- If we are not done, show the quiz content -->
      <div
        v-else-if="!finished && localPasswordValidated && localNameProvided"
        class="mt-2 border p-2 rounded bg-white"
      >
        <!-- Timers or stepwise logic, etc. If you want to fully simulate, you can do so. -->
        <p v-if="quiz.is_timed" class="text-xs text-blue-600 mb-2">
          (Simulated) This quiz might have a time limit of
          {{ quiz.quiz_time_limit }} minutes.
        </p>

        <!-- Stepwise Mode vs. Standard Mode -->
        <div v-if="quiz.quiz_type === 'stepwise'">
          <p class="mb-1 text-sm font-semibold">
            Stepwise Demo (1 question at a time)
          </p>
          <div v-if="currentQuestion">
            <p class="text-sm font-semibold">
              Q{{ currentIndex + 1 }}: {{ currentQuestion.question_text }}
            </p>
            <!-- Show options with localAnswers -->
            <div class="ml-4 mt-1 space-y-1">
              <label v-if="currentQuestion.option_a" class="block text-xs">
                <input
                  type="radio"
                  :name="'q' + currentIndex"
                  value="A"
                  v-model="localAnswers[currentIndex]"
                />
                A: {{ currentQuestion.option_a }}
              </label>
              <label v-if="currentQuestion.option_b" class="block text-xs">
                <input
                  type="radio"
                  :name="'q' + currentIndex"
                  value="B"
                  v-model="localAnswers[currentIndex]"
                />
                B: {{ currentQuestion.option_b }}
              </label>
              <label v-if="currentQuestion.option_c" class="block text-xs">
                <input
                  type="radio"
                  :name="'q' + currentIndex"
                  value="C"
                  v-model="localAnswers[currentIndex]"
                />
                C: {{ currentQuestion.option_c }}
              </label>
              <label v-if="currentQuestion.option_d" class="block text-xs">
                <input
                  type="radio"
                  :name="'q' + currentIndex"
                  value="D"
                  v-model="localAnswers[currentIndex]"
                />
                D: {{ currentQuestion.option_d }}
              </label>
              <label v-if="currentQuestion.option_e" class="block text-xs">
                <input
                  type="radio"
                  :name="'q' + currentIndex"
                  value="E"
                  v-model="localAnswers[currentIndex]"
                />
                E: {{ currentQuestion.option_e }}
              </label>
            </div>
          </div>

          <!-- Stepwise navigation -->
          <div class="mt-2 flex items-center space-x-2">
            <button
              v-if="currentIndex > 0"
              class="bg-gray-400 text-white text-xs px-2 py-1 rounded"
              @click="goPrev"
            >
              Previous
            </button>
            <button
              class="bg-blue-500 text-white text-xs px-2 py-1 rounded"
              :disabled="localAnswers[currentIndex] === null"
              @click="goNextOrFinish"
            >
              {{ isLastQuestion ? 'Finish' : 'Next' }}
            </button>
          </div>
        </div>
        <div v-else>
          <!-- standard layout - show all questions -->
          <p class="mb-1 text-sm font-semibold">All-at-once Demo</p>
          <div
            v-for="(question, qIdx) in quiz.questions"
            :key="qIdx"
            class="mb-2"
          >
            <p class="text-sm font-semibold">
              Q{{ qIdx + 1 }}: {{ question.question_text }}
            </p>
            <div class="ml-4 mt-1 space-y-1 text-xs">
              <label v-if="question.option_a" class="block">
                <input
                  type="radio"
                  :name="'q' + qIdx"
                  value="A"
                  v-model="localAnswers[qIdx]"
                />
                A: {{ question.option_a }}
              </label>
              <label v-if="question.option_b" class="block">
                <input
                  type="radio"
                  :name="'q' + qIdx"
                  value="B"
                  v-model="localAnswers[qIdx]"
                />
                B: {{ question.option_b }}
              </label>
              <label v-if="question.option_c" class="block">
                <input
                  type="radio"
                  :name="'q' + qIdx"
                  value="C"
                  v-model="localAnswers[qIdx]"
                />
                C: {{ question.option_c }}
              </label>
              <label v-if="question.option_d" class="block">
                <input
                  type="radio"
                  :name="'q' + qIdx"
                  value="D"
                  v-model="localAnswers[qIdx]"
                />
                D: {{ question.option_d }}
              </label>
              <label v-if="question.option_e" class="block">
                <input
                  type="radio"
                  :name="'q' + qIdx"
                  value="E"
                  v-model="localAnswers[qIdx]"
                />
                E: {{ question.option_e }}
              </label>
            </div>
          </div>
          <button
            class="mt-2 bg-green-600 text-white text-xs px-2 py-1 rounded"
            @click="finishAllAtOnce"
          >
            Submit
          </button>
        </div>
      </div>

      <!-- If finished, show results locally -->
      <div v-else-if="finished" class="mt-2 p-2 border rounded bg-green-50">
        <p class="text-sm font-semibold mb-1">Preview Completed!</p>
        <p class="text-xs text-gray-700 mb-2">
          Score (just a quick guess): {{ computeScore() }} /
          {{ quiz.questions?.length }}
        </p>
        <p class="text-xs text-gray-500">
          This preview does not store real results.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { defineProps } from 'vue'

// Props
const props = defineProps({
  quiz: { type: Object, default: null }, // The entire quiz object with .questions
  interactive: { type: Boolean, default: true },
})

const localPasswordValidated = ref(false)
const localNameProvided = ref(false)
const finished = ref(false)

// For name/password simulation
const enteredPassword = ref('')
const wrongPassword = ref(false)
const enteredName = ref('')

// If the quiz has questions, let's track localAnswers
// e.g. localAnswers[i] = "A" / "B" / "C" ...
const localAnswers = ref([])

// Stepwise states
const currentIndex = ref(0) // which question index in stepwise
const currentQuestion = computed(() => {
  if (!props.quiz?.questions?.length) return null
  return props.quiz.questions[currentIndex.value]
})
// If no quiz or no questions, return -1
const isLastQuestion = computed(() => {
  if (!props.quiz?.questions?.length) return false
  return currentIndex.value === props.quiz.questions.length - 1
})

// Watch quiz changes: if new questions are added, reset localAnswers
watch(
  () => props.quiz?.questions,
  newQuestions => {
    if (!newQuestions || !newQuestions.length) {
      localAnswers.value = []
      currentIndex.value = 0
    } else {
      localAnswers.value = newQuestions.map(() => null)
      currentIndex.value = 0
      finished.value = false
    }
  },
  { immediate: true },
)

// Validate password
function validatePassword() {
  if (!props.quiz?.password) {
    // no password actually set
    localPasswordValidated.value = true
    return
  }
  if (enteredPassword.value === props.quiz.password) {
    localPasswordValidated.value = true
    wrongPassword.value = false
  } else {
    wrongPassword.value = true
  }
}

function submitName() {
  if (!enteredName.value.trim()) return
  localNameProvided.value = true
}

// Stepwise: Next or finish
function goNextOrFinish() {
  if (isLastQuestion.value) {
    finishStepwise()
  } else {
    currentIndex.value++
  }
}
function goPrev() {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}
function finishStepwise() {
  finished.value = true
}

// Standard: just do a finish
function finishAllAtOnce() {
  finished.value = true
}

// For fun, a quick local score
function computeScore() {
  if (!props.quiz?.questions) return 0
  let s = 0
  props.quiz.questions.forEach((q, idx) => {
    if (localAnswers.value[idx] === q.correct_answer) s++
  })
  return s
}
</script>

<style scoped>
.preview-container {
  @apply border border-gray-200 p-3 text-sm rounded bg-white min-h-[200px];
}
</style>
