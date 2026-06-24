import subprocess
import sys

def ejecutar_pipeline():
    print("🌍 Iniciando Ingesta y Predicción en Tiempo Real...\n")
    
    # Lista de scripts en orden de dependencia
    # 1. Traer datos reales (API + Scraping)
    # 2. Limpiar y unificar (Ingesta)
    # 3. Preparar Dataset (Cálculo de métricas/xG)
    # 4. Entrenar y Predecir
    
    tareas = [
        ("Validando integridad de datos", "scripts/validador_calidad.py"),
        ("Obteniendo datos reales (API/Scraper)", "src/central_de_datos.py"),
        ("Limpiando y unificando datos", "src/ingest.py"),
        ("Calculando métricas y Dataset", "src/preparar_dataset.py"),
        ("Analizando deriva de datos", "src/analizador_deriva.py"),
        ("Entrenando modelo de predicción", "src/entrenar_modelo.py")
    ]
    
    for descripcion, script in tareas:
        print(f"--- {descripcion} ---")
        result = subprocess.run([sys.executable, script])
        if result.returncode != 0:
            print(f"❌ Error crítico en: {script}. Abortando.")
            return
        print(f"✅ {script} finalizado.\n")

    print("🏁 Pipeline completo. ¡Ya puedes consultar la predicción para el próximo partido!")

if __name__ == "__main__":
    ejecutar_pipeline()