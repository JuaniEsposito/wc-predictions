import pytest

from src.analizador import parse_result, calcular_estadisticas


class TestParseResult:
    def test_normal_result(self):
        assert parse_result("2-0") == (2, 0)

    def test_draw(self):
        assert parse_result("1-1") == (1, 1)

    def test_high_score(self):
        assert parse_result("7-0") == (7, 0)

    def test_invalid_format_returns_zeros(self):
        assert parse_result("abc") == (0, 0)

    def test_empty_string_returns_zeros(self):
        assert parse_result("") == (0, 0)

    def test_extra_dashes_returns_zeros(self):
        assert parse_result("1-2-3") == (0, 0)

    def test_non_numeric_parts_returns_zeros(self):
        assert parse_result("a-b") == (0, 0)


class TestCalcularEstadisticas:
    def test_empty_list_returns_none(self):
        assert calcular_estadisticas([]) is None

    def test_single_victory(self):
        resultados = [{"resultado": "2-0"}]
        stats = calcular_estadisticas(resultados)
        assert stats["total_partidos"] == 1
        assert stats["victorias"] == 1
        assert stats["empates"] == 0
        assert stats["derrotas"] == 0
        assert stats["porcentaje_victorias"] == 100.0
        assert stats["promedio_goles_favor"] == 2.0
        assert stats["promedio_goles_contra"] == 0.0

    def test_single_defeat(self):
        resultados = [{"resultado": "0-3"}]
        stats = calcular_estadisticas(resultados)
        assert stats["victorias"] == 0
        assert stats["derrotas"] == 1
        assert stats["porcentaje_victorias"] == 0.0

    def test_single_draw(self):
        resultados = [{"resultado": "1-1"}]
        stats = calcular_estadisticas(resultados)
        assert stats["empates"] == 1
        assert stats["victorias"] == 0
        assert stats["derrotas"] == 0

    def test_multiple_results(self):
        resultados = [
            {"resultado": "2-0"},  # win
            {"resultado": "1-1"},  # draw
            {"resultado": "0-2"},  # loss
            {"resultado": "3-1"},  # win
        ]
        stats = calcular_estadisticas(resultados)
        assert stats["total_partidos"] == 4
        assert stats["victorias"] == 2
        assert stats["empates"] == 1
        assert stats["derrotas"] == 1
        assert stats["porcentaje_victorias"] == 50.0
        assert stats["promedio_goles_favor"] == 1.5
        assert stats["promedio_goles_contra"] == 1.0

    def test_missing_resultado_key_uses_default(self):
        resultados = [{}]
        stats = calcular_estadisticas(resultados)
        assert stats["total_partidos"] == 1
        assert stats["empates"] == 1  # 0-0 is a draw
