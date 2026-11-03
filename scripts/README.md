# Automação

T08 integrará os exemplos do [guia revisado](../docs/GUIA_COMPLETO_TRABALHO1_REDES.md), adaptando o executável para `build/client`, as configurações de `configs/` e os diretórios reais dos nós.

Responsabilidades: preparar cargas fora do cronômetro, executar células/rodadas, preservar stdout/stderr e falhas, validar comprimento/hash e produzir CSVs de requisições e rodadas.

O diagnóstico de ambiente já está implementado: `check_environment.py`, `check-environment.sh` e `check-environment.ps1`. Comece por ele conforme [AMBIENTE.md](../docs/AMBIENTE.md). Ele não instala ferramentas e não executa a campanha.

Os scripts de coleta/preparação ainda não foram integrados. Não suponha que alterar a etiqueta do perfil no CSV altera a rede no CORE.
