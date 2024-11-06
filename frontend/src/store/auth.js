// store/auth.js
import { defineStore } from 'pinia'
import axios from 'axios'
// import AuthView from '@/views/AuthView.vue'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: localStorage.getItem('jwt') || null,
        user: null,
    }),
    getters: {
        isAuthenticated: (state) => !!state.token,
    },
    actions: {
        setToken(token) {
            this.token = token
            localStorage.setItem('jwt', token)
            this.fetchUser()
        },
        async fetchUser() {
            if (this.token) {
                try {
                    const response = await axios.get('http://localhost:8000/api/users/me/', {
                        headers: { Authorization: `Bearer ${this.token}` },
                    })
                    this.user = response.data
                } catch (error) {
                    console.error('Failed to fetch user data', error)
                }
            }
        },
        logout(router) {
            this.token = null
            this.user = null
            localStorage.removeItem('jwt')
            router.push('/auth')  // Use router to redirect
        },

        async ssoLogin(provider) {
            // Placeholder for SSO integration
            console.log(`Logging in with ${provider}...`)
            // Implement SSO login logic as needed
        },
    },
})
