import streamlit as st

from paginas import despesa_fiscal, o_painel, receita_fiscal, visao_geral

st.set_page_config(page_title="Painel PPAG-LOA 2027", layout="wide")

aba_painel, aba_visao_geral, aba_receita_fiscal, aba_despesa_fiscal = st.tabs(
    ["O Painel", "Visão Geral", "Receita Fiscal", "Despesa Fiscal"]
)

with aba_painel:
    o_painel.renderizar()

with aba_visao_geral:
    visao_geral.renderizar()

with aba_receita_fiscal:
    receita_fiscal.renderizar()

with aba_despesa_fiscal:
    despesa_fiscal.renderizar()
