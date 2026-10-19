"""Data loader da página Regionalização: base em nível de linha (~40 mil
linhas), codificada por dicionário (textos repetidos guardados uma única
vez; as linhas referenciam só o índice) para reduzir o tamanho do arquivo —
mesma técnica usada em site_estatico/dados_regionalizacao.json.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import _repo  # noqa: F401

from dados_regionalizacao import construir_base_enriquecida

df = construir_base_enriquecida().rename(
    columns={
        "Previsão Física 2027": "fisica",
        "Previsão Orçamentária 2027": "valor",
    }
)


def dicionario(coluna: str) -> tuple[list[str], dict[str, int]]:
    valores = sorted(df[coluna].unique())
    return valores, {valor: indice for indice, valor in enumerate(valores)}


uo_valores, uo_idx = dicionario("uo_label")
acao_valores, acao_idx = dicionario("acao_label")
regiao_valores, regiao_idx = dicionario("regiao")
produto_valores, produto_idx = dicionario("produto")
unidade_valores, unidade_idx = dicionario("unidade_medida")

municipios = df[["municipio", "municipio_ibge"]].drop_duplicates().sort_values("municipio")
municipio_idx = {nome: indice for indice, nome in enumerate(municipios["municipio"])}

dados = {
    "uo": uo_valores,
    "acao": acao_valores,
    "regiao": regiao_valores,
    "produto": produto_valores,
    "unidade": unidade_valores,
    "municipios": [
        {"nome": nome, "ibge": ibge}
        for nome, ibge in zip(municipios["municipio"], municipios["municipio_ibge"])
    ],
    "linhas": {
        "uo": df["uo_label"].map(uo_idx).tolist(),
        "acao": df["acao_label"].map(acao_idx).tolist(),
        "regiao": df["regiao"].map(regiao_idx).tolist(),
        "produto": df["produto"].map(produto_idx).tolist(),
        "unidade": df["unidade_medida"].map(unidade_idx).tolist(),
        "municipio": df["municipio"].map(municipio_idx).tolist(),
        "fisica": df["fisica"].tolist(),
        "valor": df["valor"].tolist(),
    },
}


def rejeitar_constante(constante: str) -> None:
    raise ValueError(f"valor nao serializavel em JSON: {constante}")


texto = json.dumps(dados, ensure_ascii=False)
json.loads(texto, parse_constant=rejeitar_constante)
sys.stdout.buffer.write(texto.encode("utf-8"))
