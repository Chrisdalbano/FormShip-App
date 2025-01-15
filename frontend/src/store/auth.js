import { defineStore } from 'pinia';
import axios from 'axios';

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: localStorage.getItem('jwt') || sessionStorage.getItem('jwt') || null,
        user: null,
        account: null,
    }),
    getters: {
        isAuthenticated: (state) => !!state.token,
        userDetails: (state) => state.user,
        accountDetails: (state) => state.account,
    },
    actions: {
        setToken(token) {
            this.token = token;
            localStorage.setItem('jwt', token);
            sessionStorage.setItem('jwt', token);
        },
        async fetchUser() {
            if (this.token) {
              try {
                const userResponse = await axios.get(`${apiBaseUrl}/user/profile/`, {
                  headers: { Authorization: `Bearer ${this.token}` },
                });
                this.user = userResponse.data;
          
                if (this.user.account_id) {
                  try {
                    const accountResponse = await axios.get(
                      `${apiBaseUrl}/accounts/${this.user.account_id}/`,
                      { headers: { Authorization: `Bearer ${this.token}` } }
                    );
                    this.account = accountResponse.data;
                  } catch (accountError) {
                    console.error("Failed to fetch account details:", accountError);
                    this.account = null;
                  }
                } else {
                  console.warn("No account associated with this user.");
                  this.account = null;
                }
              } catch (error) {
                console.error("Error fetching user or account details:", error);
                this.logout();
              }
            }
          },
          

        logout(router = null) {
            this.token = null;
            this.user = null;
            this.account = null;
            localStorage.removeItem('jwt');
            sessionStorage.removeItem('jwt');
            if (router) {
                router.push('/auth');
            }
        },
        initializeAuth() {
            if (this.token) {
                this.fetchUser();
            }
        },
    },
});
