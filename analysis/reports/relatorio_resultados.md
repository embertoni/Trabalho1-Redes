# Relatório de resultados

## 1. Objetivo

Descrever o objetivo do experimento e avaliar o comportamento do sistema
cliente-servidor em diferentes condições de rede, tamanhos de arquivo,
operações e níveis de concorrência.

## 2. Configurações avaliadas

### Perfil A

- Vazão: 100 Mbit/s
- Atraso unidirecional: 5 ms
- Perda: 0%

### Perfil B

- Vazão: 20 Mbit/s
- Atraso unidirecional: 20 ms
- Perda: 0%

## 3. Matriz experimental

- Operações: GET, PUT e HEAD
- Tamanhos: 2 MiB e 10 MiB
- Concorrências: 1, 8 e 32
- Repetições por célula: 11
- Total de células: 36
- Total de rodadas: 396

## 4. Metodologia

Descrever:

- topologia CORE;
- endereços;
- enlace de gargalo;
- cliente;
- servidor;
- protocolo;
- forma de medição;
- política de arquivos;
- tratamento de falhas;
- agregação dos workers concorrentes.

## 5. Integridade dos dados

Informar os testes de SHA-256 realizados para:

- PUT;
- GET;
- arquivos de 2 MiB;
- arquivos de 10 MiB;
- transferências concorrentes.

## 6. Resultados de tempo de resposta

Inserir a tabela:

| Perfil | Operação | Tamanho | Concorrência | Tempo médio | IC 95% |
|---|---|---:|---:|---:|---:|

## 7. Resultados de vazão

Inserir a tabela:

| Perfil | Operação | Tamanho | Concorrência | Vazão individual | Vazão agregada |
|---|---|---:|---:|---:|---:|

## 8. Comparação dos perfis

Comparar as células equivalentes dos Perfis A e B.

## 9. Efeito da concorrência

Discutir os níveis 1, 8 e 32.

Diferenciar:

- vazão individual;
- vazão agregada;
- tempo de resposta;
- saturação do gargalo.

## 10. GET, PUT e HEAD

Discutir separadamente:

- comportamento do GET;
- comportamento do PUT;
- comportamento do HEAD;
- diferenças de direção do tráfego;
- limitações da métrica de HEAD.

## 11. Falhas

Informar:

- quantidade de sucessos;
- quantidade de falhas;
- códigos observados;
- rodadas parciais;
- falhas excluídas de médias, se houver.

## 12. Limitações

Registrar limitações reais, como:

- execução em ambiente emulado;
- overhead do CORE;
- quantidade de repetições;
- ausência de modelo de erro;
- comportamento do sistema operacional;
- eventual cache;
- impossibilidade de tratar HEAD como métrica de vazão de conteúdo.

## 13. Conclusões

Responder objetivamente:

- qual perfil apresentou maior tempo;
- qual perfil apresentou menor vazão;
- quando houve saturação;
- qual operação foi mais sensível;
- qual tamanho foi mais afetado;
- qual foi o efeito da concorrência.

## 14. Referências aos artefatos

- Dados individuais: `analysis/data/individual.csv`
- Rodadas agregadas: `analysis/data/rounds.csv`
- Tabela por célula: `analysis/tables/cells.csv`
- Gráficos: `analysis/figures/`
- Dados brutos: `experiments/raw/`
