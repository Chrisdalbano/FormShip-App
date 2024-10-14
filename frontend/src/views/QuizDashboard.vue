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
      <button @click="promptCreateGroup" class="create-group-btn">
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
        draggable="true"
        @dragover.prevent
        @drop="handleDrop(group)"
      >
        <div class="flex justify-between items-center mb-4">
          <div class="flex items-center">
            <h3
              class="font-bold text-xl cursor-pointer"
              @click="toggleGroupExpand(group.id)"
            >
              {{ group.name }}
            </h3>
            <button @click="toggleGroupExpand(group.id)" class="ml-2">
              <span v-if="expandedGroups.includes(group.id)">&#9660;</span>
              <span v-else>&#9658;</span>
            </button>
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
          v-if="expandedGroups.includes(group.id)"
          class="quiz-grid grid grid-cols-1 gap-4"
        >
          <div
            v-for="quiz in group.quizzes"
            :key="quiz.id"
            class="quiz-card p-4 rounded-lg shadow-md relative"
            :style="{ backgroundColor: quiz.color || '#ffffff' }"
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
                @click="toggleMoreOptions(quiz.id)"
                class="more-options-button"
              >
                &#x22EE;
              </button>
            </div>

            <!-- More options dropdown -->
            <div
              v-if="selectedQuizId === quiz.id"
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
              <button @click="ungroupQuiz(quiz, group)" class="option-item">
                Ungroup
              </button>
            </div>
          </div>
        </div>
        <template v-else>
          <div v-if="group.quizzes.length > 0" class="quiz-list">
            <ul>
              <li
                v-for="quiz in group.quizzes"
                :key="quiz.id"
                class="text-gray-700 mb-2"
              >
                - {{ quiz.title }}
              </li>
            </ul>
          </div>
          <p v-else class="text-gray-500">No quizzes in this group.</p>
        </template>
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
          v-for="(quiz, index) in ungroupedQuizzes"
          :key="quiz.id"
          class="quiz-card p-4 rounded-lg shadow-md"
          :style="{ backgroundColor: quiz.color || '#ffffff' }"
          draggable="true"
          @dragstart="handleDragStart(quiz, null, index)"
          @dragover.prevent
          @drop="handleQuizDrop(index)"
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
              @click="toggleMoreOptions(quiz.id)"
              class="more-options-button"
            >
              &#x22EE;
            </button>
          </div>

          <!-- More options dropdown -->
          <div
            v-if="selectedQuizId === quiz.id"
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
const selectedQuizId = ref(null)
const draggedQuiz = ref(null)
const expandedGroups = ref([])

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

// Fetch groups and ungrouped quizzes when component mounts
onMounted(async () => {
  try {
    await fetchGroups()
    await fetchUngroupedQuizzes()
  } catch (error) {
    console.error('Error loading initial data:', error)
  }
})

// Fetch groups from backend
const fetchGroups = async () => {
  try {
    const response = await axios.get(`${apiBaseUrl}/groups/`)
    groups.value = response.data
  } catch (error) {
    console.error('Error fetching groups:', error)
  }
}

// Fetch ungrouped quizzes from backend
const fetchUngroupedQuizzes = async () => {
  try {
    const response = await axios.get(`${apiBaseUrl}/quizzes/?grouped=false`)
    ungroupedQuizzes.value = response.data
  } catch (error) {
    console.error('Error fetching ungrouped quizzes:', error)
  }
}

// Prompt for creating a new group
const promptCreateGroup = () => {
  const name = prompt('Enter the name for the new group:')
  if (name && name.trim() !== '') {
    createGroup(name.trim())
  }
}

// Create a new group
const createGroup = async name => {
  try {
    const response = await axios.post(`${apiBaseUrl}/groups/`, {
      name: name,
    })
    groups.value.push(response.data)
  } catch (error) {
    console.error('Error creating group:', error)
    alert('Failed to create a new group. Please try again.')
  }
}

// Rename a group with inline editing

// Delete a group
const deleteGroup = async groupId => {
  if (
    confirm(
      'Are you sure you want to delete this group? All quizzes in this group will be ungrouped.',
    )
  ) {
    try {
      await axios.delete(`${apiBaseUrl}/groups/${groupId}/`)

      const groupIndex = groups.value.findIndex(group => group.id === groupId)
      if (groupIndex !== -1) {
        const quizzesToUngroup = groups.value[groupIndex].quizzes
        groups.value.splice(groupIndex, 1)

        ungroupedQuizzes.value.push(...quizzesToUngroup) // Move quizzes back to ungroupedQuizzes
      }
    } catch (error) {
      console.error('Error deleting group:', error)
      alert('Failed to delete the group. Please try again.')
    }
  }
}

// Handle quiz drag start
const handleDragStart = (quiz, group, index = null) => {
  draggedQuiz.value = { quiz, group, index }
}

// Handle dropping a quiz into a group
const handleDrop = async targetGroup => {
  if (!draggedQuiz.value) return

  const { quiz, group, index } = draggedQuiz.value

  if (group) {
    group.quizzes = group.quizzes.filter(q => q.id !== quiz.id)
  } else {
    ungroupedQuizzes.value.splice(index, 1)
  }

  if (targetGroup) {
    targetGroup.quizzes.push(quiz)
  } else {
    ungroupedQuizzes.value.push(quiz)
  }

  try {
    await axios.put(`${apiBaseUrl}/quizzes/${quiz.id}/move-to-group/`, {
      group_id: targetGroup ? targetGroup.id : null,
    })
  } catch (error) {
    console.error('Error updating quiz group:', error)
    alert('Failed to move the quiz. Please try again.')
  }

  draggedQuiz.value = null
}

// Handle dropping a quiz within ungrouped quizzes to reorder
const handleQuizDrop = async targetIndex => {
  if (!draggedQuiz.value || draggedQuiz.value.group !== null) return

  const { quiz, index } = draggedQuiz.value

  ungroupedQuizzes.value.splice(index, 1)
  ungroupedQuizzes.value.splice(targetIndex, 0, quiz)

  const quizOrders = ungroupedQuizzes.value.map((quiz, idx) => ({
    id: quiz.id,
    order: idx,
  }))
  try {
    await axios.put(`${apiBaseUrl}/quizzes/update-order/`, {
      quiz_orders: quizOrders,
    })
  } catch (error) {
    console.error('Error updating quiz order:', error)
    alert('Failed to update quiz order. Please try again.')
  }

  draggedQuiz.value = null
}

// Expand or collapse a group
const toggleGroupExpand = groupId => {
  if (expandedGroups.value.includes(groupId)) {
    expandedGroups.value = expandedGroups.value.filter(id => id !== groupId)
  } else {
    expandedGroups.value.push(groupId)
  }
}

// Toggle more options for quizzes
const toggleMoreOptions = quizId => {
  selectedQuizId.value = selectedQuizId.value === quizId ? null : quizId
}

// Navigate to create a new quiz
const navigateToCreateQuiz = () => {
  router.push({ name: 'CreateQuiz' })
}

// Edit a quiz
const editQuiz = quizId => {
  router.push({ name: 'EditQuiz', params: { id: quizId } })
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

// Share a quiz
const shareQuiz = async quizId => {
  alert(
    `Shareable link for quiz ${quizId}: http://localhost:5173/quiz/${quizId}`,
  )
}

// Navigate to a quiz for testing
const navigateToQuiz = quizId => {
  router.push({ name: 'TestQuiz', params: { id: quizId } })
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

.option-item {
  @apply block w-full text-left mb-2;
}

.quiz-list {
  @apply bg-white p-3 rounded-lg shadow-md;
}
</style>
