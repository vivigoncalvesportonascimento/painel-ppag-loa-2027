"""Cálculos da página "Glossário", compartilhados entre o app Streamlit e
o gerador do site estático (GitHub Pages).
"""

from etl.glossario import carregar_glossario


def construir_lista_termos() -> list[dict]:
    df = carregar_glossario().sort_values("Termo")
    return [
        {
            "termo": linha["Termo"],
            "definicao_tecnica": linha["Definição Técnica"],
            "linguagem_simples": linha["Linguagem Simples"],
        }
        for _, linha in df.iterrows()
    ]
