"""Shared utilities for the wc-predictions pipeline.

Centralizes path constants, API configuration, standard column definitions,
and common helper functions used across multiple modules.
"""

import os
import json
from dotenv import load_dotenv
from src.exceptions import DataValidationError

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
WIKI_DIR = os.path.join(BASE_DIR, 'wiki')

# ---------------------------------------------------------------------------
# API configuration
# ---------------------------------------------------------------------------
load_dotenv()
API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
HEADERS = {"X-Auth-Token": API_KEY}

# ---------------------------------------------------------------------------
# Standard column/field definitions
# ---------------------------------------------------------------------------
COLUMNAS_ESTANDAR = ['equipo', 'oponente', 'partido', 'fecha', 'resultado']

FEATURE_COLS = [
    'xg_favor', 'xg_contra', 'xg_diferencia', 'xg_ratio', 'xg_total',
    'importancia_partido', 'dias_descanso', 'equipo_encoded', 'oponente_encoded'
]

FILTROS_INGESTA = {
    "excluir_estado": ["SCHEDULED", "TIMED"],
    "incluir_competencias": ["WC", "WCQ", "NATIONS_LEAGUE"],
    "ventana_minima_fecha": "2023-01-01",
    "excluir_amistosos_sin_verified": True
}

LLAVES_OBLIGATORIAS_FRONTMATTER = ['equipo', 'partido', 'fecha', 'resultado', 'oponente']

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def parse_result(resultado):
    """Parse a match result string (e.g. '2-0') into (goals_for, goals_against).

    Raises DataValidationError if the format is invalid.
    """
    try:
        parts = resultado.split('-')
        if len(parts) != 2:
            raise ValueError(f"Formato inesperado: '{resultado}'")
        return int(parts[0]), int(parts[1])
    except (ValueError, AttributeError) as e:
        raise DataValidationError(
            f"No se pudo parsear resultado '{resultado}': {e}"
        ) from e


def slugify(text):
    """Convert text to a filename-safe slug."""
    return str(text).lower().replace(" ", "_").replace("/", "-").replace(":", "-")


def sanitize_filename(text):
    """Remove characters invalid in filenames."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        text = text.replace(char, '-')
    return text


# ---------------------------------------------------------------------------
# xG data helpers
# ---------------------------------------------------------------------------

def load_xg_data():
    """Load the xG database from data/xg_data.json. Returns empty dict on error."""
    xg_path = os.path.join(DATA_DIR, 'xg_data.json')
    try:
        with open(xg_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def get_team_xg(team, xg_db=None, default_favor=1.2, default_contra=0.9):
    """Get xG values for a team from the xG database."""
    if xg_db is None:
        xg_db = load_xg_data()
    entry = xg_db.get(team, {})
    return entry.get('xg_favor', default_favor), entry.get('xg_contra', default_contra)


def compute_xg_features(xg_favor, xg_contra):
    """Compute derived xG features: diferencia, ratio, total."""
    xg_diferencia = xg_favor - xg_contra
    xg_ratio = xg_favor / (xg_contra + 0.01)
    xg_total = xg_favor + xg_contra
    return xg_diferencia, xg_ratio, xg_total


# ---------------------------------------------------------------------------
# I/O utilities
# ---------------------------------------------------------------------------

def save_dataframe_to_csv(df, filename, subdir=None):
    """Save a DataFrame to CSV in DATA_DIR (or a subdir of it)."""
    target_dir = os.path.join(DATA_DIR, subdir) if subdir else DATA_DIR
    os.makedirs(target_dir, exist_ok=True)
    path = os.path.join(target_dir, filename)
    df.to_csv(path, index=False)
    return path


def iter_wiki_files(wiki_dir=None):
    """Yield (file_path, filename) for all .md files in the wiki directory."""
    target = wiki_dir or WIKI_DIR
    for root, _dirs, files in os.walk(target):
        for file in files:
            if file.endswith('.md') and file != 'INDEX.md':
                yield os.path.join(root, file), file
