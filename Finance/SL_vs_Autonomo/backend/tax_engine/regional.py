from __future__ import annotations

from typing import Dict, List, Tuple

from .constants import TRAMOS_IRPF_GENERAL_NACIONAL

# Tablas autonómicas 2025 (aproximadas). Para forales, se usa aproximación.
REGIONAL_TABLES: Dict[str, List[Tuple[float, float]]] = {
    "Andalucía": TRAMOS_IRPF_GENERAL_NACIONAL,
    "Aragón": TRAMOS_IRPF_GENERAL_NACIONAL,
    "Asturias": TRAMOS_IRPF_GENERAL_NACIONAL,
    "Baleares": TRAMOS_IRPF_GENERAL_NACIONAL,
    "Canarias": TRAMOS_IRPF_GENERAL_NACIONAL,
    "Cantabria": TRAMOS_IRPF_GENERAL_NACIONAL,
    "Castilla-La Mancha": TRAMOS_IRPF_GENERAL_NACIONAL,
    "Castilla y León": TRAMOS_IRPF_GENERAL_NACIONAL,
    "Cataluña": TRAMOS_IRPF_GENERAL_NACIONAL,
    "Extremadura": TRAMOS_IRPF_GENERAL_NACIONAL,
    "Galicia": TRAMOS_IRPF_GENERAL_NACIONAL,
    "Madrid": TRAMOS_IRPF_GENERAL_NACIONAL,
    "Murcia": TRAMOS_IRPF_GENERAL_NACIONAL,
    "Navarra": TRAMOS_IRPF_GENERAL_NACIONAL,  # Foral (aprox.)
    "País Vasco": TRAMOS_IRPF_GENERAL_NACIONAL,  # Foral (aprox.)
    "La Rioja": TRAMOS_IRPF_GENERAL_NACIONAL,
    "C. Valenciana": TRAMOS_IRPF_GENERAL_NACIONAL,
}


def get_regional_brackets(region: str) -> List[Tuple[float, float]]:
    return REGIONAL_TABLES.get(region, TRAMOS_IRPF_GENERAL_NACIONAL)


def list_regions() -> List[str]:
    return sorted(REGIONAL_TABLES.keys())
