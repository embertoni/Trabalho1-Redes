# Relatório inicial da campanha experimental

## Escopo

Os dados foram consolidados a partir de `experiments/raw/json`. A unidade estatística usada nas comparações é a rodada `(scenario_id, repetition)`; workers concorrentes não são contados como repetições independentes.

## Cobertura

- Observações individuais: 5412
- Observações individuais válidas: 5412
- Observações individuais com falha: 0
- Rodadas agregadas: 396
- Células da matriz: 36

## Interpretação

`time_mean_ms` e `throughput_mean_mbps` são médias dos workers bem-sucedidos da rodada. `throughput_aggregate_mbps` é a soma das vazões individuais e deve ser usada separadamente para discutir saturação. HEAD é mantido na tabela, mas sua vazão de conteúdo é não aplicável.

## Arquivos gerados

- `analysis/data/individual.csv`: uma linha por worker.
- `analysis/data/rounds.csv`: uma linha por rodada independente.
- `analysis/tables/cells.csv`: estatísticas por célula da matriz.
- `analysis/reports/analysis_report.md`: este relatório.
- `analysis/figures/`: gráficos gerados, quando matplotlib estiver disponível.
