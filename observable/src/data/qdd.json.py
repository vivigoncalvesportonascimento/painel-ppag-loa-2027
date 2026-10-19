"""Data loader da página QDD (Quadro de Detalhamento da Despesa): base
fato + 6 dimensões já cruzadas, em nível de linha, para os 8 filtros
funcionarem no navegador.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import _repo  # noqa: F401

from dados_qdd import COLUNA_VALOR, construir_base_enriquecida

linhas = construir_base_enriquecida().rename(columns={COLUNA_VALOR: "valor"}).to_dict(orient="records")
dados = {"linhas": linhas}


def rejeitar_constante(constante: str) -> None:
    raise ValueError(f"valor nao serializavel em JSON: {constante}")


texto = json.dumps(dados, ensure_ascii=False)
json.loads(texto, parse_constant=rejeitar_constante)
sys.stdout.buffer.write(texto.encode("utf-8"))
