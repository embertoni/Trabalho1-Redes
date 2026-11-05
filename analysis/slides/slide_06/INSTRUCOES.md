# Slide 6 — Tempo de resposta: efeito da rede e da concorrência

## Uso dos materiais

Inserir get_tempo.png e get_destaques_tempo.png ou sua tabela CSV. Gráfico em segundos; tabela em milissegundos. put_tempo.png é apoio, separado de GET. A diferença A/B não isola o efeito do atraso: a capacidade também muda. Os painéis usam escalas verticais próprias, identificadas nos eixos.

## Conteúdo e fala do roteiro

**Adicionar ao slide:** usar os painéis GET A/B do gráfico de tempo do notebook, ampliados; não colocar a figura inteira com seis painéis em tamanho ilegível. Destacar o arquivo de 10 MiB:

| Concorrência | Perfil A | Perfil B |
| --- | --- | --- |
| 1 | 960,8 ms | 4.729,8 ms |
| 32 | 28.105,4 ms | 137.936,0 ms |

Legenda: “Médias entre rodadas; barras = IC95% de Student; n=11 por célula”.

**Fala sugerida — Integrante 2:**

> O primeiro resultado é o aumento do tempo com a concorrência, especialmente nos arquivos maiores. No GET de 10 mebibytes, com um cliente, a média ficou próxima de 961 milissegundos no perfil A e 4,73 segundos no perfil B. Com 32 clientes, passou para aproximadamente 28,1 e 137,9 segundos. O perfil B teve maior latência nas 18 comparações equivalentes de método, tamanho e concorrência. As barras representam a incerteza entre rodadas, não entre clientes da mesma rodada. O comportamento é compatível com maior tempo de serviço e compartilhamento de recursos. Como capacidade e atraso mudam juntos entre A e B, não podemos atribuir toda a diferença isoladamente à latência ou à banda.
