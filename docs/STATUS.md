# Estado e passagem de contexto

Atualizado em 03/11/2026.

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
