# Análise

Abra [analise_resultados.ipynb](analise_resultados.ipynb) no Jupyter ou VS Code e selecione o Python de `.venv-analysis`. O notebook inclui saídas executadas, tabelas, gráficos e síntese calculada dos resultados. A maioria das células contém Python.

A partir da raiz, para preparar o ambiente:

```bash
python3 -m venv .venv-analysis
source .venv-analysis/bin/activate
python -m pip install -r analysis/requirements-notebook.txt
bash scripts/check-environment.sh --profile all --json build/environment-all.json
# Se all tiver pendências de CORE, aprove o perfil específico antes da análise:
python scripts/check_environment.py --profile analysis --json build/environment-analysis.json
```

Escolha esse mesmo ambiente como kernel e execute todas as células em ordem. O notebook localiza a raiz tanto quando aberto em `analysis/` quanto na raiz. Não requer CORE para processar resultados já preservados; isso não valida a execução emulada. Veja [AMBIENTE.md](../docs/AMBIENTE.md).

A entrada padrão é somente `experiments/raw/json/S*.json`, com os hashes de `experiments/raw/hashes/` e a matriz em `configs/experiment_plan.csv`. Backups e `raw-final-*` são campanhas alternativas e não são concatenados. Para outra campanha, altere `RAW` explicitamente. Inconsistências estruturais interrompem a leitura; falhas de transferência são preservadas. A exportação é desativada por padrão: `EXPORTAR=True` salva tabelas e figuras em `experiments/summary/notebook/`, sem sobrescrever a análise anterior.

O processamento segue a seção 9 do [guia revisado](../docs/GUIA_COMPLETO_TRABALHO1_REDES.md): rodada como unidade do IC95% de Student, média, mediana, desvio amostral, cobertura/falhas e separação dos fatores. HEAD tem somente latência, sem vazão de conteúdo. O manifesto SHA-256 identifica os JSONs usados; as versões das bibliotecas aparecem nas saídas.

Limites encontrados: o coletor atual não preserva janela comum da rodada, portanto goodput agregado e saturação não são estimados. Os registros de PUT guardam apenas o hash da entrada, sem conferir destino. A pasta de calibração contém descrições com campos de validação vazios, sem logs ping/traceroute/iperf por sentido. São pendências de evidência, não motivos para fabricar medidas.

`scripts/analyze_results.py`, `analysis/data/`, `analysis/tables/` e os relatórios anteriores foram preservados. Seu campo `throughput_aggregate_mbps` soma taxas individuais e não representa bytes por janela comum; o notebook não o usa como goodput agregado. Seus ICs com fator 1,96 também não substituem os ICs de Student recalculados entre rodadas no notebook.


## Materiais para os slides

A seção final de [analise_resultados.ipynb](analise_resultados.ipynb) contém blocos explícitos para cada um dos 11 slides do [roteiro](reports/roteiro_video.md). Execute o notebook em ordem. Essa seção usa `GERAR_ARQUIVOS_SLIDES=True` por padrão, independentemente de `EXPORTAR`, e grava os materiais em [slides/README.md](slides/README.md).

Cada pasta `slides/slide_01/` a `slides/slide_11/` contém seus visuais e `INSTRUCOES.md`, com o trecho do roteiro e orientações de montagem. PNGs têm 2560×1440 pixels (16:9); SVGs são vetoriais; CSVs mantêm valores exatos e ICs. Os gráficos de GET/PUT são separados por perfil e tamanho; os gráficos de tempo usam segundos, enquanto as tabelas do roteiro usam milissegundos. A topologia é extraída dos XMLs, com parâmetros conferidos contra a matriz.

Para personalizar, edite `NOMES` e a tabela de contribuições na seção final. `CONTRIBUICOES_CONFIRMADAS=False` mantém o aviso de proposta. Ajuste conforme a participação real antes de confirmar. A autoavaliação também é uma sugestão. As 17 células anteriores de análise foram preservadas.

O notebook gera 16 visuais em PNG e SVG, tabelas, exemplos reais de JSON, fonte Mermaid da arquitetura, manifesto de fontes e índice: 65 arquivos ao todo nesta execução. Reexecutar atualiza os arquivos gerados de mesmo nome e preserva arquivos manuais. Use `GERAR_ARQUIVOS_SLIDES=False` para apenas exibir as prévias.

A gravação da demonstração, a captura real do CORE, a montagem da apresentação e o vídeo/narração precisam ser feitos separadamente. As instruções dos slides 3 e 5 explicam como. Nenhum tráfego é executado pela geração; nenhum dado de calibração, hash remoto de PUT ou vazão agregada é fabricado. A pasta de slides registra inventário e limites da evidência disponível.
