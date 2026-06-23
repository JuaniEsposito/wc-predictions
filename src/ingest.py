import os
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
WIKI_DIR = os.path.join(BASE_DIR, 'wiki')

# Columnas estándar que debe tener el CSV
COLUMNAS_ESTANDAR = ['equipo', 'oponente', 'partido', 'fecha', 'resultado']

def slugify(text):
    """Convierte texto a formato seguro para nombres de archivo"""
    return str(text).lower().replace(" ", "_").replace("/", "-").replace(":", "-")

def sanitize_filename(text):
    """Elimina caracteres inválidos para nombres de archivo"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        text = text.replace(char, '-')
    return text

def create_wiki_file(row, update_existing=True):
    """Crea o actualiza archivo .md en /wiki"""
    # 1. Definir carpeta y nombre
    team_dir = os.path.join(WIKI_DIR, slugify(row['equipo']))
    os.makedirs(team_dir, exist_ok=True)
    
    # Nombre de archivo: {partido}_{fecha}.md
    fecha_str = str(row['fecha']).split('T')[0] if 'T' in str(row['fecha']) else str(row['fecha'])
    file_name = f"{slugify(row['partido'])}_{fecha_str}.md"
    file_name = sanitize_filename(file_name)
    file_path = os.path.join(team_dir, file_name)
    
    # 2. Crear Frontmatter (metadatos)
    frontmatter = (
        "---\n"
        f"equipo: {row['equipo']}\n"
        f"partido: {row['partido']}\n"
        f"fecha: {row['fecha']}\n"
        f"resultado: {row['resultado']}\n"
        f"oponente: {row['oponente']}\n"
    )
    
    # Agregar fuente si existe
    if 'fuente' in row and pd.notna(row['fuente']):
        frontmatter += f"fuente: {row['fuente']}\n"
    
    frontmatter += "---\n\n"
    
    # 3. Contenido Markdown
    content = f"# Partido: {row['partido']}\n\n"
    content += f"**Resultado:** {row['resultado']}\n\n"
    content += f"**Oponente:** {row['oponente']}\n\n"
    content += f"**Fecha:** {row['fecha']}\n\n"
    content += "Detalles del encuentro."
    
    # 4. Verificar si existe y actualizar o crear nuevo
    file_exists = os.path.exists(file_path)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(frontmatter + content)
    
    return file_exists  # Retorna True si actualizó, False si creó

def ingest_csv_files():
    """Lee todos los CSVs en /data y genera archivos .md en /wiki"""
    if not os.path.exists(WIKI_DIR):
        os.makedirs(WIKI_DIR)
    
    archivos_creados = 0
    archivos_actualizados = 0
    archivos_omitidos = 0
    
    for f in os.listdir(DATA_DIR):
        file_path = os.path.join(DATA_DIR, f)
        
        # Solo procesar archivos CSV
        if not f.endswith('.csv'):
            continue
        
        # Ignorar archivos que no son de datos (encoders, modelos, etc.)
        if f.endswith('.pkl') or f.startswith('le_') or f.startswith('modelo_'):
            continue
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            
            # Verificar que tenga las columnas estándar
            columnas_csv = list(df.columns)
            if not all(col in columnas_csv for col in COLUMNAS_ESTANDAR):
                print(f"⚠️  Omitiendo {f}: no tiene columnas estándar")
                print(f"   Esperadas: {COLUMNAS_ESTANDAR}")
                print(f"   Encontradas: {columnas_csv}")
                archivos_omitidos += 1
                continue
            
            print(f"📄 Procesando {f}: {len(df)} registros")
            
            for _, row in df.iterrows():
                try:
                    fue_actualizado = create_wiki_file(row)
                    if fue_actualizado:
                        archivos_actualizados += 1
                        print(f"   🔄 Actualizado: {row['equipo']}/{slugify(row['partido'])}_{str(row['fecha']).split('T')[0]}.md")
                    else:
                        archivos_creados += 1
                        print(f"   ✅ Creado: {row['equipo']}/{slugify(row['partido'])}_{str(row['fecha']).split('T')[0]}.md")
                except Exception as e:
                    print(f"   ❌ Error procesando fila: {e}")
                    
        except Exception as e:
            print(f"❌ Error leyendo {f}: {e}")
            archivos_omitidos += 1
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE INGESTA")
    print("=" * 50)
    print(f"Archivos creados: {archivos_creados}")
    print(f"Archivos actualizados: {archivos_actualizados}")
    print(f"Archivos omitidos: {archivos_omitidos}")
    print(f"Total procesados: {archivos_creados + archivos_actualizados}")

if __name__ == "__main__":
    ingest_csv_files()
    