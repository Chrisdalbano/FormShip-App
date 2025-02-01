import { defineStore } from "pinia";
import axios from "axios";
import { useParticipantStore } from './participant'
// import { useAuthStore } from './auth'
// import { useRouter } from 'vue-router'

export const useQuizStore = defineStore("quiz", {
    state: () => ({
        quiz: null,
        userAnswers: [],
        quizType: "all_at_once",
        isTestMode: false
    }),
    actions: {
        async loadQuiz(quizId) {
            try {
                const response = await axios.get(`/api/quizzes/${quizId}/`)
                this.quiz = response.data
                this.quizType = response.data.quiz_type || "all_at_once"
                this.userAnswers = Array(response.data.questions.length).fill(null)
            } catch (error) {
                console.error('Error loading quiz:', error)
                throw error
            }
        },

        initializeQuiz(quizData) {
            if (quizData.questions?.length > 0) {
                this.userAnswers = Array(quizData.questions.length).fill(null)
            }
            this.quizType = quizData.quiz_type === "stepwise" ? "stepwise" : "all_at_once"
        },

        updateAnswer(questionIndex, answer) {
            this.userAnswers[questionIndex] = answer;
            console.log('Updated userAnswers:', this.userAnswers); // Debug
        },
        async submitAnswers(answers) {
            console.log('Submitting userAnswers:', answers)
            const participantStore = useParticipantStore()
            
            if (!participantStore.participant?.id || !participantStore.token) {
                throw new Error('Participant not authenticated')
            }

            const baseURL = window.location.origin.replace('5173', '8000')
            const axiosInstance = axios.create({
                baseURL,
                headers: {
                    'Authorization': `Bearer ${participantStore.token}`,
                    'Content-Type': 'application/json'
                }
            })

            try {
                console.log('Submitting with token:', participantStore.token)
                const response = await axiosInstance.post(
                    `/api/quizzes/${this.quiz.id}/submit/`,
                    {
                        participant_id: participantStore.participant.id,
                        answers: answers,
                        score: this.calculateScore(answers)
                    }
                )
                return response.data
            } catch (error) {
                console.error('Error submitting quiz answers:', error.response?.data || error)
                throw error
            }
        },
        calculateScore(answers) {
            return this.quiz.questions.reduce((score, question, index) => {
                return score + (answers[index] === question.correct_answer ? 1 : 0)
            }, 0)
        }
    },
});
