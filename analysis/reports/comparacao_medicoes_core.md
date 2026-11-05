# Comparação das medições CORE com a campanha e as simulações

Revisão em 05/11/2026. Foram lidos os 12 arquivos fornecidos em [comandos/](../../comandos/), sem alteração das entradas. A associação de `comandosip/comandosip` ao perfil A e `comandosipB/comandosipB` ao perfil B usa a organização das pastas e sua coerência com a matriz e os XMLs. Não há identificador de sessão/campanha ou data de execução embutidos nessas saídas; a correspondência temporal exata com cada rodada continua sem comprovação.

Esta revisão atualiza a conclusão anterior sobre falta de saídas de calibração: **agora existem medições reais fornecidas de ping, traceroute e iperf nos dois sentidos, para ambos os perfis**. Isso não equivale a reexecutar CORE nesta sessão.

## 1. Resultados extraídos

Usa-se o resumo **receiver** do iperf, sem misturar taxa enviada e recebida. A taxa é de dados TCP da ferramenta, distinta da vazão útil de uma transferência completa da aplicação.

| Perfil | Sentido do conteúdo | Banda nominal (Mbit/s) | iperf recebido (Mbit/s) | RTT médio de ping (ms) | Retransmissões TCP no emissor |
| --- | --- | --- | --- | --- | --- |
| A | Cliente → servidor | 100 | 93,9 | 10,555 | 48 |
| A | Servidor → cliente | 100 | 94,4 | 10,655 | 62 |
| B | Cliente → servidor | 20 | 18,9 | 40,588 | 11 |
| B | Servidor → cliente | 20 | 19,0 | 40,545 | 12 |

Cada perfil/sentido tem **um ensaio iperf de aproximadamente 20 s**, uma sequência de **10 pings**, e um traceroute com cinco saltos até o destino. São quatro ensaios iperf e 40 pings, todos respondidos. Não interpretar os intervalos de aproximadamente um segundo do iperf como ensaios independentes, nem calcular IC entre repetições inexistentes. Os campos `mdev` do ping são dispersão das sondas, não IC de calibração.

O arquivo `iperfR_server.txt` contém `Reverse mode, remote host 10.10.5.10 is sending` e endereço local `10.10.1.10`. Portanto, é saída do cliente iperf em modo reverso: mede conteúdo servidor→cliente, independentemente do nome do arquivo. Os tempos de receiver são 20,05/20,00 s em A e 20,09/20,01 s em B; não afirmar duração exata idêntica ou descarte inicial de 3 s, que essas saídas não mostram.

**Perda configurada, perda observada no ping e retransmissões são informações diferentes.** Os 40 pings não tiveram perda, mas o iperf contabiliza retransmissões. Não é possível inferir delas uma taxa de perda de pacotes nem sua causa específica. Também não se pode declarar TCP sem perdas apenas porque a configuração não injeta perda artificial.

## 2. Coerência com a topologia e a matriz

As rotas cliente→servidor são `10.10.1.1 → 10.10.2.2 → 10.10.3.2 → 10.10.4.2 → 10.10.5.10`; no sentido inverso, `10.10.5.1 → 10.10.4.1 → 10.10.3.1 → 10.10.2.1 → 10.10.1.10`. Correspondem aos quatro roteadores e ao destino dos XMLs de [topology/](../../topology/). Cinco saltos não significam cinco roteadores: o quinto é o host de destino.

A elevação do RTT aparece a partir do terceiro salto, após atravessar o enlace entre os roteadores de núcleo: cerca de 10,5 ms em A e 40,5–40,9 ms em B nessa posição. Isso é coerente com o gargalo escolhido. O RTT de uma sonda inclui ida e volta e comportamento do nó que responde; diferenças entre saltos não são medições exatas do atraso de um enlace isolado. Pequenas inversões de RTT entre saltos são possíveis e não demonstram redução física da distância.

A [matriz](../../configs/experiment_plan.csv) e os XMLs configuram 100 Mbit/s e 5 ms por sentido em A, 20 Mbit/s e 20 ms em B. Os RTTs medidos próximos de 10,6/40,6 ms são coerentes com contribuições de 10/40 ms do gargalo ao RTT. Assim, a indicação antiga de “latência 10 ms” em A pode ser compatível com ida e volta; não se deve convertê-la em 10 ms unidirecionais.

As taxas recebidas são 93,9–94,4% da banda nominal em A e 94,5–95,0% em B. A diferença de sentido é pequena nesses ensaios; sem repetições, não se declara equivalência estatística. Os logs acrescentam evidência operacional de conectividade, percurso e capacidade efetiva, mas ainda não incluem `tc`, inventário da sessão, monitoração de recursos ou vínculo temporal à campanha.

## 3. Comparação explícita com os valores simulados

As [fixtures](../../tests/fixtures/pendencias_simuladas/README.md) permanecem intactas e identificadas como sintéticas. Não foram recalibradas para imitar os novos números.

| Perfil/sentido | RTT real (ms) | RTT sintético médio (ms) | iperf real (Mbit/s) | iperf sintético médio (Mbit/s) |
| --- | --- | --- | --- | --- |
| A, cliente → servidor | 10,555 | 11,009 | 93,9 | 95,053 |
| A, servidor → cliente | 10,655 | 11,005 | 94,4 | 94,805 |
| B, cliente → servidor | 40,588 | 41,014 | 18,9 | 19,036 |
| B, servidor → cliente | 40,545 | 40,981 | 19,0 | 19,015 |

