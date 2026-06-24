import os
import json
import tempfile
import pandas as pd
import pytest

from src.preparar_dataset import parse_result, inyectar_xg


class TestParseResult:
    def test_normal_score(self):
        assert parse_result("3-1") == (3, 1)

    def test_zero_zero(self):
        assert parse_result("0-0") == (0, 0)

    def test_invalid_returns_zeros(self):
        assert parse_result("invalid") == (0, 0)

    def test_non_numeric(self):
        assert parse_result("x-y") == (0, 0)

    def test_high_score(self):
        assert parse_result("7-2") == (7, 2)


class TestInyectarXg:
    def test_injects_xg_from_json(self, tmp_path, monkeypatch):
        monkeypatch.setattr("src.preparar_dataset.DATA_DIR", str(tmp_path))

        xg_data = {
            "Argentina": {"xg_favor": 2.1, "xg_contra": 0.8},
            "France": {"xg_favor": 1.9, "xg_contra": 1.1},
        }
        xg_path = tmp_path / "xg_data.json"
        xg_path.write_text(json.dumps(xg_data))

        df = pd.DataFrame({"equipo": ["Argentina", "France", "Brazil"]})
        result = inyectar_xg(df)

        assert result["xg_favor"].iloc[0] == 2.1
        assert result["xg_contra"].iloc[0] == 0.8
        assert result["xg_favor"].iloc[1] == 1.9
        assert result["xg_contra"].iloc[1] == 1.1
        # Brazil not in xg_data -> defaults to 1.0
        assert result["xg_favor"].iloc[2] == 1.0
        assert result["xg_contra"].iloc[2] == 1.0

    def test_missing_xg_file_uses_defaults(self, tmp_path, monkeypatch):
        monkeypatch.setattr("src.preparar_dataset.DATA_DIR", str(tmp_path))

        df = pd.DataFrame({"equipo": ["Argentina", "France"]})
        result = inyectar_xg(df)

        assert (result["xg_favor"] == 1.0).all()
        assert (result["xg_contra"] == 1.0).all()
