# Slide 4 — Como os experimentos foram analisados

## Uso dos materiais

Usar matriz_metodo.png. matriz.csv contém todas as células. Os totais são planejados; a cobertura observada está no slide 5. A independência entre rodadas é uma hipótese, não uma garantia do gráfico.

## Conteúdo e fala do roteiro

**Adicionar ao slide:** matriz visual `2 perfis × 3 operações × 2 tamanhos × 3 concorrências = 36 células`; tamanhos 2/10 MiB; concorrências 1/8/32; 11 rodadas por célula; total de 396 rodadas e 5.412 requisições. Caixa em destaque: “Unidade do IC: rodada completa”.

**Fala sugerida — Integrante 2:**

> A matriz combina os dois perfis, três operações, arquivos de 2 e 10 mebibytes e concorrências de 1, 8 e 32. Os tamanhos representam cargas de compartilhamento de fotos e vídeos curtos. São 36 configurações, com 11 rodadas cada, totalizando 396 rodadas e 5.412 requisições. O notebook lê os JSONs brutos e confere os fatores contra a matriz. Para a inferência, calculamos médias por rodada e depois média, mediana, desvio amostral e intervalo de confiança de 95% com Student. Workers da mesma rodada compartilham recursos e não são tratados como repetições independentes.
