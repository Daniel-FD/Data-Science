"""
Tests for Seguridad Social calculations
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.tax_engine.seguridad_social import (
    calcular_ss_empresa,
    calcular_ss_trabajador,
    calcular_solidaridad,
)
from backend.tax_engine.constants import SS_EMPRESA_TIPO, SS_TRABAJADOR_TIPO


class TestSeguridadSocial:
    """Test Social Security calculations"""

    def test_ss_empresa_zero(self):
        """Test employer SS on zero salary"""
        assert calcular_ss_empresa(0) == 0

    def test_ss_trabajador_zero(self):
        """Test employee SS on zero salary"""
        assert calcular_ss_trabajador(0) == 0

    def test_ss_empresa_rate(self):
        """Test employer SS rate (30.57%)"""
        salario = 30_000
        expected = salario * SS_EMPRESA_TIPO
        assert calcular_ss_empresa(salario) == pytest.approx(expected)
        # Should be approximately 9,171€
        assert calcular_ss_empresa(salario) == pytest.approx(9_171, abs=1)

    def test_ss_trabajador_rate(self):
        """Test employee SS rate (6.5%)"""
        salario = 30_000
        expected = salario * SS_TRABAJADOR_TIPO
        assert calcular_ss_trabajador(salario) == pytest.approx(expected)
        # Should be 1,950€
        assert calcular_ss_trabajador(salario) == pytest.approx(1_950)

    def test_ss_total_30k(self):
        """Test total SS for 30K salary"""
        salario = 30_000
        empresa = calcular_ss_empresa(salario)
        trabajador = calcular_ss_trabajador(salario)
        total = empresa + trabajador
        # Total should be ~37.07%
        expected = salario * (SS_EMPRESA_TIPO + SS_TRABAJADOR_TIPO)
        assert total == pytest.approx(expected)

    def test_ss_common_50k(self):
        """Test common scenario: 50K salary"""
        salario = 50_000
        empresa = calcular_ss_empresa(salario)
        trabajador = calcular_ss_trabajador(salario)
        assert empresa == pytest.approx(50_000 * 0.3057)
        assert trabajador == pytest.approx(50_000 * 0.065)


class TestCotizacionSolidaridad:
    """Test solidarity contribution on high salaries"""

    def test_solidarity_zero(self):
        """Test solidarity on zero salary"""
        assert calcular_solidaridad(0) == 0

    def test_solidarity_below_threshold(self):
        """Test solidarity below 4,909.50€/month threshold"""
        # 4,909€/month = 58,908€/year
        salario = 58_000
        assert calcular_solidaridad(salario) == 0

    def test_solidarity_at_threshold(self):
        """Test solidarity exactly at threshold"""
        salario = 4_909.50 * 12
        assert calcular_solidaridad(salario) == 0

    def test_solidarity_first_tier(self):
        """Test solidarity first tier (4,909.50 - 5,410€/month at 0.92%)"""
        # Salary of 5,200€/month (62,400€/year)
        # Base = 5,200 - 4,909.50 = 290.50€/month
        # Contribution = 290.50 * 0.0092 = 2.67€/month = 32.06€/year
        salario = 5_200 * 12
        expected = (5_200 - 4_909.50) * 0.0092 * 12
        assert calcular_solidaridad(salario) == pytest.approx(expected, rel=0.01)

    def test_solidarity_at_first_tier_limit(self):
        """Test solidarity at 5,410€/month boundary"""
        # Base = 5,410 - 4,909.50 = 500.50€/month
        # All in first tier at 0.92%
        salario = 5_410 * 12
        expected = (5_410 - 4_909.50) * 0.0092 * 12
        assert calcular_solidaridad(salario) == pytest.approx(expected, rel=0.01)

    def test_solidarity_second_tier(self):
        """Test solidarity second tier (5,410 - 6,245€/month at 1.00%)"""
        # Salary of 6,000€/month
        # First tier: (5,410 - 4,909.50) = 500.50€ at 0.92%
        # Second tier: (6,000 - 5,410) = 590€ at 1.00%
        salario = 6_000 * 12
        first_tier = (5_410 - 4_909.50) * 0.0092
        second_tier = (6_000 - 5_410) * 0.0100
        expected = (first_tier + second_tier) * 12
        assert calcular_solidaridad(salario) == pytest.approx(expected, rel=0.01)

    def test_solidarity_at_second_tier_limit(self):
        """Test solidarity at 6,245€/month boundary"""
        salario = 6_245 * 12
        first_tier = (5_410 - 4_909.50) * 0.0092
        second_tier = (6_245 - 5_410) * 0.0100
        expected = (first_tier + second_tier) * 12
        assert calcular_solidaridad(salario) == pytest.approx(expected, rel=0.01)

    def test_solidarity_third_tier(self):
        """Test solidarity third tier (>6,245€/month at 1.17%)"""
        # Salary of 8,000€/month (96,000€/year)
        salario = 8_000 * 12
        first_tier = (5_410 - 4_909.50) * 0.0092
        second_tier = (6_245 - 5_410) * 0.0100
        third_tier = (8_000 - 6_245) * 0.0117
        expected = (first_tier + second_tier + third_tier) * 12
        assert calcular_solidaridad(salario) == pytest.approx(expected, rel=0.01)

    def test_solidarity_high_salary(self):
        """Test solidarity on high salary (100K/year)"""
        salario = 100_000
        salario_mensual = salario / 12  # ~8,333€/month
        
        first_tier = (5_410 - 4_909.50) * 0.0092
        second_tier = (6_245 - 5_410) * 0.0100
        third_tier = (salario_mensual - 6_245) * 0.0117
        expected = (first_tier + second_tier + third_tier) * 12
        
        result = calcular_solidaridad(salario)
        assert result == pytest.approx(expected, rel=0.01)
        # Should be around 350-400€/year for 100K salary
        assert 300 < result < 500

    def test_solidarity_very_high_salary(self):
        """Test solidarity on very high salary (200K/year)"""
        salario = 200_000
        salario_mensual = salario / 12  # ~16,667€/month
        
        first_tier = (5_410 - 4_909.50) * 0.0092
        second_tier = (6_245 - 5_410) * 0.0100
        third_tier = (salario_mensual - 6_245) * 0.0117
        expected = (first_tier + second_tier + third_tier) * 12
        
        result = calcular_solidaridad(salario)
        assert result == pytest.approx(expected, rel=0.01)
        # Should be around 1,400-1,700€/year for 200K salary
        assert 1_400 < result < 1_700

    def test_solidarity_common_60k(self):
        """Test common scenario: 60K salary (5K/month)"""
        # 5K/month is in first tier
        salario = 60_000
        salario_mensual = 5_000
        # Base = 5,000 - 4,909.50 = 90.50€/month
        expected = (salario_mensual - 4_909.50) * 0.0092 * 12
        assert calcular_solidaridad(salario) == pytest.approx(expected, rel=0.01)

    def test_solidarity_common_80k(self):
        """Test common scenario: 80K salary (~6,666€/month)"""
        salario = 80_000
        salario_mensual = salario / 12
        
        first_tier = (5_410 - 4_909.50) * 0.0092
        second_tier = (6_245 - 5_410) * 0.0100
        third_tier = (salario_mensual - 6_245) * 0.0117
        expected = (first_tier + second_tier + third_tier) * 12
        
        result = calcular_solidaridad(salario)
        assert result == pytest.approx(expected, rel=0.01)
