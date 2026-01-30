"""
Tests for IRPF (Impuesto sobre la Renta de las Personas Físicas) calculations
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.tax_engine.irpf import calcular_irpf_ahorro, calcular_irpf_general


class TestIRPFAhorro:
    """Test IRPF calculation for savings income (ahorro)"""

    def test_zero_income(self):
        """Test that zero income results in zero tax"""
        assert calcular_irpf_ahorro(0) == 0

    def test_negative_income(self):
        """Test that negative income results in zero tax"""
        assert calcular_irpf_ahorro(-1000) == 0

    def test_first_bracket_6000(self):
        """Test income in first bracket (up to 6,000€ at 19%)"""
        # 6,000€ should pay 19%
        expected = 6_000 * 0.19
        assert calcular_irpf_ahorro(6_000) == pytest.approx(expected)

    def test_second_bracket_50000(self):
        """Test income in second bracket (6,000-50,000€ at 21%)"""
        # 50,000€ should pay 6,000*0.19 + 44,000*0.21
        expected = 6_000 * 0.19 + 44_000 * 0.21
        assert calcular_irpf_ahorro(50_000) == pytest.approx(expected)

    def test_third_bracket_200000(self):
        """Test income in third bracket (50,000-200,000€ at 23%)"""
        # 200,000€ calculation
        expected = 6_000 * 0.19 + 44_000 * 0.21 + 150_000 * 0.23
        assert calcular_irpf_ahorro(200_000) == pytest.approx(expected)

    def test_fourth_bracket_300000(self):
        """Test income in fourth bracket (200,000-300,000€ at 27%)"""
        # 300,000€ calculation
        expected = 6_000 * 0.19 + 44_000 * 0.21 + 150_000 * 0.23 + 100_000 * 0.27
        assert calcular_irpf_ahorro(300_000) == pytest.approx(expected)

    def test_fifth_bracket_above_300000(self):
        """Test income in fifth bracket (>300,000€ at 30%)"""
        # 400,000€ calculation
        expected = 6_000 * 0.19 + 44_000 * 0.21 + 150_000 * 0.23 + 100_000 * 0.27 + 100_000 * 0.30
        assert calcular_irpf_ahorro(400_000) == pytest.approx(expected)

    def test_common_dividends_10000(self):
        """Test common scenario: 10,000€ dividends"""
        # 10,000€ should pay 6,000*0.19 + 4,000*0.21
        expected = 6_000 * 0.19 + 4_000 * 0.21
        assert calcular_irpf_ahorro(10_000) == pytest.approx(expected)

    def test_common_dividends_25000(self):
        """Test common scenario: 25,000€ dividends"""
        # 25,000€ should pay 6,000*0.19 + 19,000*0.21
        expected = 6_000 * 0.19 + 19_000 * 0.21
        assert calcular_irpf_ahorro(25_000) == pytest.approx(expected)


class TestIRPFGeneral:
    """Test IRPF calculation for general income (trabajo/actividades económicas)"""

    def test_zero_income(self):
        """Test that zero income results in zero tax"""
        assert calcular_irpf_general(0, "Madrid") == 0

    def test_negative_income(self):
        """Test that negative income results in zero tax"""
        assert calcular_irpf_general(-1000, "Madrid") == 0

    def test_first_bracket_12450(self):
        """Test income in first bracket (up to 12,450€ at 19%)"""
        expected = 12_450 * 0.19
        assert calcular_irpf_general(12_450, "Galicia") == pytest.approx(expected)

    def test_second_bracket_20200(self):
        """Test income in second bracket (12,450-20,200€ at 24%)"""
        expected = 12_450 * 0.19 + 7_750 * 0.24
        assert calcular_irpf_general(20_200, "Galicia") == pytest.approx(expected)

    def test_third_bracket_35200(self):
        """Test income in third bracket (20,200-35,200€ at 30%)"""
        expected = 12_450 * 0.19 + 7_750 * 0.24 + 15_000 * 0.30
        assert calcular_irpf_general(35_200, "Galicia") == pytest.approx(expected)

    def test_fourth_bracket_60000(self):
        """Test income in fourth bracket (35,200-60,000€ at 37%)"""
        expected = 12_450 * 0.19 + 7_750 * 0.24 + 15_000 * 0.30 + 24_800 * 0.37
        assert calcular_irpf_general(60_000, "Madrid") == pytest.approx(expected)

    def test_fifth_bracket_300000(self):
        """Test income in fifth bracket (60,000-300,000€ at 45%)"""
        expected = 12_450 * 0.19 + 7_750 * 0.24 + 15_000 * 0.30 + 24_800 * 0.37 + 240_000 * 0.45
        assert calcular_irpf_general(300_000, "Cataluña") == pytest.approx(expected)

    def test_sixth_bracket_above_300000(self):
        """Test income in sixth bracket (>300,000€ at 47%)"""
        expected = 12_450 * 0.19 + 7_750 * 0.24 + 15_000 * 0.30 + 24_800 * 0.37 + 240_000 * 0.45 + 100_000 * 0.47
        assert calcular_irpf_general(400_000, "Andalucía") == pytest.approx(expected)

    def test_common_salary_30000(self):
        """Test common scenario: 30,000€ salary"""
        expected = 12_450 * 0.19 + 7_750 * 0.24 + 9_800 * 0.30
        assert calcular_irpf_general(30_000, "Madrid") == pytest.approx(expected)

    def test_common_salary_50000(self):
        """Test common scenario: 50,000€ salary"""
        expected = 12_450 * 0.19 + 7_750 * 0.24 + 15_000 * 0.30 + 14_800 * 0.37
        assert calcular_irpf_general(50_000, "Galicia") == pytest.approx(expected)

    def test_all_regions_same_brackets(self):
        """Test that all regions use same brackets (for now)"""
        regions = [
            "Andalucía", "Aragón", "Asturias", "Baleares", "Canarias",
            "Cantabria", "Castilla-La Mancha", "Castilla y León", "Cataluña",
            "Extremadura", "Galicia", "Madrid", "Murcia", "Navarra",
            "País Vasco", "La Rioja", "C. Valenciana"
        ]
        
        test_income = 30_000
        expected = 12_450 * 0.19 + 7_750 * 0.24 + 9_800 * 0.30
        
        for region in regions:
            result = calcular_irpf_general(test_income, region)
            assert result == pytest.approx(expected), f"Region {region} failed"
