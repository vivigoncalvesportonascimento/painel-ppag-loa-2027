"""Carregamento de dados geográficos usados na página Regionalização.

As bases de planejamento (localizadores, ações) já são carregadas por
etl.limpeza_inicial.
"""

import json
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def carregar_geojson_municipios() -> dict:
    with open(ASSETS_DIR / "mg_municipios.geojson", encoding="utf-8") as f:
        return json.load(f)
