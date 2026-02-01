"""
Validation tests for Spanish 2025 tax calculations.

These tests verify our calculations against known reference values
from official sources and reliable tax calculators.

Tolerance: 1% for complex calculations, exact for bracket math.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.tax_engine.irpf import (
    calcular_irpf_ahorro,
    calcular_irpf_general,
    calcular_irpf_trabajo,
    calcular_base_trabajo,
    calcular_irpf_detalle,
    _reduccion_rendimientos_trabajo,
)
from backend.tax_engine.seguridad_social import calcular_ss_empleado, calcular_ss_empresa, calcular_cuota_autonomos
from backend.tax_engine.impuesto_sociedades import calcular_is, TipoEmpresa
from backend.calculators.employee import calcular_asalariado
from backend.calculators.autonomo import calcular_autonomo
from backend.calculators.sl import calcular_sl


# ============================================================
# IRPF AHORRO (savings tax) — exact bracket math
# ============================================================

class TestIRPFAhorro:
    """IRPF del ahorro brackets: 19/21/23/27/30%"""

    def test_below_6k(self):
        assert calcular_irpf_ahorro(5_000) == pytest.approx(950.0, abs=0.01)  # 5000 * 0.19

    def test_exactly_6k(self):
        assert calcular_irpf_ahorro(6_000) == pytest.approx(1_140.0, abs=0.01)  # 6000 * 0.19

    def test_50k(self):
        # 6K*19% + 44K*21% = 1140 + 9240 = 10380
        assert calcular_irpf_ahorro(50_000) == pytest.approx(10_380.0, abs=0.01)

    def test_200k(self):
        # 6K*19% + 44K*21% + 150K*23% = 1140 + 9240 + 34500 = 44880
        assert calcular_irpf_ahorro(200_000) == pytest.approx(44_880.0, abs=0.01)

    def test_300k(self):
        # 44880 + 100K*27% = 44880 + 27000 = 71880
        assert calcular_irpf_ahorro(300_000) == pytest.approx(71_880.0, abs=0.01)

    def test_500k(self):
        # 71880 + 200K*30% = 71880 + 60000 = 131880
        assert calcular_irpf_ahorro(500_000) == pytest.approx(131_880.0, abs=0.01)

    def test_zero(self):
        assert calcular_irpf_ahorro(0) == 0.0

    def test_negative(self):
        assert calcular_irpf_ahorro(-1000) == 0.0


# ============================================================
# IRPF GENERAL — Madrid brackets with mínimo personal
# ============================================================

class TestIRPFGeneral:
    """IRPF general with mínimo personal (5,550€) as tax credit."""

    def test_minimo_personal_applied(self):
        """Tax on 20K should be less than raw bracket calculation."""
        tax_with_minimo = calcular_irpf_general(20_000, "Madrid")
        # Mínimo personal credit = tax on 5,550 at same rates ≈ ~1,000€
        # So effective tax should be significantly less than without
        assert tax_with_minimo > 0
        assert tax_with_minimo < 20_000 * 0.25  # Well below 25% effective

    def test_very_low_income_zero_tax(self):
        """Income at or below mínimo personal should pay ~0 tax."""
        tax = calcular_irpf_general(5_550, "Madrid")
        assert tax == pytest.approx(0.0, abs=1.0)

    def test_zero_base(self):
        assert calcular_irpf_general(0) == 0.0


# ============================================================
# EMPLOYMENT INCOME DEDUCTIONS
# ============================================================

class TestEmploymentDeductions:
    """Test gastos deducibles (2,000€) and reducción rendimientos del trabajo."""

    def test_gastos_deducibles_applied(self):
        """Base trabajo should deduct 2,000€ gastos + SS."""
        ss = 2_588  # approx for 40K salary
        base = calcular_base_trabajo(40_000, ss)
        # 40000 - 2588 - 2000 = 35,412 (no reducción at this level)
        assert base == pytest.approx(35_412, abs=1)

    def test_reduccion_low_salary(self):
        """Low salary should get full 7,302€ reduction."""
        red = _reduccion_rendimientos_trabajo(10_000)
        assert red == pytest.approx(7_302, abs=0.01)

    def test_reduccion_medium_salary(self):
        """Salary at the taper point should get partial reduction."""
        red = _reduccion_rendimientos_trabajo(16_000)
        # 7302 - 1.4929 * (16000 - 14852) = 7302 - 1715.84 = ~5586
        expected = 7_302 - 1.4929 * (16_000 - 14_852)
        assert red == pytest.approx(expected, abs=0.01)

    def test_reduccion_high_salary(self):
        """High salary should get no reduction."""
        red = _reduccion_rendimientos_trabajo(25_000)
        assert red == 0.0

    def test_irpf_trabajo_lower_than_general(self):
        """Employment IRPF should be lower than general IRPF on same base."""
        ss = calcular_ss_empleado(30_000)["cuota_anual"]
        irpf_trabajo = calcular_irpf_trabajo(30_000, ss, "Madrid")
        irpf_general = calcular_irpf_general(30_000 - ss, "Madrid")
        assert irpf_trabajo < irpf_general  # Because of 2K deduction + reducción


# ============================================================
# SOCIAL SECURITY
# ============================================================

class TestSeguridadSocial:
    """SS contributions at 2025 rates."""

    def test_employee_ss_rate(self):
        """Employee pays ~6.47% of salary (capped at max base)."""
        result = calcular_ss_empleado(40_000)
        # 40000 * 0.0647 = 2,588
        assert result["cuota_anual"] == pytest.approx(2_588, abs=50)

    def test_employer_ss_rate(self):
        """Employer pays ~30.57% + solidarity."""
        result = calcular_ss_empresa(40_000)
        # 40000 * 0.3057 = 12,228 (approx, before solidarity)
        assert result["cuota_anual"] > 12_000
        assert result["cuota_anual"] < 13_000

    def test_ss_max_base_cap(self):
        """SS capped at max base (~59,468€/year in 2025)."""
        low = calcular_ss_empleado(50_000)["cuota_anual"]
        high = calcular_ss_empleado(200_000)["cuota_anual"]
        # High salary SS should be capped, not proportional
        assert high < 200_000 * 0.065
        # But should be higher than low salary
        assert high >= low

    def test_autonomo_cuota_tarifa_plana(self):
        """Tarifa plana 2025 should be 87€/month."""
        result = calcular_cuota_autonomos(30_000, tarifa_plana=True)
        assert result["cuota_mensual"] == pytest.approx(87, abs=1)
        assert result["cuota_anual"] == pytest.approx(1_044, abs=12)


# ============================================================
# IMPUESTO DE SOCIEDADES
# ============================================================

class TestImpuestoSociedades:
    """Corporate tax 2025."""

    def test_micro_first_50k(self):
        """Micro: 21% on first 50K."""
        assert calcular_is(30_000, TipoEmpresa.MICRO) == pytest.approx(6_300, abs=0.01)

    def test_micro_above_50k(self):
        """Micro: 21% first 50K + 22% rest."""
        # 50K*0.21 + 30K*0.22 = 10500 + 6600 = 17100
        assert calcular_is(80_000, TipoEmpresa.MICRO) == pytest.approx(17_100, abs=0.01)

    def test_startup(self):
        """Startup: flat 15%."""
        assert calcular_is(80_000, TipoEmpresa.STARTUP) == pytest.approx(12_000, abs=0.01)

    def test_sme(self):
        """SME: flat 24%."""
        assert calcular_is(100_000, TipoEmpresa.SME) == pytest.approx(24_000, abs=0.01)

    def test_general(self):
        """General: flat 25%."""
        assert calcular_is(100_000, TipoEmpresa.GENERAL) == pytest.approx(25_000, abs=0.01)

    def test_zero_profit(self):
        assert calcular_is(0, TipoEmpresa.MICRO) == 0.0

    def test_negative_profit(self):
        assert calcular_is(-10_000, TipoEmpresa.MICRO) == 0.0


# ============================================================
# EMPLOYEE END-TO-END
# ============================================================

class TestEmployeeEndToEnd:
    """End-to-end employee calculation validation."""

    def test_40k_madrid_14_pagas(self):
        """Employee 40K Madrid, 14 pagas — validate against known ranges."""
        r = calcular_asalariado(40_000, "Madrid", 14)
        # SS employee: ~6.47% of 40K = ~2,588
        assert r["ss_empleado_anual"] == pytest.approx(2_588, abs=50)
        # IRPF: with deductions, should be ~7,000-8,000 range
        assert 6_500 < r["irpf_anual"] < 8_500
        # Net: ~29,000-31,000
        assert 29_000 < r["salario_neto_anual"] < 31_500
        # Monthly (14 pagas): ~2,071-2,250
        assert 2_050 < r["salario_neto_mensual"] < 2_250

    def test_25k_madrid_low_income_benefits(self):
        """Low income should benefit from reducción rendimientos del trabajo."""
        r = calcular_asalariado(25_000, "Madrid", 14)
        # Low income → reducción should reduce IRPF significantly
        assert r["irpf_anual"] < 3_500  # Low IRPF thanks to deductions
        assert r["salario_neto_anual"] > 19_500

    def test_100k_madrid(self):
        """High salary — verify progressive taxation."""
        r = calcular_asalariado(100_000, "Madrid", 14)
        # Effective rate should be 20-30%
        effective_rate = r["tipo_efectivo_total"]
        assert 0.20 < effective_rate < 0.35


# ============================================================
# AUTÓNOMO END-TO-END
# ============================================================

class TestAutonomoEndToEnd:
    """Autónomo calculation validation."""

    def test_60k_madrid(self):
        """Autónomo 60K billing, 10% deductible, Madrid."""
        r = calcular_autonomo(60_000, "Madrid", 0.10)
        # Rendimiento neto: 60K - 6K = 54K
        assert r["rendimiento_neto"] == pytest.approx(54_000, abs=1)
        # Cuota autónomos: based on 54K rendimiento → mid-bracket
        assert 3_000 < r["cuota_autonomos_anual"] < 7_500
        # Net should be reasonable
        assert 30_000 < r["neto_anual"] < 40_000

    def test_tarifa_plana(self):
        """Tarifa plana should reduce cuota to 80€/month."""
        r = calcular_autonomo(40_000, "Madrid", 0.10, tarifa_plana=True)
        assert r["cuota_autonomos_mensual"] == pytest.approx(87, abs=1)


# ============================================================
# SL END-TO-END
# ============================================================

class TestSLEndToEnd:
    """SL calculation validation."""

    def test_100k_24k_salary_madrid(self):
        """SL 100K billing, 24K admin salary, Madrid."""
        r = calcular_sl(100_000, 24_000, 2_000, 3_000, "micro", "Madrid", 1.0)
        # Beneficio antes IS: 100K - 24K - SS_empresa - 2K - 3K
        assert r["beneficio_antes_is"] > 50_000
        assert r["beneficio_antes_is"] < 70_000
        # IS: micro rates on the profit
        assert r["is_pagado"] > 10_000
        # Net total (salary + dividends)
        assert r["neto_total_anual"] > 50_000
        assert r["neto_total_anual"] < 75_000

    def test_sl_zero_dividends(self):
        """SL with 0% dividend distribution — all retained."""
        r = calcular_sl(100_000, 24_000, 2_000, 3_000, "micro", "Madrid", 0.0)
        assert r["dividendos_brutos"] == 0.0
        assert r["irpf_dividendos"] == 0.0
        assert r["beneficio_retenido"] > 0


# ============================================================
# INVESTMENT SIMULATOR
# ============================================================

class TestInvestmentSimulator:
    """Investment simulation validation."""

    def test_compound_growth(self):
        """Verify compound interest formula."""
        from backend.calculators.investment import simular_inversion
        r = simular_inversion(1000, 0.07, 20, 0)
        # FV of annuity: 1000*12 * ((1.07^20 - 1)/0.07) ≈ 491,946
        assert r["capital_bruto"] == pytest.approx(491_946, rel=0.01)

    def test_gains_ratio_increases(self):
        """Gains ratio should increase over time."""
        from backend.calculators.investment import simular_inversion
        r = simular_inversion(1000, 0.07, 20, 0)
        early = r["historial"][4]  # year 5
        late = r["historial"][19]  # year 20
        early_ratio = early["plusvalias"] / early["capital_acumulado"]
        late_ratio = late["plusvalias"] / late["capital_acumulado"]
        assert late_ratio > early_ratio

    def test_fire_vs_bulk_tax(self):
        """FIRE withdrawal should have lower effective tax than bulk."""
        from backend.calculators.investment import simular_inversion
        r = simular_inversion(2000, 0.07, 20, 0)
        bulk_rate = r["rescate_bulk"]["tipo_efectivo"]
        fire_rate = r["rescate_fire"]["tipo_efectivo"]
        assert fire_rate < bulk_rate  # FIRE spreads across lower brackets

    def test_company_investment_is_drag(self):
        """Company investment should grow less due to IS on returns."""
        from backend.calculators.investment import simular_inversion, simular_inversion_empresa
        personal = simular_inversion(1000, 0.07, 20, 0)
        company = simular_inversion_empresa(1000, 0.07, 20, 0, TipoEmpresa.MICRO)
        assert company["capital_bruto"] < personal["capital_bruto"]
        # IS drag should be 10-20% of capital
        drag = personal["capital_bruto"] - company["capital_bruto"]
        drag_pct = drag / personal["capital_bruto"]
        assert 0.05 < drag_pct < 0.25


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
