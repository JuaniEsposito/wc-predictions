import pandas as pd
import pytest

from scripts.alertas import analizar_fatiga_critica, generar_reporte_completo


class TestAnalizarFatigaCritica:
    def test_specific_team_high_fatigue(self, tmp_path, monkeypatch, capsys):
        df = pd.DataFrame({
            "equipo": ["Argentina", "Argentina"],
            "oponente": ["France", "Croatia"],
            "fecha": ["2022-12-18", "2022-12-13"],
            "dias_descanso": [2, 5],
        })
        csv_path = tmp_path / "dataset_mundial.csv"
        df.to_csv(csv_path, index=False)
        monkeypatch.chdir(tmp_path)

        analizar_fatiga_critica(equipo="Argentina", dias_minimo=3)
        captured = capsys.readouterr()
        assert "ALERTA" in captured.out

    def test_specific_team_sufficient_rest(self, tmp_path, monkeypatch, capsys):
        df = pd.DataFrame({
            "equipo": ["Argentina"],
            "oponente": ["France"],
            "fecha": ["2022-12-18"],
            "dias_descanso": [7],
        })
        csv_path = tmp_path / "dataset_mundial.csv"
        df.to_csv(csv_path, index=False)
        monkeypatch.chdir(tmp_path)

        analizar_fatiga_critica(equipo="Argentina", dias_minimo=3)
        captured = capsys.readouterr()
        assert "descanso suficiente" in captured.out

    def test_team_not_found(self, tmp_path, monkeypatch, capsys):
        df = pd.DataFrame({
            "equipo": ["Argentina"],
            "oponente": ["France"],
            "fecha": ["2022-12-18"],
            "dias_descanso": [5],
        })
        csv_path = tmp_path / "dataset_mundial.csv"
        df.to_csv(csv_path, index=False)
        monkeypatch.chdir(tmp_path)

        analizar_fatiga_critica(equipo="NonExistent", dias_minimo=3)
        captured = capsys.readouterr()
        assert "no encontrado" in captured.out

    def test_all_teams_no_critical(self, tmp_path, monkeypatch, capsys):
        df = pd.DataFrame({
            "equipo": ["Argentina", "France"],
            "oponente": ["France", "Argentina"],
            "fecha": ["2022-12-18", "2022-12-18"],
            "dias_descanso": [5, 6],
        })
        csv_path = tmp_path / "dataset_mundial.csv"
        df.to_csv(csv_path, index=False)
        monkeypatch.chdir(tmp_path)

        analizar_fatiga_critica(equipo=None, dias_minimo=3)
        captured = capsys.readouterr()
        assert "No hay equipos con fatiga" in captured.out

    def test_all_teams_with_critical(self, tmp_path, monkeypatch, capsys):
        df = pd.DataFrame({
            "equipo": ["Argentina", "France"],
            "oponente": ["France", "Argentina"],
            "fecha": ["2022-12-18", "2022-12-18"],
            "dias_descanso": [1, 2],
        })
        csv_path = tmp_path / "dataset_mundial.csv"
        df.to_csv(csv_path, index=False)
        monkeypatch.chdir(tmp_path)

        analizar_fatiga_critica(equipo=None, dias_minimo=3)
        captured = capsys.readouterr()
        assert "FATIGA" in captured.out


class TestGenerarReporteCompleto:
    def test_generates_report(self, tmp_path, monkeypatch, capsys):
        df = pd.DataFrame({
            "equipo": ["Argentina", "France", "Brazil"],
            "oponente": ["France", "Argentina", "Germany"],
            "fecha": ["2022-12-18", "2022-12-18", "2022-12-09"],
            "dias_descanso": [2, 5, 8],
        })
        csv_path = tmp_path / "dataset_mundial.csv"
        df.to_csv(csv_path, index=False)
        monkeypatch.chdir(tmp_path)

        generar_reporte_completo()
        captured = capsys.readouterr()
        assert "REPORTE COMPLETO" in captured.out
        assert "Promedio" in captured.out
        assert "Fatiga alta" in captured.out

    def test_report_stats_correct(self, tmp_path, monkeypatch, capsys):
        df = pd.DataFrame({
            "equipo": ["A", "B", "C"],
            "oponente": ["B", "C", "A"],
            "fecha": ["2022-12-18", "2022-12-18", "2022-12-18"],
            "dias_descanso": [2, 4, 6],
        })
        csv_path = tmp_path / "dataset_mundial.csv"
        df.to_csv(csv_path, index=False)
        monkeypatch.chdir(tmp_path)

        generar_reporte_completo()
        captured = capsys.readouterr()
        assert "4.0" in captured.out  # mean of 2,4,6
        assert "2" in captured.out    # min
        assert "6" in captured.out    # max
