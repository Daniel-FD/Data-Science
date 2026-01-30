from __future__ import annotations

from .constants import SMI_MENSUAL, TARIFA_PLANA_MENSUAL, TARIFA_PLANA_REDUCIDA_MENSUAL

# Tramos simplificados por rendimiento mensual
CUOTAS_MENSUALES = [
    (670, 230),
    (900, 260),
    (1_166, 290),
    (1_300, 320),
    (1_700, 350),
    (1_850, 380),
    (2_030, 400),
    (2_330, 420),
    (2_760, 450),
    (3_190, 480),
    (3_620, 510),
    (4_050, 540),
    (6_000, 590),
    (float("inf"), 590),
]


def calcular_cuota_autonomos(
    rendimiento_anual: float,
    year: int,
    tarifa_plana: bool,
) -> float:
    rendimiento_mensual = rendimiento_anual / 12

    if tarifa_plana and year == 1:
        return TARIFA_PLANA_MENSUAL * 12

    if tarifa_plana and year == 2 and rendimiento_mensual <= SMI_MENSUAL:
        return TARIFA_PLANA_REDUCIDA_MENSUAL * 12

    for limite, cuota in CUOTAS_MENSUALES:
        if rendimiento_mensual <= limite:
            return cuota * 12

    return CUOTAS_MENSUALES[-1][1] * 12
