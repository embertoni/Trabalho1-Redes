# Evidências experimentais

- `calibration/`: parâmetros efetivos e saídas de ping, traceroute e iperf por perfil.
- `raw/`: dados originais de requisições/rodadas e logs por campanha, com IDs exclusivos.
- `summary/`: resultados derivados e identificados pela origem dos dados.

Ainda não há medições reais. Nunca coloque números ilustrativos ou resultados de mocks nessas pastas como se fossem campanha.

Cada campanha deve ter um manifesto com revisão do código (ou hashes dos fontes antes do commit inicial), versões, máquina/recursos, topologia e matriz utilizadas, ordem/semente, política de cache e persistência, limites de tempo, datas e arquivos gerados. Preserve a configuração usada, mesmo que o planejamento mude depois.

Dados de carga e binários podem ser recriados; evidências não podem ser inventadas ou regeneradas sem uma nova execução. CSVs, JSONs e logs não estão globalmente ignorados pelo Git. Revise volume e conteúdo antes de adicioná-los; mantenha cópia das evidências fora do repositório quando necessário e registre localização/hashes.
