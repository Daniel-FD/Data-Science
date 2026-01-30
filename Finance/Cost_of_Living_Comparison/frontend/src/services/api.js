import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const fetchCities = async () => {
  try {
    const response = await api.get('/api/cities')
    return response.data.cities
  } catch (error) {
    console.error('Error fetching cities:', error)
    throw new Error('Failed to fetch cities')
  }
}

export const convertBasic = async (salary, sourceCity, currency = 'USD') => {
  try {
    const response = await api.get('/api/convert_basic', {
      params: {
        salary,
        source_city: sourceCity,
        currency,
      },
    })
    return response.data
  } catch (error) {
    console.error('Error in basic conversion:', error)
    throw new Error(error.response?.data?.detail || 'Failed to convert salary')
  }
}

export const convertAdvanced = async (salary, sourceCity, currency, expenses) => {
  try {
    const response = await api.post('/api/convert_advanced', {
      salary,
      source_city: sourceCity,
      currency,
      expenses,
    })
    return response.data
  } catch (error) {
    console.error('Error in advanced conversion:', error)
    throw new Error(error.response?.data?.detail || 'Failed to convert salary')
  }
}

export default api
