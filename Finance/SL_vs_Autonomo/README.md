# Simulador Fiscal España 2025 - SL vs Autónomo

Simulador fiscal profesional para comparar diferentes estructuras empresariales en España: Autónomo vs Sociedad Limitada (SL) con diferentes estrategias de retribución.

## 🎯 Características

- **4 Escenarios de comparación**:
  - Autónomo con cuotas por rendimiento
  - SL con retención completa de beneficios
  - SL con distribución total de dividendos
  - SL con salario/dividendos optimizado

- **Tax Engine actualizado 2025**:
  - IRPF Ahorro: 19%-30% (actualizado >300K)
  - IRPF General: 19%-47% en 6 tramos
  - Impuesto de Sociedades: Micro (21%/22%), SME (24%), General (25%), Startup (15%)
  - Seguridad Social: Empresa (30.57%) + Trabajador (6.5%)
  - Cotización de Solidaridad en salarios >4,909.50€/mes
  - Tarifa plana autónomos: 87€/mes año 1, reducida año 2

- **17 Comunidades Autónomas**: Soporte para todas las regiones (incluye regímenes forales)

- **Bilingual**: Español e Inglés completo (ES/EN)

- **Visualizaciones avanzadas**: 8 gráficos interactivos con Recharts

- **Contenido educativo**: Explicaciones, glosario y guía "Cómo Funciona"

## 🏗️ Arquitectura

```
SL_vs_Autonomo/
├── backend/                    # FastAPI + Python
│   ├── main.py                # Entry point
│   ├── tax_engine/            # Motor de cálculo fiscal
│   │   ├── constants.py       # Tasas y tramos 2025
│   │   ├── irpf.py           # IRPF general y ahorro
│   │   ├── impuesto_sociedades.py  # IS
│   │   ├── autonomos.py      # Cuotas autónomos
│   │   ├── seguridad_social.py     # SS y solidaridad
│   │   └── regional.py       # 17 regiones
│   ├── scenarios/            # Lógica de escenarios
│   │   ├── models.py         # Pydantic schemas
│   │   ├── autonomo.py
│   │   ├── sl_retencion.py
│   │   ├── sl_dividendos.py
│   │   └── sl_mixto.py       # Optimizador
│   ├── api/
│   │   └── routes.py         # Endpoints
│   └── tests/                # Suite de tests
│       ├── test_irpf.py
│       ├── test_impuesto_sociedades.py
│       ├── test_autonomos.py
│       └── test_seguridad_social.py
├── frontend/                  # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/       # UI components
│   │   ├── charts/          # 8 visualizaciones
│   │   ├── pages/           # Simulator, HowItWorks, Glossary
│   │   ├── i18n/            # ES/EN translations
│   │   └── api/             # API client
│   └── package.json
└── simulador_fiscal.py       # Original Streamlit (referencia)
```

## 🚀 Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API disponible en: http://localhost:8000  
Docs interactiva: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App disponible en: http://localhost:5173

### Tests

```bash
cd backend
pytest tests/ -v
```

**76 tests** cubren:
- IRPF ahorro y general (20 tests)
- Impuesto de Sociedades (17 tests)
- Cuotas autónomos y tarifa plana (21 tests)
- Seguridad Social y solidaridad (18 tests)

## 📊 API Endpoints

### `POST /api/simulate`

Ejecuta los 4 escenarios y retorna resultados completos.

**Request:**
```json
{
  "facturacion": 105000,
  "gastos_deducibles": 2000,
  "gastos_personales": 12000,
  "años": 10,
  "rentabilidad": 0.06,
  "capital_inicial": 0,
  "region": "Madrid",
  "tarifa_plana": true,
  "salario_administrador": 18000,
  "gastos_gestoria": 3000,
  "aportacion_plan_pensiones": 5750,
  "turnover": 105000,
  "company_age": 1,
  "is_startup": true
}
```

**Response:**
```json
{
  "autonomo": { ... },
  "sl_retencion": { ... },
  "sl_dividendos": { ... },
  "sl_mixto": { ... },
  "optimal_salary": 45500,
  "optimal_salary_curve": [...],
  "crossover": [...]
}
```

### `GET /api/regions`

Lista de 17 comunidades autónomas.

### `GET /api/presets`

Perfiles predefinidos (Programador 80K, Consultor 120K, etc.).

## 🧪 Ejemplos de Tests

### IRPF Ahorro
```python
# 50,000€ de dividendos
# 6,000€ * 19% + 44,000€ * 21% = 10,380€
assert calcular_irpf_ahorro(50_000) == 10_380
```

