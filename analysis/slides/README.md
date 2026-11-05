# Materiais dos slides

Gerados pela seção final de `analysis/analise_resultados.ipynb`, seguindo `analysis/reports/roteiro_video.md`.

Execute todas as células com o venv de análise. Geração ativada por padrão e independente da exportação opcional da análise. PNG: 2560×1440; SVG: vetorial editável; CSV: dados exatos; INSTRUCOES.md: conteúdo/fala e tarefas manuais. Reexecutar atualiza arquivos gerados sem apagar vídeos manuais.

**A completar:** nomes e contribuições reais; gravação da demonstração; montagem; narração e vídeo. Diagramas são esquemas do código/XML, não capturas de execução. Não há dados fabricados de calibração, PUT remoto ou vazão agregada.

| Slide | Arquivo | Conteúdo |
| --- | --- | --- |
| 1 | [slide_01/objetivo.png](slide_01/objetivo.png) | Pergunta central e fatores investigados |
| 1 | [slide_01/objetivo.svg](slide_01/objetivo.svg) | Pergunta central e fatores investigados |
| 1 | [slide_01/INSTRUCOES.md](slide_01/INSTRUCOES.md) | Conteúdo, fala e instruções de montagem |
| 2 | [slide_02/arquitetura.png](slide_02/arquitetura.png) | Arquitetura, operações e publicação |
| 2 | [slide_02/arquitetura.svg](slide_02/arquitetura.svg) | Arquitetura, operações e publicação |
| 2 | [slide_02/arquitetura.mmd](slide_02/arquitetura.mmd) | Fonte Mermaid editável do diagrama |
| 2 | [slide_02/INSTRUCOES.md](slide_02/INSTRUCOES.md) | Conteúdo, fala e instruções de montagem |
| 3 | [slide_03/enlaces_perfil_A.csv](slide_03/enlaces_perfil_A.csv) | Enlaces e parâmetros do XML A |
| 3 | [slide_03/enlaces_perfil_B.csv](slide_03/enlaces_perfil_B.csv) | Enlaces e parâmetros do XML B |
| 3 | [slide_03/perfis.csv](slide_03/perfis.csv) | Parâmetros dos XMLs conferidos com a matriz |
| 3 | [slide_03/topologia.png](slide_03/topologia.png) | Nós e gargalo derivados do XML, com parâmetros dos perfis |
| 3 | [slide_03/topologia.svg](slide_03/topologia.svg) | Nós e gargalo derivados do XML, com parâmetros dos perfis |
| 3 | [slide_03/INSTRUCOES.md](slide_03/INSTRUCOES.md) | Conteúdo, fala e instruções de montagem |
| 4 | [slide_04/matriz.csv](slide_04/matriz.csv) | Matriz experimental versionada |
| 4 | [slide_04/matriz_metodo.png](slide_04/matriz_metodo.png) | Fatores, quantidades planejadas e unidade do IC |
| 4 | [slide_04/matriz_metodo.svg](slide_04/matriz_metodo.svg) | Fatores, quantidades planejadas e unidade do IC |
| 4 | [slide_04/INSTRUCOES.md](slide_04/INSTRUCOES.md) | Conteúdo, fala e instruções de montagem |
| 5 | [slide_05/cobertura.csv](slide_05/cobertura.csv) | Cobertura, ausências e falhas por célula |
| 5 | [slide_05/registros_reais.json](slide_05/registros_reais.json) | Exemplos GET/PUT copiados dos registros originais |
| 5 | [slide_05/cobertura_registros.png](slide_05/cobertura_registros.png) | Cobertura e exemplos reais sem simular terminal ao vivo |
| 5 | [slide_05/cobertura_registros.svg](slide_05/cobertura_registros.svg) | Cobertura e exemplos reais sem simular terminal ao vivo |
| 5 | [slide_05/INSTRUCOES.md](slide_05/INSTRUCOES.md) | Conteúdo, fala e instruções de montagem |
| 6 | [slide_06/get_tempo.png](slide_06/get_tempo.png) | GET: response_ms por concorrência com IC95% |
| 6 | [slide_06/get_tempo.svg](slide_06/get_tempo.svg) | GET: response_ms por concorrência com IC95% |
| 6 | [slide_06/put_tempo.png](slide_06/put_tempo.png) | PUT: response_ms por concorrência com IC95% |
| 6 | [slide_06/put_tempo.svg](slide_06/put_tempo.svg) | PUT: response_ms por concorrência com IC95% |
| 6 | [slide_06/estatisticas_tempo.csv](slide_06/estatisticas_tempo.csv) | Estatísticas de tempo de todas as células |
| 6 | [slide_06/get_destaques_tempo.csv](slide_06/get_destaques_tempo.csv) | Valores exatos GET 10 MiB, C=1/32, com IC95% |
| 6 | [slide_06/get_destaques_tempo.png](slide_06/get_destaques_tempo.png) | GET de 10 MiB — valores em destaque |
| 6 | [slide_06/get_destaques_tempo.svg](slide_06/get_destaques_tempo.svg) | GET de 10 MiB — valores em destaque |
| 6 | [slide_06/INSTRUCOES.md](slide_06/INSTRUCOES.md) | Conteúdo, fala e instruções de montagem |
| 7 | [slide_07/get_vazao_individual.png](slide_07/get_vazao_individual.png) | GET: individual_mbps por concorrência com IC95% |
| 7 | [slide_07/get_vazao_individual.svg](slide_07/get_vazao_individual.svg) | GET: individual_mbps por concorrência com IC95% |
| 7 | [slide_07/put_vazao_individual.png](slide_07/put_vazao_individual.png) | PUT: individual_mbps por concorrência com IC95% |
| 7 | [slide_07/put_vazao_individual.svg](slide_07/put_vazao_individual.svg) | PUT: individual_mbps por concorrência com IC95% |
| 7 | [slide_07/estatisticas_vazao_individual.csv](slide_07/estatisticas_vazao_individual.csv) | Estatísticas de vazão individual GET/PUT, sem HEAD |
| 7 | [slide_07/get_destaques_vazao.csv](slide_07/get_destaques_vazao.csv) | Valores exatos GET 10 MiB, C=1/32, com IC95% |
| 7 | [slide_07/get_destaques_vazao.png](slide_07/get_destaques_vazao.png) | GET de 10 MiB — valores em destaque |
| 7 | [slide_07/get_destaques_vazao.svg](slide_07/get_destaques_vazao.svg) | GET de 10 MiB — valores em destaque |
| 7 | [slide_07/FORMULA.md](slide_07/FORMULA.md) | Fórmula e interpretação da métrica |
| 7 | [slide_07/INSTRUCOES.md](slide_07/INSTRUCOES.md) | Conteúdo, fala e instruções de montagem |
| 8 | [slide_08/operacoes_tempo.csv](slide_08/operacoes_tempo.csv) | Tempo por operação, C=1, com IC95% |
| 8 | [slide_08/comparacao_operacoes.png](slide_08/comparacao_operacoes.png) | GET, PUT e HEAD — concorrência 1 |
| 8 | [slide_08/comparacao_operacoes.svg](slide_08/comparacao_operacoes.svg) | GET, PUT e HEAD — concorrência 1 |
| 8 | [slide_08/sentidos_operacoes.png](slide_08/sentidos_operacoes.png) | Sentidos do conteúdo e consulta HEAD |
| 8 | [slide_08/sentidos_operacoes.svg](slide_08/sentidos_operacoes.svg) | Sentidos do conteúdo e consulta HEAD |
| 8 | [slide_08/INSTRUCOES.md](slide_08/INSTRUCOES.md) | Conteúdo, fala e instruções de montagem |
| 9 | [slide_09/evidencias.csv](slide_09/evidencias.csv) | Inventário de evidências e pendências |
| 9 | [slide_09/calibracao_inventario.csv](slide_09/calibracao_inventario.csv) | Existência e tamanho dos arquivos esperados de calibração |
| 9 | [slide_09/evidencias_limites.png](slide_09/evidencias_limites.png) | Evidências disponíveis e limitações experimentais |
| 9 | [slide_09/evidencias_limites.svg](slide_09/evidencias_limites.svg) | Evidências disponíveis e limitações experimentais |
| 9 | [slide_09/INSTRUCOES.md](slide_09/INSTRUCOES.md) | Conteúdo, fala e instruções de montagem |
| 10 | [slide_10/contribuicoes.csv](slide_10/contribuicoes.csv) | Divisão a revisar conforme a participação real |
| 10 | [slide_10/contribuicoes.png](slide_10/contribuicoes.png) | Contribuições dos integrantes |
| 10 | [slide_10/contribuicoes.svg](slide_10/contribuicoes.svg) | Contribuições dos integrantes |
| 10 | [slide_10/INSTRUCOES.md](slide_10/INSTRUCOES.md) | Conteúdo, fala e instruções de montagem |
| 11 | [slide_11/conclusoes.csv](slide_11/conclusoes.csv) | Síntese calculada e limite da avaliação de saturação |
| 11 | [slide_11/autoavaliacao_conclusao.png](slide_11/autoavaliacao_conclusao.png) | Autoavaliação sugerida e resultados observados |
| 11 | [slide_11/autoavaliacao_conclusao.svg](slide_11/autoavaliacao_conclusao.svg) | Autoavaliação sugerida e resultados observados |
| 11 | [slide_11/INSTRUCOES.md](slide_11/INSTRUCOES.md) | Conteúdo, fala e instruções de montagem |
| Fontes | [fontes_json.csv](fontes_json.csv) | SHA-256 dos JSONs usados na análise |
| Fontes | [proveniencia.json](proveniencia.json) | Fontes e ambiente da geração |
