# Verificação obrigatória de ferramentas

Todo clone novo e toda sessão de agente começam com este diagnóstico. As instruções estão no [AGENTS.md](../AGENTS.md); `make build` também exige o perfil `dev` antes de compilar ou ligar qualquer alvo, inclusive com execução paralela do Make. Um clone Git não executa scripts automaticamente: a entrada é a instrução do agente e os comandos documentados abaixo.

## Executar

No Linux, WSL ou contêiner em que a aplicação será executada, a partir da raiz:

```bash
bash scripts/check-environment.sh --profile all --json build/environment-all.json
# Se GNU Make já estiver disponível:
make doctor
```

No Windows/PowerShell, o launcher usa a distribuição WSL padrão e o mesmo repositório:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-environment.ps1
# Para escolher uma distribuição já instalada:
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-environment.ps1 -Distribution Ubuntu-22.04
# Para diagnosticar somente o Windows (não aprova execução POSIX/CORE):
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-environment.ps1 -Native
```

Usar o launcher via `bash` evita depender do bit executável de arquivos vindos do Windows. O launcher Linux detecta ausência de Python ou versão inferior a 3.10; o launcher Windows detecta WSL/distribuição indisponível e, em modo nativo, Python ausente/inoperante. Não é necessário ter GNU Make para começar o diagnóstico.

Se o CORE utilizar um Python separado, indique-o explicitamente quando a descoberta pelo executável/venv não resolver:

```bash
bash scripts/check-environment.sh --profile all \
  --core-python /opt/core/venv/bin/python --json build/environment-all.json
```

No PowerShell, a opção equivalente é `-CorePython /opt/core/venv/bin/python` quando encaminhando ao WSL.

## Perfis e cobertura

Sempre tente `all` primeiro para levantar o conjunto completo. Depois, uma atividade pode continuar se o seu perfil específico passar, com pendências das outras frentes registradas.

| Perfil | Ferramentas e capacidades obrigatórias |
| --- | --- |
| Todos os perfis | Python >= 3.10, pip, módulos venv/ensurepip e Git |
| `dev` | Base, Linux, Bash, GCC, GNU Make, sha256sum; compilação e execução de um pequeno programa C com sockets, pthreads, relógio monotônico e mkstemp |
| `core` | `dev`, kernel Linux compatível, interface de namespaces de rede, ip/tc/ss, nft, ping, traceroute, iperf3, sysctl/top/vmstat, dd/cp; executáveis core-daemon/core-gui; importação do CORE e Tcl/Tk no Python do CORE |
| `analysis` | Base e importação real de numpy, pandas, scipy e matplotlib no Python atual |
| `all` | União de `dev`, `core` e `analysis` |

O check de ip/tc exige versão reconhecida de iproute2 >= 4.5. O teste C roda somente no Linux, cria arquivos temporários exclusivos e os remove ao terminar. Os subprocessos têm limites de tempo; permissão negada, programa quebrado ou importação com falha também impedem aprovação, mesmo que o comando exista no PATH.

Docker, Vagrant, VirtualBox e curl são inventariados como auxiliares da rota de instalação, não exigências universais. Se usar Docker, no Linux/WSL que hospeda o contêiner execute também:

```bash
bash scripts/check-environment.sh --profile dev --require-docker \
  --json build/environment-docker-host.json
