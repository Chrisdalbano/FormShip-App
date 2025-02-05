import axios from 'axios'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

class ApiService {
  constructor() {
    this.axios = axios.create({
      baseURL: apiBaseUrl,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // Add request interceptor to ensure headers are set
    this.axios.interceptors.request.use(
      (config) => {
        // Always get the latest token
        const token = this.getAuthToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Add response interceptor to handle token errors
    this.axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.clearAuthToken()
        }
        return Promise.reject(error)
      }
    )
  }

  getAuthToken() {
    return localStorage.getItem('participant_token')
  }

  setAuthToken(token) {
    if (token) {
      localStorage.setItem('participant_token', token)
      this.axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    } else {
      this.clearAuthToken()
    }
  }

  clearAuthToken() {
    localStorage.removeItem('participant_token')
    delete this.axios.defaults.headers.common['Authorization']
  }

  async get(url, config = {}) {
    try {
      const response = await this.axios.get(url, {
        ...config,
        headers: {
          ...config.headers,
          Authorization: `Bearer ${this.getAuthToken()}`
        }
      })
      return response.data
    } catch (error) {
      if (error.response?.status === 401) {
        this.clearAuthToken()
      }
      throw error
    }
  }

  async post(url, data = {}, config = {}) {
    try {
      const response = await this.axios.post(url, data, {
        ...config,
        headers: {
          ...config.headers,
          Authorization: `Bearer ${this.getAuthToken()}`
        }
      })
      return response.data
    } catch (error) {
      if (error.response?.status === 401) {
        this.clearAuthToken()
      }
      throw error
    }
  }

  async put(url, data = {}, config = {}) {
    try {
      const response = await this.axios.put(url, data, {
        ...config,
        headers: {
          ...config.headers,
          Authorization: `Bearer ${this.getAuthToken()}`
        }
      })
      return response.data
    } catch (error) {
      if (error.response?.status === 401) {
        this.clearAuthToken()
      }
      throw error
    }
  }

  async delete(url, config = {}) {
    try {
      const response = await this.axios.delete(url, {
        ...config,
        headers: {
          ...config.headers,
          Authorization: `Bearer ${this.getAuthToken()}`
        }
      })
      return response.data
    } catch (error) {
      if (error.response?.status === 401) {
        this.clearAuthToken()
      }
      throw error
    }
  }
}

export const apiService = new ApiService()
export default apiService 