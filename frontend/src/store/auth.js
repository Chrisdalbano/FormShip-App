// store/auth.js
import { defineStore } from 'pinia'
import axios from 'axios'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: localStorage.getItem('jwt') || sessionStorage.getItem('jwt') || null,
        user: null, // Holds user details
    }),
    getters: {
        isAuthenticated: (state) => !!state.token,
        userDetails: (state) => state.user, // Easy access to user details
    },
    actions: {
        setToken(token) {
            this.token = token
            localStorage.setItem('jwt', token)
            sessionStorage.setItem('jwt', token) // Backup in sessionStorage
            this.fetchUser() // Fetch user details once the token is set
        },
        async fetchUser() {
            if (this.token) {
                try {
                    const response = await axios.get(`${apiBaseUrl}/user/profile/`, {
                        headers: { Authorization: `Bearer ${this.token}` },
                    })
                    this.user = response.data
                } catch (error) {
                    console.error('Failed to fetch user data', error)
                    this.logout() // Logout if fetching user data fails
                }
            }
        },
        async updateUserDetails(updatedUserData) {
            try {
                const response = await axios.put(`${apiBaseUrl}/user/profile/`, updatedUserData, {
                    headers: { Authorization: `Bearer ${this.token}` },
                })
                this.user = { ...this.user, ...updatedUserData } // Update user details in the store
                return response.data
            } catch (error) {
                console.error('Failed to update user details', error)
                throw error
            }
        },
        logout(router) {
            this.token = null
            this.user = null
            localStorage.removeItem('jwt')
            sessionStorage.removeItem('jwt') // Clear from sessionStorage as well
            if (router) {
                router.push('/auth') // Redirect to auth page if a router instance is provided
            }
        },
        async ssoLogin(provider) {
            console.log(`Logging in with ${provider}...`)
            // Implement SSO login logic as needed
        },
        initializeAuth() {
            // Called on app initialization to restore token and user details
            if (this.token) {
                this.fetchUser() // Fetch user details if a token exists
            }
        },
    },
})
