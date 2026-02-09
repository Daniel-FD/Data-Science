import { useState, useEffect } from 'react'
import { fetchCities } from '../services/api'
import './CitySalaryForm.css'

function CitySalaryForm({ onSubmit, mode }) {
  const [salary, setSalary] = useState('')
  const [sourceCity, setSourceCity] = useState('')
  const [currency, setCurrency] = useState('USD')
  const [cities, setCities] = useState([])
  const [loading, setLoading] = useState(true)
  const [filteredCities, setFilteredCities] = useState([])
  const [showDropdown, setShowDropdown] = useState(false)

  useEffect(() => {
    const loadCities = async () => {
      try {
        const citiesList = await fetchCities()
        setCities(citiesList)
        setFilteredCities(citiesList)
      } catch (error) {
        console.error('Failed to load cities:', error)
      } finally {
        setLoading(false)
      }
    }
    loadCities()
  }, [])

  const handleCityInput = (value) => {
    setSourceCity(value)
    setShowDropdown(true)
    
    if (value.trim()) {
      const filtered = cities.filter(city =>
        city.toLowerCase().includes(value.toLowerCase())
      )
      setFilteredCities(filtered)
    } else {
      setFilteredCities(cities)
    }
  }

  const handleCitySelect = (city) => {
    setSourceCity(city)
    setShowDropdown(false)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (salary && sourceCity && onSubmit) {
      onSubmit(parseFloat(salary), sourceCity, currency)
    }
  }

  const currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'INR']

  return (
    <form className="city-salary-form" onSubmit={handleSubmit}>
      <h2>{mode === 'basic' ? 'Enter Your Details' : 'Basic Information'}</h2>
      
      <div className="form-grid">
        <div className="form-group">
          <label htmlFor="salary">Annual Salary</label>
          <input
            id="salary"
            type="number"
            value={salary}
            onChange={(e) => setSalary(e.target.value)}
            placeholder="e.g., 80000"
            min="0"
            step="1000"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="currency">Currency</label>
          <select
            id="currency"
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
          >
            {currencies.map(curr => (
              <option key={curr} value={curr}>{curr}</option>
            ))}
          </select>
        </div>

        <div className="form-group city-autocomplete">
          <label htmlFor="source-city">Your City</label>
          <input
            id="source-city"
            type="text"
            value={sourceCity}
            onChange={(e) => handleCityInput(e.target.value)}
            onFocus={() => setShowDropdown(true)}
            onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
            placeholder="Type to search..."
            required
            disabled={loading}
          />
          
          {showDropdown && filteredCities.length > 0 && (
            <ul className="city-dropdown">
              {filteredCities.slice(0, 10).map(city => (
                <li
                  key={city}
                  onClick={() => handleCitySelect(city)}
                  className="city-option"
                >
                  {city}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {mode === 'basic' && (
        <button type="submit" className="submit-button">
          Compare Cities
        </button>
      )}
    </form>
  )
}

export default CitySalaryForm
