import os
import pandas as pd
import pytest

from src.analizador_deriva import analizar_deriva


class TestAnalizarDeriva:
    def test_no_dataset_returns_true(self, tmp_path):
        result = analizar_deriva(str(tmp_path / "nonexistent.csv"))
        assert result is True

    def test_missing_columns_returns_true(self, tmp_path):
        csv_path = tmp_path / "dataset.csv"
        df = pd.DataFrame({"equipo": ["Argentina"], "goles_favor": [2]})
        df.to_csv(csv_path, index=False)

        result = analizar_deriva(str(csv_path))
        assert result is True

    def test_stable_data_returns_true(self, tmp_path):
        csv_path = tmp_path / "dataset.csv"
        df = pd.DataFrame({
            "xg_favor": [1.2, 1.3, 1.1, 1.2, 1.4, 1.2, 1.3, 1.1],
            "fecha": [
                "2023-01-01", "2023-02-01", "2023-03-01", "2023-04-01",
                "2023-05-01", "2023-06-01", "2023-06-15", "2023-06-20",
            ],
        })
        df.to_csv(csv_path, index=False)

        result = analizar_deriva(str(csv_path))
        assert result is True

    def test_high_drift_returns_false(self, tmp_path):
        csv_path = tmp_path / "dataset.csv"
        # Historical data averages ~1.0, recent data jumps to ~3.0
        df = pd.DataFrame({
            "xg_favor": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 3.0, 3.0, 3.0, 3.0],
            "fecha": [
                "2023-01-01", "2023-02-01", "2023-03-01", "2023-04-01",
                "2023-05-01", "2023-06-01", "2023-06-25", "2023-06-26",
                "2023-06-27", "2023-06-28",
            ],
        })
        df.to_csv(csv_path, index=False)

        result = analizar_deriva(str(csv_path))
        assert result is False

    def test_empty_after_date_filter_returns_true(self, tmp_path):
        csv_path = tmp_path / "dataset.csv"
        df = pd.DataFrame({
            "xg_favor": [1.0],
            "fecha": ["invalid-date"],
        })
        df.to_csv(csv_path, index=False)

        result = analizar_deriva(str(csv_path))
        assert result is True
