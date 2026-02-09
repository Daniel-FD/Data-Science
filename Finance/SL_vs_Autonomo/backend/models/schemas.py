"""
Pydantic schemas for API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


# ============================================================
# REQUEST MODELS
# ============================================================

class EmployeeRequest(BaseModel):
    salario_bruto_anual: float = Field(40_000, ge=0, le=1_000_000)
    region: str = "Madrid"
    num_pagas: int = Field(14, ge=12, le=14)


class AutonomoRequest(BaseModel):
    facturacion_anual: float = Field(60_000, ge=0, le=1_000_000)
    region: str = "Madrid"
    gastos_deducibles_pct: float = Field(0.10, ge=0, le=0.80)
    gastos_deducibles_fijos: float = Field(0, ge=0, le=100_000)
    tarifa_plana: bool = False
    cuota_personalizada: Optional[float] = None


class SLRequest(BaseModel):
    facturacion_anual: float = Field(100_000, ge=0, le=5_000_000)
    salario_administrador: float = Field(18_000, ge=0, le=300_000)
    gastos_empresa: float = Field(2_000, ge=0, le=500_000)
    gastos_gestoria: float = Field(3_000, ge=0, le=50_000)
    tipo_empresa: str = "micro"
    region: str = "Madrid"
    pct_dividendos: float = Field(1.0, ge=0, le=1.0)


class OptimalSalaryRequest(BaseModel):
    facturacion_anual: float = Field(100_000, ge=0, le=5_000_000)
    gastos_empresa: float = Field(2_000, ge=0)
    gastos_gestoria: float = Field(3_000, ge=0)
    tipo_empresa: str = "micro"
    region: str = "Madrid"
    pct_dividendos: float = Field(1.0, ge=0, le=1.0)


class CompareRequest(BaseModel):
    ingreso_anual: float = Field(60_000, ge=0, le=1_000_000, description="Annual income level for comparison")
    region: str = "Madrid"
    # Employee
    num_pagas: int = 14
    # Autónomo
    gastos_deducibles_pct: float = 0.10
    tarifa_plana: bool = False
    # SL
    salario_administrador: float = 18_000
    gastos_empresa: float = 2_000
    gastos_gestoria: float = 3_000
    tipo_empresa: str = "micro"
    pct_dividendos: float = 1.0


class InvestmentRequest(BaseModel):
    aportacion_mensual: float = Field(1_000, ge=0, le=50_000)
    rentabilidad_anual: float = Field(0.07, ge=0, le=0.30)
    anos: int = Field(20, ge=1, le=50)
    capital_inicial: float = Field(0, ge=0, le=10_000_000)
    objetivo_renta_mensual: float = Field(2_000, ge=0)


class CompareInvestmentRequest(BaseModel):
    ingreso_anual: float = Field(60_000, ge=0, le=1_000_000)
    region: str = "Madrid"
    gastos_mensuales: float = Field(1_500, ge=0, le=20_000)
    rentabilidad_anual: float = Field(0.07, ge=0, le=0.30)
    anos: int = Field(20, ge=1, le=50)
    capital_inicial: float = Field(0, ge=0)
    # Autónomo params
    gastos_deducibles_pct: float = 0.10
    tarifa_plana: bool = False
    # SL params
    salario_administrador: float = 18_000
    gastos_empresa: float = 2_000
    gastos_gestoria: float = 3_000
    tipo_empresa: str = "micro"
    pct_dividendos: float = 1.0
    num_pagas: int = 14


class CrossoverRequest(BaseModel):
    region: str = "Madrid"
    gastos_deducibles_pct: float = 0.10
    tarifa_plana: bool = False
    salario_administrador: float = 18_000
    gastos_empresa: float = 2_000
    gastos_gestoria: float = 3_000
    tipo_empresa: str = "micro"
    pct_dividendos: float = 1.0
    income_range_start: float = 20_000
    income_range_end: float = 200_000
    income_step: float = 5_000


class SensitivityRequest(BaseModel):
    aportacion_mensual: float = Field(1_000, ge=0)
    capital_inicial: float = Field(0, ge=0)
    rentabilidades: Optional[List[float]] = None
    horizontes: Optional[List[int]] = None


class InvestmentOptimizerRequest(BaseModel):
    facturacion_anual: float = Field(100_000, ge=10_000, le=2_000_000)
    gastos_personales_mensuales: float = Field(2_000, ge=0, le=20_000)
    region: str = "Madrid"
    rentabilidad_anual: float = Field(0.07, ge=0, le=0.30)
    anos: int = Field(20, ge=1, le=50)
    capital_inicial: float = Field(0, ge=0)
    gastos_deducibles_pct: float = Field(0.10, ge=0, le=1.0)
    tarifa_plana: bool = False
    gastos_empresa: float = Field(2_000, ge=0)
    gastos_gestoria: float = Field(3_000, ge=0)
    tipo_empresa: str = "micro"
    num_salary_steps: int = Field(50, ge=10, le=200)
