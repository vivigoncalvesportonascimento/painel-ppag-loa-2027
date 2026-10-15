import streamlit as st

from paginas import (
    acao_orcamentaria,
    despesa_fiscal,
    despesa_orgao,
    glossario,
    links_uteis,
    loa_investimentos,
    o_painel,
    programa,
    qdd,
    receita_fiscal,
    regionalizacao,
    visao_geral,
)

st.set_page_config(page_title="Painel PPAG-LOA 2027", layout="wide")

(
    aba_painel,
    aba_visao_geral,
    aba_receita_fiscal,
    aba_despesa_fiscal,
    aba_despesa_orgao,
    aba_loa_investimentos,
    aba_links_uteis,
    aba_regionalizacao,
    aba_glossario,
    aba_acao_orcamentaria,
    aba_programa,
    aba_qdd,
) = st.tabs(
    [
        "O Painel",
        "Visão Geral",
        "Receita Fiscal",
        "Despesa Fiscal",
        "Despesa por Órgão",
        "LOA Investimentos",
        "Links Úteis",
        "Regionalização",
        "Glossário",
        "Ação Orçamentária",
        "Programa",
        "QDD",
    ]
)

with aba_painel:
    o_painel.renderizar()

with aba_visao_geral:
    visao_geral.renderizar()

with aba_receita_fiscal:
    receita_fiscal.renderizar()

with aba_despesa_fiscal:
    despesa_fiscal.renderizar()

with aba_despesa_orgao:
    despesa_orgao.renderizar()

with aba_loa_investimentos:
    loa_investimentos.renderizar()

with aba_links_uteis:
    links_uteis.renderizar()

with aba_regionalizacao:
    regionalizacao.renderizar()

with aba_glossario:
    glossario.renderizar()

with aba_acao_orcamentaria:
    acao_orcamentaria.renderizar()

with aba_programa:
    programa.renderizar()

with aba_qdd:
    qdd.renderizar()
