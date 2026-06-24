import subprocess
import sys

from src.exceptions import PipelineStepError


def ejecutar_pipeline():
    print("Iniciando Ingesta y Prediccion en Tiempo Real...\n")

    tareas = [
        ("Validando integridad de datos", "scripts/validador_calidad.py"),
        ("Obteniendo datos reales (API/Scraper)", "src/central_de_datos.py"),
        ("Limpiando y unificando datos", "src/ingest.py"),
        ("Calculando metricas y Dataset", "src/preparar_dataset.py"),
        ("Analizando deriva de datos", "src/analizador_deriva.py"),
        ("Entrenando modelo de prediccion", "src/entrenar_modelo.py")
    ]

    for descripcion, script in tareas:
        print(f"--- {descripcion} ---")
        if script.startswith("src/") and script.endswith(".py"):
            module = script[:-3].replace("/", ".")
            cmd = [sys.executable, "-m", module]
        else:
            cmd = [sys.executable, script]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            raise PipelineStepError(
                step_name=script,
                cause=RuntimeError(stderr or f"Exit code {result.returncode}"),
            )
        if result.stdout:
            print(result.stdout, end="")
        print(f"{script} finalizado.\n")

    print("Pipeline completo.")


if __name__ == "__main__":
    ejecutar_pipeline()
