<template>
  <div class="quiz-management-container">
    <h1 class="text-3xl font-bold mb-4">Manage Quiz: {{ quiz.title }}</h1>

    <!-- Tabs for navigation -->
    <div class="tabs-container">
      <button
        v-for="tab in tabs"
        :key="tab.name"
        @click="selectTab(tab.name)"
        :class="{ active: activeTab === tab.name }"
        class="tab-button"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <component
        :is="currentTabComponent"
        :quiz-id="quizId"
        :quiz-data="quiz"
        @quiz-updated="onQuizUpdated"
      />
    </div>

    <!-- Footer actions -->
    <div class="actions mt-4">
      <button @click="saveChanges" class="btn btn-primary">Save Changes</button>
      <button
        v-if="!quiz.is_published"
        @click="publishQuiz"
        class="btn btn-success"
      >
        Publish Quiz
      </button>
      <button
        v-if="quiz.is_testing && !quiz.is_published"
        @click="launchTestingMode"
        class="btn btn-secondary"
      >
        Launch in Testing Mode
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

import EditQuiz from '../components/QuizAdmin/EditQuiz.vue'
import QuizAdministration from '../components/QuizAdmin/QuizAdministration.vue'
import QuizAnalysis from '../components/QuizAdmin/QuizAnalysis.vue'

const route = useRoute()
const quizId = route.params.id
const quiz = ref({})
const tabs = [
  { name: 'edit', label: 'Edit', component: EditQuiz },
  { name: 'admin', label: 'Administration', component: QuizAdministration },
  { name: 'analysis', label: 'Analysis', component: QuizAnalysis },
]
const activeTab = ref('edit')

onMounted(async () => {
  await fetchQuiz()
})

const fetchQuiz = async () => {
  try {
    const response = await axios.get(`/api/quizzes/${quizId}/`)
    quiz.value = response.data
  } catch (error) {
    console.error('Error fetching quiz data:', error)
  }
}

const selectTab = tabName => {
  activeTab.value = tabName
}

const currentTabComponent = computed(
  () => tabs.find(tab => tab.name === activeTab.value)?.component,
)

const saveChanges = async () => {
  try {
    await axios.put(`/api/quizzes/${quizId}/`, quiz.value)
    alert('Changes saved successfully!')
  } catch (error) {
    console.error('Error saving quiz changes:', error)
    alert('Failed to save changes.')
  }
}

const publishQuiz = async () => {
  try {
    await axios.patch(`/api/quizzes/${quizId}/publish/`, { is_published: true })
    quiz.value.is_published = true
    alert('Quiz published successfully!')
  } catch (error) {
    console.error('Error publishing quiz:', error)
    alert('Failed to publish quiz.')
  }
}

const launchTestingMode = async () => {
  try {
    // Backend may log that the quiz is launched in testing mode
    await axios.post(`/api/quizzes/${quizId}/launch-testing/`, {
      is_testing: true,
    })
    alert('Quiz launched in testing mode!')
  } catch (error) {
    console.error('Error launching testing mode:', error)
    alert('Failed to launch testing mode.')
  }
}

const onQuizUpdated = updatedQuiz => {
  quiz.value = updatedQuiz
}
</script>

<style scoped>
.tabs-container {
  display: flex;
  border-bottom: 2px solid #e5e7eb;
  margin-bottom: 1rem;
}
.tab-button {
  padding: 0.5rem 1rem;
  cursor: pointer;
  background: none;
  border: none;
  font-size: 1rem;
  margin-right: 1rem;
}
.tab-button.active {
  border-bottom: 2px solid #3b82f6;
  font-weight: bold;
  color: #3b82f6;
}
.actions .btn {
  margin-right: 1rem;
}
</style>
