import { defineStore } from 'pinia'
import axios from 'axios'

export const useParticipantStore = defineStore('participant', {
  state: () => ({
    participant: null,
    token: null,
    currentQuiz: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
  },

  actions: {
    async setParticipantData(data) {
      console.log('[Store] Setting participant data:', data)
      
      this.participant = {
        id: data.participant_id,
        name: data.name,
        email: data.email
      }
      
      this.token = data.token
      
      // Save token to localStorage
      if (this.token) {
        console.log('[Store] Saving token to localStorage:', this.token.substring(0, 20) + '...')
        localStorage.setItem('participant_token', this.token)
        
        // Set axios default headers
        console.log('[Store] Setting axios default Authorization header')
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
      }
      
      console.log('[Store] Participant data set successfully')
    },

    setCurrentQuiz(quiz) {
      this.currentQuiz = quiz
    },

    clearParticipantData() {
      this.participant = null
      this.token = null
      this.currentQuiz = null
      localStorage.removeItem('participant_token')
      delete axios.defaults.headers.common['Authorization']
    },

    getAuthHeader() {
      return this.token ? { Authorization: `Bearer ${this.token}` } : {}
    }
  }
}) 