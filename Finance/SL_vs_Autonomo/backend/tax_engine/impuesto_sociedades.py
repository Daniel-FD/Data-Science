"""
Impuesto de Sociedades (Corporate Tax) calculator.

2025 rates:
  - Startup (first 2 profitable years): 15%
  - Micro-enterprise (<€1M turnover): 21% on first €50K, 22% on rest
  - SME (€1M-10M turnover): 24%
  - General: 25%
"""

from enum import Enum
from .constants import (
    IS_TIPO_STARTUP,
    IS_MICRO_TRAMO1_RATE,
    IS_MICRO_TRAMO1_LIMIT,
    IS_MICRO_TRAMO2_RATE,
    IS_SME_RATE,
    IS_GENERAL_RATE,
    IS_MICRO_TURNOVER_LIMIT,
    IS_SME_TURNOVER_LIMIT,
)


class TipoEmpresa(str, Enum):
    STARTUP = "startup"
    MICRO = "micro"
    SME = "sme"
    GENERAL = "general"


def determinar_tipo_empresa(turnover: float, years: int) -> TipoEmpresa:
    """Determine company type based on turnover and age."""
    if years <= 2:
        return TipoEmpresa.STARTUP
    elif turnover < IS_MICRO_TURNOVER_LIMIT:
        return TipoEmpresa.MICRO
    elif turnover < IS_SME_TURNOVER_LIMIT:
        return TipoEmpresa.SME
    else:
        return TipoEmpresa.GENERAL


def calcular_is(
    beneficio: float,
    tipo_empresa: TipoEmpresa = TipoEmpresa.MICRO,
) -> float:
    """
    Calculate Impuesto de Sociedades (Corporate Tax).

    Args:
        beneficio: Taxable profit (base imponible)
        tipo_empresa: Company type determining applicable rates
    """
    if beneficio <= 0:
        return 0.0

    if tipo_empresa == TipoEmpresa.STARTUP:
        return beneficio * IS_TIPO_STARTUP

    elif tipo_empresa == TipoEmpresa.MICRO:
        if beneficio <= IS_MICRO_TRAMO1_LIMIT:
            return beneficio * IS_MICRO_TRAMO1_RATE
        else:
            return (
                IS_MICRO_TRAMO1_LIMIT * IS_MICRO_TRAMO1_RATE
                + (beneficio - IS_MICRO_TRAMO1_LIMIT) * IS_MICRO_TRAMO2_RATE
            )

    elif tipo_empresa == TipoEmpresa.SME:
        return beneficio * IS_SME_RATE

    else:  # GENERAL
        return beneficio * IS_GENERAL_RATE


def calcular_is_detalle(
    beneficio: float,
    tipo_empresa: TipoEmpresa = TipoEmpresa.MICRO,
) -> dict:
    """Calculate IS with detailed breakdown."""
    total = calcular_is(beneficio, tipo_empresa)
    effective_rate = total / beneficio if beneficio > 0 else 0.0

    return {
        "total": total,
        "effective_rate": effective_rate,
        "tipo_empresa": tipo_empresa.value,
        "beneficio": beneficio,
        "beneficio_neto": beneficio - total,
    }
