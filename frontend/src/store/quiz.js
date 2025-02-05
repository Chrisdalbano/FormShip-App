import { defineStore } from 'pinia'
import apiService from '@/services/api'

export const useQuizStore = defineStore('quiz', {
  state: () => ({
    // Participant state
    token: localStorage.getItem('participant_token') || null,
    participant: null,
    isInitialized: false,

    // Quiz state
    currentQuiz: null,
    linkedQuizzes: [],
    quizResults: {},
    
    // Loading states
    loading: false,
    error: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    getAuthHeader: (state) => {
      return state.token ? { Authorization: `Bearer ${state.token}` } : {}
    },
    getQuizById: (state) => (id) => {
      return state.linkedQuizzes.find(quiz => quiz.id === id)
    },
    getQuizResults: (state) => (id) => {
      return state.quizResults[id]
    }
  },

  actions: {
    // Authentication and Profile Management
    async authenticateParticipant({ endpoint, email, password, name }) {
      try {
        // Clear any existing token first
        this.clearParticipantData()

        const response = await apiService.post(`/participants/${endpoint}/`, {
          email,
          password,
          name
        })

        if (!response.token) {
          throw new Error('No token received from server')
        }

        // Set token and update state
        apiService.setAuthToken(response.token)
        this.token = response.token
        this.participant = {
          id: response.participant_id,
          name: response.name,
          email: response.email
        }
        this.isInitialized = true

        // Verify the token works by making a test request
        try {
          await apiService.get('/participants/me/')
        } catch (error) {
          console.error('Token verification failed:', error)
          this.clearParticipantData()
          throw new Error('Authentication failed - could not verify token')
        }

        return response
      } catch (error) {
        console.error('Authentication error:', error)
        this.clearParticipantData()
        throw error
      }
    },

    async setParticipantData(data) {
      if (!data.token) {
        throw new Error('Token is required for participant data')
      }

      try {
        // Clear any existing token first
        this.clearParticipantData()

        // Set new token
        apiService.setAuthToken(data.token)
        this.token = data.token

        // Verify the token works with a test request
        try {
          const participantData = await apiService.get('/participants/me/')
          // Only update state after token is verified
          this.participant = {
            id: participantData.id || data.participant_id,
            name: participantData.name || data.name,
            email: participantData.email || data.email
          }
          this.isInitialized = true

          if (data.currentQuiz) {
            await this.setCurrentQuiz(data.currentQuiz)
          }
        } catch (error) {
          console.error('Token verification failed:', error)
          this.clearParticipantData()
          throw new Error('Authentication failed - could not verify token')
        }
      } catch (error) {
        console.error('Failed to set participant data:', error)
        this.clearParticipantData()
        throw error
      }
    },

    clearParticipantData() {
      apiService.clearAuthToken() // Clear token from API service first
      this.token = null
      this.participant = null
      this.currentQuiz = null
      this.linkedQuizzes = []
      this.quizResults = {}
      this.isInitialized = false
    },

    async updateProfile(data) {
      const response = await apiService.put('/participants/me/update/', data)
      this.participant = {
        ...this.participant,
        name: response.name,
        email: response.email
      }
      return response
    },

    // Quiz Access and Management
    async verifyQuizAccess(quizId) {
      if (!quizId) {
        throw new Error('Quiz ID is required')
      }

      try {
        // First verify participant authentication
        if (!this.token || !this.isInitialized) {
          return {
            success: false,
            requiredAction: 'REQUIRE_AUTH',
            quizData: {
              id: quizId,
              title: 'Quiz Access Required',
              access_control: 'login_required',
              is_published: true
            }
          }
        }

        // Verify token is still valid
        try {
          await apiService.get('/participants/me/')
        } catch (error) {
          if (error.response?.status === 401) {
            this.clearParticipantData()
            return {
              success: false,
              requiredAction: 'REQUIRE_AUTH',
              quizData: {
                id: quizId,
                title: 'Quiz Access Required',
                access_control: 'login_required',
                is_published: true
              }
            }
          }
          throw error
        }

        // Now try to access the quiz
        const response = await apiService.get(`/quizzes/${quizId}/`)
        await this.loadLinkedQuizzes()
        
        return { 
          success: true, 
          quizData: response,
          requiredAction: null
        }
      } catch (error) {
        console.error('Quiz access error:', error)
        if (error.response?.status === 401) {
          this.clearParticipantData()
          return {
            success: false,
            requiredAction: 'REQUIRE_AUTH',
            quizData: {
              id: quizId,
              title: 'Quiz Access Required',
              access_control: 'login_required',
              is_published: true
            }
          }
        } else if (error.response?.status === 403) {
          const errorData = error.response.data || {}
          return {
            success: false,
            requiredAction: errorData.required_action || 'NOT_INVITED',
            quizData: {
              id: quizId,
              title: errorData.quiz_title || 'Quiz Access Required',
              access_control: errorData.access_control || 'invitation',
              is_published: errorData.is_published || false
            }
          }
        }
        throw error
      }
    },

    async verifyQuizPassword(quizId, password) {
      const response = await apiService.post(`/quizzes/${quizId}/verify-access/`, { password })
      await this.loadLinkedQuizzes() // Load quizzes after successful verification
      return response
    },

    async verifyQuizInvitation(quizId, email) {
      const response = await apiService.post(`/quizzes/${quizId}/verify-access/`, { email })
      await this.loadLinkedQuizzes() // Load quizzes after successful verification
      return response
    },

    // Quiz Participation
    async setCurrentQuiz(quiz) {
      this.currentQuiz = quiz
      if (!this.linkedQuizzes.find(q => q.id === quiz.id)) {
        await this.loadLinkedQuizzes()
      }
    },

    async loadLinkedQuizzes() {
      if (!this.isAuthenticated) return

      try {
        const data = await apiService.get('/participants/my-quizzes/')
        this.linkedQuizzes = data
      } catch (error) {
        console.error('Failed to load linked quizzes:', error)
      }
    },

    async loadQuizResults(quizId) {
      const data = await apiService.get(`/quizzes/${quizId}/results/`)
      this.quizResults[quizId] = data
      return data
    },

    async submitQuizAnswers(quizId, answers) {
      const data = await apiService.post(`/quizzes/${quizId}/submit/`, { answers })
      // Update linked quizzes to reflect completion
      await this.loadLinkedQuizzes()
      return data
    },

    // Initialization
    async initializeFromStorage() {
      if (!this.token) return false

      try {
        const data = await apiService.get('/participants/me/')
        this.participant = {
          id: data.id,
          name: data.name,
          email: data.email
        }
        
        this.isInitialized = true
        await this.loadLinkedQuizzes()
        return true
      } catch {
        this.clearParticipantData()
        return false
      }
    }
  }
})
