import os
import frontmatter

WIKI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wiki')

LLAVES_OBLIGATORIAS = ['equipo', 'partido', 'fecha', 'resultado', 'oponente']

def validar_frontmatter():
    archivos_con_errores = []
    total_archivos = 0
    
    for root, dirs, files in os.walk(WIKI_DIR):
        for file in files:
            if file.endswith('.md'):
                total_archivos += 1
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        post = frontmatter.load(f)
                        metadata = post.metadata
                        
                        llaves_faltantes = []
                        for llave in LLAVES_OBLIGATORIAS:
                            if llave not in metadata:
                                llaves_faltantes.append(llave)
                        
                        if llaves_faltantes:
                            archivos_con_errores.append({
                                'archivo': file_path,
                                'llaves_faltantes': llaves_faltantes
                            })
                except Exception as e:
                    archivos_con_errores.append({
                        'archivo': file_path,
                        'error': str(e)
                    })
    
    print(f"Total de archivos .md analizados: {total_archivos}")
    print(f"Archivos con errores: {len(archivos_con_errores)}")
    
    if archivos_con_errores:
        print("\n⚠️  ARCHIVOS CON ERRORES:")
        print("-" * 60)
        for error in archivos_con_errores:
            if 'llaves_faltantes' in error:
                print(f"Archivo: {error['archivo']}")
                print(f"  Llaves faltantes: {', '.join(error['llaves_faltantes'])}")
            else:
                print(f"Archivo: {error['archivo']}")
                print(f"  Error: {error['error']}")
            print("-" * 60)
    else:
        print("\n✅ Todos los archivos tienen el frontmatter correcto.")

if __name__ == "__main__":
    validar_frontmatter()
