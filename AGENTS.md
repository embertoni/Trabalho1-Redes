# Instruções para agentes de IA

Estas instruções se aplicam ao repositório inteiro. A finalidade é desenvolver e avaliar a aplicação do enunciado com mudanças pequenas, reproduzíveis e verificáveis.

## Contexto e ordem de leitura

Antes de editar, leia `README.md`, `docs/STATUS.md`, a tarefa relevante em `docs/PLANO_DESENVOLVIMENTO.md` e `docs/DECISOES.md`. Consulte a seção correspondente de `docs/GUIA_COMPLETO_TRABALHO1_REDES.md` e, para exigências acadêmicas ou dúvidas de interpretação, o enunciado em `docs/referencias/`.

O enunciado e esclarecimentos documentados do professor são a referência dos requisitos. O guia revisado propõe implementação e método experimental; suas sugestões não são novas exigências do professor. O PDF do guia original tem defeitos documentados e não deve ser tratado como implementação de referência validada.

## Primeira ação obrigatória: verificar o ambiente

Em todo clone novo, no início de cada sessão de trabalho e sempre que trocar de máquina, distribuição, contêiner ou ambiente Python, execute o inventário completo **antes de implementar ou executar o trabalho**:

- Linux/WSL/contêiner: `bash scripts/check-environment.sh --profile all --json build/environment-all.json`.
- Windows/PowerShell: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-environment.ps1` (executa na distribuição WSL padrão; use `-Distribution` para escolher outra).
- Sem WSL utilizável: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-environment.ps1 -Native` produz um diagnóstico nativo, mas não aprova Linux/CORE.

Se Python ou WSL nem puderem iniciar, a mensagem do launcher já é uma pendência: não pule a verificação. Leia `docs/AMBIENTE.md`, informe o que falta e prepare as ferramentas dentro do escopo/permissões disponíveis. O diagnóstico não instala nada automaticamente. Após qualquer correção, repita-o no ambiente em que os programas realmente vão rodar. Não reutilize o relatório de outra máquina como prova de disponibilidade local.

O perfil `all` deve sempre ser tentado primeiro. Se houver pendências, execute o perfil da tarefa (`dev`, `core` ou `analysis`) e só prossiga com ações dependentes quando esse perfil retornar 0. Documentação e outras ações independentes podem continuar com as pendências registradas. Não instale CORE no Windows nativo para contornar o erro de ambiente. Na rota Docker, verifique também o host com `--profile dev --require-docker` e repita o inventário dentro do contêiner CORE. Em Python separado para análise, execute também o perfil `analysis` dentro do venv ativo.

Informe o resultado na passagem de contexto. `tools_ready=true` só comprova os checks de ferramentas do perfil, não valida a emulação. Antes de T07/T10/T11, ainda é necessário criar a sessão CORE e validar nós, rotas, gargalo e tráfego nos dois sentidos. O relatório sempre mantém `core_runtime_validated=false`.

## Escopo e continuidade

- Atenda ao pedido atual do usuário. Não implemente todo o trabalho quando o pedido for apenas organização, revisão ou uma tarefa específica.
- Verifique `git status --short` antes de mudar arquivos. Preserve alterações existentes e os documentos de referência.
- Escolha tarefas pelos pré-requisitos do plano. Mantenha o estado real; não marque algo como concluído por haver apenas um esqueleto, comentário ou plano.
- Faça escolhas rotineiras dentro do escopo autorizado e registre decisões que afetem interface, protocolo ou metodologia.
- A ambiguidade de GET/PUT/HEAD está em `docs/DECISOES.md`. Sem esclarecimento novo, use a proposta conservadora ali descrita sem apresentá-la como ordem do professor.
- Se houver vários agentes atuando, distribua arquivos e responsabilidades sem sobreposição. Combine interfaces antes de mudanças dependentes e não sobrescreva trabalho alheio. Não inicie delegação apenas por existir este documento.
- Não faça commit, push, publicação ou submissão acadêmica sem autorização correspondente do usuário.

## Contratos de implementação

- Aplicação em C com API de sockets POSIX, destinada ao Linux/CORE. Python é permitido em testes, automação e análise, não como substituto do servidor/cliente C.
- Fontes e cabeçalhos em `src/`; binários em `build/`. O Makefile da raiz é o ponto de compilação.
- Planejamento inicial: `server.c`, `client.c`, `protocol.c` e `protocol.h`; módulos extras são permitidos quando tiverem responsabilidade clara.
- Referência de interface: seção 4 do guia. Ao executar no repositório, use `build/server` e `build/client`; adapte os scripts do guia que usam `./server` e `./client`.
- Documente o subconjunto de HTTP antes de implementá-lo. GET/PUT, sobrescrita, atendimento simultâneo e resposta com código em caso de erro são essenciais.
- Trate mensagens parciais, arquivos binários, tamanhos inválidos, desconexão e limites. Não assuma uma mensagem por `send/recv`.
- Use temporários únicos por operação e publicação atômica. PID não identifica uma thread. Não serialize transferências inteiras com um lock global.
- Mantenha stdout do cliente para uma linha JSON por tentativa, inclusive falhas; diagnósticos em stderr. Preserve o contrato de campos e métricas da seção 4 do guia.
- Use relógio monotônico e registre explicitamente os limites da medição. Falha não é amostra de sucesso com vazão zero.
- Não introduza frameworks, serviços ou dependências sem necessidade do trabalho.

## Experimentos e evidências

- CORE é obrigatório para os resultados emulados. Testes em localhost são funcionais, não evidência da topologia.
- Cliente e servidor ficam em acessos distintos, com núcleo e um enlace de gargalo. Não configure erro/perda.
- Calibre os dois sentidos e preserve parâmetros, versões, rotas, ping, traceroute e iperf.
- Diferencie célula, rodada independente e requisição concorrente. Para os ICs, não trate clientes da mesma rodada como repetições independentes.
- Preserve dados brutos e falhas. Separe simulações de ferramentas dos dados reais: resultados simulados vão em `tests/fixtures/` ou pasta temporária, nunca na campanha real.
- Não fabrique resultados, referências, contribuições individuais ou aprovação de requisitos. Só declare execução ou teste que de fato ocorreu.
- Use a matriz versionada em `configs/`; registre qualquer alteração antes de coletar novamente.

## Validação proporcional

Para código C, compile com os avisos do Makefile e execute os testes relevantes disponíveis. Corrija avisos causados pela mudança. Para protocolo e concorrência, valide conteúdo e falhas, não apenas o exit code. Para análise, confira unidades, agrupamento, falhas, n e origem dos dados.

Para documentação e configuração, confira links, caminhos e coerência com as interfaces. Não crie testes artificiais que apenas repitam texto da implementação. Não declare testes aprovados se o executor não existe ou não encontra casos.

Se uma ferramenta ou ambiente não estiver disponível, registre o comando não executado e a limitação. Windows sem GCC/CORE não permite afirmar que o aplicativo foi validado.

## Passagem de contexto e comunicação

Escreva explicações, documentação e relatos em português; identificadores de código podem usar inglês. Ao concluir uma tarefa de desenvolvimento, atualize seu estado no plano e `docs/STATUS.md` com:

1. Mudança concreta e arquivos afetados.
2. Decisões/contratos alterados, se houver.
3. Comandos de validação e resultado real.
4. Limitações e próximo passo disponível.

Mantenha o registro curto. Não copie históricos de conversa inteiros e não apresente implementação futura como funcionalidade pronta.
