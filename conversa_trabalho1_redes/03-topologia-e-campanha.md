# Fase 3 — CORE, perfis e campanha experimental

## Integração com CORE

A aplicação foi integrada à topologia CORE. O servidor deveria ser executado no nó `Servidor`, com endereço `10.10.5.10`, e o cliente no nó `Cliente`, com endereço `10.10.1.10`.

Foram definidos testes de:

- conectividade;
- PUT atravessando a topologia;
- GET atravessando a topologia;
- HEAD;
- arquivos binários;
- arquivo inexistente;
- dez transferências simultâneas;
- comparação de SHA-256.

Os arquivos temporários da execução foram organizados como:

```text
Cliente:
/tmp/trabalho1-core/client-data
/tmp/trabalho1-core/client-output

Servidor:
/tmp/trabalho1-core/server-data
```

## Arquivos de calibração

Foi explicado que os arquivos em `experiments/calibration/` são evidências da preparação e validação do ambiente. Eles registram topologia, endereçamento, gargalo, ping, traceroute, iperf3 e execução da aplicação no CORE.

Foram listados como esperados:

```text
experiments/calibration/runtime-minimo.txt
experiments/calibration/topologia-etapa4.txt
experiments/calibration/aplicacao-core.txt
```

Também foram distinguidos os arquivos de código, topologia, dados brutos, análise e artefatos temporários.

## Piloto experimental

A Etapa 11 foi reorganizada para separar claramente o repositório e os nós CORE. Os arquivos de entrada deveriam ser criados diretamente no nó Cliente, especialmente:

```text
/tmp/trabalho1-core/client-data/pilot-2MiB.bin
```

O arquivo do servidor deveria ficar em:

```text
/tmp/trabalho1-core/server-data/pilot-2MiB.bin
```

O resultado do GET deveria ficar em:

```text
/tmp/trabalho1-core/client-output/pilot-2MiB-downloaded.bin
```

O usuário perguntou qual era o caminho de `/caminho/para/pilot-2MiB.bin`; foi esclarecido que era apenas um marcador e que o caminho correto seria `/tmp/trabalho1-core/client-data/pilot-2MiB.bin`.

## Matriz experimental

A matriz real foi apresentada pelo usuário em `configs/experiment_plan.csv` com 36 cenários:

```text
S001–S018: Perfil A
S019–S036: Perfil B
```

Cada cenário tem 11 repetições, totalizando:

```text
36 × 11 = 396 rodadas
```

Os fatores são:

| Fator | Valores |
|---|---|
| Perfil | A e B |
| Vazão | A: 100 Mbit/s; B: 20 Mbit/s |
| Atraso unidirecional | A: 5 ms; B: 20 ms |
| Operação | GET, PUT e HEAD |
| Tamanho | 2 MiB e 10 MiB |
| Concorrência | 1, 8 e 32 |
| Repetições | 11 |

Foi esclarecido que os 396 testes não deveriam ser executados manualmente.

## Automatização

Foi gerado `scripts/run_campaign.py`, que lê a matriz e executa os cenários automaticamente. O script controla perfil, cenário, repetições, concorrência, cliente, servidor, arquivos de entrada e diretórios de resultados.

Comandos principais:

```bash
python3 scripts/run_campaign.py \
  --profile A \
  --scenario S001 \
  --repetitions 1 \
  --client /work/build/client \
  --server-host 10.10.5.10 \
  --server-port 9000 \
  --input-dir /tmp/trabalho1-core/client-data \
  --raw-root /work/experiments/raw \
  --output-root /tmp/trabalho1-core/client-output/campaign
```

Depois do piloto:

```bash
python3 scripts/run_campaign.py \
  --profile A \
  --client /work/build/client \
  --server-host 10.10.5.10 \
  --server-port 9000 \
  --input-dir /tmp/trabalho1-core/client-data \
  --raw-root /work/experiments/raw \
  --output-root /tmp/trabalho1-core/client-output/campaign
```

Para o Perfil B, o mesmo comando utiliza `--profile B`.

O script gera JSON individual por worker, logs, hashes, manifestos e resumo do perfil.

## Modelagem do Perfil B

Foi explicado que o Perfil B deve ser uma cópia do Perfil A, alterando somente o enlace de gargalo entre `R-Nucleo-1:eth1` e `R-Nucleo-2:eth0`.

Valores do Perfil A:

| Campo | Valor |
|---|---:|
| Bandwidth | `100000000` bps |
| Delay | `5000` µs |
| Jitter | `0` |
| Loss | `0.0%` |
| Duplicate | `0%` |
| Buffer | `0` |
| Symmetric Link Effects | habilitado |

Valores do Perfil B:

| Campo | Valor |
|---|---:|
| Bandwidth | `20000000` bps |
| Delay | `20000` µs |
| Jitter | `0` |
| Loss | `0.0%` |
| Duplicate | `0%` |
| Buffer | `0` |
| Symmetric Link Effects | habilitado |

O Perfil B deve preservar os nós, IPs, rotas, redes e conexões. A troca deve ser feita em uma nova sessão CORE.

O arquivo recomendado é:

```text
topology/trabalho1-etapa4-perfil-B.xml
```

## Ordem de execução dos testes

A ordem consolidada foi:

1. compilar no WSL;
2. abrir o CORE;
3. abrir e validar o Perfil A;
4. configurar `100000000` bps e `5000` µs;
5. iniciar o servidor;
6. criar os arquivos de carga no Cliente;
7. preparar os arquivos para GET e HEAD;
8. executar o piloto `S001`;
9. executar `S001–S018`;
10. validar os resultados;
11. parar a sessão;
12. abrir o Perfil B;
13. configurar `20000000` bps e `20000` µs;
14. iniciar nova sessão e servidor;
15. recriar ou disponibilizar as cargas;
16. preparar GET e HEAD;
17. executar o piloto `S019`;
18. executar `S019–S036`;
19. validar 396 manifestos.

O usuário informou que terminou os testes e perguntou pela próxima etapa.
