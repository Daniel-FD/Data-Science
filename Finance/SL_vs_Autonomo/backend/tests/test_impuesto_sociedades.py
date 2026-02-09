"""
Tests for Impuesto de Sociedades calculations
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.tax_engine.impuesto_sociedades import calcular_is, TipoEmpresa, determinar_tipo_empresa


class TestImpuestoSociedades:
    """Test IS (Corporate Tax) calculations"""

    def test_zero_beneficio(self):
        """Test that zero profit results in zero tax"""
        assert calcular_is(0, TipoEmpresa.MICRO) == 0

    def test_negative_beneficio(self):
        """Test that negative profit results in zero tax"""
        assert calcular_is(-10_000, TipoEmpresa.MICRO) == 0

    def test_startup_first_year(self):
        """Test startup rate (15%) for first profitable year"""
        beneficio = 50_000
        expected = beneficio * 0.15
        assert calcular_is(beneficio, TipoEmpresa.STARTUP) == pytest.approx(expected)

    def test_startup_second_year(self):
        """Test startup rate (15%) for second profitable year"""
        beneficio = 75_000
        expected = beneficio * 0.15
        assert calcular_is(beneficio, TipoEmpresa.STARTUP) == pytest.approx(expected)

    def test_startup_third_year_reverts(self):
        """Test that startup rate doesn't apply after 2 years"""
        # After 2 years, should use micro/SME/general rates
        beneficio = 60_000
        # Micro: first 50K at 21%, rest at 22%
        expected = 50_000 * 0.21 + 10_000 * 0.22
        # Using determinar_tipo_empresa for year 3 with <1M turnover gives MICRO
        tipo = determinar_tipo_empresa(500_000, 3)
        assert tipo == TipoEmpresa.MICRO
        assert calcular_is(beneficio, tipo) == pytest.approx(expected)

    def test_micro_under_50k(self):
        """Test micro company (<1M turnover) with profit under 50K"""
        beneficio = 30_000
        expected = 30_000 * 0.21
        assert calcular_is(beneficio, TipoEmpresa.MICRO) == pytest.approx(expected)

    def test_micro_at_50k(self):
        """Test micro company exactly at 50K profit"""
        beneficio = 50_000
        expected = 50_000 * 0.21
        assert calcular_is(beneficio, TipoEmpresa.MICRO) == pytest.approx(expected)

    def test_micro_above_50k(self):
        """Test micro company with profit above 50K"""
        beneficio = 80_000
        # First 50K at 21%, remaining 30K at 22%
        expected = 50_000 * 0.21 + 30_000 * 0.22
        assert calcular_is(beneficio, TipoEmpresa.MICRO) == pytest.approx(expected)

    def test_sme_low_turnover(self):
        """Test SME (1M-10M turnover) at 24%"""
        beneficio = 100_000
        expected = beneficio * 0.24
        assert calcular_is(beneficio, TipoEmpresa.SME) == pytest.approx(expected)

    def test_sme_mid_turnover(self):
        """Test SME (5M turnover) at 24%"""
        beneficio = 200_000
        expected = beneficio * 0.24
        assert calcular_is(beneficio, TipoEmpresa.SME) == pytest.approx(expected)

    def test_sme_high_turnover(self):
        """Test SME (9.9M turnover) at 24%"""
        beneficio = 150_000
        expected = beneficio * 0.24
        assert calcular_is(beneficio, TipoEmpresa.SME) == pytest.approx(expected)

    def test_general_low(self):
        """Test general rate (25%) for 10M+ turnover"""
        beneficio = 300_000
        expected = beneficio * 0.25
        assert calcular_is(beneficio, TipoEmpresa.GENERAL) == pytest.approx(expected)

    def test_general_high(self):
        """Test general rate (25%) for large company"""
        beneficio = 1_000_000
        expected = beneficio * 0.25
        assert calcular_is(beneficio, TipoEmpresa.GENERAL) == pytest.approx(expected)

    def test_common_freelancer_60k(self):
        """Test common scenario: freelancer with 60K profit, 100K turnover"""
        beneficio = 60_000
        # Micro: 50K at 21%, 10K at 22%
        expected = 50_000 * 0.21 + 10_000 * 0.22
        assert calcular_is(beneficio, TipoEmpresa.MICRO) == pytest.approx(expected)

    def test_common_consultant_120k(self):
        """Test common scenario: consultant with 120K profit, 180K turnover"""
        beneficio = 120_000
        # Micro: 50K at 21%, 70K at 22%
        expected = 50_000 * 0.21 + 70_000 * 0.22
        assert calcular_is(beneficio, TipoEmpresa.MICRO) == pytest.approx(expected)

    def test_determinar_tipo_empresa_startup(self):
        """Test that companies <= 2 years old are classified as startups"""
        assert determinar_tipo_empresa(500_000, 1) == TipoEmpresa.STARTUP
        assert determinar_tipo_empresa(500_000, 2) == TipoEmpresa.STARTUP

    def test_determinar_tipo_empresa_micro(self):
        """Test micro company classification (<1M turnover, >2 years)"""
        assert determinar_tipo_empresa(999_999, 3) == TipoEmpresa.MICRO
        assert determinar_tipo_empresa(500_000, 5) == TipoEmpresa.MICRO

    def test_determinar_tipo_empresa_sme(self):
        """Test SME classification (1M-10M turnover, >2 years)"""
        assert determinar_tipo_empresa(1_000_000, 3) == TipoEmpresa.SME
        assert determinar_tipo_empresa(5_000_000, 5) == TipoEmpresa.SME
        assert determinar_tipo_empresa(9_999_999, 10) == TipoEmpresa.SME

    def test_determinar_tipo_empresa_general(self):
        """Test general classification (>=10M turnover, >2 years)"""
        assert determinar_tipo_empresa(10_000_000, 3) == TipoEmpresa.GENERAL
        assert determinar_tipo_empresa(50_000_000, 10) == TipoEmpresa.GENERAL

    def test_edge_micro_to_sme(self):
        """Test edge case at 1M turnover boundary"""
        beneficio = 100_000
        # Just under 1M = micro rates
        tipo_micro = determinar_tipo_empresa(999_999, 3)
        result_micro = calcular_is(beneficio, tipo_micro)
        expected_micro = 50_000 * 0.21 + 50_000 * 0.22
        assert result_micro == pytest.approx(expected_micro)

        # At 1M = SME rates
        tipo_sme = determinar_tipo_empresa(1_000_000, 3)
        result_sme = calcular_is(beneficio, tipo_sme)
        expected_sme = 100_000 * 0.24
        assert result_sme == pytest.approx(expected_sme)

    def test_edge_sme_to_general(self):
        """Test edge case at 10M turnover boundary"""
        beneficio = 500_000
        # Just under 10M = SME rates
        tipo_sme = determinar_tipo_empresa(9_999_999, 3)
        result_sme = calcular_is(beneficio, tipo_sme)
        expected_sme = 500_000 * 0.24
        assert result_sme == pytest.approx(expected_sme)

        # At 10M = general rates
        tipo_general = determinar_tipo_empresa(10_000_000, 3)
        result_general = calcular_is(beneficio, tipo_general)
        expected_general = 500_000 * 0.25
        assert result_general == pytest.approx(expected_general)
