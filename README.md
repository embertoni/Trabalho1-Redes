# Trabalho 1 - Redes de Computadores

Aplicação cliente-servidor de arquivos em C e avaliação de desempenho no CORE.

**Estado atual:** repositório preparado para desenvolvimento. Servidor, cliente, testes automatizados e campanha experimental ainda não foram implementados. O prazo registrado no enunciado é 05/11/2026.

## Comece aqui

1. Leia as [instruções para agentes](AGENTS.md).
2. Execute a [verificação obrigatória do ambiente](docs/AMBIENTE.md) e resolva as pendências necessárias para sua tarefa.
3. Consulte o [enunciado](docs/referencias/trabalho1_redes_enunciado.pdf) e o [guia completo revisado](docs/GUIA_COMPLETO_TRABALHO1_REDES.md).
4. Escolha uma tarefa disponível no [plano de desenvolvimento](docs/PLANO_DESENVOLVIMENTO.md), observando dependências.
5. Consulte as [decisões e ambiguidades](docs/DECISOES.md) e o [estado do projeto](docs/STATUS.md).
6. Implemente, valide no ambiente apropriado e registre a passagem de contexto.

O guia em PDF original está em [docs/referencias](docs/referencias/guia_execucao_trabalho1_redes.pdf). Ele contém problemas identificados no guia revisado; não copie seu código sem revisão.

## Organização

| Caminho | Responsabilidade |
| --- | --- |
| `src/` | Servidor, cliente e protocolo em C |
| `tests/` | Testes de protocolo, integração, integridade e concorrência |
| `scripts/` | Preparação, coleta e automação |
| `analysis/` | Estatística e gráficos |
| `configs/` | Matriz de cenários e configurações versionadas |
| `topology/` | Sessões CORE, endereçamento, rotas e parâmetros |
| `experiments/calibration/` | Evidências de ping, traceroute e iperf |
| `experiments/raw/` | Dados brutos e logs identificados por execução |
| `experiments/summary/` | Resultados processados, derivados dos dados brutos |
| `docs/` | Referências, guia, planejamento, decisões e estado |
| `build/` | Binários e objetos gerados, ignorados pelo Git |

## Ambiente e comandos

O desenvolvimento dos sockets POSIX, a compilação e os testes de integração são destinados ao **Linux**, no laboratório, em VM ou WSL com ambiente CORE validado. Editar no Windows é possível; isso não valida o comportamento da aplicação no Linux.

Antes de começar, em todo clone novo e no início de cada sessão de agente:

```bash
# Linux/WSL/contêiner: não requer Make já instalado.
bash scripts/check-environment.sh --profile all --json build/environment-all.json
```

```powershell
# Windows: encaminha a verificação para o WSL padrão.
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-environment.ps1
```

O diagnóstico verifica execução/versões, compila um programa C de prova no Linux, importa as dependências de análise e informa o que falta. Não instala nada automaticamente. Se falhar, não execute ações dependentes antes de corrigir o perfil correspondente. Detalhes de perfis, Docker, venv e limites estão em [AMBIENTE.md](docs/AMBIENTE.md). Ferramentas instaladas não comprovam que o CORE foi calibrado.

O Makefile está preparado para os arquivos planejados `src/server.c`, `src/client.c` e `src/protocol.c`. Ainda não existem fontes para compilar:

```bash
make help
make doctor
# Depois de implementar os fontes, no Linux com GCC e GNU Make:
make build
# Binários esperados: build/server e build/client
make clean
```

Há testes do diagnóstico com `python3 -m unittest discover -s tests -p 'test_environment.py' -v` ou `make test-environment`. A suíte da aplicação continua pendente em T03. Os scripts de coleta/análise impressos no guia também precisam ser integrados e adaptados aos caminhos de `build/` antes de uso.

A [matriz CSV](configs/experiment_plan.csv) contém uma proposta de 36 células, incluindo HEAD como extensão conservadora. Ela não contém medições e deve ser congelada somente após a revisão das decisões e o piloto.

## Entrega

Conforme o enunciado: código(s) do servidor e link de vídeo-relatório de até 10 minutos, com contribuições individuais e autoavaliação. Cliente, testes, dados, scripts e sessão CORE ajudam a reproduzir o trabalho. As pastas de desenvolvimento não representam uma entrega já concluída.
