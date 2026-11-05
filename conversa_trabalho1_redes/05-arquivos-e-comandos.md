# Comandos e arquivos operacionais consolidados

## Compilação

```bash
cd ~/projetos/Trabalho1-Redes
make clean
make build
```

```bash
/tmp/test_protocol
```

## CORE

```bash
docker start core-trabalho1
docker exec -it core-trabalho1 bash
cd /work
core-gui
```

## Perfil A

```text
Bandwidth: 100000000 bps
Delay: 5000 us
Jitter: 0
Loss: 0.0
Duplicate: 0
Buffer: 0
Symmetric Link Effects: habilitado
```

## Perfil B

```text
Bandwidth: 20000000 bps
Delay: 20000 us
Jitter: 0
Loss: 0.0
Duplicate: 0
Buffer: 0
Symmetric Link Effects: habilitado
```

## Servidor

```bash
/work/build/server \
  --host 10.10.5.10 \
  --port 9000 \
  --root /tmp/trabalho1-core/server-data
```

## GET

```bash
/work/build/client \
  --host 10.10.5.10 \
  --port 9000 \
  --method GET \
  --remote /arquivo.bin \
  --output /tmp/trabalho1-core/client-output/arquivo.bin
```

## PUT

```bash
/work/build/client \
  --host 10.10.5.10 \
  --port 9000 \
  --method PUT \
  --remote /arquivo.bin \
  --input /tmp/trabalho1-core/client-data/arquivo.bin
```

## HEAD

```bash
/work/build/client \
  --host 10.10.5.10 \
  --port 9000 \
  --method HEAD \
  --remote /arquivo.bin
```

## Cargas

```bash
mkdir -p /tmp/trabalho1-core/client-data

dd if=/dev/urandom \
  of=/tmp/trabalho1-core/client-data/workload-2MiB.bin \
  bs=1M count=2 status=progress

dd if=/dev/urandom \
  of=/tmp/trabalho1-core/client-data/workload-10MiB.bin \
  bs=1M count=10 status=progress
```

## Campanha automatizada

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

Para o Perfil B, substitua:

```text
--profile A
```

por:

```text
--profile B
```

## Análise

```bash
python3 scripts/analyze_results.py \
  --raw experiments/raw/json \
  --out analysis
```

## Validações

```bash
find experiments/raw/manifests -name 'S*.txt' | wc -l
find experiments/raw/json -name 'S*.json' | wc -l
```

```bash
sha256sum \
  /tmp/trabalho1-core/client-data/workload-2MiB.bin \
  /tmp/trabalho1-core/server-data/workload-2MiB.bin
```

## Estrutura final

```text
Trabalho1-Redes/
├── docs/
│   └── CONTRATO_PROTOCOLO.md
├── src/
│   ├── client.c
│   ├── protocol.c
│   ├── protocol.h
│   └── server.c
├── tests/
│   └── test_protocol.c
├── topology/
│   ├── trabalho1-etapa4.xml
│   ├── trabalho1-etapa4-perfil-A.xml
│   └── trabalho1-etapa4-perfil-B.xml
├── configs/
│   └── experiment_plan.csv
├── scripts/
│   ├── run_campaign.py
│   └── analyze_results.py
├── experiments/
│   ├── calibration/
│   ├── pilot/
│   └── raw/
└── analysis/
    ├── data/
    ├── figures/
    ├── reports/
    └── tables/
```
