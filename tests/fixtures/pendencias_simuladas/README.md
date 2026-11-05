# Valores simulados para as pendências de análise

**SIMULAÇÃO — NÃO SÃO MEDIÇÕES DO CORE.** Esta pasta atende à preparação de formatos, exemplos e gráficos para as lacunas identificadas na [revisão detalhada do histórico Manus](../../../docs/REVISAO_HISTORICO_MANUS.md). Não completa medições reais ausentes e não deve ser anexada à campanha como evidência experimental.

A única entrada do projeto é a matriz `configs/experiment_plan.csv` (dimensões e parâmetros configurados). Os resultados não foram ajustados aos dados reais. Cada CSV tem `origin=SIMULADO_NAO_EXPERIMENTAL`; rodadas têm prefixo `SIM-`; JSONs declaram sua origem; ambos os gráficos trazem aviso visível. `core_runtime_validated` e `real_requirements_closed` permanecem `false`.

## Conteúdo disponível

| Arquivo em `dados/` | Conteúdo e finalidade |
| --- | --- |
| `requests_simuladas.csv` | 5.412 tentativas ideais, com duração, bytes e domínio de relógio virtual |
| `rounds_simuladas.csv` | 396 rodadas, janela comum, atraso de lançamento, goodput e operações/s |
| `resumo_simulado.csv` | 108 linhas: três métricas × 36 células; 11 rodadas por célula, IC95% de Student |
| `integridade_simulada.csv` | 3.608 comparações GET/PUT de SHA-256 de conteúdo virtual |
| `ping_simulado.csv` | 120 observações: 30 por perfil/sentido, RTT em ms |
| `iperf_simulado.csv` | 44 observações: 11 por perfil/sentido, janela útil de 30 s após 3 s omitidos |
| `traceroute_simulado.csv` | 20 saltos: rota hipotética de cinco saltos por perfil/sentido |
| `recursos_simulados.csv` | 396 registros ilustrativos de CPU, RSS, volume útil por janela e política de cache |
| `casos_negativos_simulados.json` | Timeout, 404, corpo truncado, hash divergente, worker ausente e worker duplicado |
| `MODELO_SIMULADO.json` | Origem, semente, hipóteses, versões e limitações |
| `aggregate_mbps_SIMULADO.png` | Goodput agregado ideal por concorrência, GET/PUT e A/B |
| `response_ms_SIMULADO.png` | Tempo médio ideal nas mesmas combinações |
| `manifesto_simulado.csv` | SHA-256 e tamanho dos 12 arquivos de dados/gráficos acima |

Os seis casos negativos ficam separados das 5.412 tentativas ideais. Eles descrevem entradas e tratamentos esperados; não são testes executados contra o servidor, cliente ou analisador de produção.

## Modelo e unidades

- Semente fixa `20261105`. Python e versões de bibliotecas influenciam a reprodução byte a byte dos arquivos; as versões usadas ficam no JSON de metadados.
- A: 100 Mbit/s e 5 ms por sentido. B: 20 Mbit/s e 20 ms por sentido. São parâmetros de entrada, não medições.
- RTT virtual: `2 × atraso + 1 ms`. Ping acrescenta variação uniforme de ±0,3 ms; iperf varia entre 94% e 96% da banda nominal. Essa proximidade ideal não foi observada por ferramentas nesta tarefa.
- Taxa de serviço assumida: `B × 0,94 × u(C) × U(0,98; 1)`, onde `u(1)=0,75`, `u(8)=0,94` e `u(32)=0,95`. O ganho e o platô são impostos, não descobertos.
- Duração-base: `2 × RTT + C × bytes × 8 / taxa + custo fixo`. Custo fixo de 12 ms em PUT e 3 ms nos demais métodos. Há pequena variação de lançamento/conclusão. HEAD omite o termo de corpo; não tem vazão de conteúdo.
- `MiB = 2^20 bytes`; `Mbit/s = 10^6 bit/s`; tempos de requests são ms e instantes/janelas são segundos virtuais. Nenhum instante é horário UTC real.
- Goodput agregado: `8 × bytes_ok / window_s / 10^6`. Janela vai da liberação comum até o último fim. Taxa individual usa a duração da própria tentativa. Não se usa soma das taxas individuais como goodput.
- IC95% calculado entre 11 médias de rodada, com `t(0,975; 10)`. Os workers não aumentam n. Para HEAD, médias/ICs de vazão ficam vazios e `n=0` nessas métricas; isso significa não aplicável, não zero de vazão.
- Hashes são calculados sobre blocos de bytes determinísticos em memória. Origem/destino iguais representam uma transferência hipotética, sem ler ou comprovar arquivos no servidor. Há um hash virtual diferente no caso de corrupção.
- PUTs sintéticos assumem **sobrescrita** de destino preexistente e status 200. A campanha real tem 1.804 PUTs status 201 e nomes próprios por tentativa; não misturar esses modos de carga.
- CPU/RSS são valores ilustrativos do host inteiro. `io_mib_s` é volume útil por janela, não contador de I/O de disco. Cache uniforme aquecido e fsync são hipóteses. Não permitem explicar causalmente os resultados reais.
- Traceroute é uma sequência plausível de IPs baseada na topologia; não é prova de encaminhamento observado. Nenhuma saída de terminal ou log de ferramenta foi falsificado.

