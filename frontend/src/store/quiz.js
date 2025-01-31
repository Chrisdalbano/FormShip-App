import { defineStore } from "pinia";
import axios from "axios";
import { useAuthStore } from './auth'
import { useRouter } from 'vue-router'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

export const useQuizStore = defineStore("quiz", {
    state: () => ({
        quiz: null,
        participantId: null,
        userAnswers: [],
        quizType: "all-at-once",
    }),
    actions: {
        async loadQuiz(quizId) {
            try {
                const res = await axios.get(`/api/quizzes/${quizId}/`);
                console.log("Loaded Quiz Data:", res.data);  // Debugging line
                this.quiz = res.data;

                // Check access control
                if (this.quiz.access_control === 'login_required') {
                    const authStore = useAuthStore()
                    if (!authStore.isAuthenticated) {
                        throw new Error('Authentication required')
                    }
                }

                if (res.data.questions && res.data.questions.length > 0) {
                    this.userAnswers = Array(res.data.questions.length).fill(null);
                } else {
                    console.error("Error: No questions found in the quiz!");
                }

                this.quizType = res.data.quiz_type === "stepwise" ? "stepwise" : "all-at-once";

                // Only create participant if needed
                if (!this.quiz.access_control === 'login_required') {
                    const participantRes = await axios.post(`/api/participants/quiz/${quizId}/`, {
                        name: "Guest User",
                    });
                    console.log("Participant Created:", participantRes.data);
                    this.participantId = participantRes.data.id;
                }
            } catch (error) {
                console.error("Error loading quiz:", error);
                if (error.message === 'Authentication required') {
                    // Redirect to login
                    const router = useRouter()
                    router.push({
                        name: 'Login',
                        query: { redirect: `/quiz/${quizId}` }
                    });
                }
                throw error;
            }
        },
        updateAnswer(questionIndex, answer) {
            this.userAnswers[questionIndex] = answer;
            console.log('Updated userAnswers:', this.userAnswers); // Debug
        },
        async submitAnswers() {
            console.log('Submitting userAnswers:', this.userAnswers); // Debug
            if (!this.participantId) {
                this.participantId = localStorage.getItem(`participant_${this.quiz.id}`);
                if (!this.participantId) {
                    console.error("Participant ID missing. Cannot submit quiz.");
                    return;
                }
            }

            try {
                // Submit answers
                await axios.post(`${apiBaseUrl}/quizzes/${this.quiz.id}/submit/`, {
                    participant_id: this.participantId,
                    quiz_id: this.quiz.id,
                    answers: this.userAnswers,
                });
            } catch (error) {
                console.error("Error submitting quiz answers:", error.response?.data || error.message);
                throw error;
            }
        }
    },
});