O modelo ideal acrescentava 1 ms ao RTT teórico; as médias reais ficam entre 0,350 e 0,454 ms abaixo das médias sintéticas. A calibração sintética de iperf fica entre 0,015 e 1,153 Mbit/s acima do valor real correspondente. Essa proximidade é descritiva, não validação estatística: as fixtures têm 30 pings e 11 ensaios virtuais de 30 s por sentido, enquanto os dados reais têm 10 pings e um ensaio de cerca de 20 s. O modelo tampouco representava as retransmissões observadas.

A sequência de endereços simulada coincide com os traceroutes novos porque foi construída a partir da mesma topologia; isso não transforma a rota sintética em observação independente.

Na aplicação, a diferença é maior. GET de 10 MiB:

| Perfil/concorrência | Tempo real (ms) | Tempo sintético (ms) | Taxa individual real (Mbit/s) | Taxa individual sintética (Mbit/s) |
| --- | --- | --- | --- | --- |
| A, 1 | 960,836 | 1.213,880 | 87,322 | 69,108 |
| A, 32 | 28.105,378 | 30.324,774 | 2,997 | 2,766 |
| B, 1 | 4.729,790 | 6.053,510 | 17,744 | 13,858 |
| B, 32 | 137.935,970 | 151.367,335 | 0,609 | 0,554 |

A hipótese arbitrária de utilização de 75% para um cliente ajuda a explicar por que o modelo subestima essas taxas; ela não foi ajustada experimentalmente. Logo, **não usar curvas sintéticas para preencher resultados medidos ou concluir saturação real**. Os 72 pares de métricas em `comparacao_aplicacao_simulada.csv` mantêm HEAD sem taxa, sem transformar ausência de aplicabilidade em zero.

## 4. Relação com os resultados da aplicação

A conferência dos 5.412 JSONs ativos recuperou 396 rodadas e 36 células com 11 rodadas completas. As médias destacadas no roteiro permanecem iguais às calculadas no notebook. No GET de 10 MiB e um cliente, 87,322 Mbit/s em A e 17,744 Mbit/s em B ficam abaixo dos ensaios iperf no mesmo sentido servidor→cliente, de 94,4 e 19,0 Mbit/s. As razões descritivas são aproximadamente 92,5% e 93,4%, mas não são uma eficiência universal nem uma comparação pareada no tempo.

Iperf mede um fluxo por cerca de 20 s; a aplicação mede uma operação finita que inclui conexão, processamento e I/O. A diferença não deve ser integralmente atribuída a protocolo, disco ou retransmissão sem experimentos que isolem esses custos. A direção cliente→servidor é a referência adequada para PUT.

Os novos ensaios não fornecem a janela comum das rodadas concorrentes da aplicação. Portanto, permanece inválido multiplicar a média individual por C ou somar taxas para declarar goodput agregado. O ponto de saturação do serviço não passa a estar medido porque o iperf atingiu uma taxa próxima da nominal.

A/B alteram simultaneamente largura de banda e atraso; as comparações mostram o efeito combinado. Também continuam sem solução pelos novos logs: hash do destino PUT, prova de sobrescrita na campanha (os 1.804 PUTs são 201), recursos/cache e divergências de HEAD/erros identificadas na revisão do código.

## 5. Aplicação ao roteiro

O [roteiro revisado](roteiro_video.md) mantém 11 slides e 9min40s. Insere calibração real no slide 4, reúne matriz e demonstração no slide 5 e usa o slide 9 para relacionar medição TCP, transferência da aplicação e concorrência. Nenhum valor sintético entra como resultado. Mantém contribuições propostas para dois integrantes e autoavaliação com melhorias concretas.

As referências, limitações de documentação e instruções de montagem ficam apenas na abertura técnica do roteiro, fora da apresentação. Slides e falas não citam documentos. Nos slides, as ressalvas são sobre as próprias medições: tamanho da amostra, métricas distintas e limites da conclusão.

## Reproduzir a comparação

Após o inventário `all` obrigatório e aprovação do perfil `analysis` no venv:

```bash
.venv-analysis/bin/python analysis/comparar_medicoes_core.py
```

O script lê as entradas reais e sintéticas separadamente, extrai os resumos de receptor/emissor, confere os sentidos, preserva os três RTTs de cada salto e produz em [comparacao_core/](comparacao_core/): seis CSVs, gráfico PNG/SVG e identificação SHA-256 dos 12 arquivos reais (um dos seis CSVs). Não inicia rede, não modifica os logs, não executa testes C e não grava em `experiments/raw/`.

O PNG mede 2560×1440 e pode ser usado no slide 4; o SVG permite editar a composição. Não há barras de IC de calibração, pois existe apenas um ensaio independente por perfil/sentido. Os gráficos anteriores de desempenho da aplicação continuam utilizáveis, mas o notebook e o PDF do roteiro não foram regenerados nesta revisão.

Ambiente nesta tarefa: `all` retornou 1 por ausência de CORE e bibliotecas no Python de sistema; `analysis` no venv retornou 0. A extração e a comparação terminaram sem erro. O campo local `core_runtime_validated=false` continua correto: analisar medições fornecidas não equivale a validar uma sessão ativa nesta máquina.
