import os
import pytest

from src.index_generator import generar_indice


class TestGenerarIndice:
    def test_generates_index_from_md_files(self, tmp_path, monkeypatch):
        wiki_dir = tmp_path / "wiki"
        wiki_dir.mkdir()
        monkeypatch.setattr("src.index_generator.WIKI_DIR", str(wiki_dir))
        monkeypatch.setattr("src.index_generator.INDEX_FILE", str(wiki_dir / "INDEX.md"))

        md_content = """---
equipo: Argentina
partido: Argentina vs France
resultado: "3-3"
oponente: France
---
"""
        (wiki_dir / "arg_fra.md").write_text(md_content)
        generar_indice()

        index_path = wiki_dir / "INDEX.md"
        assert index_path.exists()
        content = index_path.read_text()
        assert "Argentina" in content
        assert "France" in content
        assert "arg_fra.md" in content

    def test_empty_wiki_generates_empty_index(self, tmp_path, monkeypatch):
        wiki_dir = tmp_path / "wiki"
        wiki_dir.mkdir()
        monkeypatch.setattr("src.index_generator.WIKI_DIR", str(wiki_dir))
        monkeypatch.setattr("src.index_generator.INDEX_FILE", str(wiki_dir / "INDEX.md"))

        generar_indice()

        index_path = wiki_dir / "INDEX.md"
        assert index_path.exists()
        content = index_path.read_text()
        assert "Índice de Partidos" in content

    def test_multiple_teams_sorted(self, tmp_path, monkeypatch):
        wiki_dir = tmp_path / "wiki"
        wiki_dir.mkdir()
        monkeypatch.setattr("src.index_generator.WIKI_DIR", str(wiki_dir))
        monkeypatch.setattr("src.index_generator.INDEX_FILE", str(wiki_dir / "INDEX.md"))

        for team, oponent in [("Zaire", "Brazil"), ("Argentina", "France")]:
            md = f"""---
equipo: {team}
partido: {team} vs {oponent}
resultado: "1-0"
oponente: {oponent}
---
"""
            (wiki_dir / f"{team.lower()}.md").write_text(md)

        generar_indice()
        content = (wiki_dir / "INDEX.md").read_text()
        # Argentina should come before Zaire (sorted)
        assert content.index("Argentina") < content.index("Zaire")

    def test_skips_index_md(self, tmp_path, monkeypatch):
        wiki_dir = tmp_path / "wiki"
        wiki_dir.mkdir()
        monkeypatch.setattr("src.index_generator.WIKI_DIR", str(wiki_dir))
        monkeypatch.setattr("src.index_generator.INDEX_FILE", str(wiki_dir / "INDEX.md"))

        # Create an INDEX.md - should be skipped during scan
        (wiki_dir / "INDEX.md").write_text("old index")
        md_content = """---
equipo: Brazil
partido: Brazil vs Germany
resultado: "1-7"
oponente: Germany
---
"""
        (wiki_dir / "match.md").write_text(md_content)

        generar_indice()
        content = (wiki_dir / "INDEX.md").read_text()
        assert "Brazil" in content
        assert "old index" not in content

    def test_handles_subdirectories(self, tmp_path, monkeypatch):
        wiki_dir = tmp_path / "wiki"
        wiki_dir.mkdir()
        subdir = wiki_dir / "group_a"
        subdir.mkdir()
        monkeypatch.setattr("src.index_generator.WIKI_DIR", str(wiki_dir))
        monkeypatch.setattr("src.index_generator.INDEX_FILE", str(wiki_dir / "INDEX.md"))

        md_content = """---
equipo: Spain
partido: Spain vs Morocco
resultado: "0-0"
oponente: Morocco
---
"""
        (subdir / "spa_mor.md").write_text(md_content)

        generar_indice()
        content = (wiki_dir / "INDEX.md").read_text()
        assert "Spain" in content
        assert "group_a" in content  # relative path should include subdir
