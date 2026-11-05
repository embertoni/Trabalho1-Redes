# Revisão do histórico Manus e das evidências do projeto

> Atualização posterior em 05/11/2026: a nova pasta `comandos/` acrescentou medições reais de ping, traceroute e iperf para A/B nos dois sentidos. A conclusão anterior de ausência dessas saídas foi superada parcialmente. Consulte a [comparação atualizada](../analysis/reports/comparacao_medicoes_core.md); as demais lacunas de janela comum, integridade PUT, recursos e vínculo de sessão permanecem. O texto abaixo preserva o estado examinado antes da chegada dos novos logs.

Revisão de 05/11/2026. Escopo: leitura dos seis arquivos de `conversa_trabalho1_redes`, comparação com fontes, coleta, análise e artefatos locais; criação de dados sintéticos isolados. Não houve nova campanha CORE nem alteração da aplicação.

## Como interpretar a comparação

O [índice do histórico](../conversa_trabalho1_redes/00-INDICE.md) informa que os arquivos preservam uma sequência temática e comandos principais. Eles são um relato organizado, não uma transcrição integral com saídas, horários e identidade de cada execução. O relato ajuda a reconstruir decisões, mas uma afirmação de sucesso nele não substitui a saída original de teste ou medição.

Os documentos de desenvolvimento orientam a revisão de contratos e métodos; não entram como amostras nem comprovam resultados. Para a análise quantitativa, prevalecem os registros da campanha ativa em `experiments/raw/`, com os limites de coleta descritos abaixo. Os backups não foram concatenados. O [enunciado](referencias/trabalho1_redes_enunciado.pdf) é a referência acadêmica; as escolhas do [guia revisado](GUIA_COMPLETO_TRABALHO1_REDES.md) e do [contrato](CONTRATO_PROTOCOLO.md) são identificadas como escolhas técnicas, sem transformar toda recomendação em exigência do professor.

Classificações usadas: **presente** significa artefato inspecionado; **relatado** significa afirmação do histórico sem comprovação completa preservada; **pendente** significa evidência ou validação ainda necessária. Inspeção estática não equivale a executar testes.

## Passo a passo comparado

### 1. Requisitos, guia e repositório

A [fase 1](../conversa_trabalho1_redes/01-guia-e-repositorio.md) descreve a preparação do guia e a correção da identificação inicial do repositório. O repositório atual contém referências, guia revisado, decisões e contrato separado. Isso corrobora a organização descrita, mas não valida retrospectivamente cada comando. GET/PUT são centrais; HEAD continua sendo a extensão conservadora registrada em D04. Os defeitos conhecidos do guia original impedem usá-lo como implementação de referência validada.

### 2. Ambiente Windows, WSL e Docker

O histórico relata problemas na construção da imagem, preparação intermediária de `emane-python` e instalação de traceroute/iperf3 no contêiner. A existência dessas instruções é coerente com a rota Docker do guia, seção 3, mas não comprova qual imagem e versão executaram cada rodada.

Nesta sessão o inventário `all` no WSL retornou 1: faltam CORE e bibliotecas de análise no Python de sistema. O perfil `analysis` no venv existente retornou 0. Isso permite a simulação local; não valida CORE. A ausência de CORE neste WSL não prova que o contêiner utilizado anteriormente estivesse sem CORE. Para reprodução, registrar inventário no host e no contêiner efetivamente usados, identidade da imagem, versões e sessão CORE validada.

### 3. Contrato e organização da aplicação

A [fase 2](../conversa_trabalho1_redes/02-protocolo-e-implementacao.md) apresenta a criação de contrato, biblioteca de protocolo, servidor e cliente. Esses artefatos estão presentes em [src/](../src/) e no [contrato](CONTRATO_PROTOCOLO.md). A estrutura corresponde à proposta da seção 4 do guia: sockets POSIX, TCP, C, cabeçalhos textuais e corpo binário com comprimento explícito.

README, abertura do plano e trechos antigos do STATUS ainda dizem que não há fontes/campanha. Isso está desatualizado: os arquivos existem. Não se deve usar esses trechos para negar o trabalho realizado, nem marcar automaticamente todas as tarefas como concluídas porque os arquivos existem. Esta revisão registra a discrepância; não reescreve todo o planejamento histórico.

### 4. Parser, ASan e testes de protocolo

O histórico relata detecção de overflow ao usar `%257s` e correção para `%256s`. A leitura de [protocol.c](../src/protocol.c) confirma o limite `%256s` no parsing da primeira linha. [tests/test_protocol.c](../tests/test_protocol.c) está presente. A execução bem-sucedida com sanitizadores é relatada, mas os arquivos do histórico não incluem o log integral que ligue esse resultado ao commit atual.

