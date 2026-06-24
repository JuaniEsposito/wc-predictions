import os
import tempfile
import pandas as pd
import pytest

from src.ingest import slugify, sanitize_filename, create_wiki_file


class TestSlugify:
    def test_basic_text(self):
        assert slugify("Argentina") == "argentina"

    def test_spaces_replaced(self):
        assert slugify("Costa Rica") == "costa_rica"

    def test_slashes_replaced(self):
        assert slugify("Group A/B") == "group_a-b"

    def test_colons_replaced(self):
        assert slugify("Match: Final") == "match-_final"

    def test_numeric_input(self):
        assert slugify(123) == "123"

    def test_empty_string(self):
        assert slugify("") == ""


class TestSanitizeFilename:
    def test_removes_invalid_chars(self):
        result = sanitize_filename('file<name>:test"path\\more|chars?star*')
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert '"' not in result
        assert "\\" not in result
        assert "|" not in result
        assert "?" not in result
        assert "*" not in result

    def test_valid_filename_unchanged(self):
        assert sanitize_filename("valid_filename.md") == "valid_filename.md"

    def test_all_invalid_chars_become_dash(self):
        result = sanitize_filename('<>:"/\\|?*')
        assert result == "-" * 9


class TestCreateWikiFile:
    def test_creates_new_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr("src.ingest.WIKI_DIR", str(tmp_path))

        row = {
            "equipo": "Argentina",
            "oponente": "France",
            "partido": "Final",
            "fecha": "2022-12-18",
            "resultado": "4-2",
        }
        result = create_wiki_file(row)
        assert result is False  # False means created (not updated)

        team_dir = tmp_path / "argentina"
        assert team_dir.exists()
        files = list(team_dir.iterdir())
        assert len(files) == 1

        content = files[0].read_text(encoding="utf-8")
        assert "equipo: Argentina" in content
        assert "resultado: 4-2" in content
        assert "# Partido: Final" in content

    def test_updates_existing_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr("src.ingest.WIKI_DIR", str(tmp_path))

        row = {
            "equipo": "Argentina",
            "oponente": "France",
            "partido": "Final",
            "fecha": "2022-12-18",
            "resultado": "4-2",
        }
        create_wiki_file(row)
        result = create_wiki_file(row)
        assert result is True  # True means updated

    def test_handles_datetime_with_T(self, tmp_path, monkeypatch):
        monkeypatch.setattr("src.ingest.WIKI_DIR", str(tmp_path))

        row = {
            "equipo": "Brazil",
            "oponente": "Serbia",
            "partido": "Group G",
            "fecha": "2022-11-24T19:00:00Z",
            "resultado": "2-0",
        }
        result = create_wiki_file(row)
        assert result is False

        team_dir = tmp_path / "brazil"
        files = list(team_dir.iterdir())
        assert len(files) == 1
        assert "2022-11-24" in files[0].name

    def test_includes_fuente_when_present(self, tmp_path, monkeypatch):
        monkeypatch.setattr("src.ingest.WIKI_DIR", str(tmp_path))

        row = {
            "equipo": "Spain",
            "oponente": "Germany",
            "partido": "Group E",
            "fecha": "2022-11-27",
            "resultado": "1-1",
            "fuente": "api",
        }
        create_wiki_file(row)

        team_dir = tmp_path / "spain"
        files = list(team_dir.iterdir())
        content = files[0].read_text(encoding="utf-8")
        assert "fuente: api" in content