# Em seguida, dentro do contêiner CORE, com o projeto montado:
cd /work
bash scripts/check-environment.sh --profile all --json build/environment-container.json
```

`--require-docker` testa cliente e acesso ao daemon. No launcher Windows, use `-RequireDocker`. Vagrant/VirtualBox só precisam funcionar se forem a rota escolhida; valide então a inicialização e o acesso à VM conforme o guia. Um caminho de Docker listado no inventário opcional não significa que seu daemon foi validado.

Análise pode usar um venv separado. Ative-o e execute `--profile analysis` nele. Os demais checks devem ocorrer no Linux/imagem dos nós: pacotes presentes apenas no Windows ou no host não ficam automaticamente disponíveis no contêiner. Se o inventário `all` acusar pacotes de análise ausentes no ambiente CORE, registre essa separação e anexe também o relatório aprovado do venv de análise.

## Resultado e ação

- Exit code **0**: todos os checks obrigatórios do perfil passaram.
- Exit code **1**: dependência ausente, incompatível ou sem permissão/condição de executar.
- Exit code **2** no programa Python: argumento inválido ou impossibilidade de gravar relatório.
- `AVISO`: validação manual ainda necessária; não vira aprovação de execução CORE.
- `OPCIONAL`: auxiliar não exigido para todas as rotas.

O JSON contém data UTC, Python/sistema, perfil e resultado de cada check. É específico do ambiente atual e fica em `build/`, ignorado pelo Git. Não é resultado experimental. Registre no STATUS o resumo relevante e repita após trocar máquina, contêiner, distribuição, venv ou ferramentas. Relatórios locais podem conter caminhos e mensagens do sistema; revise antes de compartilhar.

Não inicie ações dependentes de checks obrigatórios reprovados. Diagnostique a causa e instale/corrija o necessário no ambiente apropriado, respeitando suas permissões. Documentação e outras ações independentes podem continuar. O diagnóstico não usa sudo, não instala/baixa pacotes, não inicia daemon/GUI e não altera forwarding, interfaces ou regras de firewall. A opção `--require-docker` consulta o daemon do contexto Docker atual, que pode ser remoto; não gera tráfego experimental.

## Preparar dependências ausentes

No Ubuntu usado pelo guia, os pacotes abaixo atendem as ferramentas gerais (o comando é uma instrução para execução consciente; não é disparado pelo diagnóstico):

```bash
sudo apt update
sudo apt install -y build-essential git bash coreutils python3 python3-pip \
  python3-venv python3-tk iproute2 nftables iputils-ping traceroute iperf3 procps
```

Instale o CORE conforme o [guia revisado](GUIA_COMPLETO_TRABALHO1_REDES.md) e as [instruções oficiais](https://coreemu.github.io/core/install.html). Kernel e requisitos do emulador não são substituídos por instalar um pacote Python de nome semelhante. Para Windows, prepare WSL2 ou VM Linux conforme o guia; não instale ferramentas POSIX nativas aleatórias para obter um diagnóstico aprovado.

Para análise, no Python escolhido:

```bash
python3 -m venv .venv-analysis
source .venv-analysis/bin/activate
python -m pip install -r analysis/requirements.txt
python scripts/check_environment.py --profile analysis --json build/environment-analysis.json
```

O arquivo de requisitos é a lista inicial de dependências. Antes da campanha, fixe e registre as versões efetivamente validadas; este diagnóstico mostra as instaladas, sem afirmar compatibilidade com um programa de análise ainda não implementado.

## O que continua obrigatório validar no CORE

Mesmo com exit code 0, verifique:

1. Daemon e GUI abrem no ambiente escolhido e uma sessão com nós é criada.
2. Os nós conseguem usar namespaces e configurar enlaces com os privilégios necessários.
3. Binários, ferramentas e pastas estão disponíveis nos terminais dos nós.
4. Cliente e servidor se alcançam por suas rotas de acesso/núcleo.
5. O gargalo é aplicado nos dois sentidos, sem perda configurada, e é validado com ping/traceroute/iperf3.

Esses passos produzem evidências de T07/T10. O relatório de ferramentas mantém `core_runtime_validated=false`, inclusive quando tudo instalado passou. Nenhum agente deve interpretá-lo como validação funcional da emulação.

## Testar o próprio diagnóstico

```bash
python3 -m unittest discover -s tests -p 'test_environment.py' -v
# Ou: make test-environment
```

No Windows, o mesmo executor pode ser chamado com `python`. Esses testes são do diagnóstico de ambiente, não da aplicação C ou de uma campanha real.
