<template>
  <div class="zen-container">
    <h1 class="text-3xl font-bold mb-4">Your Quiz Dashboard</h1>
    <p class="text-lg mb-6">
      Create a new quiz or manage your existing quizzes below.
    </p>

    <div class="button-container mb-6 flex gap-4">
      <button @click="navigateToCreateQuiz" class="create-quiz-btn">
        Create New Quiz
      </button>
      <button @click="promptCreateGroup" class="create-group-btn">
        Create New Group
      </button>
    </div>

    <div
      v-if="groups && groups.length"
      class="group-list grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
    >
      <QuizGroupCard
        v-for="group in groups"
        :key="group.id"
        :group="group"
        :isExpanded="expandedGroups.includes(group.id)"
        :selectedQuizId="selectedQuizId"
        @rename-group="renameGroup"
        @delete-group="deleteGroup"
        @toggle-expand="toggleGroupExpand"
        @update-color="updateGroupColorFront"
        @drag-start="handleDragStart"
        @drop="handleDrop"
        @navigate-quiz="navigateToQuiz"
        @edit-quiz="editQuiz"
        @duplicate-quiz="duplicateQuiz"
        @delete-quiz="deleteQuiz"
        @ungroup-quiz="ungroupQuiz"
        @toggle-options="toggleMoreOptions"
      />
    </div>

    <div
      v-if="ungroupedQuizzes && ungroupedQuizzes.length"
      class="ungrouped-quizzes mt-8"
    >
      <h2 class="text-2xl font-semibold mb-4">Ungrouped Quizzes:</h2>
      <div
        class="quiz-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
      >
        <QuizCard
          v-for="(quiz, index) in ungroupedQuizzes"
          :key="quiz.id"
          :quiz="quiz"
          :selectedQuizId="selectedQuizId"
          @drag-start="handleDragStart(quiz, null, index)"
          @navigate-quiz="navigateToQuiz"
          @edit-quiz="editQuiz"
          @toggle-options="toggleMoreOptions"
          @duplicate-quiz="duplicateQuiz"
          @delete-quiz="deleteQuiz"
        />
      </div>
    </div>
    <p v-else class="text-gray-600 mt-6">No ungrouped quizzes found.</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import useGroupApi from '../composables/useGroupApi'
import useDragAndDrop from '../composables/useDragAndDrop'
import QuizGroupCard from '../components/QuizGroupCard.vue'
import QuizCard from '../components/QuizCard.vue'
import axios from 'axios'

const router = useRouter()
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

// Reactive state for ungrouped quizzes, selected quiz options, and expanded groups
const ungroupedQuizzes = ref([])
const selectedQuizId = ref(null)
const expandedGroups = ref([])

// Group API composable
const {
  groups,
  fetchGroups,
  createGroup,
  updateGroupName,
  updateGroupColor,
  deleteGroup,
} = useGroupApi(apiBaseUrl)

// Drag-and-Drop composable
const { handleDragStart, handleDrop } = useDragAndDrop(
  apiBaseUrl,
  ungroupedQuizzes,
  groups,
)

// Fetch data on mount
onMounted(async () => {
  await fetchGroups()
  await fetchUngroupedQuizzes()
})

// Toggle options dropdown for quizzes
const toggleMoreOptions = quizId => {
  selectedQuizId.value = selectedQuizId.value === quizId ? null : quizId
}

// Fetch ungrouped quizzes
const fetchUngroupedQuizzes = async () => {
  try {
    const response = await axios.get(`${apiBaseUrl}/quizzes/?grouped=false`)
    ungroupedQuizzes.value = response.data
  } catch (error) {
    console.error('Error fetching ungrouped quizzes:', error)
  }
}

// Duplicate a quiz
const duplicateQuiz = async quizId => {
  try {
    const response = await axios.post(
      `${apiBaseUrl}/quizzes/${quizId}/duplicate/`,
    )
    const duplicatedQuiz = response.data

    const group = groups.value.find(g => g.quizzes.some(q => q.id === quizId))
    if (group) {
      group.quizzes.push(duplicatedQuiz)
    } else {
      ungroupedQuizzes.value.push(duplicatedQuiz)
    }
  } catch (error) {
    console.error('Error duplicating quiz:', error)
    alert('Failed to duplicate quiz. Please try again.')
  }
}

// Delete a quiz
const deleteQuiz = async quizId => {
  if (confirm('Are you sure you want to delete this quiz?')) {
    try {
      await axios.delete(`${apiBaseUrl}/quizzes/${quizId}/`)

      const group = groups.value.find(g => g.quizzes.some(q => q.id === quizId))
      if (group) {
        group.quizzes = group.quizzes.filter(q => q.id !== quizId)
      } else {
        ungroupedQuizzes.value = ungroupedQuizzes.value.filter(
          q => q.id !== quizId,
        )
      }
    } catch (error) {
      console.error('Error deleting quiz:', error)
      alert('Failed to delete quiz. Please try again.')
    }
  }
}

// Ungroup a quiz
const ungroupQuiz = async (quiz, group) => {
  group.quizzes = group.quizzes.filter(q => q.id !== quiz.id)
  ungroupedQuizzes.value.push(quiz)

  try {
    await axios.put(`${apiBaseUrl}/quizzes/${quiz.id}/move-to-group/`, {
      group_id: null,
    })
  } catch (error) {
    console.error('Error ungrouping quiz:', error)
    alert('Failed to ungroup quiz. Please try again.')
  }
}

// Additional actions for navigation and group management
const navigateToCreateQuiz = () => router.push({ name: 'CreateQuiz' })
const editQuiz = quizId =>
  router.push({ name: 'EditQuiz', params: { id: quizId } })
const navigateToQuiz = quizId =>
  router.push({ name: 'TestQuiz', params: { id: quizId } })

// Prompt to create a new group
const promptCreateGroup = () => {
  const name = prompt('Enter the name for the new group:')
  if (name && name.trim() !== '') {
    createGroup(name.trim())
  }
}

// Rename group
const renameGroup = group => {
  const newName = prompt('Enter the new name for the group:', group.name)
  if (newName && newName.trim() !== '') {
    updateGroupName(group.id, newName.trim())
  }
}

// Update group color
const updateGroupColorFront = async group => {
  const newColor = prompt(
    'Enter the new color for the group (e.g., #FF5733):',
    group.color,
  )
  if (newColor && newColor.trim() !== '') {
    try {
      await updateGroupColor(group.id, newColor.trim())
      group.color = newColor // Update the color locally for immediate UI feedback
    } catch (error) {
      console.error('Error updating group color:', error)
      alert('Failed to update group color. Please try again.')
    }
  }
}

// Toggle expanded state of a group
const toggleGroupExpand = groupId => {
  if (expandedGroups.value.includes(groupId)) {
    expandedGroups.value = expandedGroups.value.filter(id => id !== groupId)
  } else {
    expandedGroups.value.push(groupId)
  }
}
</script>

<style scoped>
.create-quiz-btn,
.create-group-btn {
  @apply bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700;
}
</style>
