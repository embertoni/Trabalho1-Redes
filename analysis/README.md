# Análise

T09 integrará o processamento e os gráficos propostos na seção 9 do [guia revisado](../docs/GUIA_COMPLETO_TRABALHO1_REDES.md).

Entradas: dados brutos e metadados de execução. Saídas: tabelas em `experiments/summary/` e gráficos com unidades/fatores identificados.

Preserve falhas e tamanho amostral; não misture perfis; use rodadas para IC, não clientes concorrentes como se fossem independentes. A lista inicial de dependências está em `requirements.txt`; registre e fixe as versões realmente validadas antes da campanha. Execute o perfil `analysis` do diagnóstico no venv ativo, conforme [AMBIENTE.md](../docs/AMBIENTE.md). Ainda não existe programa de análise integrado.
