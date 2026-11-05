# Slide 9 — O que podemos concluir e quais são os limites

## Uso dos materiais

Inserir evidencias_limites.png. Os CSVs sustentam o quadro. Não inventar gráficos de ping, iperf, CPU ou vazão agregada. Uma nova coleta deve preservar calibração, hash do destino PUT e início/fim monotônicos comuns da rodada; o notebook não cria essas evidências retroativamente.

## Conteúdo e fala do roteiro

**Adicionar ao slide:** duas colunas, “Evidências disponíveis” e “Pendências”. Na primeira: cobertura completa, separação dos fatores, hashes GET compatíveis, IC entre rodadas. Na segunda: hash do destino PUT; logs de calibração por sentido; janela comum da rodada. Uma frase destacada: “Compartilhamento observado; ponto de saturação não determinado”.

**Fala sugerida — Integrante 2:**

> A análise identificou limitações relevantes. Primeiro, os hashes de GET permitem comparar entrada e saída, enquanto os registros de PUT preservam apenas o hash da entrada. Portanto, não declaramos integridade comprovada do destino para toda a campanha. Segundo, os arquivos disponíveis de calibração descrevem a topologia, mas não preservam os logs de ping, traceroute e iperf necessários para verificar os dois sentidos. Terceiro, falta uma janela comum medida da rodada. A análise anterior somava vazões individuais, o que não equivale a dividir bytes totais pela duração conjunta. O notebook deixa a vazão agregada indisponível. Podemos descrever aumento de tempo e queda da taxa individual, mas não estabelecer com rigor o ponto de saturação nem atribuí-lo exclusivamente ao enlace. Uma nova coleta deve preservar essas evidências e acompanhar recursos do host.
