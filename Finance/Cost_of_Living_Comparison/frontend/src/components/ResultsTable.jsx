import { useState, useMemo } from 'react'
import './ResultsTable.css'

function ResultsTable({ results }) {
  const [sortConfig, setSortConfig] = useState({ key: 'equivalent_salary', direction: 'asc' })
  const [searchTerm, setSearchTerm] = useState('')

  const sortedAndFilteredResults = useMemo(() => {
    let filtered = results.results

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(
        item =>
          item.city.toLowerCase().includes(searchTerm.toLowerCase()) ||
          item.country.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Sort
    const sorted = [...filtered].sort((a, b) => {
      const aValue = a[sortConfig.key]
      const bValue = b[sortConfig.key]

      if (typeof aValue === 'string') {
        return sortConfig.direction === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue)
      }

      return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue
    })

    return sorted
  }, [results.results, sortConfig, searchTerm])

  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }))
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: results.currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value)
  }

  const getSortIcon = (key) => {
    if (sortConfig.key !== key) return '⇅'
    return sortConfig.direction === 'asc' ? '↑' : '↓'
  }

  return (
    <div className="results-table-container">
      <div className="results-header">
        <div className="results-info">
          <h2>Salary Comparison Results</h2>
          <p>
            Based on {formatCurrency(results.source_salary)} in{' '}
            <strong>{results.source_city}</strong>
          </p>
          <p className="results-count">
            Showing {sortedAndFilteredResults.length} cities
          </p>
        </div>

        <div className="search-box">
          <input
            type="text"
            placeholder="Search cities or countries..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
      </div>

      <div className="table-wrapper">
        <table className="results-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('city')} className="sortable">
                City {getSortIcon('city')}
              </th>
              <th onClick={() => handleSort('country')} className="sortable">
                Country {getSortIcon('country')}
              </th>
              <th onClick={() => handleSort('equivalent_salary')} className="sortable">
                Equivalent Salary {getSortIcon('equivalent_salary')}
              </th>
              <th onClick={() => handleSort('cost_index')} className="sortable">
                Cost Index {getSortIcon('cost_index')}
              </th>
              <th>Difference</th>
            </tr>
          </thead>
          <tbody>
            {sortedAndFilteredResults.map((item, index) => {
              const difference = item.equivalent_salary - results.source_salary
              const percentDiff = ((difference / results.source_salary) * 100).toFixed(1)
              const isHigher = difference > 0

              return (
                <tr key={`${item.city}-${index}`}>
                  <td className="city-cell">{item.city}</td>
                  <td>{item.country}</td>
                  <td className="salary-cell">
                    {formatCurrency(item.equivalent_salary)}
                  </td>
                  <td className="index-cell">{item.cost_index.toFixed(1)}</td>
                  <td className={`difference-cell ${isHigher ? 'higher' : 'lower'}`}>
                    {isHigher ? '+' : ''}
                    {formatCurrency(difference)}
                    <span className="percent">({percentDiff}%)</span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {sortedAndFilteredResults.length === 0 && (
        <div className="no-results">
          <p>No cities found matching "{searchTerm}"</p>
        </div>
      )}
    </div>
  )
}

export default ResultsTable
