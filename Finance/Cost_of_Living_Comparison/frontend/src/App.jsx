import { useState } from 'react'
import CitySalaryForm from './components/CitySalaryForm'
import ExpenseBreakdown from './components/ExpenseBreakdown'
import ResultsTable from './components/ResultsTable'
import MapView from './components/MapView'
import { convertBasic, convertAdvanced, fetchCities } from './services/api'
import './App.css'

function App() {
  const [mode, setMode] = useState('basic') // 'basic' or 'advanced'
  const [view, setView] = useState('table') // 'table' or 'map'
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [results, setResults] = useState(null)

  const handleBasicSubmit = async (salary, sourceCity, currency) => {
    setLoading(true)
    setError(null)
    
    try {
      const data = await convertBasic(salary, sourceCity, currency)
      setResults(data)
    } catch (err) {
      setError(err.message || 'Failed to fetch results')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleAdvancedSubmit = async (salary, sourceCity, currency, expenses) => {
    setLoading(true)
    setError(null)
    
    try {
      const data = await convertAdvanced(salary, sourceCity, currency, expenses)
      setResults(data)
    } catch (err) {
      setError(err.message || 'Failed to fetch results')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>💰 Cost of Living Comparison</h1>
        <p>Compare your salary across cities worldwide</p>
      </header>

      <div className="app-container">
        {/* Mode Selector */}
        <div className="mode-selector">
          <button
            className={mode === 'basic' ? 'active' : ''}
            onClick={() => setMode('basic')}
          >
            Basic Mode
          </button>
          <button
            className={mode === 'advanced' ? 'active' : ''}
            onClick={() => setMode('advanced')}
          >
            Advanced Mode
          </button>
        </div>

        {/* Input Form */}
        <div className="input-section">
          <CitySalaryForm
            onSubmit={mode === 'basic' ? handleBasicSubmit : null}
            mode={mode}
          />
          
          {mode === 'advanced' && (
            <ExpenseBreakdown onSubmit={handleAdvancedSubmit} />
          )}
        </div>

        {/* Loading State */}
        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Calculating equivalent salaries...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="error">
            <p>⚠️ {error}</p>
          </div>
        )}

        {/* Results */}
        {results && !loading && (
          <>
            <div className="view-selector">
              <button
                className={view === 'table' ? 'active' : ''}
                onClick={() => setView('table')}
              >
                📊 Table View
              </button>
              <button
                className={view === 'map' ? 'active' : ''}
                onClick={() => setView('map')}
              >
                🗺️ Map View
              </button>
            </div>

            <div className="results-section">
              {view === 'table' ? (
                <ResultsTable results={results} />
              ) : (
                <MapView results={results} />
              )}
            </div>
          </>
        )}
      </div>

      <footer className="app-footer">
        <p>Data powered by cost of living indices | Built with React + FastAPI</p>
      </footer>
    </div>
  )
}

export default App