O comando `/tmp/test_protocol` depende de um binário temporário de outra sessão. Para concluir a validação, recompilar o executor no ambiente atual, preservar comando, compilador, revisão e stdout/stderr, e conferir casos efetivamente executados. Nesta revisão não houve execução da suíte C.

### 5. Concorrência, arquivos temporários e erros do servidor

[server.c](../src/server.c) contém atendimento por threads, temporários e publicação por rename, coerentes com a arquitetura relatada. Entretanto, presença do mecanismo não comprova todos os cenários de corrida, desconexão e erro.

Há divergências estáticas que merecem teste específico: HEAD anuncia `Content-Length: 0` para arquivo existente, enquanto o contrato prevê o tamanho que GET retornaria; caminhos de erro do PUT em chmod, recepção, fsync, close e rename seguem para cleanup sem resposta estruturada nessa função. Nem toda desconexão permite responder, mas erros locais antes do envio do cabeçalho exigem revisão individual. Dados sintéticos não corrigem essas divergências. Nenhuma mudança foi feita no servidor.

### 6. Cliente, temporização e testes em localhost

O histórico relata PUT/GET/HEAD, 404, binários de 1/2 MiB, sobrescrita e dez GETs simultâneos com hashes. Isso descreve bons testes funcionais, mas não preserva todas as saídas nem comprova comportamento em CORE. [client.c](../src/client.c) usa `CLOCK_MONOTONIC`; isso sustenta o mecanismo de duração individual, não a existência de relógios comparáveis entre máquinas.

É preciso registrar exatamente o que o intervalo inclui: conexão, transferência, persistência, publicação e fechamento. Não reconstruir uma janela de rodada usando apenas durações individuais ou relógios monotônicos de hosts distintos.

### 7. Topologia e endereçamento

A [fase 3](../conversa_trabalho1_redes/03-topologia-e-campanha.md) descreve a topologia cliente → roteador de acesso → dois roteadores de núcleo → roteador de acesso → servidor. Os [XMLs](../topology/) contêm esses seis nós e cinco enlaces, com cliente `10.10.1.10`, servidor `10.10.5.10` e sub-redes intermediárias `10.10.2.0/30`, `10.10.3.0/30`, `10.10.4.0/30`.

O gargalo está entre os roteadores de núcleo. Nos XMLs, A configura 100 Mbit/s e 5.000 µs por sentido; B configura 20 Mbit/s e 20.000 µs por sentido. Configuração salva é evidência da intenção de configuração; exige confirmação por sessão ativa, rotas e `tc`. Largura de banda zero nos outros enlaces deve ser interpretada conforme a configuração CORE, não como medição de enlace sem capacidade.

### 8. Calibração e distinção entre RTT e atraso

O histórico orienta ping, traceroute e iperf, mas [experiments/calibration/](../experiments/calibration/) contém principalmente descrições: `topologia-perfil-B.txt` tem campos de validação sem valores. `runtime-minimo.txt` e `aplicacao-core.txt`, citados na sequência, não foram encontrados nessa pasta. O texto do perfil A menciona 10 ms sem delimitar claramente RTT versus atraso unidirecional; o XML indica 5 ms por sentido, compatível com contribuição de aproximadamente 10 ms ao RTT. Não reinterpretar esse texto como uma medição de ping.

Faltam resultados brutos de ida e volta que confirmem taxa efetiva, RTT, rota e gargalo. Os CSVs sintéticos de ping/iperf/traceroute fornecidos agora ilustram o formato e as unidades; não são logs dessas ferramentas.

### 9. Piloto e preparação do estado

Os registros em [experiments/pilot/](../experiments/pilot/) incluem GET 200, PUT 201, HEAD 200 e erro 404. O GET de 2 MiB registra 310,101 ms e 54,102 Mbit/s; o PUT registra 303,481 ms e 55,283 Mbit/s. Esses números são de registros existentes, não da simulação. Há hash de entrada, mas os campos para comparação com destino não constituem uma comprovação completa de integridade PUT.

É necessário congelar política de cache/aquecimento, fsync, arquivos preexistentes e recursos do host. A matriz continua com `planning_status=proposed`; a contagem de execução não substitui o registro da metodologia efetivamente usada.

### 10. Matriz e cobertura da campanha

A [matriz](../configs/experiment_plan.csv) possui 36 células: dois perfis × três métodos × dois tamanhos × três concorrências, com 11 rodadas. A inspeção dos JSONs ativos confirmou 5.412 requisições, 396 pares únicos cenário/rodada e 36 cenários. Há 1.804 GETs `ok/200`, 1.804 PUTs `ok/201` e 1.804 HEADs `ok/200`.

