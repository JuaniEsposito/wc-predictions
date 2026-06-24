import os
import frontmatter
import random
from src.exceptions import DataValidationError

WIKI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wiki')

def generar_xg_realista(goles_favor, goles_contra):
    # Genera un xG basado en los goles reales, con un margen de aleatoriedad
    xg_f = max(0.5, goles_favor + random.uniform(-0.5, 0.5))
    xg_c = max(0.5, goles_contra + random.uniform(-0.5, 0.5))
    return round(xg_f, 2), round(xg_c, 2)

def actualizar_wiki():
    for root, dirs, files in os.walk(WIKI_DIR):
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                
                # Solo agregamos si no existen ya
                if 'xg_favor' not in post.metadata:
                    resultado = post.metadata.get('resultado', '0-0')
                    parts = resultado.split('-')
                    if len(parts) != 2:
                        raise DataValidationError(
                            f"Formato de resultado inválido en {file}: '{resultado}'"
                        )
                    try:
                        g_f, g_c = int(parts[0]), int(parts[1])
                    except ValueError as e:
                        raise DataValidationError(
                            f"Goles no numéricos en {file}: '{resultado}'"
                        ) from e
                    xg_f, xg_c = generar_xg_realista(g_f, g_c)
                    
                    post.metadata['xg_favor'] = xg_f
                    post.metadata['xg_contra'] = xg_c
                    
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(frontmatter.dumps(post))
                    print(f"Actualizado: {file} con xG {xg_f}-{xg_c}")

if __name__ == "__main__":
    actualizar_wiki()
