"""Tax engine for Spanish fiscal calculations (2025)."""

from .constants import *
from .irpf import calcular_irpf_general, calcular_irpf_ahorro
from .impuesto_sociedades import calcular_is
from .seguridad_social import (
    calcular_ss_empleado,
    calcular_ss_empresa,
    calcular_cuota_autonomos,
    calcular_cotizacion_solidaridad,
)
from .regional import get_tramos_irpf_region, REGIONES_DISPONIBLES
