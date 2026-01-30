import { MapContainer, TileLayer, Marker, Popup, CircleMarker } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import './MapView.css'

// Fix for default marker icons in React Leaflet
import L from 'leaflet'
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

function MapView({ results }) {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: results.currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value)
  }

  // Calculate color based on salary relative to source
  const getColor = (salary) => {
    const ratio = salary / results.source_salary
    if (ratio < 0.7) return '#28a745' // Green - much cheaper
    if (ratio < 0.9) return '#20c997' // Teal - cheaper
    if (ratio < 1.1) return '#ffc107' // Yellow - similar
    if (ratio < 1.3) return '#fd7e14' // Orange - expensive
    return '#dc3545' // Red - very expensive
  }

  // Calculate marker size based on salary
  const getRadius = (salary) => {
    const ratio = salary / results.source_salary
    return Math.max(5, Math.min(20, ratio * 10))
  }

  // Filter results with valid coordinates
  const validResults = results.results.filter(
    item => item.latitude && item.longitude
  )

  return (
    <div className="map-view-container">
      <div className="map-header">
        <h2>Global Salary Map</h2>
        <p>
          Comparing {formatCurrency(results.source_salary)} in{' '}
          <strong>{results.source_city}</strong>
        </p>
        
        <div className="map-legend">
          <h4>Cost of Living:</h4>
          <div className="legend-items">
            <div className="legend-item">
              <span className="legend-color" style={{ backgroundColor: '#28a745' }}></span>
              Much Lower (&lt;70%)
            </div>
            <div className="legend-item">
              <span className="legend-color" style={{ backgroundColor: '#20c997' }}></span>
              Lower (70-90%)
            </div>
            <div className="legend-item">
              <span className="legend-color" style={{ backgroundColor: '#ffc107' }}></span>
              Similar (90-110%)
            </div>
            <div className="legend-item">
              <span className="legend-color" style={{ backgroundColor: '#fd7e14' }}></span>
              Higher (110-130%)
            </div>
            <div className="legend-item">
              <span className="legend-color" style={{ backgroundColor: '#dc3545' }}></span>
              Much Higher (&gt;130%)
            </div>
          </div>
        </div>
      </div>

      <div className="map-wrapper">
        <MapContainer
          center={[20, 0]}
          zoom={2}
          style={{ height: '600px', width: '100%' }}
          scrollWheelZoom={true}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {validResults.map((item, index) => (
            <CircleMarker
              key={`${item.city}-${index}`}
              center={[item.latitude, item.longitude]}
              radius={getRadius(item.equivalent_salary)}
              fillColor={getColor(item.equivalent_salary)}
              color="#fff"
              weight={2}
              opacity={1}
              fillOpacity={0.7}
            >
              <Popup>
                <div className="map-popup">
                  <h3>{item.city}</h3>
                  <p className="popup-country">{item.country}</p>
                  <div className="popup-details">
                    <div className="popup-row">
                      <span className="popup-label">Equivalent Salary:</span>
                      <span className="popup-value salary">
                        {formatCurrency(item.equivalent_salary)}
                      </span>
                    </div>
                    <div className="popup-row">
                      <span className="popup-label">Cost Index:</span>
                      <span className="popup-value">{item.cost_index.toFixed(1)}</span>
                    </div>
                    <div className="popup-row">
                      <span className="popup-label">Difference:</span>
                      <span className={`popup-value ${
                        item.equivalent_salary > results.source_salary ? 'higher' : 'lower'
                      }`}>
                        {((item.equivalent_salary / results.source_salary - 1) * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>

      <div className="map-stats">
        <div className="stat-card">
          <h4>Cities Analyzed</h4>
          <p className="stat-value">{validResults.length}</p>
        </div>
        <div className="stat-card">
          <h4>Cheapest City</h4>
          <p className="stat-value">
            {validResults.length > 0 && validResults[0].city}
          </p>
          <p className="stat-detail">
            {validResults.length > 0 && formatCurrency(validResults[0].equivalent_salary)}
          </p>
        </div>
        <div className="stat-card">
          <h4>Most Expensive</h4>
          <p className="stat-value">
            {validResults.length > 0 && validResults[validResults.length - 1].city}
          </p>
          <p className="stat-detail">
            {validResults.length > 0 && formatCurrency(validResults[validResults.length - 1].equivalent_salary)}
          </p>
        </div>
      </div>
    </div>
  )
}

export default MapView
