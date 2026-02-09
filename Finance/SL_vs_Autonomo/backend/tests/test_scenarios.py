"""
Integration tests for complete scenarios
Tests realistic end-to-end calculations for common professional profiles
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.scenarios.models import SimulationRequest
from backend.scenarios.autonomo import simulate_autonomo
from backend.scenarios.sl_retencion import simulate_sl_retencion
from backend.scenarios.sl_dividendos import simulate_sl_dividendos
from backend.scenarios.sl_mixto import optimize_salary


class TestCommonScenarios:
    """Test complete scenarios for common professional profiles"""

    def test_programmer_60k_madrid(self):
        """Test: Programmer with 60K income in Madrid"""
        req = SimulationRequest(
            facturacion=60_000,
            gastos_deducibles=2_000,
            gastos_personales=18_000,
            años=5,
            rentabilidad=0.06,
            capital_inicial=0,
            region="Madrid",
            tarifa_plana=True,
            salario_administrador=18_000,
            gastos_gestoria=3_000,
            aportacion_plan_pensiones=2_000,
            turnover=60_000,
            company_age=1,
            is_startup=True,
        )

        # Run all scenarios
        autonomo = simulate_autonomo(req)
        sl_retencion = simulate_sl_retencion(req)
        sl_dividendos = simulate_sl_dividendos(req)
        sl_mixto, optimal_salary, curve = optimize_salary(req)

        # Basic sanity checks
        assert autonomo.renta_mensual_neta > 0
        assert sl_retencion.renta_mensual_neta > 0
        assert sl_dividendos.renta_mensual_neta > 0
        assert sl_mixto.renta_mensual_neta > 0

        # SL retention should typically have highest monthly net due to compound growth
        assert sl_retencion.renta_mensual_neta > autonomo.renta_mensual_neta

        # All scenarios should have reasonable tax burden (<80% total including all costs)
        for scenario in [autonomo, sl_retencion, sl_dividendos, sl_mixto]:
            total_tax = sum(scenario.tax_breakdown.values()) + scenario.impuestos_rescate
            total_income = req.facturacion * req.años
            tax_rate = total_tax / total_income if total_income > 0 else 0
            assert 0 < tax_rate < 0.8, f"Tax rate {tax_rate:.2%} seems unreasonable"

        # Optimal salary should be within reasonable range
        assert 0 <= optimal_salary <= req.facturacion

        # Curve should have multiple points
        assert len(curve) > 10

        # Year-by-year historial should match años
        assert len(autonomo.historial) == req.años

    def test_consultant_120k_barcelona(self):
        """Test: Consultant with 120K income in Cataluña"""
        req = SimulationRequest(
            facturacion=120_000,
            gastos_deducibles=4_000,
            gastos_personales=24_000,
            años=10,
            rentabilidad=0.07,
            capital_inicial=10_000,
            region="Cataluña",
            tarifa_plana=False,  # Beyond tarifa plana eligibility
            salario_administrador=30_000,
            gastos_gestoria=4_000,
            aportacion_plan_pensiones=5_000,
            turnover=120_000,
            company_age=3,
            is_startup=False,
        )

        autonomo = simulate_autonomo(req)
        sl_retencion = simulate_sl_retencion(req)
        sl_dividendos = simulate_sl_dividendos(req)
        sl_mixto, optimal_salary, curve = optimize_salary(req)

        # With compound growth, final capital should be substantial
        assert autonomo.capital_bruto > 100_000
        assert sl_retencion.capital_bruto > 100_000

        # Monthly net should be reasonable for 120K income
        assert autonomo.renta_mensual_neta > 1_000
        assert sl_retencion.renta_mensual_neta > 1_000

        # Capital should grow over time
        assert autonomo.historial[-1].capital_acumulado > autonomo.historial[0].capital_acumulado

        # Tax breakdown should include all expected components
        assert "irpf" in autonomo.tax_breakdown or "cuota_autonomos" in autonomo.tax_breakdown
        assert "is" in sl_retencion.tax_breakdown
        assert "ss" in sl_retencion.tax_breakdown

    def test_designer_45k_galicia(self):
        """Test: Designer with 45K income in Galicia"""
        req = SimulationRequest(
            facturacion=45_000,
            gastos_deducibles=1_500,
            gastos_personales=15_000,
            años=7,
            rentabilidad=0.05,
            capital_inicial=5_000,
            region="Galicia",
            tarifa_plana=True,
            salario_administrador=15_000,
            gastos_gestoria=2_500,
            aportacion_plan_pensiones=1_500,
            turnover=45_000,
            company_age=1,
            is_startup=True,
        )

        autonomo = simulate_autonomo(req)
        sl_retencion = simulate_sl_retencion(req)
        sl_dividendos = simulate_sl_dividendos(req)
        sl_mixto, optimal_salary, curve = optimize_salary(req)

        # For lower income, autónomo might be competitive
        scenarios = {
            "autonomo": autonomo,
            "sl_retencion": sl_retencion,
            "sl_dividendos": sl_dividendos,
            "sl_mixto": sl_mixto,
        }

        # All should provide some monthly net income
        for name, scenario in scenarios.items():
            assert scenario.renta_mensual_neta >= 0, f"{name} has negative monthly net"

        # Net capital should be positive (after taxes on gains)
        for name, scenario in scenarios.items():
            assert scenario.capital_neto > 0, f"{name} has non-positive net capital"

    def test_freelancer_80k_madrid_comparison(self):
        """Test: Compare all 4 scenarios for 80K freelancer in Madrid"""
        req = SimulationRequest(
            facturacion=80_000,
            gastos_deducibles=3_000,
            gastos_personales=20_000,
            años=10,
            rentabilidad=0.06,
            capital_inicial=0,
            region="Madrid",
            tarifa_plana=True,
            salario_administrador=20_000,
            gastos_gestoria=3_500,
            aportacion_plan_pensiones=4_000,
            turnover=80_000,
            company_age=1,
            is_startup=True,
        )

        autonomo = simulate_autonomo(req)
        sl_retencion = simulate_sl_retencion(req)
        sl_dividendos = simulate_sl_dividendos(req)
        sl_mixto, optimal_salary, curve = optimize_salary(req)

        # SL Mixto should be at least as good as the other SL scenarios
        # (since it's the optimized version)
        assert sl_mixto.renta_mensual_neta >= sl_dividendos.renta_mensual_neta * 0.95  # Allow 5% tolerance
        assert sl_mixto.renta_mensual_neta >= sl_retencion.renta_mensual_neta * 0.70  # Retention might be better due to compound growth

        # All scenarios should have completed all years
        assert len(autonomo.historial) == 10
        assert len(sl_retencion.historial) == 10
        assert len(sl_dividendos.historial) == 10
        assert len(sl_mixto.historial) == 10

        # Optimal salary should be reasonable
        assert 15_000 <= optimal_salary <= 80_000

    def test_high_income_150k_all_regions(self):
        """Test: High income scenario across different regions"""
        base_req = SimulationRequest(
            facturacion=150_000,
            gastos_deducibles=5_000,
            gastos_personales=30_000,
            años=5,
            rentabilidad=0.06,
            capital_inicial=20_000,
            region="Madrid",  # Will be changed
            tarifa_plana=False,
            salario_administrador=40_000,
            gastos_gestoria=5_000,
            aportacion_plan_pensiones=6_000,
            turnover=150_000,
            company_age=5,
            is_startup=False,
        )

        regions_to_test = ["Madrid", "Cataluña", "Andalucía", "Galicia", "C. Valenciana"]

        results = {}
        for region in regions_to_test:
            req = base_req.model_copy()
            req.region = region
            autonomo = simulate_autonomo(req)
            results[region] = autonomo.renta_mensual_neta

        # Since all regions currently use the same brackets, results should be identical
        # This test will catch when we add regional variation
        unique_results = set(results.values())
        # For now, all should be the same
        # When regional tables are added, this assertion will need updating
        assert len(unique_results) == 1, "Expected same results for all regions (currently using national tables)"

    def test_edge_case_minimal_income(self):
        """Test: Edge case with minimal income"""
        req = SimulationRequest(
            facturacion=15_000,
            gastos_deducibles=500,
            gastos_personales=8_000,
            años=3,
            rentabilidad=0.04,
            capital_inicial=0,
            region="Madrid",
            tarifa_plana=True,
            salario_administrador=15_000,
            gastos_gestoria=1_500,
            aportacion_plan_pensiones=0,
            turnover=15_000,
            company_age=1,
            is_startup=True,
        )

        autonomo = simulate_autonomo(req)
        sl_dividendos = simulate_sl_dividendos(req)

        # Even with low income, should not have negative results
        assert autonomo.renta_mensual_neta >= 0
        assert sl_dividendos.renta_mensual_neta >= 0
        assert autonomo.capital_neto >= 0
        assert sl_dividendos.capital_neto >= 0

    def test_long_horizon_30_years(self):
        """Test: Long investment horizon (30 years)"""
        req = SimulationRequest(
            facturacion=70_000,
            gastos_deducibles=2_500,
            gastos_personales=18_000,
            años=30,
            rentabilidad=0.07,
            capital_inicial=10_000,
            region="Madrid",
            tarifa_plana=False,
            salario_administrador=25_000,
            gastos_gestoria=3_000,
            aportacion_plan_pensiones=3_500,
            turnover=70_000,
            company_age=10,
            is_startup=False,
        )

        autonomo = simulate_autonomo(req)
        sl_retencion = simulate_sl_retencion(req)

        # With 30 years and 7% return, compound growth should be significant
        assert autonomo.capital_bruto > 500_000
        assert sl_retencion.capital_bruto > 500_000

        # Monthly retirement income should be substantial
        assert autonomo.renta_mensual_neta > 1_000
        assert sl_retencion.renta_mensual_neta > 1_000

        # Historial should have 30 entries
        assert len(autonomo.historial) == 30
        assert len(sl_retencion.historial) == 30

        # Capital should grow monotonically (each year > previous)
        for i in range(1, 30):
            assert autonomo.historial[i].capital_acumulado > autonomo.historial[i-1].capital_acumulado
