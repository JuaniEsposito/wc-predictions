import pandas as pd
import pytest

from src.central_de_datos import (
    calcular_importancia_partido,
    calcular_dias_descanso,
    aplicar_filtros_avanzados,
)


class TestCalcularImportanciaPartido:
    def test_final_2022(self):
        result = calcular_importancia_partido("2022-12-18", "Argentina", "France")
        assert result == 1.6

    def test_semifinal_2022(self):
        result = calcular_importancia_partido("2022-12-13", "Argentina", "Croatia")
        assert result == 1.5

    def test_quarterfinal_2022(self):
        result = calcular_importancia_partido("2022-12-09", "France", "England")
        assert result == 1.4

    def test_round_of_16_2022(self):
        result = calcular_importancia_partido("2022-12-03", "Argentina", "Australia")
        assert result == 1.3

    def test_group_stage_2022(self):
        result = calcular_importancia_partido("2022-11-22", "Argentina", "Saudi Arabia")
        assert result == 1.0

    def test_copa_america_2021(self):
        result = calcular_importancia_partido("2021-07-10", "Argentina", "Brazil")
        assert result == 1.2

    def test_euro_2020(self):
        result = calcular_importancia_partido("2021-07-11", "Italy", "England")
        assert result == 1.2

    def test_generic_match_default(self):
        result = calcular_importancia_partido("2023-09-07", "Uruguay", "Chile")
        assert result == 1.0

    def test_non_finalist_2022(self):
        result = calcular_importancia_partido("2022-12-18", "Brazil", "Serbia")
        assert result == 1.0


class TestCalcularDiasDescanso:
    def test_with_previous_match(self):
        df = pd.DataFrame({
            "equipo": ["Argentina", "Argentina"],
            "fecha": ["2022-12-03", "2022-12-09"],
        })
        result = calcular_dias_descanso(df, "Argentina", "2022-12-13")
        assert result == 4

    def test_no_previous_match_returns_default(self):
        df = pd.DataFrame({"equipo": ["Brazil"], "fecha": ["2022-12-10"]})
        result = calcular_dias_descanso(df, "Argentina", "2022-12-13")
        assert result == 7

    def test_minimum_one_day(self):
        df = pd.DataFrame({
            "equipo": ["Argentina", "Argentina"],
            "fecha": ["2022-12-12", "2022-12-12"],
        })
        result = calcular_dias_descanso(df, "Argentina", "2022-12-12")
        assert result == 7  # No previous matches before the date

    def test_empty_dataframe_returns_default(self):
        df = pd.DataFrame({"equipo": [], "fecha": []})
        result = calcular_dias_descanso(df, "Argentina", "2022-12-13")
        assert result == 7


class TestAplicarFiltrosAvanzados:
    def test_filters_out_zero_score_matches(self):
        df = pd.DataFrame({
            "goles_favor": [2, 0, 1],
            "goles_contra": [0, 0, 1],
            "fecha": ["2023-06-01", "2023-06-02", "2023-06-03"],
        })
        result = aplicar_filtros_avanzados(df)
        assert len(result) == 2

    def test_filters_by_date(self):
        df = pd.DataFrame({
            "goles_favor": [2, 1],
            "goles_contra": [1, 0],
            "fecha": ["2022-06-01", "2023-06-01"],
        })
        result = aplicar_filtros_avanzados(df)
        assert len(result) == 1
        assert result.iloc[0]["fecha"] == "2023-06-01"

    def test_filters_scheduled_estado(self):
        df = pd.DataFrame({
            "goles_favor": [2, 1, 3],
            "goles_contra": [1, 0, 2],
            "fecha": ["2023-06-01", "2023-06-02", "2023-06-03"],
            "estado": ["FINISHED", "SCHEDULED", "FINISHED"],
        })
        result = aplicar_filtros_avanzados(df)
        assert len(result) == 2

    def test_filters_friendly_competencia(self):
        df = pd.DataFrame({
            "goles_favor": [2, 1, 3],
            "goles_contra": [1, 0, 2],
            "fecha": ["2023-06-01", "2023-06-02", "2023-06-03"],
            "competencia": ["WC", "FRIENDLY", "WCQ"],
        })
        result = aplicar_filtros_avanzados(df)
        assert len(result) == 2

    def test_no_columns_for_optional_filters(self):
        df = pd.DataFrame({
            "goles_favor": [2, 1],
            "goles_contra": [1, 1],
            "fecha": ["2023-06-01", "2023-06-02"],
        })
        result = aplicar_filtros_avanzados(df)
        assert len(result) == 2
