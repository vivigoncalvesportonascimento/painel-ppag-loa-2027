"""Construtores de gráficos Plotly reaproveitados por várias páginas."""

import pandas as pd
import plotly.express as px


def grafico_percentual_horizontal(
    df: pd.DataFrame, coluna_categoria: str, coluna_valor: str, titulo: str
) -> "px.Figure":
    """Barras horizontais com o % do total de `coluna_valor`, por `coluna_categoria`.

    Altura calculada pela quantidade de categorias, para caber rótulos
    maiores; o card visível (CSS) que a envolve controla a rolagem.
    """
    categorias = df[coluna_categoria].str.strip()
    agrupado = df.groupby(categorias)[coluna_valor].sum()
    percentual = (agrupado / agrupado.sum() * 100).sort_values(ascending=True)

    percentual_df = percentual.reset_index()
    percentual_df.columns = [coluna_categoria, "percentual"]

    altura = max(340, 32 * len(percentual_df) + 90)

    fig = px.bar(
        percentual_df,
        x="percentual",
        y=coluna_categoria,
        orientation="h",
        title=f"<b>{titulo}</b>",
        text=percentual_df["percentual"].map(lambda v: f"{v:.1f}%"),
        labels={"percentual": "% do total", coluna_categoria: ""},
        color_discrete_sequence=["#0047AB"],
    )
    fig.update_traces(textfont_size=15, textposition="outside")
    fig.update_layout(
        showlegend=False,
        height=altura,
        font=dict(family="system-ui, -apple-system, Segoe UI, Arial, sans-serif", color="#1f2933"),
        title=dict(font=dict(size=16, color="#1f2933")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=30, t=40, b=10),
        yaxis=dict(tickfont=dict(size=11), automargin=True),
        xaxis=dict(gridcolor="#eef1f4"),
    )
    return fig
