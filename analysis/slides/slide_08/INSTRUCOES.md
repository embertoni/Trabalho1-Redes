# Slide 8 — GET, PUT e HEAD

## Uso dos materiais

Usar comparacao_operacoes.png e sentidos_operacoes.png. operacoes_tempo.csv permite uma tabela editável. A linha HEAD não mede transferência de arquivo nem RTT e não deve receber vazão zero.

## Conteúdo e fala do roteiro

**Adicionar ao slide:** três cartões: GET transfere servidor→cliente; PUT transfere cliente→servidor; HEAD recebe metadados. Exemplo com concorrência 1:

| Operação e tamanho | Tempo A | Tempo B |
| --- | --- | --- |
| GET, 10 MiB | 960,8 ms | 4.729,8 ms |
| PUT, 10 MiB | 1.171,9 ms | 4.814,3 ms |
| HEAD, referência 2 MiB | 22,1 ms | 83,2 ms |

**Fala sugerida — Integrante 1:**

> GET e PUT transferem conteúdo em sentidos opostos e também envolvem custos diferentes de leitura, escrita e confirmação. Com um cliente e arquivo de 10 mebibytes, o PUT levou cerca de 1,17 segundo em A e 4,81 segundos em B. Já o HEAD sobre o arquivo de referência de 2 mebibytes levou aproximadamente 22 e 83 milissegundos. Como HEAD não envia o corpo, seu tamanho de referência não representa bytes transferidos. Por isso, analisamos sua latência e mantemos sua vazão de conteúdo como não aplicável. Esses tempos também não devem ser interpretados como medições de RTT por ping.
