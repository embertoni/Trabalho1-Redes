# Slide 7 — Vazão útil individual

## Uso dos materiais

Usar get_vazao_individual.png e get_destaques_vazao.png, ou os CSVs. Adicionar a fórmula de FORMULA.md. PUT é apoio. Os painéis não medem vazão agregada nem provam queda da capacidade total do serviço; observar as escalas verticais próprias de cada perfil.

## Conteúdo e fala do roteiro

**Adicionar ao slide:** painéis GET A/B do gráfico de vazão individual do notebook; destacar 10 MiB e esta tabela:

| Concorrência | Perfil A | Perfil B |
| --- | --- | --- |
| 1 | 87,322 Mbit/s | 17,744 Mbit/s |
| 32 | 2,997 Mbit/s | 0,609 Mbit/s |

Adicionar a fórmula `vazão individual = bytes úteis × 8 / tempo em segundos / 10⁶`. Não usar o gráfico antigo de HEAD nem o campo antigo `throughput_aggregate_mbps` como vazão medida do enlace.

**Fala sugerida — Integrante 1:**

> A vazão aqui é a taxa útil de cada transferência, calculada a partir dos bytes do arquivo e de sua duração. No GET de 10 mebibytes com um cliente, obtivemos aproximadamente 87,3 megabits por segundo em A e 17,7 em B. Com 32 clientes, a média individual caiu para cerca de 3 e 0,61 megabit por segundo. O perfil B teve menor vazão individual nas 12 comparações equivalentes de GET e PUT. A redução por cliente é coerente com o compartilhamento dos recursos disponíveis. Contudo, esses valores não são a vazão agregada da rodada; a queda individual, sozinha, não demonstra uma queda da capacidade total do serviço.
