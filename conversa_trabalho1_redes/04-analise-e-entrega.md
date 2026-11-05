# Fase 4 — análise, documentação e entrega

## Validação dos resultados

Depois da campanha, foi solicitado validar:

```bash
find experiments/raw/manifests -name 'S*.txt' | wc -l
find experiments/raw/json -name 'S*.json' | wc -l
cat experiments/raw/summary-profile-A.json
cat experiments/raw/summary-profile-B.json
```

O esperado era obter 396 manifestos, JSONs válidos e resumos para os dois perfis. Também foi recomendado fazer backup de `experiments/raw` antes da análise.

## Consolidação estatística

Foi gerado `scripts/analyze_results.py`. O script lê os JSONs reais e cria:

```text
analysis/data/individual.csv
analysis/data/rounds.csv
analysis/tables/cells.csv
analysis/reports/analysis_report.md
analysis/figures/
```

A regra estatística adotada é que a unidade experimental é a rodada identificada por:

```text
scenario_id + repetition
```

Os workers concorrentes são agregados dentro da rodada e não são considerados repetições independentes.

As métricas incluem:

- média;
- mediana;
- mínimo;
- máximo;
- intervalo de confiança de 95%;
- vazão média individual;
- vazão agregada;
- número de workers válidos;
- falhas e rodadas parciais.

Foi destacada a necessidade de separar vazão individual de vazão agregada ao discutir saturação.

## Interpretação

A documentação final deve comparar células equivalentes entre os Perfis A e B, mantendo constantes:

- operação;
- tamanho;
- concorrência.

As perguntas de análise são:

- o Perfil B aumenta o tempo;
- o Perfil B reduz a vazão;
- o atraso afeta mais arquivos pequenos;
- a menor vazão afeta mais arquivos grandes;
- GET e PUT apresentam diferenças;
- concorrência aumenta a vazão agregada;
- concorrência aumenta o tempo individual;
- ocorre saturação;
- existem falhas ou rodadas parciais.

HEAD deve ser tratado separadamente, pois não transfere corpo e não possui vazão de conteúdo aplicável.

## Relatório final

Foi orientado criar:

```text
analysis/reports/relatorio_resultados.md
analysis/reports/roteiro_video.md
```

O relatório deve conter objetivo, configurações, matriz, metodologia, integridade, tempo, vazão, comparação dos perfis, concorrência, GET/PUT/HEAD, falhas, limitações e conclusões.

O roteiro do vídeo deve conter introdução, arquitetura, topologia, execução, resultados, saturação, conclusões e contribuições individuais, com duração máxima de 10 minutos.

## Revisão final

A etapa final inclui:

```bash
make clean
make build
/tmp/test_protocol
```

Também foi prevista uma validação funcional curta com PUT, GET, HEAD e SHA-256.

O pacote final deve preservar:

- código do servidor;
- código do cliente;
- protocolo compartilhado;
- testes;
- scripts de campanha e análise;
- topologias;
- contrato do protocolo;
- dados brutos;
- tabelas;
- gráficos;
- relatório;
- roteiro do vídeo.

Devem ser excluídos temporários, `__pycache__`, binários locais e arquivos de sistema quando não forem necessários para a entrega.

## Pacote de entrega

Foi sugerida a criação de:

```bash
tar -czf ~/Trabalho1-Redes-entrega.tar.gz \
  -C /tmp Trabalho1-Redes-entrega
```

O pacote deveria ser conferido com:

```bash
sha256sum ~/Trabalho1-Redes-entrega.tar.gz
```

A entrega principal foi identificada como código do servidor e link do vídeo, com os demais artefatos servindo para reprodução e auditoria.

## Encerramento

O usuário solicitou que toda a conversa fosse escrita em múltiplos arquivos Markdown para download. Este diretório contém o índice e os arquivos organizados por fase.
