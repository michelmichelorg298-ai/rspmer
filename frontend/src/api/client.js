import axios from 'axios'

const BASE_URL = '/api'

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('fruitmer_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('fruitmer_token')
      localStorage.removeItem('fruitmer_user')
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login: (username, password) => {
    const form = new URLSearchParams()
    form.append('username', username)
    form.append('password', password)
    return apiClient.post('/token', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },
  me: (overrideToken) => {
    const config = overrideToken ? { headers: { Authorization: `Bearer ${overrideToken}` } } : {}
    return apiClient.get('/me', config).then(r => r.data)
  },
  changePassword: (oldPassword, newPassword) => {
    return apiClient.post('/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    }).then(r => r.data)
  },
}

const buildCrud = (prefix) => ({
  list: (params = {}) => apiClient.get(prefix, { params }).then(r => r.data),
  get: (id) => apiClient.get(`${prefix}/${id}`).then(r => r.data),
  create: (data) => apiClient.post(prefix, data).then(r => r.data),
  update: (id, data) => apiClient.put(`${prefix}/${id}`, data).then(r => r.data),
  remove: (id) => apiClient.delete(`${prefix}/${id}`).then(r => r.data),
})

export const productsApi = buildCrud('/products')
export const fournituresApi = buildCrud('/fournitures')
export const ventesApi = buildCrud('/ventes')
export const retoursApi = buildCrud('/commandes-retour')
export const usersApi = buildCrud('/users')

export const kpisApi = {
  getLots: (productId) => apiClient.get('/kpis/lots', { params: productId ? { product_id: productId } : {} }).then(r => r.data),
  getAnalytics: (fournitureId) => apiClient.get(`/kpis/analytics/${fournitureId}`).then(r => r.data),
}

export default apiClient
