"""
Tax constants for Spain 2025.
All monetary values in EUR. Rates as decimals (0.19 = 19%).
"""

# ============================================================
# IRPF DEL AHORRO (savings income: dividends, capital gains)
# Applied nationally (no regional variation)
# ============================================================
TRAMOS_IRPF_AHORRO = [
    (6_000, 0.19),
    (50_000, 0.21),
    (200_000, 0.23),
    (300_000, 0.27),
    (float("inf"), 0.30),  # Updated 2025: was 0.28
]

# ============================================================
# IRPF GENERAL — ESTATAL (state portion, same everywhere)
# ============================================================
TRAMOS_IRPF_ESTATAL = [
    (12_450, 0.095),
    (20_200, 0.12),
    (35_200, 0.15),
    (60_000, 0.185),
    (300_000, 0.225),
    (float("inf"), 0.245),
]

# ============================================================
# IMPUESTO DE SOCIEDADES (Corporate Tax) 2025
# ============================================================
IS_TIPO_STARTUP = 0.15           # First 2 profitable years
IS_MICRO_TRAMO1_RATE = 0.21     # Micro (<1M turnover): first 50K
IS_MICRO_TRAMO1_LIMIT = 50_000
IS_MICRO_TRAMO2_RATE = 0.22     # Micro (<1M turnover): rest
IS_SME_RATE = 0.24              # SME (1M-10M turnover)
IS_GENERAL_RATE = 0.25          # General rate
IS_MICRO_TURNOVER_LIMIT = 1_000_000
IS_SME_TURNOVER_LIMIT = 10_000_000

# ============================================================
# SEGURIDAD SOCIAL — EMPLOYEE (Régimen General)
# ============================================================
# Employee contributions (worker pays)
SS_EMPLEADO_CONTINGENCIAS = 0.0470
SS_EMPLEADO_DESEMPLEO = 0.0155
SS_EMPLEADO_FORMACION = 0.0010
SS_EMPLEADO_MEI = 0.0012
SS_EMPLEADO_TOTAL = (
    SS_EMPLEADO_CONTINGENCIAS
    + SS_EMPLEADO_DESEMPLEO
    + SS_EMPLEADO_FORMACION
    + SS_EMPLEADO_MEI
)  # ~6.47%

# Employer contributions (company pays)
SS_EMPRESA_CONTINGENCIAS = 0.2360
SS_EMPRESA_DESEMPLEO = 0.0550
SS_EMPRESA_FOGASA = 0.0020
SS_EMPRESA_FP = 0.0060
SS_EMPRESA_MEI = 0.0067
SS_EMPRESA_TOTAL = (
    SS_EMPRESA_CONTINGENCIAS
    + SS_EMPRESA_DESEMPLEO
    + SS_EMPRESA_FOGASA
    + SS_EMPRESA_FP
    + SS_EMPRESA_MEI
)  # ~30.57%

# Contribution bases (2025)
SS_BASE_MINIMA_MENSUAL = 1_381.20
SS_BASE_MAXIMA_MENSUAL = 4_909.50
SS_BASE_MINIMA_ANUAL = SS_BASE_MINIMA_MENSUAL * 12
SS_BASE_MAXIMA_ANUAL = SS_BASE_MAXIMA_MENSUAL * 12

# ============================================================
# COTIZACIÓN DE SOLIDARIDAD (Solidarity contribution 2025)
# On salary exceeding the maximum contribution base
# ============================================================
SOLIDARIDAD_TRAMOS = [
    (0.10, 0.0092),   # 0-10% above max: 0.92%
    (0.50, 0.0100),   # 10-50% above max: 1.00%
    (float("inf"), 0.0117),  # >50% above max: 1.17%
]

# ============================================================
# AUTÓNOMOS — CUOTA (2025 income-based system)
# Monthly contribution by monthly net income bracket
# ============================================================
CUOTA_AUTONOMOS_TABLA = [
    (670, 230),
    (900, 260),
    (1_166.70, 290),
    (1_300, 320),
    (1_500, 350),
    (1_700, 370),
    (1_850, 390),
    (2_030, 400),
    (2_330, 410),
    (2_760, 450),
    (3_190, 480),
    (3_620, 510),
    (4_050, 540),
    (6_000, 590),
    (float("inf"), 590),  # Maximum
]

TARIFA_PLANA_MENSUAL = 87.0      # First 12 months for new autónomos
TARIFA_PLANA_MESES = 12
TARIFA_PLANA_REDUCIDA_MENSUAL = 172.0  # Months 13-24 second-year reduced tarifa plana
TARIFA_PLANA_EXTENDIDA_MENSUAL = TARIFA_PLANA_REDUCIDA_MENSUAL  # Backwards-compatible alias
SMI_ANUAL_2025 = 15_876.0        # Salario Mínimo Interprofesional
SMI_MENSUAL = SMI_ANUAL_2025 / 12  # Monthly SMI derived from annual

# ============================================================
# SL FORMATION & ONGOING COSTS (informational)
# ============================================================
SL_CAPITAL_MINIMO = 1.0           # Updated 2025 (was 3,000)
SL_COSTE_CONSTITUCION_TIPICO = 1_500.0
SL_COSTE_GESTORIA_ANUAL_TIPICO = 3_000.0

# ============================================================
# IRPF PERSONAL ALLOWANCES & WORK DEDUCTIONS
# ============================================================
MINIMO_PERSONAL = 5_550.0             # Mínimo del contribuyente (art. 57 LIRPF)
MINIMO_DESCENDIENTE_1 = 2_400.0       # 1st child
MINIMO_DESCENDIENTE_2 = 2_700.0       # 2nd child
MINIMO_DESCENDIENTE_3 = 4_000.0       # 3rd child

GASTOS_DEDUCIBLES_TRABAJADOR = 2_000.0  # "Otros gastos deducibles" for employment income (art. 19.2f LIRPF)

# Reducción por rendimientos del trabajo (art. 20 LIRPF) — 2025
# If rendimiento neto del trabajo <= 14,852 → 7,302 reduction
# If 14,852 < rend_neto <= 17,673.52 → 7,302 - 1.75 * (rend_neto - 14,852)
REDUCCION_TRABAJO_LIMITE_INFERIOR = 14_852.0
REDUCCION_TRABAJO_LIMITE_SUPERIOR = 19_747.5  # 14,852 + 7,302/1.4929 ~= 19,747.5 (punto donde se anula)
REDUCCION_TRABAJO_MAXIMO = 7_302.0
REDUCCION_TRABAJO_PENDIENTE = 1.4929  # slope of taper

# ============================================================
# INVESTMENT DEFAULTS
# ============================================================
REGLA_4_PERCENT = 0.04
RENTABILIDAD_DEFAULT = 0.07
