<template>
  <div class="zen-container">
    <h1 class="text-3xl font-bold mb-4">Your Quiz Dashboard</h1>
    <p class="text-lg mb-6">
      Create a new quiz or manage your existing quizzes below.
    </p>

    <!-- Button to create a new quiz or group -->
    <div class="button-container mb-6 flex gap-4">
      <button @click="navigateToCreateQuiz" class="create-quiz-btn">
        Create New Quiz
      </button>
      <button @click="createGroup" class="create-group-btn">
        Create New Group
      </button>
    </div>

    <!-- List of existing groups -->
    <div
      v-if="groups && groups.length"
      class="group-list grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
    >
      <div
        v-for="group in groups"
        :key="group.id"
        class="group-card p-4 rounded-lg shadow-md"
        :style="{ backgroundColor: group.color || '#f3f4f6' }"
        @dragover.prevent
        @drop="handleDrop(group)"
      >
        <div class="flex justify-between items-center mb-4">
          <div>
            <h3 class="font-bold text-xl">{{ group.name }}</h3>
          </div>
          <div class="flex gap-2">
            <button class="group-options-button" @click="renameGroup(group)">
              Rename
            </button>
            <button class="group-options-button" @click="deleteGroup(group.id)">
              Delete
            </button>
          </div>
        </div>

        <!-- List of quizzes in the group -->
        <div
          v-if="group.quizzes && group.quizzes.length"
          class="quiz-grid grid grid-cols-1 gap-4"
        >
          <div
            v-for="quiz in group.quizzes"
            :key="quiz.id"
            class="quiz-card p-4 bg-white rounded-lg shadow-md relative"
            draggable="true"
            @dragstart="handleDragStart(quiz, group)"
          >
            <h3 class="font-semibold text-lg">{{ quiz.title }}</h3>
            <p class="text-sm text-gray-600 mb-4">Topic: {{ quiz.topic }}</p>
            <div class="flex justify-between">
              <button
                class="primary-button bg-green-500"
                @click="navigateToQuiz(quiz.id)"
              >
                Test
              </button>
              <button
                class="primary-button bg-blue-500"
                @click="shareQuiz(quiz.id)"
              >
                Share
              </button>
              <button
                @click="toggleMoreOptions(quiz)"
                class="more-options-button"
              >
                &#x22EE;
              </button>
            </div>

            <!-- More options dropdown -->
            <div
              v-if="quiz.showOptions"
              class="options-dropdown bg-gray-200 absolute top-full left-0 mt-2 p-4 rounded-lg shadow-md z-10"
            >
              <button @click="editQuiz(quiz.id)" class="option-item">
                Edit
              </button>
              <button @click="duplicateQuiz(quiz.id)" class="option-item">
                Duplicate
              </button>
              <button @click="deleteQuiz(quiz.id)" class="option-item">
                Delete
              </button>
            </div>
          </div>
        </div>
        <p v-else class="text-gray-500">No quizzes in this group.</p>
      </div>
    </div>

    <!-- List of ungrouped quizzes -->
    <div
      v-if="ungroupedQuizzes && ungroupedQuizzes.length"
      class="ungrouped-quizzes mt-8"
    >
      <h2 class="text-2xl font-semibold mb-4">Ungrouped Quizzes:</h2>
      <div
        class="quiz-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
      >
        <div
          v-for="quiz in ungroupedQuizzes"
          :key="quiz.id"
          class="quiz-card p-4 bg-white rounded-lg shadow-md"
          draggable="true"
          @dragstart="handleDragStart(quiz, null)"
        >
          <h3 class="font-semibold text-lg">{{ quiz.title }}</h3>
          <p class="text-sm text-gray-600 mb-4">Topic: {{ quiz.topic }}</p>
          <div class="flex justify-between">
            <button
              class="primary-button bg-green-500"
              @click="navigateToQuiz(quiz.id)"
            >
              Test
            </button>
            <button
              class="primary-button bg-blue-500"
              @click="shareQuiz(quiz.id)"
            >
              Share
            </button>
            <button
              @click="toggleMoreOptions(quiz)"
              class="more-options-button"
            >
              &#x22EE;
            </button>
          </div>

          <!-- More options dropdown -->
          <div
            v-if="quiz.showOptions"
            class="options-dropdown bg-gray-200 absolute top-full left-0 mt-2 p-4 rounded-lg shadow-md z-10"
          >
            <button @click="editQuiz(quiz.id)" class="option-item">Edit</button>
            <button @click="duplicateQuiz(quiz.id)" class="option-item">
              Duplicate
            </button>
            <button @click="deleteQuiz(quiz.id)" class="option-item">
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
    <p v-else class="text-gray-600 mt-6">No ungrouped quizzes found.</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const groups = ref([])
const ungroupedQuizzes = ref([])

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

onMounted(async () => {
  try {
    await fetchGroups()
    await fetchUngroupedQuizzes()
  } catch (error) {
    console.error('Error loading initial data:', error)
  }
})

const fetchGroups = async () => {
  try {
    const response = await axios.get(`${apiBaseUrl}/groups/`)
    groups.value = response.data
  } catch (error) {
    console.error('Error fetching groups:', error)
  }
}

