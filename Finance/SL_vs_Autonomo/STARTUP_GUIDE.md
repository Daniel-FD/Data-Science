# 🚀 Startup Guide - Simulador Fiscal SL vs Autónomo

This guide will help you run the fiscal simulator on your local machine.

## Prerequisites

Before starting, ensure you have installed:
- **Python 3.11+** - [Download here](https://www.python.org/downloads/)
- **Node.js 18+** - [Download here](https://nodejs.org/)
- **Git** - [Download here](https://git-scm.com/)

## Quick Start (Easiest Method)

### 🪟 Windows
1. Open the `Finance/SL_vs_Autonomo` folder
2. Double-click `start.bat`
3. Two terminal windows will open (backend and frontend)
4. Your browser will automatically open at http://localhost:5173

### 🐧 Linux / 🍎 macOS
1. Open terminal in `Finance/SL_vs_Autonomo` folder
2. Run: `./start.sh`
3. Open your browser at http://localhost:5173

---

## Manual Setup (Step by Step)

If you prefer manual control or the automated scripts don't work:

### Step 1: Backend Setup

```bash
# Navigate to backend directory
cd Finance/SL_vs_Autonomo/backend

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the backend server
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Backend will be running at:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Step 2: Frontend Setup

Open a **new terminal window** (keep backend running):

```bash
# Navigate to frontend directory
cd Finance/SL_vs_Autonomo/frontend

# Install dependencies (first time only)
npm install

# Start the development server
npm run dev
```

**Frontend will be running at:**
- App: http://localhost:5173

### Step 3: Access the Application

1. Open your browser
2. Navigate to: **http://localhost:5173**
3. The app will automatically connect to the backend API

---

## What You'll See

### 🎨 Frontend (React App)
- **Main Page**: Fiscal simulator with input parameters
- **Charts**: 8 interactive visualizations
- **Comparisons**: Side-by-side scenario analysis
- **Language Toggle**: Switch between Spanish and English

### 🔧 Backend (API)
- **Interactive Docs**: Visit http://localhost:8000/docs
- **API Endpoints**:
  - `GET /api/regions` - List of 17 comunidades autónomas
  - `GET /api/presets` - Quick preset profiles
  - `POST /api/simulate` - Run full simulation
  - `GET /health` - Health check

---

## Troubleshooting

### Port Already in Use

If you see "port already in use" errors:

**Backend (port 8000):**
```bash
# Find and kill process on Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# On Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

**Frontend (port 5173):**
```bash
# Find and kill process on Windows:
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# On Linux/Mac:
lsof -ti:5173 | xargs kill -9
```

### Dependencies Not Installing

**Backend:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Try installing again
pip install -r requirements.txt
```

**Frontend:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Backend Import Errors

Make sure you're in the correct directory and virtual environment is activated:
```bash
cd Finance/SL_vs_Autonomo/backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -c "from backend.main import app; print('✅ Backend imports work!')"
```

### Frontend Not Connecting to Backend

1. Check that backend is running at http://localhost:8000/health
2. Verify the `.env` file exists in `frontend/` folder:
   ```
   VITE_API_BASE=http://localhost:8000
   ```
3. Restart the frontend dev server after changing `.env`

### Browser Shows Blank Page

1. Check browser console (F12) for errors
2. Verify both servers are running (backend and frontend)
3. Try clearing browser cache (Ctrl+Shift+Del)
4. Try a different browser

---

## Testing the Installation

### Test Backend
```bash
# Navigate to backend
cd Finance/SL_vs_Autonomo/backend

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run tests
pytest tests/ -v

# Should show: 83 passed in ~0.2s
```

### Test API Manually
```bash
# Test health endpoint
curl http://localhost:8000/health

# Should return: {"status":"ok"}

# Test regions endpoint
curl http://localhost:8000/api/regions

# Should return list of 17 regions
```

### Test Frontend
1. Open http://localhost:5173
2. You should see the fiscal simulator interface
3. Select a region from the dropdown
4. Click on a preset profile (e.g., "Programador 80K")
5. The form should populate with values
6. Click "Simular" button
7. Results should appear with charts

---

## Configuration

### Environment Variables

**Backend** - No configuration needed (uses defaults)

**Frontend** - `frontend/.env`:
```env
VITE_API_BASE=http://localhost:8000
```

### Custom Ports

**Backend** - Edit the uvicorn command:
```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 9000
```

**Frontend** - Edit `frontend/vite.config.ts`:
```typescript
export default defineConfig({
  server: {
    port: 3000,  // Change this
    proxy: {
      '/api': {
        target: 'http://localhost:9000',  // Update backend port
        changeOrigin: true,
      }
    }
  },
});
```

---

## Development Tips

### Hot Reload

Both servers support hot reload:
- **Backend**: Changes to `.py` files automatically restart the server
- **Frontend**: Changes to `.tsx`, `.ts`, `.css` files automatically update the browser

### API Documentation

While the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test all API endpoints directly from the Swagger interface!

### Browser DevTools

Use browser DevTools (F12) to:
- Inspect network requests to the API
- Debug React components
- Check console for errors
- Monitor performance

### VSCode Extensions (Recommended)

- **Python** - Microsoft
- **Pylance** - Microsoft
- **ESLint** - Microsoft
- **Prettier** - Prettier
- **Vite** - antfu

---

## Stopping the Servers

### Using Scripts
- **Windows**: Close the terminal windows
- **Linux/Mac**: Press `Ctrl+C` in the terminal

### Manual
```bash
# Stop backend: Press Ctrl+C in backend terminal
# Stop frontend: Press Ctrl+C in frontend terminal
```

---

## Production Deployment

For production deployment instructions, see:
- `README.md` - Deployment section
- `REVIEW_SUMMARY.md` - Production readiness assessment

---

## Need Help?

### Check Logs
- **Backend logs**: Terminal where backend is running
- **Frontend logs**: Browser console (F12)
- **Network errors**: Browser DevTools → Network tab

### Common Issues
1. ✅ **Tests passing but app not working**: Restart both servers
2. ✅ **API calls failing**: Check CORS and backend URL configuration
3. ✅ **Blank page**: Check browser console for JavaScript errors
4. ✅ **Slow loading**: Check network connection and API response times

### Documentation
- `README.md` - Full documentation
- `REVIEW_SUMMARY.md` - Implementation details
- `SECURITY.md` - Security information

---

## Quick Reference

```bash
# Backend
cd Finance/SL_vs_Autonomo/backend
source venv/bin/activate
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Frontend
cd Finance/SL_vs_Autonomo/frontend
npm run dev

# Tests
cd Finance/SL_vs_Autonomo/backend
pytest tests/ -v
```

**URLs:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

**Happy Simulating! 🎉**