### Impuesto Sociedades
```python
# Micro empresa, 80K beneficio, <1M facturación
# 50K * 21% + 30K * 22% = 17,100€
assert calcular_is(80_000, 800_000, 1, False) == 17_100
```

### Cuota Autónomos
```python
# 60K rendimiento = 5,000€/mes -> tramo (4,050-6,000) = 590€/mes
assert calcular_cuota_autonomos(60_000, 3, False) == 7_080  # 590*12
```

### Solidaridad
```python
# 100K salario = 8,333€/mes
# Aplica sobre >4,909.50€/mes en 3 tramos
# Result: ~378€/año
assert 300 < calcular_solidaridad(100_000) < 500
```

## 🎨 Frontend Features

### Componentes principales:
- **Sidebar**: Inputs con tooltips, presets, validación
- **ResultsBanner**: "Mejor opción" destacada
- **MetricsCards**: 4 KPIs principales
- **ComparisonTable**: Tabla comparativa
- **DetailTabs**: Detalle año a año
- **Explanations**: Bloques educativos colapsables

### 8 Gráficos (Recharts):
1. **CapitalEvolution**: Evolución del capital (4 líneas)
2. **MonthlyIncome**: Renta mensual neta (barras agrupadas)
3. **TaxWaterfall**: Cascada impositiva (waterfall chart)
4. **EffectiveTaxRate**: Tipo efectivo vs facturación
5. **OptimalSalary**: Curva de optimización salario/dividendos
6. **TaxComposition**: Composición de impuestos (pie charts)
7. **SensitivityHeatmap**: Mapa de sensibilidad (años × rentabilidad)
8. **CrossoverPoint**: Punto de cruce entre escenarios

## 🌍 Bilingual Support

Archivos de traducción completos:
- `frontend/src/i18n/es.json`
- `frontend/src/i18n/en.json`

Toggle de idioma en navbar. Formato de números localizado.

## 📝 Notas Fiscales 2025

### IRPF Ahorro (dividendos, plusvalías)
| Tramo | Tipo |
|-------|------|
| 0-6K | 19% |
| 6-50K | 21% |
| 50-200K | 23% |
| 200-300K | 27% |
| >300K | **30%** |

### IRPF General (salarios, autónomos)
| Tramo | Tipo |
|-------|------|
| 0-12,450 | 19% |
| 12,450-20,200 | 24% |
| 20,200-35,200 | 30% |
| 35,200-60,000 | 37% |
| 60,000-300,000 | 45% |
| >300,000 | **47%** |

### Impuesto de Sociedades
- **Micro** (<1M facturación): 21% primeros 50K, 22% resto
- **SME** (1-10M): 24%
- **General** (>10M): 25%
- **Startup** (2 primeros años rentables): 15%

### Seguridad Social
- **Empresa**: 30.57%
- **Trabajador**: 6.5%
- **Solidaridad** (>4,909.50€/mes):
  - 4,909.50-5,410: 0.92%
  - 5,410-6,245: 1.00%
  - >6,245: 1.17%

### Autónomos
- **Tarifa plana**: 87€/mes año 1, 172€/mes año 2 si renta<SMI
- **Cuotas por rendimiento**: 14 tramos desde 230€/mes (≤670€/mes renta) hasta 590€/mes (>6,000€/mes renta)

## ⚠️ Disclaimer

> **Simulador orientativo. Consulta con un asesor fiscal profesional.**
> 
> Datos fiscales actualizados a enero 2025. Las normativas pueden variar. Los regímenes forales (Navarra, País Vasco) son aproximaciones.

## 🔧 Tech Stack

### Backend
- Python 3.11+
- FastAPI
- Pydantic v2
- Uvicorn
- Pytest

### Frontend
- React 18
- TypeScript
- Vite
- TailwindCSS
- Recharts
- React Router
- i18next
- React Query

## 📦 Deployment

### Producción Backend
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Producción Frontend
```bash
npm run build
# Sirve dist/ con nginx/Apache o via backend CORS
```

### Docker (Opcional)
```dockerfile
# Backend
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]

# Frontend
FROM node:18-alpine AS build
WORKDIR /app
COPY frontend/package*.json .
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
```

## 🤝 Contributing

1. Fork el repo
2. Crea una rama (`git checkout -b feature/mejora`)
3. Commit cambios (`git commit -m 'Añade nueva feature'`)
4. Push (`git push origin feature/mejora`)
5. Abre un Pull Request

## 📄 License

MIT License - ver LICENSE file

## 👨‍💻 Autor

Daniel-FD

---

**¿Preguntas?** Abre un issue en GitHub
