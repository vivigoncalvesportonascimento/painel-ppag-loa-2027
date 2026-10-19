// Decodifica o JSON codificado por dicionário de data/regionalizacao.json.py
// (textos repetidos guardados uma única vez; as linhas referenciam só o
// índice) — mesmo formato e mesma técnica do site estático.
export function decodificarLinhas(dadosReg) {
  const { uo, acao, regiao, produto, unidade, municipios, linhas } = dadosReg;
  const total = linhas.valor.length;
  const resultado = new Array(total);
  for (let i = 0; i < total; i += 1) {
    const municipio = municipios[linhas.municipio[i]];
    resultado[i] = {
      uo_label: uo[linhas.uo[i]],
      acao_label: acao[linhas.acao[i]],
      regiao: regiao[linhas.regiao[i]],
      produto: produto[linhas.produto[i]],
      unidade_medida: unidade[linhas.unidade[i]],
      municipio: municipio.nome,
      municipio_ibge: municipio.ibge,
      fisica: linhas.fisica[i],
      valor: linhas.valor[i]
    };
  }
  return resultado;
}
