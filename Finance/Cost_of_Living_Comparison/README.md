# Cost of Living Comparison Tool

A modern, minimalistic web application that compares cost of living across 4,956 cities worldwide. Calculate equivalent salaries based on your current location and desired destination to make informed relocation decisions.

![Cost of Living Comparison](https://img.shields.io/badge/cities-4956-blue) ![Python](https://img.shields.io/badge/Python-3.11+-green) ![React](https://img.shields.io/badge/React-18-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.104-teal)

## ✨ Features

- **4,956 Cities**: Comprehensive dataset covering major cities worldwide
- **Two Comparison Modes**:
  - **Basic Mode**: Quick salary conversion with simple cost of living comparison
  - **Advanced Mode**: Detailed expense breakdown by category (housing, food, transportation, etc.)
- **Interactive Visualization**:
  - **Table View**: Sortable results with detailed metrics
  - **Map View**: Geographic visualization with color-coded affordability markers
- **Multi-Currency Support**: Convert salaries across major world currencies
- **Real-Time Search**: Fast city autocomplete powered by intelligent filtering
- **Modern UI/UX**: Clean, minimalistic design optimized for usability

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **npm** or **yarn**

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Daniel-FD/Data-Science.git
cd Data-Science/Finance/Cost_of_Living_Comparison
```

2. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
```

3. **Frontend Setup**
```bash
cd ../frontend
npm install
cp .env.example .env
```

### Running Locally

**Terminal 1 - Backend:**
```bash
cd backend
python3 main.py
```
Backend runs on `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend runs on `http://localhost:3000`

Visit `http://localhost:3000` in your browser.

## 🐳 Docker Deployment

Run the entire stack with Docker:

```bash
docker-compose up --build
```

Access:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

## 📊 Dataset

The application uses the **Kaggle Global Cost of Living Dataset v2** with:
- 4,956 cities across 195 countries
- 55+ cost metrics per city
- Regular updates with real-world data

Data includes: meals, groceries, transportation, utilities, rent, and more.

## 🏗️ Architecture

### Backend (FastAPI)
```
backend/
├── main.py                 # FastAPI application & endpoints
├── services/
│   ├── data_loader.py      # Dataset processing
│   ├── numbeo_service.py   # Cost calculations
│   └── fx_service.py       # Currency conversion
├── models/
│   └── schemas.py          # Pydantic models
└── data/
    └── kaggle/
        └── cost-of-living_v2.csv
```

### Frontend (React + Vite)
```
frontend/
├── src/
│   ├── App.jsx             # Main application
│   ├── components/
│   │   ├── CitySalaryForm.jsx
│   │   ├── ExpenseBreakdown.jsx
│   │   ├── ResultsTable.jsx
│   │   └── MapView.jsx
│   └── services/
│       └── api.js          # API client
```

## 📡 API Endpoints

### GET `/api/cities`
Get all available cities
```json
["New York, United States", "London, United Kingdom", ...]
```

### GET `/api/convert_basic`
Basic salary conversion
```
?salary=100000&source_city=New York, United States&currency=USD
```

### POST `/api/convert_advanced`
Advanced conversion with expense breakdown
```json
{
  "salary": 100000,
  "source_city": "New York, United States",
  "currency": "USD",
  "categories": {
    "housing": 30,
    "food": 15,
    "transportation": 10,
    "utilities": 5,
    "healthcare": 10,
    "entertainment": 10,
    "savings": 20
  }
}
```

## 🎨 Technologies

**Backend:**
- FastAPI 0.104.1
- Python 3.11+
- Pandas 2.1.4
- Uvicorn (ASGI server)

**Frontend:**
- React 18.2.0
- Vite 5.4.20
- Axios
- Leaflet (Maps)
- Recharts (Charts)

**DevOps:**
- Docker & Docker Compose
- Nginx (production)

## 🔧 Configuration

### Backend `.env`
```env
# No configuration needed - works out of the box
```

### Frontend `.env`
```env
VITE_API_URL=http://localhost:8000
```

For production, update `VITE_API_URL` to your backend domain.

## 📈 Performance

- **Dataset Load Time**: ~2 seconds (4,956 cities)
- **API Response Time**: <100ms average
- **Search Autocomplete**: Real-time (<50ms)
- **Memory Usage**: ~150MB backend, ~80MB frontend

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Dataset: [Kaggle Global Cost of Living](https://www.kaggle.com/datasets/mvieira101/global-cost-of-living)
- Maps: [Leaflet](https://leafletjs.com/)
- Icons: OpenStreetMap contributors

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ for informed relocation decisions**
