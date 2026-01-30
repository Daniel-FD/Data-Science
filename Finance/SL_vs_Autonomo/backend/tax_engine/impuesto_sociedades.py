from __future__ import annotations


def calcular_is(beneficio: float, turnover: float, profitable_years: int, is_startup: bool) -> float:
    if beneficio <= 0:
        return 0.0

    if is_startup and profitable_years <= 2:
        return beneficio * 0.15

    if turnover < 1_000_000:
        tramo1 = min(beneficio, 50_000)
        tramo2 = max(0.0, beneficio - 50_000)
        return tramo1 * 0.21 + tramo2 * 0.22

    if turnover < 10_000_000:
        return beneficio * 0.24

    return beneficio * 0.25
