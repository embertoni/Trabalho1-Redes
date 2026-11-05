# Plano de desenvolvimento

Este plano organiza trabalho para pessoas e agentes de IA. A preparação do repositório está concluída; as tarefas de implementação abaixo estão **a fazer**. Use `docs/STATUS.md` para a passagem de contexto. Não há necessidade de executar todas as tarefas em uma única solicitação.

## Ordem e critérios de conclusão

| ID | Estado | Dependências | Escopo e arquivos principais | Concluído quando |
| --- | --- | --- | --- | --- |
| T00 | Ferramenta pronta; verificação recorrente | Nenhuma | `scripts/check_environment.py`, launchers e `docs/AMBIENTE.md` | Em cada clone/sessão, inventário `all` executado no ambiente real; pendências registradas e perfil da tarefa aprovado antes das ações dependentes |
| T01 | A fazer | Nenhuma | Formalizar protocolo e CLI em `docs/CONTRATO_PROTOCOLO.md`; atualizar decisões | Enquadramento das mensagens, códigos, limites, HEAD, JSON, medição e falhas definidos sem contradições |
| T02 | A fazer | T01 | `src/protocol.h`, `src/protocol.c` | Parsing e I/O parcial implementados; entradas inválidas e arquivos binários cobertos por testes relevantes |
| T03 | A fazer | T01 | Executor e casos em `tests/`; integração ao Makefile | Comando documentado executa casos reais, detecta falhas e falha quando casos obrigatórios estiverem ausentes |
| T04 | A fazer | T02 | `src/server.c` | Atendimento concorrente, GET/PUT e HEAD proposto; integridade, temporários e erros validados |
| T05 | A fazer | T02 | `src/client.c` | CLI e JSON compatíveis com contrato; operação completa cronometrada; falhas e sobrescrita validadas |
| T06 | A fazer | T03, T04, T05 | Integração funcional em localhost | Casos da seção 4.5 do guia aprovados, incluindo interrupções, sobrescrita e concorrência |
| T07 | A fazer | Nenhuma | `topology/` e ambiente Linux | Sessão CORE reproduzível com endereços, rotas, acessos e núcleo; A/B calibrados em ambos os sentidos |
| T08 | A fazer | T01, T06 | `scripts/` e formatos de CSV | Coleta adaptada a `build/client`; barreira, logs, hashes, timeouts e requisições/rodadas verificados com testes do coletor |
| T09 | Parcial: notebook executado; fixtures pendentes | T01 | `analysis/` | Processamento e gráficos isolam fatores, preservam falhas e usam rodada como unidade de IC; validados com fixtures identificadas |
| T10 | A fazer | T06, T07, T08 | Piloto e `configs/` | Tempos/recursos estimados, metodologia estabilizada e matriz congelada com justificativas |
| T11 | A fazer | T09, T10 | Campanha em `experiments/` | Todas as células executadas com repetições, integridade e evidências; falhas e novas tentativas preservadas |
| T12 | A fazer | T11 | Resultados e discussão | Estatísticas, gráficos, limites, gargalos e saturação sustentados pelos dados |
| T13 | Parcial: roteiro e materiais de slides gerados; vídeo pendente | T12 | Documentação e entrega | README reproduzível, código revisado, vídeo até 10 min, contribuições/autoavaliação e checklist completo |

T03 pode começar com os contratos e crescer junto dos módulos; seus casos de integração só serão executáveis após T04/T05. T07 pode ser investigada independentemente dos fontes. T09 pode usar fixtures sintéticas explicitamente identificadas antes da campanha. A disponibilidade dessas frentes não é uma ordem para criar agentes paralelos.

Em 05/11/2026, a documentacao interna de `src/server.c` foi revisada com comentarios, sem alterar o codigo pre-processado. Essa atividade esta concluida no escopo solicitado; nao substitui os criterios funcionais de T04. Validacao e limites em `docs/STATUS.md`.

## Como trabalhar em uma tarefa

1. Execute T00, confira o estado do Git, o contexto atual e as dependências. A disponibilidade das ferramentas é local: a ferramenta de verificação pronta não significa que todas as máquinas estejam preparadas.
2. Identifique arquivos de responsabilidade e contratos compartilhados.
3. Marque a tarefa como em andamento quando realmente começar.
4. Implemente o mínimo necessário e valide comportamento relevante.
5. Atualize documentação afetada, estado da tarefa e passagem de contexto.

Não modifique protocolo ou schema silenciosamente durante uma tarefa de coleta/análise. Mudanças de contrato exigem revisar seus consumidores.

## Passagem de contexto

Ao encerrar uma sessão de desenvolvimento, acrescente ou atualize em `STATUS.md`:

```text
Tarefa:
Estado:
Arquivos alterados:
Decisões:
Validação executada e resultado:
Limitação ou dependência:
Próximo passo:
```

Se várias pessoas/agentes estiverem trabalhando, registrem responsáveis e arquivos antes de editar. Prefiram responsabilidades separadas, como protocolo, aplicação, testes e análise. Só integrem trabalhos dependentes depois de conferir os contratos e as validações.
