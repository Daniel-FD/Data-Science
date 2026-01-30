import { useState, useEffect } from 'react'
import CitySalaryForm from './CitySalaryForm'
import './ExpenseBreakdown.css'

function ExpenseBreakdown({ onSubmit }) {
  const [salary, setSalary] = useState('')
  const [sourceCity, setSourceCity] = useState('')
  const [currency, setCurrency] = useState('USD')
  const [expenses, setExpenses] = useState({
    rent: 1500,
    food: 600,
    transport: 300,
    utilities: 200,
    entertainment: 400
  })

  const handleExpenseChange = (category, value) => {
    setExpenses(prev => ({
      ...prev,
      [category]: parseFloat(value) || 0
    }))
  }

  const handleFormSubmit = (sal, city, curr) => {
    setSalary(sal)
    setSourceCity(city)
    setCurrency(curr)
  }

  const handleAdvancedSubmit = (e) => {
    e.preventDefault()
    if (salary && sourceCity) {
      onSubmit(parseFloat(salary), sourceCity, currency, expenses)
    }
  }

  const totalExpenses = Object.values(expenses).reduce((sum, val) => sum + val, 0)

  const getPercentage = (value) => {
    return totalExpenses > 0 ? ((value / totalExpenses) * 100).toFixed(1) : 0
  }

  return (
    <div className="expense-breakdown">
      <CitySalaryForm 
        onSubmit={handleFormSubmit} 
        mode="advanced"
      />

      <div className="expense-form">
        <h2>Your Monthly Expenses</h2>
        <p className="expense-subtitle">
          Adjust the sliders to match your spending pattern
        </p>

        <div className="expense-items">
          {Object.entries(expenses).map(([category, value]) => (
            <div key={category} className="expense-item">
              <div className="expense-header">
                <label htmlFor={`expense-${category}`}>
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </label>
                <span className="expense-value">
                  {currency} {value.toFixed(0)}
                  <span className="expense-percentage">
                    ({getPercentage(value)}%)
                  </span>
                </span>
              </div>
              
              <input
                id={`expense-${category}`}
                type="range"
                min="0"
                max="5000"
                step="50"
                value={value}
                onChange={(e) => handleExpenseChange(category, e.target.value)}
                className="expense-slider"
              />
              
              <input
                type="number"
                min="0"
                step="10"
                value={value}
                onChange={(e) => handleExpenseChange(category, e.target.value)}
                className="expense-input"
              />
            </div>
          ))}
        </div>

        <div className="expense-summary">
          <h3>Total Monthly Expenses</h3>
          <p className="total-amount">{currency} {totalExpenses.toFixed(2)}</p>
          <p className="annual-amount">
            Annual: {currency} {(totalExpenses * 12).toFixed(2)}
          </p>
        </div>

        <button 
          type="button" 
          className="submit-button"
          onClick={handleAdvancedSubmit}
          disabled={!salary || !sourceCity}
        >
          Compare with Personal Budget
        </button>
      </div>
    </div>
  )
}

export default ExpenseBreakdown