Isso corrobora a execução registrada da matriz, mas status de sucesso sozinho não comprova rota, capacidade real, integridade remota ou ausência de tentativas omitidas. O notebook já distingue essas limitações; a campanha não foi repetida nesta revisão.

### 11. Coletor e janela comum

[run_campaign.py](../scripts/run_campaign.py) inicia tarefas com `ThreadPoolExecutor`, sem barreira explícita nem persistência da janela comum. Calcula um tempo de subprocesso, mas não o salva no registro normal. `started_utc` é preenchido depois que o subprocesso termina: o nome do campo não autoriza interpretá-lo como início real da tentativa. O subprocesso também não recebe timeout global; a opção `--io-timeout 60` do cliente não é automaticamente um prazo total do processo.

Para goodput agregado, registrar no coordenador um instante monotônico de liberação e a conclusão de cada worker, com domínio de relógio explícito. Usar `8 × bytes úteis verificados / (fim da rodada − liberação)` em bit/s, depois dividir por 10^6. Esse intervalo inclui o escalonamento do coordenador e deve ser descrito como tal. Os hashes devem ser verificados fora dessa janela, e uma rodada inválida não entra silenciosamente nas médias de sucesso.

### 12. Integridade e sobrescrita PUT

O coletor salva hash da entrada e, em GET, da saída local. Para PUT não coleta o hash do destino no servidor. Um envio de tamanho esperado e resposta 201 não prova igualdade do conteúdo remoto.

Além disso, usa `/campaign-<cenário>-r<rodada>-w<worker>.bin`, nome próprio de cada tentativa. Todos os 1.804 PUTs ativos retornam 201. Portanto, esta campanha mostra criação segundo a telemetria, não uma campanha de sobrescrita. O teste de sobrescrita relatado na fase 2 é evidência narrativa separada. Para comprovar a funcionalidade, executar teste com arquivo previamente existente e conferir hash após substituição; para medir desempenho de sobrescrita, preparar previamente cada destino fora do intervalo e registrar esse modo de carga.

As fixtures modelam sobrescrita ideal com status 200 e hashes de payloads virtuais. Essa diferença é intencional e está identificada; não deve ser usada para reinterpretar os PUTs reais como sobrescritas.

### 13. Análise estatística e saturação

A [fase 4](../conversa_trabalho1_redes/04-analise-e-entrega.md) acerta ao distinguir rodada de worker. Porém, [analyze_results.py](../scripts/analyze_results.py) soma taxas individuais para o campo agregado, usa 1,96 no IC e considera rodada `ok` quando todos os registros observados são `ok`, mesmo que falte um worker esperado. Esses detalhes não são resolvidos apenas pela descrição correta no histórico.

O [notebook atual](../analysis/analise_resultados.ipynb) usa Student entre rodadas e mantém agregado indisponível sem janela comum. O arquivo legado e seus produtos precisam ser harmonizados antes de uma entrega final com números consistentes. A suíte sintética fornecida aqui confere seus próprios dados; não é um teste automático do notebook nem do analisador legado.

A comparação A/B mantém operação, tamanho e concorrência, mas altera simultaneamente banda e atraso. Ela sustenta um efeito combinado dos perfis; não identifica isoladamente a contribuição causal da banda ou do atraso. Curvas sintéticas de platô têm a saturação imposta pelo modelo. Para uma conclusão experimental, medir janela comum e calibração; para separar os fatores, planejar perfis adicionais mantendo um deles fixo e registrar a mudança antes da coleta.

### 14. Recursos, cache e possíveis gargalos locais

O material não fornece uma série suficiente de CPU, memória e I/O associada às rodadas. Não é possível concluir que o host nunca limitou a emulação nem atribuir diferenças GET/PUT exclusivamente à rede. Os valores novos de recursos são ilustrações; `io_mib_s` representa volume útil por janela e não uma leitura de disco real. Cache aquecido e fsync são hipóteses do modelo. A medição real deve identificar o escopo dos contadores e considerar que vários nós emulados podem compartilhar o mesmo host.

### 15. Relatório, slides, contribuições e entrega

A fase 4 propõe relatório e vídeo; a [fase 5](../conversa_trabalho1_redes/05-arquivos-e-comandos.md) reúne comandos, inclusive caminhos temporários de outra sessão. Eles precisam ser adaptados ao checkout atual antes de execução, sem tratar o exemplo de empacotamento como arquivo já produzido.

