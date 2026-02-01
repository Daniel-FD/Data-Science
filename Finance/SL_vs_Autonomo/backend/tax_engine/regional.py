"""
Regional IRPF tables for all 17 Comunidades Autónomas + Ceuta/Melilla.

Each region defines its AUTONÓMICA portion of IRPF.
Total IRPF = estatal portion + autonómica portion.

Format: list of (upper_limit, rate) tuples.
The rate is the autonómica marginal rate for income up to upper_limit.

Sources: Agencia Tributaria, regional tax agencies (2025 data).
Note: Navarra and País Vasco have foral regimes with their own complete
tax systems. We approximate them using their published rates, but users
should be aware these are simplified approximations.
"""

from typing import List, Tuple, Dict

# Autonómica portion per region
# Format: [(upper_limit, marginal_rate), ...]
TRAMOS_AUTONOMICOS: Dict[str, List[Tuple[float, float]]] = {
    "Andalucía": [
        (12_450, 0.095),
        (20_200, 0.12),
        (28_000, 0.15),
        (35_200, 0.155),
        (50_000, 0.175),
        (60_000, 0.186),
        (120_000, 0.227),
        (float("inf"), 0.245),
    ],
    "Aragón": [
        (12_450, 0.10),
        (20_200, 0.125),
        (34_000, 0.155),
        (50_000, 0.19),
        (60_000, 0.21),
        (70_000, 0.225),
        (90_000, 0.235),
        (150_000, 0.245),
        (float("inf"), 0.25),
    ],
    "Asturias": [
        (12_450, 0.10),
        (17_707, 0.12),
        (33_007, 0.14),
        (53_407, 0.185),
        (70_000, 0.215),
        (90_000, 0.225),
        (175_000, 0.245),
        (float("inf"), 0.255),
    ],
    "Baleares": [
        (10_000, 0.095),
        (18_000, 0.115),
        (30_000, 0.1475),
        (48_000, 0.175),
        (70_000, 0.19),
        (90_000, 0.225),
        (175_000, 0.235),
        (float("inf"), 0.245),
    ],
    "Canarias": [
        (12_450, 0.09),
        (17_707, 0.115),
        (33_007, 0.14),
        (53_407, 0.185),
        (90_000, 0.235),
        (float("inf"), 0.245),
    ],
    "Cantabria": [
        (12_450, 0.095),
        (20_200, 0.12),
        (35_200, 0.15),
        (46_000, 0.175),
        (60_000, 0.195),
        (90_000, 0.22),
        (175_000, 0.245),
        (float("inf"), 0.255),
    ],
    "Castilla-La Mancha": [
        (12_450, 0.095),
        (20_200, 0.12),
        (35_200, 0.15),
        (60_000, 0.185),
        (float("inf"), 0.225),
    ],
    "Castilla y León": [
        (12_450, 0.095),
        (20_200, 0.12),
        (35_200, 0.15),
        (53_407, 0.185),
        (float("inf"), 0.225),
    ],
    "Cataluña": [
        (12_450, 0.105),
        (17_707, 0.12),
        (33_007, 0.155),
        (53_407, 0.185),
        (90_000, 0.215),
        (120_000, 0.235),
        (175_000, 0.24),
        (float("inf"), 0.255),
    ],
    "Extremadura": [
        (12_450, 0.095),
        (20_200, 0.12),
        (24_000, 0.145),
        (35_200, 0.155),
        (60_000, 0.195),
        (80_000, 0.225),
        (100_000, 0.24),
        (120_000, 0.245),
        (float("inf"), 0.25),
    ],
    "Galicia": [
        (12_450, 0.095),
        (20_200, 0.12),
        (35_200, 0.15),
        (60_000, 0.185),
        (float("inf"), 0.225),
    ],
    "Madrid": [
        (12_450, 0.085),
        (17_707, 0.1075),
        (33_007, 0.1275),
        (53_407, 0.1700),
        (float("inf"), 0.2075),
    ],
    "Murcia": [
        (12_450, 0.098),
        (20_200, 0.12),
        (34_000, 0.15),
        (60_000, 0.185),
        (float("inf"), 0.235),
    ],
    "Navarra": [
        # Foral regime — uses its own complete system.
        # These are TOTAL rates (not just autonómica), so we store them
        # differently and handle in get_tramos_irpf_region().
        (4_215, 0.13),
        (8_430, 0.22),
        (16_859, 0.25),
        (27_519, 0.28),
        (42_389, 0.3652),
        (64_170, 0.3952),
        (96_406, 0.4252),
        (180_000, 0.4452),
        (315_000, 0.4702),
        (float("inf"), 0.4902),
    ],
    "País Vasco": [
        # Foral regime (Bizkaia as representative).
        # TOTAL rates, handled specially.
        (17_360, 0.23),
        (32_820, 0.28),
        (48_280, 0.35),
        (68_150, 0.40),
        (99_370, 0.45),
        (174_580, 0.46),
        (float("inf"), 0.49),
    ],
    "La Rioja": [
        (12_450, 0.09),
        (20_200, 0.115),
        (35_200, 0.15),
        (50_000, 0.175),
        (60_000, 0.185),
        (120_000, 0.23),
        (float("inf"), 0.265),
    ],
    "Comunidad Valenciana": [
        (12_450, 0.10),
        (17_707, 0.12),
        (33_007, 0.14),
        (53_407, 0.175),
        (80_000, 0.225),
        (120_000, 0.24),
        (175_000, 0.245),
        (float("inf"), 0.255),
    ],
    "Ceuta": [
        # Uses general state rates with 50% deduction on local income
        (12_450, 0.095),
        (20_200, 0.12),
        (35_200, 0.15),
        (60_000, 0.185),
        (float("inf"), 0.225),
    ],
    "Melilla": [
        # Same as Ceuta
        (12_450, 0.095),
        (20_200, 0.12),
        (35_200, 0.15),
        (60_000, 0.185),
        (float("inf"), 0.225),
    ],
}

