"""
Tests for autónomo calculations (cuota and tarifa plana)
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.tax_engine.autonomos import calcular_cuota_autonomos
from backend.tax_engine.constants import TARIFA_PLANA_MENSUAL, TARIFA_PLANA_REDUCIDA_MENSUAL, SMI_MENSUAL


class TestCuotaAutonomos:
    """Test autónomo monthly fee (cuota) calculations"""

    def test_tarifa_plana_year_1(self):
        """Test tarifa plana in first year (87€/month)"""
        cuota = calcular_cuota_autonomos(30_000, 1, True)
        expected = TARIFA_PLANA_MENSUAL * 12
        assert cuota == pytest.approx(expected)

    def test_tarifa_plana_year_2_low_income(self):
        """Test tarifa plana in second year with income <= SMI (172€/month)"""
        # Income below SMI
        rendimiento = SMI_MENSUAL * 12 * 0.8  # 80% of SMI
        cuota = calcular_cuota_autonomos(rendimiento, 2, True)
        expected = TARIFA_PLANA_REDUCIDA_MENSUAL * 12
        assert cuota == pytest.approx(expected)

    def test_tarifa_plana_year_2_high_income(self):
        """Test tarifa plana in second year with income > SMI (normal rates apply)"""
        # Income above SMI - should use normal brackets
        rendimiento = 40_000  # ~3,333€/month
        cuota = calcular_cuota_autonomos(rendimiento, 2, True)
        # 3,333€/month falls in bracket (3,190, 3,620) -> 510€/month
        expected = 510 * 12
        assert cuota == pytest.approx(expected)

    def test_tarifa_plana_year_3(self):
        """Test that tarifa plana doesn't apply after year 2"""
        cuota_year3 = calcular_cuota_autonomos(30_000, 3, True)
        cuota_normal = calcular_cuota_autonomos(30_000, 3, False)
        assert cuota_year3 == cuota_normal

    def test_no_tarifa_plana_year_1(self):
        """Test normal rates when tarifa plana not selected"""
        rendimiento = 20_000  # ~1,666€/month
        cuota = calcular_cuota_autonomos(rendimiento, 1, False)
        # 1,666€/month falls in bracket (1,300, 1,700) -> 350€/month
        expected = 350 * 12
        assert cuota == pytest.approx(expected)

    def test_lowest_bracket(self):
        """Test lowest income bracket (<=670€/month = 230€ cuota)"""
        rendimiento = 600 * 12  # 600€/month
        cuota = calcular_cuota_autonomos(rendimiento, 1, False)
        expected = 230 * 12
        assert cuota == pytest.approx(expected)

    def test_bracket_900(self):
        """Test bracket (670, 900) = 260€ cuota"""
        rendimiento = 800 * 12  # 800€/month
        cuota = calcular_cuota_autonomos(rendimiento, 1, False)
        expected = 260 * 12
        assert cuota == pytest.approx(expected)

    def test_bracket_1166(self):
        """Test bracket (900, 1,166) = 290€ cuota"""
        rendimiento = 1_000 * 12  # 1,000€/month
        cuota = calcular_cuota_autonomos(rendimiento, 1, False)
        expected = 290 * 12
        assert cuota == pytest.approx(expected)

    def test_bracket_1300(self):
        """Test bracket (1,166, 1,300) = 320€ cuota"""
        rendimiento = 1_200 * 12  # 1,200€/month
        cuota = calcular_cuota_autonomos(rendimiento, 1, False)
        expected = 320 * 12
        assert cuota == pytest.approx(expected)

    def test_bracket_1700(self):
        """Test bracket (1,300, 1,700) = 350€ cuota"""
        rendimiento = 1_500 * 12  # 1,500€/month
        cuota = calcular_cuota_autonomos(rendimiento, 1, False)
        expected = 350 * 12
        assert cuota == pytest.approx(expected)

    def test_bracket_1850(self):
        """Test bracket (1,700, 1,850) = 380€ cuota"""
        rendimiento = 1_750 * 12  # 1,750€/month
        cuota = calcular_cuota_autonomos(rendimiento, 1, False)
        expected = 380 * 12
        assert cuota == pytest.approx(expected)

    def test_bracket_2030(self):
        """Test bracket (1,850, 2,030) = 400€ cuota"""
        rendimiento = 1_900 * 12  # 1,900€/month
        cuota = calcular_cuota_autonomos(rendimiento, 1, False)
        expected = 400 * 12
        assert cuota == pytest.approx(expected)

    def test_bracket_2330(self):
        """Test bracket (2,030, 2,330) = 420€ cuota"""
        rendimiento = 2_100 * 12  # 2,100€/month
        cuota = calcular_cuota_autonomos(rendimiento, 1, False)
        expected = 420 * 12
        assert cuota == pytest.approx(expected)

    def test_bracket_2760(self):
        """Test bracket (2,330, 2,760) = 450€ cuota"""
        rendimiento = 2_500 * 12  # 2,500€/month
        cuota = calcular_cuota_autonomos(rendimiento, 1, False)
        expected = 450 * 12
        assert cuota == pytest.approx(expected)

    def test_bracket_3190(self):
        """Test bracket (2,760, 3,190) = 480€ cuota"""
        rendimiento = 3_000 * 12  # 3,000€/month
        cuota = calcular_cuota_autonomos(rendimiento, 1, False)
        expected = 480 * 12
        assert cuota == pytest.approx(expected)

    def test_bracket_3620(self):
        """Test bracket (3,190, 3,620) = 510€ cuota"""
        rendimiento = 3_400 * 12  # 3,400€/month
        cuota = calcular_cuota_autonomos(rendimiento, 1, False)
        expected = 510 * 12
        assert cuota == pytest.approx(expected)

    def test_bracket_4050(self):
        """Test bracket (3,620, 4,050) = 540€ cuota"""
        rendimiento = 3_800 * 12  # 3,800€/month
        cuota = calcular_cuota_autonomos(rendimiento, 1, False)
        expected = 540 * 12
        assert cuota == pytest.approx(expected)

    def test_bracket_6000(self):
        """Test bracket (4,050, 6,000) = 590€ cuota"""
        rendimiento = 5_000 * 12  # 5,000€/month
        cuota = calcular_cuota_autonomos(rendimiento, 1, False)
        expected = 590 * 12
        assert cuota == pytest.approx(expected)

    def test_highest_bracket(self):
        """Test highest bracket (>6,000€/month) = 590€ cuota"""
        rendimiento = 100_000  # ~8,333€/month
        cuota = calcular_cuota_autonomos(rendimiento, 1, False)
        expected = 590 * 12
        assert cuota == pytest.approx(expected)

    def test_common_programmer_60k(self):
        """Test common scenario: programmer with 60K income"""
        rendimiento = 60_000  # 5,000€/month
        # Year 1 with tarifa plana
        cuota_tp = calcular_cuota_autonomos(rendimiento, 1, True)
        assert cuota_tp == pytest.approx(TARIFA_PLANA_MENSUAL * 12)
        
        # Year 3 without tarifa plana
        cuota_normal = calcular_cuota_autonomos(rendimiento, 3, False)
        assert cuota_normal == pytest.approx(590 * 12)

    def test_common_designer_35k(self):
        """Test common scenario: designer with 35K income"""
        rendimiento = 35_000  # ~2,916€/month
        # Falls in bracket (2,760, 3,190) = 480€
        cuota = calcular_cuota_autonomos(rendimiento, 1, False)
        assert cuota == pytest.approx(480 * 12)
