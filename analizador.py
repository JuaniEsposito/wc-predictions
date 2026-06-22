import os
import frontmatter # Requiere: pip install python-frontmatter

# Ruta a tu carpeta de wiki
WIKI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wiki')

def parse_result(resultado):
    """Parsea el resultado (ej: '2-0') y retorna goles a favor y en contra"""
    try:
        parts = resultado.split('-')
        if len(parts) == 2:
            return int(parts[0]), int(parts[1])
    except:
        pass
    return 0, 0

def calcular_estadisticas(resultados):
    """Calcula métricas estadísticas de los partidos"""
    total_partidos = len(resultados)
    if total_partidos == 0:
        return None
    
    victorias = 0
    empates = 0
    derrotas = 0
    total_goles_favor = 0
    total_goles_contra = 0
    
    for r in resultados:
        resultado = r.get('resultado', '0-0')
        goles_favor, goles_contra = parse_result(resultado)
        
        total_goles_favor += goles_favor
        total_goles_contra += goles_contra
        
        if goles_favor > goles_contra:
            victorias += 1
        elif goles_favor == goles_contra:
            empates += 1
        else:
            derrotas += 1
    
    porcentaje_victorias = (victorias / total_partidos) * 100
    promedio_goles_favor = total_goles_favor / total_partidos
    promedio_goles_contra = total_goles_contra / total_partidos
    
    return {
        'total_partidos': total_partidos,
        'victorias': victorias,
        'empates': empates,
        'derrotas': derrotas,
        'porcentaje_victorias': porcentaje_victorias,
        'promedio_goles_favor': promedio_goles_favor,
        'promedio_goles_contra': promedio_goles_contra
    }

def analizar_wiki():
    resultados = []
    
    # Recorrer todos los archivos en la carpeta wiki y subcarpetas
    for root, dirs, files in os.walk(WIKI_DIR):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                
                # Leer el archivo con frontmatter
                with open(file_path, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                    resultados.append(post.metadata)

    # Mostrar reporte simple
    print(f"{'EQUIPO':<15} | {'PARTIDO':<15} | {'RESULTADO':<10}")
    print("-" * 45)
    for r in resultados:
        print(f"{r.get('equipo', 'N/A'):<15} | {r.get('partido', 'N/A'):<15} | {r.get('resultado', 'N/A'):<10}")
    
    # Calcular y mostrar estadísticas
    print("\n" + "=" * 45)
    print("RESUMEN ESTADÍSTICO")
    print("=" * 45)
    
    estadisticas = calcular_estadisticas(resultados)
    if estadisticas:
        print(f"Total de partidos: {estadisticas['total_partidos']}")
        print(f"Victorias: {estadisticas['victorias']} ({estadisticas['porcentaje_victorias']:.1f}%)")
        print(f"Empates: {estadisticas['empates']}")
        print(f"Derrotas: {estadisticas['derrotas']}")
        print(f"Promedio goles a favor: {estadisticas['promedio_goles_favor']:.2f}")
        print(f"Promedio goles en contra: {estadisticas['promedio_goles_contra']:.2f}")
    else:
        print("No hay datos suficientes para calcular estadísticas.")

if __name__ == "__main__":
    analizar_wiki()