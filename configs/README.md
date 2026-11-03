# Configurações

`experiment_plan.csv` é uma **proposta de planejamento**, não um arquivo de resultados ou uma campanha aprovada. Suas 36 células representam a alternativa conservadora GET/PUT/HEAD do guia.

| Coluna | Significado |
| --- | --- |
| `scenario_id` | Identificador único da célula |
| `profile` | A (fibra simplificada) ou B (4G simplificado) |
| `bandwidth_mbps` | Capacidade configurada por sentido, em Mbit/s |
| `delay_oneway_ms` | Atraso configurado em cada sentido, em ms |
| `operation` | GET, PUT ou HEAD |
| `workload` | Aplicação representada pelo tamanho |
| `file_size_bytes` | Tamanho do recurso; em HEAD não é tamanho de corpo transferido |
| `concurrency` | Requisições liberadas por rodada |
| `repetitions` | Rodadas medidas, excluindo aquecimento |
| `planning_status` | `proposed` até o piloto e congelamento |

A usa 100 Mbit/s e 5 ms por sentido; B usa 20 Mbit/s e 20 ms. Esses números são escolhas simplificadas de modelagem, não valores universais das tecnologias.

Antes de T11, T10 deve revisar a viabilidade, justificar os representantes de carga/tecnologia e registrar o congelamento da matriz. O coletor deverá ler ou validar esta matriz; a simples existência do CSV não automatiza a configuração do CORE. Para HEAD, a vazão de conteúdo é não aplicável.
