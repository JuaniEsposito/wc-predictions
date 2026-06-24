import os
import json
import pandas as pd
import pytest

from scripts.validador_calidad import validar_datos


class TestValidarDatos:
    def test_missing_contract_returns_false(self, tmp_path, monkeypatch):
        monkeypatch.setattr("scripts.validador_calidad.WIKI_DIR", str(tmp_path / "wiki"))
        monkeypatch.setattr("scripts.validador_calidad.DATA_DIR", str(tmp_path / "data"))
        os.makedirs(tmp_path / "wiki", exist_ok=True)
        os.makedirs(tmp_path / "data", exist_ok=True)

        result = validar_datos()
        assert result is False

    def test_missing_dataset_returns_true(self, tmp_path, monkeypatch):
        wiki_dir = tmp_path / "wiki"
        data_dir = tmp_path / "data"
        wiki_dir.mkdir()
        data_dir.mkdir()
        monkeypatch.setattr("scripts.validador_calidad.WIKI_DIR", str(wiki_dir))
        monkeypatch.setattr("scripts.validador_calidad.DATA_DIR", str(data_dir))

        contract = {
            "columnas_obligatorias": ["equipo", "oponente", "goles_favor"],
            "xG_max": 5.0,
            "xG_min": 0.0,
            "dias_descanso_max": 60,
            "importancia_partido_max": 2.0,
        }
        (wiki_dir / "data_contract.json").write_text(json.dumps(contract))

        result = validar_datos()
        assert result is True

    def test_valid_dataset_passes(self, tmp_path, monkeypatch):
        wiki_dir = tmp_path / "wiki"
        data_dir = tmp_path / "data"
        wiki_dir.mkdir()
        data_dir.mkdir()
        monkeypatch.setattr("scripts.validador_calidad.WIKI_DIR", str(wiki_dir))
        monkeypatch.setattr("scripts.validador_calidad.DATA_DIR", str(data_dir))

        contract = {
            "columnas_obligatorias": ["equipo", "oponente", "goles_favor"],
            "xG_max": 5.0,
            "xG_min": 0.0,
            "dias_descanso_max": 60,
            "importancia_partido_max": 2.0,
        }
        (wiki_dir / "data_contract.json").write_text(json.dumps(contract))

        df = pd.DataFrame({
            "equipo": ["Argentina", "France"],
            "oponente": ["France", "Argentina"],
            "goles_favor": [4, 2],
            "xg_favor": [2.1, 1.8],
            "dias_descanso": [5, 4],
            "importancia_partido": [1.6, 1.6],
        })
        df.to_csv(data_dir / "dataset_mundial.csv", index=False)

        result = validar_datos()
        assert result is True

    def test_missing_required_columns_fails(self, tmp_path, monkeypatch):
        wiki_dir = tmp_path / "wiki"
        data_dir = tmp_path / "data"
        wiki_dir.mkdir()
        data_dir.mkdir()
        monkeypatch.setattr("scripts.validador_calidad.WIKI_DIR", str(wiki_dir))
        monkeypatch.setattr("scripts.validador_calidad.DATA_DIR", str(data_dir))

        contract = {
            "columnas_obligatorias": ["equipo", "oponente", "goles_favor"],
            "xG_max": 5.0,
            "xG_min": 0.0,
            "dias_descanso_max": 60,
            "importancia_partido_max": 2.0,
        }
        (wiki_dir / "data_contract.json").write_text(json.dumps(contract))

        df = pd.DataFrame({"equipo": ["Argentina"], "other_col": [1]})
        df.to_csv(data_dir / "dataset_mundial.csv", index=False)

        result = validar_datos()
        assert result is False

    def test_xg_out_of_range_fails(self, tmp_path, monkeypatch):
        wiki_dir = tmp_path / "wiki"
        data_dir = tmp_path / "data"
        wiki_dir.mkdir()
        data_dir.mkdir()
        monkeypatch.setattr("scripts.validador_calidad.WIKI_DIR", str(wiki_dir))
        monkeypatch.setattr("scripts.validador_calidad.DATA_DIR", str(data_dir))

        contract = {
            "columnas_obligatorias": ["equipo", "oponente", "goles_favor"],
            "xG_max": 5.0,
            "xG_min": 0.0,
            "dias_descanso_max": 60,
            "importancia_partido_max": 2.0,
        }
        (wiki_dir / "data_contract.json").write_text(json.dumps(contract))

        df = pd.DataFrame({
            "equipo": ["Argentina"],
            "oponente": ["France"],
            "goles_favor": [4],
            "xg_favor": [10.0],  # exceeds xG_max of 5.0
        })
        df.to_csv(data_dir / "dataset_mundial.csv", index=False)

        result = validar_datos()
        assert result is False

    def test_null_critical_column_fails(self, tmp_path, monkeypatch):
        wiki_dir = tmp_path / "wiki"
        data_dir = tmp_path / "data"
        wiki_dir.mkdir()
        data_dir.mkdir()
        monkeypatch.setattr("scripts.validador_calidad.WIKI_DIR", str(wiki_dir))
        monkeypatch.setattr("scripts.validador_calidad.DATA_DIR", str(data_dir))

        contract = {
            "columnas_obligatorias": ["equipo", "oponente", "goles_favor"],
            "xG_max": 5.0,
            "xG_min": 0.0,
            "dias_descanso_max": 60,
            "importancia_partido_max": 2.0,
        }
        (wiki_dir / "data_contract.json").write_text(json.dumps(contract))

        df = pd.DataFrame({
            "equipo": [None, "France"],
            "oponente": ["France", "Argentina"],
            "goles_favor": [4, 2],
        })
        df.to_csv(data_dir / "dataset_mundial.csv", index=False)

        result = validar_datos()
        assert result is False
