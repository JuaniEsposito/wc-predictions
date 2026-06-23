import os
import frontmatter

WIKI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wiki')
INDEX_FILE = os.path.join(WIKI_DIR, 'INDEX.md')

def generar_indice():
    partidos_por_equipo = {}
    
    for root, dirs, files in os.walk(WIKI_DIR):
        for file in files:
            if file.endswith('.md') and file != 'INDEX.md':
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        post = frontmatter.load(f)
                        metadata = post.metadata
                        
                        equipo = metadata.get('equipo', 'Sin equipo')
                        partido = metadata.get('partido', 'Sin nombre')
                        resultado = metadata.get('resultado', 'N/A')
                        oponente = metadata.get('oponente', 'N/A')
                        
                        if equipo not in partidos_por_equipo:
                            partidos_por_equipo[equipo] = []
                        
                        # Calcular ruta relativa desde WIKI_DIR
                        rel_path = os.path.relpath(file_path, WIKI_DIR)
                        
                        partidos_por_equipo[equipo].append({
                            'partido': partido,
                            'resultado': resultado,
                            'oponente': oponente,
                            'ruta': rel_path
                        })
                except Exception as e:
                    print(f"Error leyendo {file_path}: {e}")
    
    # Generar contenido del INDEX.md
    contenido = "# Índice de Partidos\n\n"
    contenido += "Este índice contiene todos los partidos registrados en la wiki.\n\n"
    
    for equipo in sorted(partidos_por_equipo.keys()):
        contenido += f"## {equipo}\n\n"
        contenido += "| Partido | Oponente | Resultado | Enlace |\n"
        contenido += "|---------|----------|-----------|--------|\n"
        
        for p in partidos_por_equipo[equipo]:
            # Convertir ruta relativa a formato de enlace Markdown
            enlace = p['ruta'].replace('\\', '/')
            contenido += f"| {p['partido']} | {p['oponente']} | {p['resultado']} | [{p['partido']}]({enlace}) |\n"
        
        contenido += "\n"
    
    # Escribir el archivo INDEX.md
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print(f"✅ Índice generado exitosamente: {INDEX_FILE}")
    print(f"   Total de equipos: {len(partidos_por_equipo)}")
    total_partidos = sum(len(p) for p in partidos_por_equipo.values())
    print(f"   Total de partidos: {total_partidos}")

if __name__ == "__main__":
    generar_indice()
