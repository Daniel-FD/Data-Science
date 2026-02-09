"""
Vercel Serverless Function Adapter
===================================
Wraps the FastAPI backend for Vercel's Python serverless runtime.
"""

import sys
from pathlib import Path

# Add backend to Python path so imports work
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# Import from backend package
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

# Create FastAPI app
app = FastAPI(
    title="Simulador Fiscal Espana",
    description="API for Spanish tax regime comparison",
    version="2.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROOT
# ============================================================

@app.get("/api")
async def api_root():
    return {
        "name": "Simulador Fiscal Espana",
        "version": "2.0.0",
        "status": "ok",
    }


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


# Vercel handler
handler = Mangum(app, lifespan="off")
