# Decisões e ambiguidades

Este registro distingue exigências, propostas iniciais e esclarecimentos confirmados. As propostas abaixo orientam a implementação na ausência de nova informação; ainda precisam ser detalhadas em T01. Nenhum esclarecimento do professor foi registrado até agora.

| ID | Estado | Tema | Diretriz e motivo |
| --- | --- | --- | --- |
| D01 | Exigência | Linguagem e ambiente | Sockets em C; resultados experimentais no CORE. Windows é ambiente de edição, não substituto do Linux/CORE. |
| D02 | Proposta inicial | Transporte e concorrência | TCP e threads POSIX por conexão, com recursos próprios por atendimento. |
| D03 | Proposta inicial | Protocolo | Subconjunto documentado de HTTP com comprimento explícito e conexão encerrada por operação, conciliando a nomenclatura HTTP do enunciado. Não alegar conformidade completa. |
| D04 | Ambiguidade com proposta conservadora | Operações | GET/PUT são explícitos. A seção 2.2 do enunciado contém redação ambígua sobre haver apenas dois métodos. Incluir HEAD como extensão conservadora até eventual esclarecimento; não apresentá-lo como método expressamente exigido. |
| D05 | Proposta inicial | Arquivos | Nomes remotos planos confinados à raiz; temporários únicos e publicação atômica. Sobrescrita obrigatória; política para PUTs do mesmo nome documentada. |
| D06 | Proposta inicial | CLI e telemetria | Interface da seção 4 do guia; cliente com uma linha JSON por tentativa e diagnósticos em stderr. Executáveis locais em `build/`. |
| D07 | Proposta inicial | Matriz | Perfis A/B, 2/10 MiB, concorrência 1/8/32 e 11 rodadas; ver `configs/experiment_plan.csv`. Revisar no piloto antes de congelar. |
| D08 | Proposta inicial | Inferência estatística | Rodada como unidade independente; falhas separadas; vazão útil individual e agregada identificadas. |
| D09 | Convenção do repositório | Artefatos | Código versionado; binários/arquivos de carga ignorados; CSV, JSON e logs de evidência não são ignorados globalmente. |
| D10 | A detalhar em T01/T10 | Cache, persistência e tempo | Guia recomenda aquecimento uniforme, relógio monotônico, conexão incluída e fsync no PUT; formalizar as fronteiras e manter política idêntica na campanha. |
| D11 | Convenção do repositório | Verificação de ferramentas | Inventário `all` obrigatório em cada clone/sessão e troca de ambiente; perfis para ações dependentes; `make build` exige `dev`; sem instalação automática nem alegação de CORE validado. |

## Registro de alterações

Ao alterar uma decisão, registre data, justificativa, origem da informação e arquivos/consumidores afetados. Uma confirmação real do professor deve identificar o esclarecimento sem inventar aprovação. Alterações por critério técnico do grupo devem ser identificadas como escolhas do grupo.
