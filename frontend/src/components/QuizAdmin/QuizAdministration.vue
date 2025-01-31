<template>
  <div
    class="quiz-admin w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg"
  >
    <h1 class="text-2xl font-bold mb-6">
      Quiz Administration: {{ quiz.title }}
    </h1>

    <div v-if="loading" class="text-center text-gray-500 mb-4">
      Loading administration panel...
    </div>

    <div v-else>
      <!-- Shareable URL -->
      <div v-if="quiz.is_published" class="mb-6">
        <label class="block font-semibold text-gray-700 mb-2">
          Shareable URL:
        </label>
        <div class="flex items-center gap-2">
          <input
            type="text"
            class="input-field w-full"
            :value="shareableUrl"
            readonly
          />
          <button
            @click="copyShareableUrl"
            class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Copy
          </button>
        </div>
      </div>

      <!-- Quiz Status -->
      <div class="mb-6">
        <p>
          <strong>Status:</strong>
          <span
            :class="{
              'text-green-600': quiz.is_published,
              'text-yellow-600': !quiz.is_published,
            }"
          >
            {{ quiz.is_published ? 'Published' : 'Unpublished' }}
          </span>
        </p>
        <p>
          <strong>Testing Mode:</strong>
          <span
            :class="{
              'text-green-600': quiz.is_testing,
              'text-gray-600': !quiz.is_testing,
            }"
          >
            {{ quiz.is_testing ? 'Enabled' : 'Disabled' }}
          </span>
        </p>
        <p>
          <strong>Access Control:</strong>
          {{ accessControlDisplay }}
        </p>
      </div>

      <!-- Administration Settings -->
      <section class="mb-6">
        <h2 class="text-xl font-semibold mb-4">Settings</h2>
        <div class="flex flex-col gap-3">
          <div>
            <input
              type="checkbox"
              id="isPublished"
              v-model="quiz.is_published"
            />
            <label for="isPublished" class="ml-2">Publish Quiz?</label>
          </div>
          <div>
            <input type="checkbox" id="isTesting" v-model="quiz.is_testing" />
            <label for="isTesting" class="ml-2">Enable Testing Mode?</label>
          </div>
          <div>
            <label
              for="accessControl"
              class="block font-semibold text-gray-700 mb-2"
            >
              Access Control
            </label>
            <select
              id="accessControl"
              v-model="quiz.access_control"
              class="input-field w-full"
            >
              <option value="public">Public</option>
              <option value="invitation">Invitation Only</option>
              <option value="login_required">Login Required</option>
            </select>
          </div>
        </div>
      </section>

      <!-- Actions -->
      <section class="actions flex flex-col gap-4">
        <button
          @click="saveSettings"
          class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Save Changes
        </button>
        <button
          v-if="!quiz.is_published"
          @click="publishQuiz"
          class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Publish Quiz
        </button>
        <button
          @click="launchTestingMode"
          class="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-700"
        >
          Launch in Testing Mode
        </button>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useRoute } from 'vue-router'

const route = useRoute()
const quizId = route.params.id
const quiz = ref({})
const loading = ref(true)
const shareableUrl = computed(() => {
  if (!quiz.value?.is_published) {
    return 'Quiz is not published yet.'
  }
  
  const baseUrl = window.location.origin
  
  switch (quiz.value.access_control) {
    case 'login_required':
      return `${baseUrl}/quiz/access/${quiz.value.id}`
    case 'invitation':
      return `${baseUrl}/quiz/invite/${quiz.value.id}`
    case 'public':
      return `${baseUrl}/quiz/${quiz.value.id}`
    default:
      return 'No URL available'
  }
})

onMounted(async () => {
  await fetchQuiz()
})

const fetchQuiz = async () => {
  try {
    const res = await axios.get(`/api/quizzes/${quizId}/`)
    quiz.value = res.data
  } catch (err) {
    console.error('Error fetching quiz:', err)
  } finally {
    loading.value = false
  }
}

const saveSettings = async () => {
  try {
    const res = await axios.patch(`/api/quizzes/${quizId}/update-status/`, {
      is_published: quiz.value.is_published,
      is_testing: quiz.value.is_testing,
      access_control: quiz.value.access_control,
    })
    quiz.value = res.data
    alert('Quiz settings saved successfully!')
  } catch (err) {
    console.error('Error saving quiz settings:', err)
    alert('Failed to save quiz settings.')
  }
}

const publishQuiz = async () => {
  try {
    const res = await axios.patch(`/api/quizzes/${quizId}/update-status/`, {
      is_published: true,
      access_control: quiz.value.access_control
    })
    quiz.value = res.data
    await fetchQuiz()
    alert('Quiz published successfully!')
  } catch (err) {
    console.error('Error publishing quiz:', err)
    alert('Failed to publish quiz.')
  }
}

const launchTestingMode = () => {
  window.open(`/quiz/${quizId}?test=true`, '_blank')
}

const copyShareableUrl = () => {
  navigator.clipboard.writeText(shareableUrl.value)
  alert('Shareable URL copied to clipboard!')
}

const accessControlDisplay = computed(() => {
  const mapping = {
    public: 'Public',
    invitation: 'Invitation Only',
    login_required: 'Login Required',
  }
  return mapping[quiz.value.access_control] || 'Unknown'
})
</script>

<style scoped>
.input-field {
  @apply border border-gray-300 px-3 py-2 rounded focus:outline-none focus:ring;
}

.actions button {
  @apply w-full;
}
</style>
