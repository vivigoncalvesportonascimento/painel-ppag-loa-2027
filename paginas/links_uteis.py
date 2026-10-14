"""Página 7: Links úteis."""

import html

import streamlit as st

_LINKS = [
    {
        "titulo": "Plano Plurianual de Ação Governamental - PPAG",
        "descricao": (
            "Apresenta no site da Secretaria de Estado de Planejamento e Gestão - "
            "SEPLAG, um breve resumo do que é o PPAG e inclui os documentos do PPAG "
            "vigente e dos exercícios anteriores. Também inclui os relatórios "
            "bimestrais de monitoramento do plano, o relatório anual de avaliação, "
            "os balanços sociais e materiais de apoio (manuais, treinamentos, "
            "conceitos e formulários)."
        ),
        "link": "https://www.mg.gov.br/planejamento/pagina/planejamento-e-orcamento/plano-plurianual-de-acao-governamental-ppag/plano-plurianual-de-acao",
    },
    {
        "titulo": "Lei de Diretrizes Orçamentárias - LDO",
        "descricao": (
            "Apresenta no site da Secretaria de Estado de Planejamento e Gestão - "
            "SEPLAG, um breve resumo do que é a LDO e inclui os documentos da LDO "
            "vigente e dos exercícios anteriores. Traz também alguns materiais de "
            "apoio, tais como, a base de execução histórica das receitas e as "
            "regras e diretrizes gerais para a estimativa de receita."
        ),
        "link": "https://www.mg.gov.br/planejamento/pagina/planejamento-e-orcamento/lei-de-diretrizes-orcamentarias-ldo/lei-de-diretrizes-orcamentarias",
    },
    {
        "titulo": "Lei Orçamentária Anual - LOA",
        "descricao": (
            "Apresenta no site da Secretaria de Estado de Planejamento e Gestão - "
            "SEPLAG, um breve resumo do que é a LOA e inclui os documentos da LOA "
            "vigente e dos exercícios anteriores. Além disso, traz o Decreto de "
            "Programação Orçamentária, o Classificador Econômico da Despesa, o "
            "Ementário da Receita e a relação de receitas que são desvinculadas "
            "por meio da Emenda nº 93/2016 (DREM)."
        ),
        "link": "https://www.mg.gov.br/planejamento/pagina/planejamento-e-orcamento/lei-orcamentaria-anual-loa/lei-orcamentaria-anual-loa",
    },
    {
        "titulo": "ALMG - Leis que compõem o Sistema Orçamentário",
        "descricao": (
            "Página no site da Assembleia Legislativa do Estado de Minas Gerais, "
            "que contém as leis do sistema orçamentário estadual, a saber: PMDI, "
            "PPAG, LDO e LOA. Nesta página é possível consultar o andamento, as "
            "discussões e as emendas relativo as leis em questão."
        ),
        "link": "https://www.almg.gov.br/atividade-parlamentar/orcamento-do-estado/inicial/",
    },
    {
        "titulo": "Portal da Transparência - MG",
        "descricao": (
            "O Portal da Transparência de MG apresenta uma série de informações e "
            "consultas sobre despesas, receitas, incluindo algumas bases em "
            "formato de dados abertos."
        ),
        "link": "https://www.transparencia.mg.gov.br/",
    },
    {
        "titulo": "Legislação de Finanças Públicas - Lei nº 4.320, de 17 de março de 1964",
        "descricao": (
            "A Lei Federal nº 4.320, de 17 de março de 1964, dispõe sobre as "
            "normas gerais de Direito Financeiro para a elaboração e controle dos "
            "orçamentos e balanços da União, dos Estados, dos Municípios e do "
            "Distrito Federal."
        ),
        "link": "https://www.planalto.gov.br/ccivil_03/leis/l4320.htm",
    },
    {
        "titulo": "Legislação de Finanças Públicas - Lei Complementar nº 101, de 04 de maio de 2000",
        "descricao": (
            "A Lei Federal Complementar nº 101, de 04 de maio de 2000, conhecida "
            "como Lei de Responsabilidade Fiscal (LRF), estabelece as normas de "
            "finanças públicas voltadas para a responsabilidade na gestão fiscal "
            "e dá outras providências."
        ),
        "link": "https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp101.htm",
    },
]

_CSS_CARD_LINK = """
<style>
.link-card {
    background: #ffffff;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    padding: 1.1rem 1.25rem;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1rem;
}
.link-card h4 {
    margin: 0;
    font-size: 0.98rem;
    color: #1f2933;
}
.link-card p {
    margin: 0;
    font-size: 0.85rem;
    color: #616e7c;
    flex-grow: 1;
}
.link-card a {
    font-size: 0.85rem;
    font-weight: 700;
    color: #0047AB;
    text-decoration: none;
}
.link-card a:hover {
    text-decoration: underline;
}
</style>
"""


def renderizar() -> None:
    st.title("Links Úteis")
    st.markdown(_CSS_CARD_LINK, unsafe_allow_html=True)

    for inicio in range(0, len(_LINKS), 3):
        colunas = st.columns(3)
        for coluna, item in zip(colunas, _LINKS[inicio : inicio + 3]):
            with coluna:
                _renderizar_card(item)


def _renderizar_card(item: dict) -> None:
    st.markdown(
        f"""
        <div class="link-card">
            <h4>{html.escape(item['titulo'])}</h4>
            <p>{html.escape(item['descricao'])}</p>
            <a href="{html.escape(item['link'])}" target="_blank" rel="noopener noreferrer">
                Acessar página →
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )
