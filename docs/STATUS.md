# Estado e passagem de contexto

Atualizado em 05/11/2026.

## Materiais dos slides no notebook — 05/11/2026

- Acrescentadas 26 células ao fim de `analysis/analise_resultados.ipynb`, preservando o conteúdo das 17 anteriores. Total: 43 células, 25 Python. Cada slide do roteiro tem bloco identificado, geração de conteúdo e instruções. Atualizados `analysis/README.md` e T13 no plano, mantida parcial: gravação e montagem final pendentes.
- Gerados em `analysis/slides/`: 16 visuais em PNG 2560×1440 e SVG, tabelas CSV, instruções por slide com trechos do roteiro, exemplos reais de JSON, arquitetura Mermaid e índices/manifastos. São 65 arquivos, separados em 11 pastas e arquivos comuns. Parâmetros XML A/B conferidos contra a matriz; gráficos e IC95% reutilizam as estatísticas por rodada. Nenhum protocolo, dado bruto, fonte C ou XML foi alterado nesta tarefa.
- Geração de slides ativada por `GERAR_ARQUIVOS_SLIDES=True`, independente de `EXPORTAR`. Nomes e contribuições ficam como placeholders/proposta, configuráveis; instruções de gravação explicam o que não pode ser gerado no notebook. Não foram produzidos vídeo, narração, captura CORE nem evidências experimentais ausentes.
- Ambiente: inventário `all` no WSL retornou 1 (CORE e bibliotecas ausentes no Python de sistema); perfil `analysis` no venv existente retornou 0. Nenhuma dependência instalada nesta tarefa; runtime CORE não validado.
- Validação: execução integral via nbclient/kernel do venv (`build/execute_notebook.py`) sem erros; nbformat válido; fontes das 17 células originais comparadas e preservadas. `build/verify_slide_assets.py` conferiu hashes dos 64 arquivos listados, dimensão/integridade dos 16 PNGs, parsing dos SVGs, links do índice e médias/ICs das tabelas GET de destaque contra JSONs brutos. Inspeção visual de todos os visuais em folhas de contato aprovada. `git diff --check` executado.
- Limites/próximo passo: montar os slides com os materiais gerados, confirmar nomes/contribuições, gravar demonstração real e ensaiar 9min40s. Goodput agregado, calibração por sentido e hash do destino PUT continuam sem evidência suficiente; T09 continua sem a suíte de fixtures da análise.

## Comentarios do servidor — 05/11/2026

- Revisao documental de `src/server.c`: bloco inicial sobre renomeacoes internas e mudancas de formatacao que preservam a logica; comentarios concisos nas funcoes e nos blocos de CLI, rede, arquivos, erros, PUT/GET/HEAD e threads. Nenhuma linha original removida, alterada ou reordenada; interfaces, constantes e chamadas preservadas.
- `all` no WSL retornou 1 (CORE e bibliotecas de analise ausentes no Python de sistema); `dev` retornou 0. `make build` compilou e ligou o servidor sem avisos. Comparacao `gcc -D_POSIX_C_SOURCE=200809L -Isrc -std=c11 -E -P src/server.c` antes/depois produziu conteudo identico; `git diff --check` conferido.
- Sem mudanca de contrato ou correcao funcional. O comentario de HEAD descreve o comportamento atual (comprimento anunciado zero), sem afirmar conformidade com o cabecalho GET previsto no guia. Nao foram repetidos testes de transferencia ou campanha CORE; a equivalencia verificada e do codigo pre-processado.
- Documentacao solicitada concluida; T04 nao e marcada como validacao funcional completa. Proximo passo disponivel: revisar/testar divergencias funcionais em tarefa propria, se solicitado.

## Roteiro do vídeo — 05/11/2026

- Reescrito `analysis/reports/roteiro_video.md`: 11 slides, conteúdo visual e falas, duração planejada de 9min40s, contribuições propostas para dois integrantes e autoavaliação. Proposta de divisão deve ser ajustada à participação real; nenhuma contribuição foi tratada como fato comprovado.
- Exemplos numéricos conferidos nos JSONs da campanha ativa, coerentes com o notebook. Mantidas as limitações de hash do destino PUT, calibração e janela agregada. XMLs confirmam A=100 Mbit/s/5 ms e B=20 Mbit/s/20 ms por sentido como parâmetros configurados.
- Validação documental: 11 intervalos contínuos somam 580 segundos; links locais conferidos; `git diff --check`. Inventário `all` repetido no WSL retornou 1 por ausência de CORE e bibliotecas no Python de sistema; tarefa documental independente, sem executar análise ou tráfego.
- T13 permanece pendente: roteiro não equivale a slides montados, vídeo gravado ou submissão. Próximo passo: ajustar nomes/contribuições, preparar os visuais, ensaiar e gravar.

## Atualização de análise — 05/11/2026

- T09 parcial: criado `analysis/analise_resultados.ipynb` (17 células, 12 Python), com saídas executadas, leitura dos JSONs brutos, manifesto SHA-256, cobertura da matriz, falhas, hashes, estatísticas por rodada, IC95% de Student, gráficos e comparações A/B. Atualizados `analysis/README.md`, `analysis/requirements-notebook.txt` e o estado de T09 no plano. Não foi reavaliada a conclusão das outras tarefas; os registros antigos abaixo descrevem a preparação e estão desatualizados quanto à existência de fontes e dados.
- Dados efetivamente lidos: 5.412 requisições, 396 rodadas, 36 células, 11 rodadas completas por célula; zero falhas detectadas de telemetria ou hashes GET divergentes. B teve maior latência em 18/18 comparações equivalentes e menor vazão individual em 12/12 comparações GET/PUT.
- Decisões: protocolo e matriz preservados. Notebook não usa soma de taxas como goodput agregado, não usa workers como repetições independentes e mantém HEAD sem vazão. PUT permanece condicionado à telemetria, pois falta hash do destino. Campanhas de backup não são concatenadas.
- Ambiente: launcher PowerShell falhou na conversão do caminho WSL; inventário direto `wsl -d Ubuntu --cd /home/ember/projetos/Trabalho1-Redes bash scripts/check-environment.sh --profile all --json build/environment-all.json` retornou 1 (CORE e bibliotecas ausentes no Python de sistema). No venv existente, `.venv-analysis/bin/python scripts/check_environment.py --profile analysis --json build/environment-analysis.json` retornou 0. Instalados nbformat, nbclient e ipykernel somente nesse venv; versões de análise registradas no notebook. `core_runtime_validated=false`.
- Validação: todas as células Python compiladas; `nbformat.validate` aprovado; execução integral por `nbclient` com kernel do venv via script temporário `build/execute_notebook.py` aprovada e saídas salvas. Python 3.14.4, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1 e matplotlib 3.11.2. Nenhuma campanha ou tráfego CORE executado nesta sessão.
- Remoto: `git ls-remote origin` consultado; HEAD e `refs/heads/main` iguais ao HEAD local `2ba1776dc8331c80a1eb91f3bd33f5f7ed8987ed`. Sem merge, pull, commit ou push. Preservados os dois arquivos não rastreados preexistentes em `docs/`.
- Limites/próximo passo: T09 continua parcial, sem suíte de fixtures de análise. Preservar janela monotônica comum, hashes de destino PUT e calibração ping/traceroute/iperf por sentido antes de concluir saturação ou T12. A análise antiga e seus artefatos foram preservados.

## Concluído

- Leitura e comparação documental dos dois PDFs.
- Guia revisado, com problemas encontrados, roteiro e exemplos de coleta/análise.
- Organização das referências em `docs/referencias/`.
- Estrutura inicial, instruções para agentes, plano, decisões e matriz proposta.
- Makefile preparado para a futura aplicação, sem fontes artificiais ou implementação vazia.
- Diagnóstico obrigatório de ferramentas com launchers Linux/WSL/PowerShell, relatório JSON local e perfis `all`, `dev`, `core` e `analysis`.
- Verificação recorrente T00 nas instruções dos agentes; `make build` exige perfil `dev`. A lista inicial de dependências de análise está em `analysis/requirements.txt`.

