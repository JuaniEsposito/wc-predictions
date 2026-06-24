import random
import pytest

from src.agregar_xg_automatico import generar_xg_realista


class TestGenerarXgRealista:
    def test_returns_two_floats(self):
        xg_f, xg_c = generar_xg_realista(2, 1)
        assert isinstance(xg_f, float)
        assert isinstance(xg_c, float)

    def test_minimum_value_is_half(self):
        # Even with 0 goals and negative random offset, min should be 0.5
        random.seed(42)
        for _ in range(100):
            xg_f, xg_c = generar_xg_realista(0, 0)
            assert xg_f >= 0.5
            assert xg_c >= 0.5

    def test_values_close_to_goals(self):
        random.seed(0)
        xg_f, xg_c = generar_xg_realista(3, 1)
        # Should be within +/-0.5 of the actual goals (or at minimum 0.5)
        assert 0.5 <= xg_f <= 3.5
        assert 0.5 <= xg_c <= 1.5

    def test_rounded_to_two_decimals(self):
        random.seed(7)
        xg_f, xg_c = generar_xg_realista(2, 2)
        assert xg_f == round(xg_f, 2)
        assert xg_c == round(xg_c, 2)

    def test_high_goals(self):
        random.seed(99)
        xg_f, xg_c = generar_xg_realista(7, 5)
        assert xg_f >= 0.5
        assert xg_c >= 0.5
        assert xg_f <= 7.5
        assert xg_c <= 5.5