const fetchUngroupedQuizzes = async () => {
  try {
    const response = await axios.get(`${apiBaseUrl}/quizzes/?grouped=false`)
    ungroupedQuizzes.value = response.data
  } catch (error) {
    console.error('Error fetching ungrouped quizzes:', error)
  }
}

const navigateToCreateQuiz = () => {
  router.push({ name: 'CreateQuiz' })
}

const navigateToQuiz = quizId => {
  router.push({ name: 'TestQuiz', params: { id: quizId } })
}

const createGroup = async () => {
  const groupName = prompt('Enter group name:')
  if (groupName) {
    try {
      const response = await axios.post(`${apiBaseUrl}/groups/`, {
        name: groupName,
      })
      groups.value.push(response.data)
      alert('Group created successfully!')
    } catch (error) {
      console.error('Error creating group:', error)
    }
  }
}

const renameGroup = group => {
  const newName = prompt('Enter new group name:', group.name)
  if (newName && newName !== group.name) {
    group.name = newName
    try {
      axios.put(`${apiBaseUrl}/groups/${group.id}/`, { name: newName })
    } catch (error) {
      console.error('Error renaming group:', error)
    }
  }
}

const deleteGroup = async groupId => {
  if (confirm('Are you sure you want to delete this group?')) {
    try {
      await axios.delete(`${apiBaseUrl}/groups/${groupId}/`)
      groups.value = groups.value.filter(group => group.id !== groupId)
      alert('Group deleted successfully!')
    } catch (error) {
      console.error('Error deleting group:', error)
    }
  }
}

const shareQuiz = quizId => {
  alert(
    `Shareable link for quiz ${quizId}: http://localhost:5173/quiz/${quizId}`,
  )
}

const duplicateQuiz = async quizId => {
  try {
    const response = await axios.post(
      `${apiBaseUrl}/quizzes/${quizId}/duplicate/`,
    )
    const group = groups.value.find(g => g.quizzes.some(q => q.id === quizId))
    if (group) {
      group.quizzes.push(response.data)
    } else {
      ungroupedQuizzes.value.push(response.data)
    }
    alert('Quiz duplicated successfully!')
  } catch (error) {
    console.error('Error duplicating quiz:', error)
  }
}

const deleteQuiz = async quizId => {
  if (confirm('Are you sure you want to delete this quiz?')) {
    try {
      await axios.delete(`${apiBaseUrl}/quizzes/${quizId}/`)
      groups.value.forEach(group => {
        group.quizzes = group.quizzes.filter(quiz => quiz.id !== quizId)
      })
      ungroupedQuizzes.value = ungroupedQuizzes.value.filter(
        quiz => quiz.id !== quizId,
      )
      alert('Quiz deleted successfully!')
    } catch (error) {
      console.error('Error deleting quiz:', error)
      alert('Failed to delete quiz. Please try again.')
    }
  }
}

const editQuiz = quizId => {
  router.push({ name: 'EditQuiz', params: { id: quizId } })
}

const toggleMoreOptions = quiz => {
  quiz.showOptions = !quiz.showOptions
}

// Drag-and-Drop functionality
let draggedQuiz = null
let draggedFromGroup = null

const handleDragStart = (quiz, group) => {
  draggedQuiz = quiz
  draggedFromGroup = group
}

const handleDrop = async targetGroup => {
  if (draggedQuiz) {
    if (draggedFromGroup) {
      // Remove quiz from the original group
      draggedFromGroup.quizzes = draggedFromGroup.quizzes.filter(
        quiz => quiz.id !== draggedQuiz.id,
      )
    } else {
      // Remove quiz from ungrouped quizzes
      ungroupedQuizzes.value = ungroupedQuizzes.value.filter(
        quiz => quiz.id !== draggedQuiz.id,
      )
    }

    // Add quiz to the new group or ungrouped quizzes
    if (targetGroup) {
      targetGroup.quizzes.push(draggedQuiz)
    } else {
      ungroupedQuizzes.value.push(draggedQuiz)
    }

    // Update backend
    try {
      await axios.put(`${apiBaseUrl}/move-quiz-to-group/${draggedQuiz.id}/`, {
        group_id: targetGroup ? targetGroup.id : null,
      })
    } catch (error) {
      console.error('Error updating quiz group:', error)
    }

    // Reset dragged data
    draggedQuiz = null
    draggedFromGroup = null
  }
}
</script>

<style scoped>
.create-quiz-btn,
.create-group-btn {
  @apply bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700;
}

.group-list,
.quiz-grid {
  @apply mt-4;
}

.group-card {
  @apply p-4 rounded-lg shadow-md;
}

.quiz-card {
  @apply p-4 rounded-lg shadow-md;
}

.primary-button {
  @apply text-white px-3 py-2 rounded-lg;
}

.more-options-button {
  @apply text-gray-700;
}

.options-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 0.5rem;
  background-color: #f3f4f6;
  padding: 1rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.option-item {
  @apply block w-full text-left mb-2;
}
</style>