# Regions that use foral regime (complete own tax system)
REGIONES_FORALES = {"Navarra", "País Vasco"}

# All available regions
REGIONES_DISPONIBLES = sorted(TRAMOS_AUTONOMICOS.keys())

# Estatal portion (imported at call time to avoid circular imports)
from .constants import TRAMOS_IRPF_ESTATAL


def _calcular_por_tramos(base: float, tramos: List[Tuple[float, float]]) -> float:
    """Calculate tax using progressive brackets."""
    if base <= 0:
        return 0.0
    impuesto = 0.0
    restante = base
    limite_anterior = 0.0
    for limite, tipo in tramos:
        tramo = min(restante, limite - limite_anterior)
        if tramo <= 0:
            break
        impuesto += tramo * tipo
        restante -= tramo
        limite_anterior = limite
    return impuesto


def get_tramos_irpf_region(region: str) -> List[Tuple[float, float]]:
    """
    Get combined IRPF brackets (estatal + autonómica) for a region.

    For foral regimes (Navarra, País Vasco), returns their own complete
    tax table directly (they don't use estatal+autonómica split).

    For common regime regions, combines state and regional brackets into
    a merged progressive table.
    """
    if region not in TRAMOS_AUTONOMICOS:
        raise ValueError(f"Unknown region: {region}. Available: {REGIONES_DISPONIBLES}")

    if region in REGIONES_FORALES:
        # Foral regimes: their table IS the complete IRPF
        return TRAMOS_AUTONOMICOS[region]

    # Common regime: we need to combine estatal + autonómica.
    # Since they have different bracket boundaries, we merge them.
    # Collect all boundary points
    estatal = TRAMOS_IRPF_ESTATAL
    autonomica = TRAMOS_AUTONOMICOS[region]

    # Get all unique boundary points
    boundaries = set()
    for tramos in [estatal, autonomica]:
        prev = 0.0
        for limite, _ in tramos:
            if limite != float("inf"):
                boundaries.add(limite)
            prev = limite
    boundaries = sorted(boundaries)
    boundaries.append(float("inf"))

    # For each segment, find the applicable estatal + autonómica rate
    combined = []
    for boundary in boundaries:
        # Find estatal rate at this boundary (use midpoint)
        test_amount = boundary if boundary != float("inf") else (boundaries[-2] + 1 if len(boundaries) > 1 else 1)
        mid = (0 if not combined else combined[-1][0] if combined[-1][0] != float("inf") else 0) + 0.01

        e_rate = _find_marginal_rate(mid if boundary == boundaries[0] else (combined[-1][0] if combined and combined[-1][0] != float("inf") else 0) + 0.01, estatal)
        a_rate = _find_marginal_rate(mid if boundary == boundaries[0] else (combined[-1][0] if combined and combined[-1][0] != float("inf") else 0) + 0.01, autonomica)

        combined.append((boundary, e_rate + a_rate))

    # Simplify: rebuild properly using boundary segments
    return _build_combined_tramos(estatal, autonomica, boundaries)


def _find_marginal_rate(amount: float, tramos: List[Tuple[float, float]]) -> float:
    """Find the marginal rate applicable at a given amount."""
    prev = 0.0
    for limite, rate in tramos:
        if amount <= limite:
            return rate
        prev = limite
    return tramos[-1][1]


def _build_combined_tramos(
    estatal: List[Tuple[float, float]],
    autonomica: List[Tuple[float, float]],
    boundaries: List[float],
) -> List[Tuple[float, float]]:
    """Build combined brackets from estatal + autonómica using unified boundaries."""
    combined = []
    for boundary in boundaries:
        # Use a point just above the previous boundary to find the rate in this segment
        prev_boundary = combined[-1][0] if combined else 0
        if prev_boundary == float("inf"):
            break
        test_point = prev_boundary + 1.0

        e_rate = _find_marginal_rate(test_point, estatal)
        a_rate = _find_marginal_rate(test_point, autonomica)
        combined.append((boundary, round(e_rate + a_rate, 4)))

    # Deduplicate consecutive identical rates
    deduped = []
    for limit, rate in combined:
        if deduped and deduped[-1][1] == rate and deduped[-1][0] != float("inf"):
            deduped[-1] = (limit, rate)
        else:
            deduped.append((limit, rate))

    return deduped


def calcular_irpf_general_regional(base: float, region: str) -> float:
    """Calculate total IRPF general for a given region."""
    tramos = get_tramos_irpf_region(region)
    return _calcular_por_tramos(base, tramos)
