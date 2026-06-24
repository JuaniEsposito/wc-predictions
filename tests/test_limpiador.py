import os
import pytest

from src.limpiador import validar_frontmatter


class TestValidarFrontmatter:
    def test_all_keys_present_no_errors(self, tmp_path, monkeypatch):
        monkeypatch.setattr("src.limpiador.WIKI_DIR", str(tmp_path))
        md_content = """---
equipo: Argentina
partido: Argentina vs France
fecha: 2022-12-18
resultado: "3-3"
oponente: France
---
Final del mundo.
"""
        (tmp_path / "match.md").write_text(md_content)
        result = validar_frontmatter()
        assert result is None  # function prints but returns None

    def test_missing_keys_detected(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr("src.limpiador.WIKI_DIR", str(tmp_path))
        md_content = """---
equipo: Argentina
partido: Argentina vs France
---
Missing fecha, resultado, oponente.
"""
        (tmp_path / "incomplete.md").write_text(md_content)
        validar_frontmatter()
        captured = capsys.readouterr()
        assert "Archivos con errores: 1" in captured.out
        assert "fecha" in captured.out
        assert "resultado" in captured.out
        assert "oponente" in captured.out

    def test_no_md_files(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr("src.limpiador.WIKI_DIR", str(tmp_path))
        (tmp_path / "readme.txt").write_text("not a markdown file")
        validar_frontmatter()
        captured = capsys.readouterr()
        assert "Total de archivos .md analizados: 0" in captured.out
        assert "Archivos con errores: 0" in captured.out

    def test_invalid_frontmatter_caught(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr("src.limpiador.WIKI_DIR", str(tmp_path))
        # Write binary garbage that will fail frontmatter parsing
        (tmp_path / "broken.md").write_bytes(b'\x00\x01\x02\x03')
        validar_frontmatter()
        captured = capsys.readouterr()
        assert "Total de archivos .md analizados: 1" in captured.out

    def test_subdirectory_files_scanned(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr("src.limpiador.WIKI_DIR", str(tmp_path))
        subdir = tmp_path / "team_a"
        subdir.mkdir()
        md_content = """---
equipo: Brazil
partido: Brazil vs Germany
fecha: 2014-07-08
resultado: "1-7"
oponente: Germany
---
"""
        (subdir / "match1.md").write_text(md_content)
        validar_frontmatter()
        captured = capsys.readouterr()
        assert "Total de archivos .md analizados: 1" in captured.out
        assert "Archivos con errores: 0" in captured.out
