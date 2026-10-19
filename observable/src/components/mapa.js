// Mapa coroplético dos municípios de MG — destaque binário (azul = município
// selecionado no filtro, cinza = demais), igual ao site estático
// (dados_regionalizacao.py: construir_mapa / script.js: atualizarMapaRegionalizacao).
import * as Plot from "@observablehq/plot";
import { formatarMoeda } from "./utils.js";

const COR_DESTAQUE = "#0047AB";
const COR_SEM_DESTAQUE = "#cbd2d9";

export function mapaRegionalizacao(geojson, linhas, municipioSelecionado, { width } = {}) {
  const valoresPorIbge = new Map();
  for (const linha of linhas) {
    valoresPorIbge.set(linha.municipio_ibge, (valoresPorIbge.get(linha.municipio_ibge) || 0) + linha.valor);
  }

  const ibgeSelecionado = municipioSelecionado
    ? linhas.find((l) => l.municipio === municipioSelecionado)?.municipio_ibge
    : null;

  return Plot.plot({
    width,
    height: 540,
    projection: "mercator",
    marks: [
      Plot.geo(geojson.features, {
        fill: (f) => (f.properties.id === ibgeSelecionado ? COR_DESTAQUE : COR_SEM_DESTAQUE),
        stroke: "#ffffff",
        strokeWidth: 0.4,
        title: (f) =>
          `${f.properties.name}\nPrevisão Orçamentária 2027: ${formatarMoeda(valoresPorIbge.get(f.properties.id) || 0)}`
      })
    ]
  });
}
