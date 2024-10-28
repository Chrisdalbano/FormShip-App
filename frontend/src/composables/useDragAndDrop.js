// composables/useDragAndDrop.js

import { ref } from 'vue'
import axios from 'axios'

export default function useDragAndDrop(apiBaseUrl, ungroupedQuizzes) {
  const draggedQuiz = ref(null)

  const handleDragStart = (quiz, group, index = null) => {
    draggedQuiz.value = { quiz, group, index }
  }

  const handleDrop = async (targetGroup) => {
    if (!draggedQuiz.value) return
    const { quiz, group, index } = draggedQuiz.value

    // Remove quiz from original location
    if (group) {
      group.quizzes = group.quizzes.filter(q => q.id !== quiz.id)
    } else {
      ungroupedQuizzes.value.splice(index, 1)
    }

    // Add quiz to new location
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

  return {
    handleDragStart,
    handleDrop
  }
}