Existe [roteiro de 11 slides](../analysis/reports/roteiro_video.md), notebook e materiais em `analysis/slides/`. A revisão textual mais recente do roteiro não regenerou todos os materiais anteriores. É necessário alinhar versões, confirmar contribuições reais de dois integrantes, ensaiar e gravar até 10 minutos. Não há base para fabricar participação individual, vídeo, submissão ou aprovação de requisitos. Essas pendências não são preenchíveis com números simulados.

## O que a nova pasta resolve e o que permanece real

| Pendência | Artefato sintético disponibilizado | Ação necessária para conclusão real |
| --- | --- | --- |
| Formato de calibração A/B e ambos os sentidos | 120 pings, 44 iperfs e 20 saltos de rota | Executar ferramentas na sessão CORE e preservar saídas, parâmetros e versão |
| Janela comum e goodput | 396 rodadas com liberação/fim e bytes | Instrumentar coletor, registrar relógio comum e recolher campanha necessária |
| Destino PUT e sobrescrita | Hashes virtuais e modo overwrite explícito | Testar arquivo preexistente e comparar SHA-256 no servidor fora da janela |
| Falhas, truncamento e registros inválidos | Seis casos negativos com resultado esperado | Integrar ao pipeline de análise e executar casos funcionais reais |
| Estatística por rodada | 108 linhas de resumo, IC Student e dois gráficos | Harmonizar consumidores e validar inferências apenas com dados adequados |
| Cache/CPU/memória/I/O | 396 linhas ilustrativas | Monitorar o host e registrar política, escopo e intervalo |
| Divergências HEAD/erros PUT | Descrição nesta revisão | Revisar código e executar testes específicos em tarefa própria |
| Contribuições, vídeo e submissão | Nenhum dado fictício criado | Confirmar participação, montar, gravar e entregar |

Pasta: [tests/fixtures/pendencias_simuladas](../tests/fixtures/pendencias_simuladas/README.md). Os dados não completam retrospectivamente medições ausentes. Nenhum requisito real foi encerrado por simulação.

## Sequência prática para registrar corretamente as medições

1. Resolver divergências de implementação e executar testes de protocolo/integridade, com logs ligados ao commit. Manter a campanha antiga intacta.
2. Identificar novo `campaign_id`, revisão, alterações locais, binários/hashes, matriz, versões, hardware, contêiner e parâmetros CORE. Fixar cache, persistência e modo PUT. Usar nova pasta de campanha, sem sobrescrever tentativas.
3. Validar a sessão: seis nós, rotas nos dois sentidos, perda/erro configurados em zero e `tc` nos dois lados do gargalo. Salvar saídas completas, data e comandos. A verificação de ferramentas não substitui essa etapa.
4. Calibrar A/B nos dois sentidos com ping, traceroute e iperf3, registrando duração, aquecimento omitido e taxa recebida. Distinguir atraso de um sentido, RTT, taxa nominal e taxa útil medida. Definir tolerâncias e política de repetição antes dos resultados.
5. Usar barreira do coordenador; registrar liberação, início/fim de cada worker, timeouts totais, exit code, stdout/stderr, tamanho e status. Guardar timestamps UTC reais de início/fim para rastreio e monotônicos para durações; não subtrair monotônicos de hosts diferentes.
6. Verificar conteúdo fora da janela de desempenho: entrada e destino GET/PUT, tamanho e SHA-256. Em PUT de sobrescrita, preparar o arquivo anterior antes da rodada e preservar prova da substituição. Evitar que verificações concorrentes contaminem as rodadas de desempenho.
7. Preservar falhas e tentativas repetidas, identificar workers esperados/observados, duplicatas e rodadas parciais. Registrar recursos e excluir/contabilizar cada rodada por regra prévia, nunca convertendo falha em sucesso com taxa zero.
8. Analisar células equivalentes, usando rodada como unidade de IC; mostrar n, falhas e proveniência. Para saturação, usar bytes por janela comum e calibração, explicando que a taxa inclui os custos definidos para a operação. Não somar taxas individuais.
9. Só então substituir hipóteses ilustrativas por evidências novas, alinhar relatório/notebook/slides e concluir a entrega com as contribuições confirmadas.

## Validação desta revisão

- Inventário `all`: retorno 1; perfil `analysis` no venv: retorno 0. `core_runtime_validated=false`.
- Inspeção estática do histórico, contratos, fontes, scripts e XMLs; contagem dos JSONs ativos. Testes C, tráfego e calibração CORE não executados nesta tarefa.
- Geração e verificação das fixtures pelos comandos do README próprio. Essas verificações avaliam coerência sintética, não o desempenho ou a correção funcional da aplicação.
- Nenhuma alteração de protocolo, fonte C, matriz, XML, dado bruto, notebook, roteiro ou PDF nesta tarefa. As alterações locais anteriores foram preservadas; sem commit ou push.
