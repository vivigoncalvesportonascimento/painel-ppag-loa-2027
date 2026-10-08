import streamlit as st

from paginas import o_painel, visao_geral

st.set_page_config(page_title="Painel PPAG-LOA 2027", layout="wide")

aba_painel, aba_visao_geral = st.tabs(["O Painel", "Visão Geral"])

with aba_painel:
    o_painel.renderizar()

with aba_visao_geral:
    visao_geral.renderizar()
