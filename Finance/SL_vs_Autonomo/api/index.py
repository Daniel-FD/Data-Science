"""
Vercel Serverless Function - FastAPI Backend
=============================================
Vercel has built-in ASGI support for FastAPI.
No need for mangum - just export the app.
"""

import sys
import os
from pathlib import Path

# Add paths for imports to work in both local dev and Vercel
function_dir = Path(__file__).parent
project_root = function_dir.parent

# Add project root first (for local development: backend/ is sibling to api/)
sys.path.insert(0, str(project_root))
# Add function dir (for Vercel: backend/ is bundled inside api/ via includeFiles)
sys.path.insert(0, str(function_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Create app first
app = FastAPI(
    title="Simulador Fiscal Espana",
    description="API for Spanish tax regime comparison",
    version="2.0.0",
)

# CORS - allow all origins for API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track import status
BACKEND_AVAILABLE = False
IMPORT_ERROR = None

# Try to import backend modules
try:
    from backend.models.schemas import (
        EmployeeRequest, AutonomoRequest, SLRequest, OptimalSalaryRequest,
        CompareRequest, InvestmentRequest, CompareInvestmentRequest,
        CrossoverRequest, SensitivityRequest, InvestmentOptimizerRequest,
    )
    from backend.calculators.employee import calcular_asalariado
    from backend.calculators.autonomo import calcular_autonomo, calcular_facturacion_para_salario
    from backend.calculators.sl import calcular_sl, encontrar_salario_optimo
    from backend.calculators.investment import (
        simular_inversion, generar_sensibilidad,
        comparar_escenarios_inversion, optimizar_inversion_autonomo_vs_sl
    )
    from backend.tax_engine.regional import REGIONES_DISPONIBLES
    BACKEND_AVAILABLE = True
except ImportError as e:
    IMPORT_ERROR = str(e)


# ============================================================
# DEBUG / ROOT
# ============================================================

@app.get("/api")
async def api_root():
    return {
        "name": "Simulador Fiscal Espana",
        "version": "2.0.0",
        "status": "ok" if BACKEND_AVAILABLE else "error",
        "backend_available": BACKEND_AVAILABLE,
        "import_error": IMPORT_ERROR,
    }


@app.get("/api/debug")
async def debug_info():
    """Debug endpoint to check paths and imports."""
    info = {
        "sys_path": sys.path[:5],
        "function_dir": str(function_dir),
        "project_root": str(project_root),
        "backend_available": BACKEND_AVAILABLE,
        "import_error": IMPORT_ERROR,
    }

    # Check what files exist
    try:
        info["function_dir_contents"] = os.listdir(function_dir)
    except Exception as e:
        info["function_dir_contents"] = str(e)

    # Check for backend in both locations
    backend_in_func = function_dir / "backend"
    backend_in_root = project_root / "backend"

    info["backend_in_function_dir"] = backend_in_func.exists()
    info["backend_in_project_root"] = backend_in_root.exists()

    if backend_in_func.exists():
        try:
            info["backend_contents"] = os.listdir(backend_in_func)
        except Exception as e:
            info["backend_contents"] = str(e)
    elif backend_in_root.exists():
        try:
            info["backend_contents"] = os.listdir(backend_in_root)
        except Exception as e:
            info["backend_contents"] = str(e)

    return info


# ============================================================
# CONDITIONAL ENDPOINTS (only if backend loaded)
# ============================================================

if BACKEND_AVAILABLE:
    # ============================================================
    # INDIVIDUAL CALCULATORS
    # ============================================================

    @app.post("/api/employee")
    async def calculate_employee(req: EmployeeRequest):
        return calcular_asalariado(req.salario_bruto_anual, req.region, req.num_pagas)


    @app.post("/api/autonomo")
    async def calculate_autonomo(req: AutonomoRequest):
        return calcular_autonomo(
            req.facturacion_anual, req.region,
            req.gastos_deducibles_pct, req.gastos_deducibles_fijos,
            req.tarifa_plana, req.cuota_personalizada,
        )


    @app.post("/api/sl")
    async def calculate_sl(req: SLRequest):
        return calcular_sl(
            req.facturacion_anual, req.salario_administrador,
            req.gastos_empresa, req.gastos_gestoria,
            req.tipo_empresa, req.region, req.pct_dividendos,
        )


    @app.post("/api/sl/optimal-salary")
    async def calculate_optimal_salary(req: OptimalSalaryRequest):
        return encontrar_salario_optimo(
            req.facturacion_anual, req.gastos_empresa,
            req.gastos_gestoria, req.tipo_empresa,
            req.region, req.pct_dividendos,
        )


    # ============================================================
    # COMPARISON
    # ============================================================

    @app.post("/api/compare")
    async def compare_regimes(req: CompareRequest):
        """Side-by-side comparison of all 3 tax regimes."""
        employee = calcular_asalariado(req.ingreso_anual, req.region, req.num_pagas)
        autonomo = calcular_autonomo(
            req.ingreso_anual, req.region, req.gastos_deducibles_pct,
            tarifa_plana=req.tarifa_plana,
        )
        sl = calcular_sl(
            req.ingreso_anual, req.salario_administrador,
            req.gastos_empresa, req.gastos_gestoria,
            req.tipo_empresa, req.region, req.pct_dividendos,
        )

        nets = {
            "employee": employee["salario_neto_mensual"],
            "autonomo": autonomo["neto_mensual"],
            "sl": sl["neto_total_mensual"],
        }
        best = max(nets, key=nets.get)

        return {
            "employee": employee,
            "autonomo": autonomo,
            "sl": sl,
            "best_regime": best,
            "net_monthly": nets,
        }


    @app.post("/api/compare/crossover")
    async def crossover_analysis(req: CrossoverRequest):
        """At what income level does SL beat Autonomo?"""
        points = []
        income = req.income_range_start
        while income <= req.income_range_end:
            emp = calcular_asalariado(income, req.region)
            auto = calcular_autonomo(
                income, req.region, req.gastos_deducibles_pct,
                tarifa_plana=req.tarifa_plana,
            )
            sl_res = calcular_sl(
                income, req.salario_administrador,
                req.gastos_empresa, req.gastos_gestoria,
                req.tipo_empresa, req.region, req.pct_dividendos,
            )
            points.append({
                "income": income,
                "employee_net": emp["salario_neto_mensual"],
                "autonomo_net": auto["neto_mensual"],
                "sl_net": sl_res["neto_total_mensual"],
            })
            income += req.income_step

        crossovers = []
        for i in range(1, len(points)):
            prev, curr = points[i - 1], points[i]
            if (prev["autonomo_net"] >= prev["sl_net"]) != (curr["autonomo_net"] >= curr["sl_net"]):
                crossovers.append({
                    "type": "autonomo_sl",
                    "approximate_income": (prev["income"] + curr["income"]) / 2,
                })

        return {"points": points, "crossovers": crossovers}


    # ============================================================
    # INVESTMENT
    # ============================================================

    @app.post("/api/investment")
    async def calculate_investment(req: InvestmentRequest):
        return simular_inversion(
            req.aportacion_mensual, req.rentabilidad_anual,
            req.anos, req.capital_inicial, req.objetivo_renta_mensual,
        )


    @app.post("/api/investment/compare")
    async def compare_investment(req: CompareInvestmentRequest):
        """Compare investment outcomes across all 3 regimes."""
        emp = calcular_asalariado(req.ingreso_anual, req.region, req.num_pagas)
        auto = calcular_autonomo(
            req.ingreso_anual, req.region, req.gastos_deducibles_pct,
            tarifa_plana=req.tarifa_plana,
        )
        sl_res = calcular_sl(
            req.ingreso_anual, req.salario_administrador,
            req.gastos_empresa, req.gastos_gestoria,
            req.tipo_empresa, req.region, req.pct_dividendos,
        )

        return comparar_escenarios_inversion(
            neto_empleado_mensual=emp["salario_neto_mensual"],
            neto_autonomo_mensual=auto["neto_mensual"],
            neto_sl_mensual=sl_res["neto_total_mensual"],
            gastos_mensuales=req.gastos_mensuales,
            rentabilidad_anual=req.rentabilidad_anual,
            anos=req.anos,
            capital_inicial=req.capital_inicial,
        )


    @app.post("/api/investment/optimizer")
    async def investment_optimizer(req: InvestmentOptimizerRequest):
        return optimizar_inversion_autonomo_vs_sl(
            facturacion_anual=req.facturacion_anual,
            gastos_personales_mensuales=req.gastos_personales_mensuales,
            region=req.region,
            rentabilidad_anual=req.rentabilidad_anual,
            anos=req.anos,
            capital_inicial=req.capital_inicial,
            gastos_deducibles_pct=req.gastos_deducibles_pct,
            tarifa_plana=req.tarifa_plana,
            gastos_empresa=req.gastos_empresa,
            gastos_gestoria=req.gastos_gestoria,
            tipo_empresa=req.tipo_empresa,
            num_salary_steps=req.num_salary_steps,
        )


    @app.post("/api/investment/sensitivity")
    async def sensitivity_analysis(req: SensitivityRequest):
        return generar_sensibilidad(
            req.aportacion_mensual, req.capital_inicial,
            req.rentabilidades, req.horizontes,
        )


    # ============================================================
    # UTILITY
    # ============================================================

    @app.get("/api/regions")
    async def get_regions():
        return {"regions": REGIONES_DISPONIBLES}


    @app.get("/api/presets")
    async def get_presets():
        return {
            "presets": [
                {"label": "Programador", "income": 45_000, "icon": "💻"},
                {"label": "Consultor Senior", "income": 80_000, "icon": "📊"},
                {"label": "Director / C-Level", "income": 120_000, "icon": "🏢"},
                {"label": "Disenador Freelance", "income": 35_000, "icon": "🎨"},
                {"label": "Medico", "income": 55_000, "icon": "🏥"},
                {"label": "Abogado", "income": 65_000, "icon": "⚖️"},
            ]
        }


    @app.post("/api/autonomo/reverse")
    async def reverse_autonomo(
        salario_neto_objetivo: float = 30_000,
        region: str = "Madrid",
        gastos_deducibles_pct: float = 0.10,
        tarifa_plana: bool = False
    ):
        """How much must an autonomo bill to match a given salary?"""
        facturacion = calcular_facturacion_para_salario(
            salario_neto_objetivo, region, gastos_deducibles_pct, tarifa_plana
        )
        return {"salario_neto_objetivo": salario_neto_objetivo, "facturacion_necesaria": facturacion}

else:
    # Backend not available - provide error endpoints
    @app.get("/api/regions")
    async def get_regions_error():
        return JSONResponse(
            status_code=500,
            content={"error": "Backend not available", "details": IMPORT_ERROR}
        )

    @app.get("/api/presets")
    async def get_presets_error():
        return JSONResponse(
            status_code=500,
            content={"error": "Backend not available", "details": IMPORT_ERROR}
        )