## Ainda não implementado ou executado

- Servidor e cliente C; biblioteca de protocolo.
- Executor de testes da aplicação e integração dos scripts de coleta/análise do guia. Os testes do diagnóstico de ferramentas já existem separadamente.
- Instalação/validação do CORE neste ambiente.
- Topologia executável, calibração e campanha.
- Resultados reais, gráficos e vídeo.

O guia contém exemplos de ferramentas já verificados em revisão anterior, mas ainda não integrados como programas neste repositório. Eles não constituem uma aplicação pronta.

## Próximo passo

Começar pela verificação T00 no Linux/WSL/contêiner que será usado, conforme `docs/AMBIENTE.md`. Depois, T01: formalizar o contrato de protocolo e interfaces a partir do guia e das decisões. T07 pode ser investigada independentemente, conforme o pedido do usuário.

## Validação da preparação

Os documentos originais foram movimentados com comparação de SHA-256. A validação estática via `python -X utf8 -` conferiu links locais e blocos de 13 arquivos Markdown, UTF-8/LF, receitas com tabs no Makefile e as 36 combinações únicas da matriz (396 rodadas e 5.412 requisições). Todos esses checks passaram.

`git check-ignore build/server client-data/test.bin .env` confirmou a exclusão dos artefatos e configurações locais previstos. Na preparação anterior ao commit inicial, `git status --short` confirmou que os arquivos ainda não eram rastreados. Compilação C, execução do GNU Make e execução CORE não foram realizadas; GCC e GNU Make não foram encontrados diretamente no PowerShell durante a preparação.

## Cuidados para a próxima sessão

- Consulte `git log -1 --oneline` e `git status --short` para verificar a revisão e as alterações locais da sessão. Relatórios em `build/` e caches são locais e não integram os commits.
- Os scripts do guia usam `./client`/`./server`; integrar com `build/client`/`build/server`.
- Não iniciar coleta enquanto integridade, metodologia e calibração estiverem pendentes.

## Diagnóstico de ferramentas nesta sessão

- O inventário `all` foi executado diretamente por Python e pelo launcher PowerShell com `-Native`; retornou **1**, corretamente indicando que este Windows nativo não é o ambiente POSIX/CORE exigido.
- Git, Python, pip, venv/ensurepip, numpy, pandas e matplotlib foram encontrados no Python atual. SciPy está ausente. GCC, GNU Make, ferramentas de rede Linux e CORE não foram encontrados como ferramentas utilizáveis neste ambiente. O alias de Bash localizado pelo PATH não executou.
- Docker foi apenas localizado como auxiliar; seu daemon não foi consultado. Nenhum pacote foi instalado, daemon iniciado ou rede alterada.
- O relatório atual está em `build/environment-all.json`, ignorado pelo Git. Ele não comprova nada sobre uma distribuição WSL ou contêiner que não tenha sido examinado.
- A sintaxe do launcher PowerShell foi validada com o parser nativo e a do launcher Bash com `bash -n` do Git for Windows. Isso não equivale à execução da rota WSL.
- A compatibilidade sintática Python 3.10 foi conferida para o diagnóstico e seus testes. O exemplo de hash no guia passou a usar leitura por blocos, compatível com esse mínimo, em lugar de `hashlib.file_digest`.
- `python -X utf8 -m unittest discover -s tests -p test_environment.py -v`: **28 testes aprovados**, cobrindo ausência/falha de comandos, timeout, compilação/execução simuladas, versões de iproute2, perfis, daemon Docker exigido por opção, importações e relatório. Os cenários simulados não são execução real do CORE.
- Links locais e blocos Python da documentação foram conferidos. Compilação C real, execução do Make e validação funcional CORE continuam pendentes.
