from __future__ import annotations

from typing import List, Tuple

# 2025 - IRPF Ahorro (actualizado)
TRAMOS_AHORRO_2025: List[Tuple[float, float]] = [
    (6_000, 0.19),
    (50_000, 0.21),
    (200_000, 0.23),
    (300_000, 0.27),
    (float("inf"), 0.30),
]

# 2025 - IRPF General nacional base (aproximado)
TRAMOS_IRPF_GENERAL_NACIONAL: List[Tuple[float, float]] = [
    (12_450, 0.19),
    (20_200, 0.24),
    (35_200, 0.30),
    (60_000, 0.37),
    (300_000, 0.45),
    (float("inf"), 0.47),
]

# SMI 2025 (aproximado)
SMI_ANUAL = 15_876
SMI_MENSUAL = SMI_ANUAL / 12

# Tarifa plana autónomos
TARIFA_PLANA_MENSUAL = 87
TARIFA_PLANA_REDUCIDA_MENSUAL = 172

# Seguridad Social
SS_EMPRESA_TIPO = 0.3057
SS_TRABAJADOR_TIPO = 0.065

# Cotización de solidaridad (sobre salarios elevados, mensual)
# Tramos aproximados. Ajustar a normativa vigente.
SOLIDARITY_TIERS_MENSUAL: List[Tuple[float, float]] = [
    (5_410, 0.0092),
    (6_245, 0.0100),
    (float("inf"), 0.0117),
]