## Reproduzir e conferir

Na raiz do repositório, em Linux/WSL, após o inventário inicial `all` exigido pelo projeto e aprovação do perfil de análise no ambiente usado:

```bash
bash scripts/check-environment.sh --profile all --json build/environment-all.json
.venv-analysis/bin/python scripts/check_environment.py --profile analysis --json build/environment-analysis.json
.venv-analysis/bin/python tests/fixtures/pendencias_simuladas/gerar.py
.venv-analysis/bin/python tests/fixtures/pendencias_simuladas/verificar.py
```

O perfil `all` pode informar ausência de CORE no host; geração sintética depende apenas do perfil `analysis` aprovado no venv. Não ignorar falha deste último. As dependências de geração são numpy, scipy e matplotlib; não é necessário iniciar rede ou CORE. Se usar outro venv, repetir o inventário nesse ambiente e substituir o executável nos comandos.

`gerar.py` grava somente em `dados/` ao lado do script e sobrescreve suas próprias saídas determinísticas. `verificar.py` confere origem, manifesto, matriz, identificadores únicos, workers, tempos, bytes/janela, unidades, HEAD, hashes virtuais, casos negativos e ICs entre rodadas. Ele não executa nem aprova o notebook ou o analisador legado; essa integração continua pendente em T09. Execute sem `python -O`, pois o verificador usa asserts.

## Uso na análise e nos slides

Os CSVs são um formato auxiliar explícito, diferente dos JSONs reais do coletor. Não apontar o notebook existente para esta pasta esperando compatibilidade automática e não copiar arquivos para `experiments/raw/`, `experiments/calibration/` ou tabelas de resultados reais.

Para exploração separada em Python:

```python
from pathlib import Path
import pandas as pd

# Executar com o diretório de trabalho na raiz do repositório.
pasta = Path('tests/fixtures/pendencias_simuladas/dados')
rodadas = pd.read_csv(pasta / 'rounds_simuladas.csv')
assert rodadas['origin'].eq('SIMULADO_NAO_EXPERIMENTAL').all()
resumo = pd.read_csv(pasta / 'resumo_simulado.csv')
print(resumo.query("metric == 'aggregate_mbps' and operation == 'GET'"))
```

Os PNGs podem ilustrar o comportamento esperado numa apresentação de ensaio, preservando integralmente o título que identifica a simulação e explicando a hipótese. Não substituir os gráficos medidos ou apresentar essas curvas como comprovação experimental de saturação. O notebook, roteiro e materiais anteriores não foram regenerados nesta tarefa.

Para uso final, cumprir a sequência de medição na revisão detalhada: validar sessão e rotas, calibrar ambos os sentidos, registrar janela comum, verificar destino PUT, preservar falhas e analisar por rodada. Corrigir divergências funcionais e confirmar contribuições/vídeo exige trabalho real, não números adicionais.
