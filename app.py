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
    aba_acao_orcamentaria,
    aba_programa,
    aba_regionalizacao,
    aba_receita_fiscal,
    aba_despesa_fiscal,
    aba_despesa_orgao,
    aba_qdd,
    aba_loa_investimentos,
    aba_glossario,
    aba_links_uteis,
) = st.tabs(
    [
        "Sobre o Painel",
        "Visão Geral",
        "Ação Orçamentária",
        "Programa",
        "Regionalização",
        "Receita Fiscal",
        "Despesa Fiscal",
        "Despesa por Órgão",
        "QDD",
        "LOA Investimentos",
        "Glossário",
        "Links Úteis",
    ]
)

with aba_painel:
    o_painel.renderizar()

with aba_visao_geral:
    visao_geral.renderizar()

with aba_acao_orcamentaria:
    acao_orcamentaria.renderizar()

with aba_programa:
    programa.renderizar()

with aba_regionalizacao:
    regionalizacao.renderizar()

with aba_receita_fiscal:
    receita_fiscal.renderizar()

with aba_despesa_fiscal:
    despesa_fiscal.renderizar()

with aba_despesa_orgao:
    despesa_orgao.renderizar()

with aba_qdd:
    qdd.renderizar()

with aba_loa_investimentos:
    loa_investimentos.renderizar()

with aba_glossario:
    glossario.renderizar()

with aba_links_uteis:
    links_uteis.renderizar()
