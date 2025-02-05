const handleViewResults = () => {
  router.push(`/participant/quizzes/${participantStore.currentQuiz.id}/results`)
}

<template>
  <div class="container mt-5">
    <div class="card">
      <div class="card-body text-center">
        <h2 class="card-title mb-4">Quiz Completed!</h2>
        <p class="card-text">Thank you for completing the quiz.</p>
        
        <div class="d-grid gap-2 col-6 mx-auto">
          <button @click="handleViewResults" class="btn btn-primary mb-2">
            View Results
          </button>
          <router-link to="/participant/quizzes" class="btn btn-secondary">
            Back to My Quizzes
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useParticipantStore } from '@/store/participant'

const router = useRouter()
const participantStore = useParticipantStore()
</script> 