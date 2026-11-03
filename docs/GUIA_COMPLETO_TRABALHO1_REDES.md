# Guia completo do Trabalho 1 de Redes de Computadores

Avaliação de Desempenho de Cliente-Servidor de Arquivos - ICT/UNIFESP.

Revisão feita em 03/11/2026 a partir de [trabalho1_redes_enunciado.pdf](referencias/trabalho1_redes_enunciado.pdf), de 22/10/2026, e [guia_execucao_trabalho1_redes.pdf](referencias/guia_execucao_trabalho1_redes.pdf). As páginas citadas abaixo são as páginas físicas dos PDFs. Em caso de divergência, prevalece o enunciado e eventual esclarecimento do professor.

Este documento é um roteiro de implementação, validação, experimento e entrega. Os comandos de `server` e `client` especificam a interface a implementar; esses programas ainda não existem neste repositório. Os trechos em Python são ferramentas de coleta e análise para salvar nos caminhos indicados. A revisão documental não equivale a uma execução do CORE ou a uma validação experimental da aplicação.

## 1. Resultado da comparação

**O guia original é abrangente, mas não está inteiramente correto nem pronto para ser seguido sem ajustes.** Ele cobre GET/PUT, concorrência, CORE, estatísticas e vídeo, mas apresenta os problemas abaixo.

| Ponto | Local no guia original | Problema e correção |
| --- | --- | --- |
| Entrega | pp. 2, 11-12 | A frase para enviar somente o link no Classroom pode ser entendida como a entrega inteira. O enunciado, p. 1, exige **código(s) do servidor e link do vídeo**. Somente o arquivo de vídeo é substituído pelo link. |
| Quantidade de operações | pp. 9 e 11 | O guia assume apenas GET/PUT sem mencionar que o enunciado, p. 2, diz literalmente "Neste caso não apenas duas (GET e PUT)". Há ambiguidade; ver seção 2. |
| Protocolo | pp. 3 e 12-19 | O protocolo próprio não é HTTP, embora o enunciado use "servidor HTTP" e "cliente HTTP" na seção 2.1. Para evitar essa divergência, este roteiro recomenda um subconjunto documentado de HTTP sobre sockets C. |
| PUT concorrente | p. 16 | O temporário é `destino.tmp.<getpid()>`, mas threads compartilham PID. PUTs simultâneos do mesmo nome podem truncar o mesmo temporário, corromper conteúdo e falhar no `rename`. Usar `mkstemp` por requisição. |
| GET concorrente | p. 18 | O cliente usa `destino.tmp` fixo. Dois downloads para o mesmo destino colidem. Usar temporários únicos e destinos distintos na campanha. |
| Caminhos e parser | pp. 13-16 | O comentário de `validate_relative_path` inverte o retorno real; rejeitar `..` não impede fuga por links simbólicos. `sscanf` também não valida integralmente os campos numéricos e campos extras. Especificar gramática estrita e confinamento à raiz. |
| Erros durante transferência | pp. 15-19 | Há retornos por falha de I/O sem resposta estruturada; depois de um cabeçalho de sucesso já enviado, não se pode inserir outro status no corpo. Detectar truncamento no cliente, registrar falha e enviar código sempre que a fase do protocolo ainda permitir. |
| Medição | pp. 9 e 19 | O texto recomenda incluir a conexão, mas o cronômetro do cliente começa depois de `connect_to`. Iniciar antes da conexão e terminar após a conclusão definida para GET/PUT. |
| Interface de coleta | pp. 10 e 19 | O comando `--csv ... --id ...` não existe no cliente do apêndice; ele imprime texto chave/valor e não registra falhas em CSV. Definir uma interface única e um coletor compatível. |
| Topologia | pp. 7-8 | A cadeia com três roteadores precisa de quatro sub-redes ponto a ponto/acesso, mas a tabela apresenta três e não fornece rotas. A seção 5 traz endereçamento e roteamento completos. |
| Ambiente de execução | pp. 5-8 | Compilar no WSL não torna arquivos e ferramentas automaticamente disponíveis no contêiner CORE. É preciso montar/copiar o projeto e compilar no ambiente em que os nós executarão. WSL/Docker é uma opção, não uma exigência do trabalho nem garantia de funcionamento. |
| Calibração | p. 8 | Falta validar explicitamente a direção inversa, relevante porque GET e PUT têm sentidos opostos. Usar iperf3 normal e `-R`. |
| CSV ilustrativo | p. 9 | Uma linha declara 677,4 Mbit/s numa rede de 100 Mbit/s. Não é uma referência plausível de transferência completa pelo gargalo. Não usar números fictícios como resultados. |
| Estatística e gráficos | pp. 20-21 | Sem `status`, `df.get('status', 200).astype(...)` falha. Gráficos agrupam redes e outros fatores, o IC só cobre tempo, e requisições concorrentes podem inflar o tamanho amostral. Agregar por rodada independente e separar os fatores. |
| Cache e saturação | pp. 10-11 | Apagar arquivos não limpa cache de páginas. Aumentar concorrência exige distinguir vazão individual de vazão agregada para avaliar saturação. Definir política de cache e medir ambas. |

Não foram compilados os fontes impressos no PDF. Os defeitos de código acima foram identificados por inspeção; não é necessário pressupor que toda quebra visual de linha do PDF seja um defeito do fonte original.

## 2. Requisitos e decisões de interpretação

### 2.1 Obrigações explícitas

| Origem no enunciado | O que cumprir | Evidência a produzir |
| --- | --- | --- |
| p. 1, observações | Grupo de no máximo 3 alunos; prazo **05/11/2026** | Integrantes, data e submissão |
| p. 1, entregáveis | Código(s) do servidor; vídeo de até 10 minutos hospedado em nuvem; enviar o link do vídeo | Fontes compiláveis e link acessível no Classroom |
| p. 1, seção 1 | API de sockets em C; múltiplos clientes conectados e atendidos simultaneamente | Código, compilação e teste concorrente |
| p. 1, seção 1 | GET baixa e substitui arquivo local; desconsiderar GET condicional | Testes com hash antes/depois |
| p. 1, seção 1 | PUT envia e substitui arquivo no servidor | Testes com hash antes/depois |
| p. 1, seção 1 | Respostas de acordo com o método; códigos de erro enviados ao cliente | Tabela de códigos e testes negativos |
| p. 1, seção 2.1 | Usar CORE; acessos e núcleo; servidor e cliente em redes de acesso diferentes | Sessão salva e desenho |
| p. 1, seção 2.1 | Escolher um enlace de gargalo e configurar vazão e latência; não configurar erro | Parâmetros e captura das configurações |
| p. 1, seção 2.1 | Validar RTT fim a fim/até saltos com ping e traceroute; vazão com iperf | Logs de calibração |
| p. 2, seção 2.2 | Tamanhos distintos típicos de duas aplicações de Internet; operações; baixa/média/alta concorrência; duas tecnologias de acesso | Matriz e justificativas |
| p. 2, seção 2.3 | Repetir cada configuração n vezes; o texto recomenda n > 10 no ambiente controlado | Adotar ao menos 11 rodadas por célula |
| p. 2, seções 2.3-2.4 | Tempo de resposta e vazão por GET/PUT; estatística básica, IC, gráficos, gargalos e saturação | Dados brutos, tabelas e discussão |
| pp. 1-2, vídeo | Introdução/motivação, o que/como/por que/onde, resultados, conclusões, contribuições individuais e autoavaliação | Roteiro e vídeo até 10 minutos |

TCP, threads POSIX, porta 9000, tamanhos, níveis de concorrência, IC de 95%, scripts e estrutura de diretórios são escolhas deste roteiro. O enunciado não fixa esses detalhes. Entregar também o cliente, scripts e sessão CORE é recomendado para reprodução, mas o entregável de código explicitamente nomeado é o servidor.

### 2.2 Duas ambiguidades que o guia original deveria mencionar

**Operações.** A seção 1 exige GET/PUT, a seção 2.3 volta a citar PUT/GET, mas a seção 2.2 contém a expressão transcrita na seção 1 deste guia. Não é possível afirmar documentalmente que exista autorização para ignorar o "não". Registre eventual esclarecimento do professor. Sem esclarecimento, a alternativa conservadora deste roteiro é implementar e avaliar **HEAD como terceira operação**, mantendo toda a campanha e as métricas obrigatórias de GET/PUT. HEAD retorna os metadados do GET sem corpo; sua latência é analisada separadamente e sua vazão de conteúdo é **não aplicável**. HEAD é uma escolha de extensão, não um método explicitamente solicitado pelo professor.

**HTTP.** A seção 1 fala em métodos similares aos do HTTP e não define formato de mensagem, enquanto a seção 2.1 chama os processos de HTTP. Recomenda-se implementar GET/PUT e, na alternativa conservadora, HEAD usando mensagens HTTP, em vez de assumir que o protocolo proprietário do PDF atende inequivocamente a essa redação. Não é necessário implementar todos os recursos do HTTP para realizar a campanha controlada. Documente o subconjunto e as limitações; não alegue conformidade completa.

## 3. Preparar o ambiente

### 3.1 Caminho preferencial: laboratório com CORE instalado

O Anexo I, p. 3, permite usar a máquina do laboratório. Esta é a primeira opção para reduzir o trabalho de instalação. Em terminais separados:

```bash
# Terminal 1, se o daemon ainda não estiver ativo:
sudo core-daemon
# Terminal 2, sessão gráfica Linux:
core-gui
```

Antes de prosseguir, crie dois nós ligados, inicie a sessão, abra os terminais dos nós e teste ping. Confirme que GCC, Python, traceroute e iperf3 existem **no ambiente dos nós**. Os nós CORE utilizam o software disponibilizado pelo ambiente que os hospeda. Veja a [instalação oficial](https://coreemu.github.io/core/install.html) e o [tutorial de rede cabeada](https://coreemu.github.io/core/tutorials/tutorial1.html).

### 3.2 Computador próprio com Windows

O trabalho exige CORE, não Windows, WSL, Vagrant ou Docker especificamente. Use uma VM Linux com sessão gráfica ou WSL2 se a máquina suportar o CORE. A instalação do Anexo I usa Vagrant/Bionic e comandos antigos de chave APT; trate-a como referência do professor e siga as instruções atuais do fornecedor para instalar ferramentas em distribuições atuais.

No PowerShell como administrador, uma opção de preparação é:

```powershell
wsl --install -d Ubuntu-22.04
# Reinicie se solicitado e conclua a criação do usuário Linux.
wsl --update
wsl --list --verbose
```

Verifique que a distribuição está em WSL2. Consulte a [documentação da Microsoft](https://learn.microsoft.com/en-us/windows/wsl/install). Mantenha o projeto no sistema Linux, por exemplo `~/trabalho1-redes`, e registre a versão efetivamente usada. Se optar por Docker Desktop, habilite a integração com essa distribuição e verifique `docker version`; siga a [documentação de integração WSL](https://docs.docker.com/desktop/features/wsl/).

No Linux que hospedará o experimento, instale as ferramentas que faltarem:

```bash
sudo apt update
sudo apt install -y build-essential git python3 python3-venv iproute2 \
  iputils-ping traceroute iperf3 procps curl ca-certificates x11-xserver-utils
mkdir -p ~/trabalho1-redes
cd ~/trabalho1-redes
mkdir -p src scripts topology experiments/calibration experiments/raw analysis \
  server-data client-data client-output
```

### 3.3 CORE em Docker: alternativa com montagem explícita

Faça os comandos no Linux com Docker funcionando. Os nomes abaixo constam da [documentação oficial do CORE para Docker](https://coreemu.github.io/core/install_docker.html). Use revisão conhecida do repositório e registre o commit; não atualize o ambiente durante a campanha.

```bash
mkdir -p ~/tools
cd ~/tools
git clone https://github.com/coreemu/core.git
cd core
git rev-parse HEAD
docker build -t emane-python -f dockerfiles/Dockerfile.emane-python .
docker build -t core-trabalho1 -f dockerfiles/Dockerfile.ubuntu .

# PROJECT deve conter o projeto no sistema Linux.
PROJECT="$HOME/trabalho1-redes"
docker run -itd --name core-trabalho1 --privileged --init \
  -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  --mount "type=bind,source=$PROJECT,target=/work" \
  --entrypoint /opt/core/venv/bin/core-daemon core-trabalho1
```

Em sessão X11 convencional, autorize o usuário do contêiner conforme o mecanismo do servidor X (`xhost +local:root` é o exemplo oficial) e abra:

```bash
docker exec -it core-trabalho1 core-gui
docker exec -it core-trabalho1 bash
```

No shell do contêiner, instale ferramentas ausentes, entre em `/work` e compile ali. Em WSLg/Docker Desktop, exibição gráfica e recursos de rede dependem da integração do host: os comandos X11 acima não garantem funcionamento. Se não for possível criar nós, abrir terminais e validar enlaces, use o laboratório ou uma VM Linux com ambiente gráfico; não faça a campanha em localhost como substituição do CORE.

Verifique `docker logs core-trabalho1` e a documentação de instalação se houver falhas. Regras de forwarding do Docker podem interferir no CORE; diagnostique antes de alterar regras. Não trate `hello-world` ou abrir a GUI como prova de que o emulador está funcional.

### 3.4 Registrar o ambiente

Registre sistema/kernel, CPU/RAM, versões de CORE, GCC, Python e iperf3, revisão do código e limites relevantes. Dentro do ambiente de execução:

```bash
uname -a
gcc --version
python3 --version
iperf3 --version
ip -V
ulimit -n
```

No Docker, registre também a imagem efetiva com `docker image inspect core-trabalho1`. Fixe as dependências de análise com `pip freeze` depois da instalação. Compile dentro do mesmo Linux/imagem dos nós para evitar incompatibilidade de bibliotecas.

## 4. Implementar a aplicação em C

### 4.1 Arquitetura e interface

Organização proposta:

```text
src/server.c       socket/bind/listen/accept; atendimento concorrente
src/client.c       conexão, GET/PUT/HEAD e telemetria JSON
src/protocol.c     envio completo, parser, tamanho e erros
src/protocol.h
Makefile
scripts/run_cell.py
analysis/analyze.py
topology/          sessão CORE e parâmetros de cada perfil
experiments/       calibração, dados brutos, logs e resumos
README.md          instruções, versões, decisões e integrantes
```

Interface a implementar, usada nos exemplos e no coletor deste guia:

```bash
./server --bind 0.0.0.0 --port 9000 --root /work/server-data
./client HOST PORT GET REMOTE_PATH LOCAL_PATH
./client HOST PORT PUT REMOTE_PATH LOCAL_PATH
./client HOST PORT HEAD REMOTE_PATH
```

`REMOTE_PATH` é uma chave relativa à raiz do servidor; `LOCAL_PATH` é um caminho no cliente. O cliente escreve **uma linha JSON em stdout em todas as tentativas**, inclusive falhas; diagnóstico adicional vai para stderr. Retorna 0 no sucesso e valor diferente de 0 na falha. Exemplo de formato, com valores meramente ilustrativos e sem valor de resultado experimental:

```json
{"status":200,"bytes":2097152,"response_ms":1000.0,"throughput_mbps":16.777216,"error":""}
```

`status` é o código recebido do servidor; use 0 se não foi possível obter resposta válida. `bytes` conta o conteúdo efetivamente transferido, sem cabeçalhos. Em falha, `throughput_mbps` deve ser `null`; em HEAD, `bytes` é 0 e `throughput_mbps` também é `null`. Para GET/PUT concluídos, aplique a fórmula da seção 7. O JSON deve usar números finitos e `null`, não `NaN`.

### 4.2 Protocolo recomendado

Use TCP e mensagens HTTP com linhas terminadas em `\r\n`, cabeçalhos encerrados em `\r\n\r\n` e corpo binário com tamanho explícito. O conjunto controlado usa uma requisição por conexão e `Connection: close`. O cliente envia `Host`; em PUT envia `Content-Length` decimal sem sinal. O GET não é condicional e não usa cache HTTP. Referências: [sintaxe HTTP/1.1, RFC 9112](https://www.rfc-editor.org/rfc/rfc9112.html) e [semântica dos métodos, RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html).

```text
GET /foto_2MiB.bin HTTP/1.1\r\n
Host: 10.0.4.2:9000\r\n
Connection: close\r\n
\r\n
```

Em GET, retornar 200 com `Content-Length` igual ao tamanho e depois exatamente esses bytes. Em PUT, validar destino e comprimento, receber o corpo inteiro, concluir a gravação e só então confirmar. Use 201 quando criou um recurso e 200 ou 204 quando substituiu; 200/201 podem ter `Content-Length: 0`, enquanto 204 não leva corpo nem esse cabeçalho. HEAD retorna os cabeçalhos que GET retornaria, incluindo o tamanho do arquivo, **sem enviar/esperar corpo**.

Limite explicitamente o escopo de teste a requisições com `Content-Length`, sem `Transfer-Encoding`, `Expect: 100-continue`, pipelining ou TLS. Rejeite formatos não suportados de maneira documentada. Não use um cliente HTTP genérico como substituto do cliente C na coleta principal.

| Situação | Código HTTP recomendado |
| --- | --- |
| GET/HEAD válido | 200 |
| PUT criou arquivo | 201 |
| PUT substituiu arquivo | 200 ou 204 |
| Requisição malformada ou comprimento inválido | 400 |
| Acesso não permitido | 403 |
| GET/HEAD de arquivo inexistente | 404 |
| Método conhecido mas não permitido no recurso | 405 e cabeçalho `Allow` |
| Método não implementado | 501 |
| PUT sem comprimento exigido | 411 |
| Arquivo excede limite definido | 413 |
| Falha de I/O antes de iniciar a resposta | 500 |
| Limite de atendimento atingido | 503 |

O enunciado exige códigos de erro, mas não lista números específicos. Os códigos acima são a política HTTP recomendada. Para erros, encerre a conexão após a resposta. Se a transferência truncar depois de um status de sucesso, o cliente deve detectar tamanho incompleto, preservar o arquivo anterior e registrar falha; não interpretar bytes de uma segunda linha de status como arquivo.

### 4.3 Concorrência e integridade

Use `socket(AF_INET, SOCK_STREAM, 0)`, `bind`, `listen`, `accept` e uma thread POSIX ou processo por conexão. Em threads, passe estrutura própria por conexão, libere recursos e use `pthread_detach` ou `join`. Não proteja a transferência inteira por um mutex global: isso serializaria os clientes.

Implemente laços de envio, recebimento e gravação: chamadas podem transferir menos bytes do que o solicitado. Trate `EINTR`, EOF prematuro, retorno zero de escrita, falha de conexão e `SIGPIPE`. Leia no máximo o restante de cada corpo. Dados recebidos junto com o fim dos cabeçalhos precisam ser preservados para o corpo, não descartados. Veja a [documentação de recv](https://man7.org/linux/man-pages/man2/recv.2.html).

Para PUT e GET local, crie temporário **único por operação, no mesmo diretório do destino**, com `mkstemp`; nunca use somente PID ou nome fixo. Verifique `snprintf`, gravações, `fsync` se adotado, `close` e `rename`; remova o temporário em erro. Só substitua o destino após receber o conteúdo inteiro. `rename` no mesmo sistema de arquivos permite publicação atômica. Referências: [mkstemp](https://man7.org/linux/man-pages/man3/mkstemp.3.html) e [rename](https://man7.org/linux/man-pages/man2/rename.2.html).

Defina a política para PUTs do mesmo nome, por exemplo: a última publicação atômica bem-sucedida vence. Nesse caso, um GET já aberto pode concluir a versão anterior, sempre íntegra. Teste essa propriedade separadamente. A campanha principal usa destinos de PUT distintos por cliente, evitando misturar disputa de nome com limite de rede.

Defina também o que significa persistência: este roteiro recomenda `fsync` no temporário de PUT antes da confirmação, e informa que isso não equivale sozinho a garantir persistência do nome após queda de energia. Se o objetivo incluir essa garantia, sincronize também o diretório após publicar. Mantenha a política igual em toda a campanha e explique o custo de disco incluído.

### 4.4 Parser e caminhos

Defina limites para cabeçalho, caminho, arquivo e tempo máximo sem progresso. Faça parsing estrito de comprimento: rejeite negativos, overflow, lixo após número e cabeçalhos de comprimento conflitantes. Não aceite que `sscanf` ignore campos extras.

Uma política simples para este trabalho é aceitar somente nomes planos na raiz, com letras ASCII, dígitos, `_`, `-` e `.`, rejeitando nomes vazios, `.`/`..`, nomes reservados a temporários e qualquer barra, barra invertida, escape percentual ou byte NUL. A barra inicial do alvo HTTP é removida antes dessa validação. Assim, os nomes da campanha são válidos e não há necessidade de subdiretórios remotos. Documente essa restrição. Se implementar subdiretórios, valide cada componente e bloqueie links simbólicos e fugas em toda a resolução, não apenas no nome final.

Abra a raiz uma vez e use operações relativas a seu descritor. Para nomes planos, `openat` com `O_NOFOLLOW` e verificação de arquivo regular evita seguir um link final em GET. Mantenha a raiz sob controle do experimento. Rejeitar a substring `..` por si só não implementa confinamento. Veja [open/openat](https://man7.org/linux/man-pages/man2/open.2.html).

### 4.5 Compilar e testar antes do CORE

Com os arquivos implementados, compile no Linux dos nós:

```bash
gcc -std=c11 -D_POSIX_C_SOURCE=200809L -Wall -Wextra -Wpedantic -O2 \
  -pthread -o server src/server.c src/protocol.c
gcc -std=c11 -D_POSIX_C_SOURCE=200809L -Wall -Wextra -Wpedantic -O2 \
  -o client src/client.c src/protocol.c
```

Primeiro teste em `127.0.0.1`; depois repita no CORE. Não publique resultados de localhost como resultados da emulação.

| Teste | Critério de aprovação |
| --- | --- |
| GET novo e GET sobrescrevendo conteúdo diferente | Tamanho e SHA-256 do destino iguais aos da origem |
| PUT novo e PUT sobrescrevendo conteúdo diferente | Tamanho e SHA-256 do servidor iguais aos do cliente |
| Arquivo vazio, binário com NUL, tamanho maior que o buffer e tamanho não múltiplo do buffer | Conteúdo exato; nenhuma dependência de terminadores de string |
| Arquivo ausente, método inválido, comprimento inválido, acesso negado | Código esperado; servidor continua atendendo |
| Comprimento anunciado maior que corpo enviado; desconexão durante GET/PUT | Falha registrada; destino anterior preservado; temporário removido |
| 1, 8 e 32 requisições com nomes distintos | Atendimento sobreposto, sem corrupção ou bloqueio global |
| PUTs do mesmo nome e GET durante PUT | Arquivos íntegros segundo a política de publicação |
| Tentativa de sair da raiz e link simbólico na raiz | Acesso rejeitado |
| HEAD, se adotado | Cabeçalhos corretos, nenhum corpo e nenhuma alteração de arquivo |

Use `sha256sum` fora do intervalo cronometrado. Testes de permissão devem executar o servidor sem privilégios que contornem a restrição. Guarde comandos e saídas em `experiments/functional/`.

## 5. Montar uma topologia completa no CORE

Use cinco nós: C1 e S1 como hosts; R1, R2 e R3 como roteadores. R1 e R3 representam acesso; R2, núcleo. Uma topologia mínima consistente é:

```text
acesso do cliente       trânsito/núcleo                  acesso do servidor
C1 -------- R1 =============== R2 -------- R3 -------- S1
10.0.1.0/24    10.0.2.0/24       10.0.3.0/24   10.0.4.0/24
                 gargalo
```

No editor, configure endereços e interfaces conforme a tabela. Os nomes `eth0/eth1` abaixo são uma convenção deste roteiro: confira `ip -br addr` e adapte se a ordem dos enlaces gerar outros nomes.

| Nó | Interface | Endereço/prefixo | Vizinho |
| --- | --- | --- | --- |
| C1 | eth0 | 10.0.1.2/24 | R1 |
| R1 | eth0 | 10.0.1.1/24 | C1 |
| R1 | eth1 | 10.0.2.1/24 | R2 |
| R2 | eth0 | 10.0.2.2/24 | R1 |
| R2 | eth1 | 10.0.3.1/24 | R3 |
| R3 | eth0 | 10.0.3.2/24 | R2 |
| R3 | eth1 | 10.0.4.1/24 | S1 |
| S1 | eth0 | 10.0.4.2/24 | R3 |

Escolha **roteamento estático ou dinâmico**, evitando configurações conflitantes. Para o estático abaixo, desative os serviços de anúncio dinâmico nos roteadores e habilite encaminhamento IPv4. Execute as linhas no terminal do nó indicado; salve-as como serviços/hooks da sessão para repetição:

```bash
# C1
ip route replace default via 10.0.1.1
# S1
ip route replace default via 10.0.4.1
# R1
sysctl -w net.ipv4.ip_forward=1
ip route replace 10.0.3.0/24 via 10.0.2.2
ip route replace 10.0.4.0/24 via 10.0.2.2
# R2
sysctl -w net.ipv4.ip_forward=1
ip route replace 10.0.1.0/24 via 10.0.2.1
ip route replace 10.0.4.0/24 via 10.0.3.2
# R3
sysctl -w net.ipv4.ip_forward=1
ip route replace 10.0.1.0/24 via 10.0.3.1
ip route replace 10.0.2.0/24 via 10.0.3.1
```

Inicie a sessão e valide ping entre C1 e S1 nos dois sentidos. O traceroute de C1 a S1 deve mostrar R1, R2 e R3 antes de S1, salvo filtragem das respostas ICMP. Salve a sessão em `topology/`, uma captura legível, endereços e rotas. O nome/extensão do arquivo depende da versão do CORE; preserve o formato nativo daquela versão.

Os nós CORE não necessariamente isolam todo o sistema de arquivos como máquinas independentes. Utilize caminhos separados: `/work/server-data`, `/work/client-data` e `/work/client-output`, ou seus equivalentes no laboratório. Execute o servidor **no terminal de S1**, e o coletor/clientes **no terminal de C1**. O IP de destino sempre é `10.0.4.2`, nunca localhost.

## 6. Configurar e calibrar o gargalo

### 6.1 Perfis de acesso

Configure somente R1-R2 como gargalo. Os demais enlaces devem ter capacidade superior, por exemplo 1 Gbit/s se o host sustentar, e atraso adicional zero. Deixe **perda/erro, duplicação e jitter artificial em zero**. Não introduza perda para simular uma tecnologia.

| Perfil | Tecnologia representada | Capacidade por sentido | Atraso de ida e de volta no enlace | Contribuição aproximada ao RTT |
| --- | --- | --- | --- | --- |
| A | Banda larga fixa por fibra, plano de entrada | 100 Mbit/s | 5 ms em cada sentido | 10 ms |
| B | Acesso móvel 4G/LTE, condição moderada | 20 Mbit/s | 20 ms em cada sentido | 40 ms |

São **valores de modelagem simplificados**, não médias universais nem medidas do Brasil. A escolha contrasta acesso fixo e móvel e deve ser justificada no relatório. Como contexto empírico, a Ofcom publica [medidas de banda larga fixa](https://www.ofcom.org.uk/siteassets/resources/documents/research-and-data/broadband-research/broadband-speeds/home-broadband-performance-september-2023/march-23-home-broadband-performance.pdf?v=330131) e [resultados de redes móveis](https://www.ofcom.org.uk/phones-and-broadband/mobile-phones/mobile-matters?language=en). Não copie números de "latência" dessas fontes como RTT sem conferir a definição. A simetria de vazão e a ausência de variação temporal são limitações explícitas desta emulação.

No CORE, abra a configuração do enlace R1-R2 e confira as unidades mostradas. Se os campos estiverem em bit/s e microssegundos, A equivale a `100000000` e `5000`; B a `20000000` e `20000`. Se a interface oferecer configurações por direção, ajuste ambas. Confirme os valores efetivos no runtime, por exemplo com `tc -s qdisc show` e `tc -s class show` nas interfaces envolvidas. Não aplique um segundo `netem` manual sobre o que o CORE já configurou.

### 6.2 Calibração obrigatória

No terminal S1, mantenha um servidor iperf3:

```bash
iperf3 -s
```

No terminal C1, para cada perfil, ajuste `PROFILE` e grave os resultados:

```bash
PROFILE=A
mkdir -p /work/experiments/calibration/$PROFILE
ip -br addr > /work/experiments/calibration/$PROFILE/client-ip.txt
ip route > /work/experiments/calibration/$PROFILE/client-route.txt
ping -c 30 10.0.4.2 > /work/experiments/calibration/$PROFILE/ping.txt
traceroute -n 10.0.4.2 > /work/experiments/calibration/$PROFILE/traceroute.txt
iperf3 -c 10.0.4.2 -t 30 -O 3 -J > /work/experiments/calibration/$PROFILE/iperf-put.json
iperf3 -c 10.0.4.2 -t 30 -O 3 -R -J > /work/experiments/calibration/$PROFILE/iperf-get.json
```

Ping também para `10.0.1.1`, `10.0.2.2` e `10.0.3.2`, salvando saídas, verifica RTT até os roteadores alcançáveis. Os RTTs do traceroute são de ida e volta de cada sonda; subtrair saltos não mede diretamente o atraso unidirecional de um enlace. Faça também ping no sentido S1-C1.

O teste iperf3 normal mede C1-S1, direção principal do PUT; `-R` mede S1-C1, direção do GET. `-O 3` omite o início da medição segundo a [documentação do iperf3](https://software.es.net/iperf/invoking.html). Se necessário, repita com `-P 4` como diagnóstico de limite de um fluxo, mantendo a distinção nos registros. Não execute iperf durante a campanha da aplicação.

O RTT sem carga deve se aproximar de 10 ms em A e 40 ms em B, acrescido dos demais custos. A vazão TCP deve ser compatível com a capacidade, considerando cabeçalhos, janelas, CPU e duração. Se a capacidade medida for sistematicamente inferior, investigue antes de coletar: rota, unidade, sentido configurado, janela TCP, filas, CPU e forwarding. Não invente uma tolerância como se viesse do enunciado; documente a diferença observada e seu diagnóstico.

## 7. Planejar as configurações experimentais

### 7.1 Matriz proposta

| Fator | Níveis |
| --- | --- |
| Conteúdo/tamanho | 2 MiB para compartilhamento de fotos; 10 MiB para envio/download de vídeo curto |
| Métodos obrigatórios | GET e PUT |
| Extensão conservadora | HEAD, pela ambiguidade descrita na seção 2 |
| Concorrência | 1, 8 e 32 requisições simultâneas |
| Rede | A e B da seção 6 |
| Repetições | 11 rodadas independentes por combinação |

Associe os tamanhos a duas aplicações concretas: compartilhamento de fotos em uma aplicação social e transferência de vídeo curto em uma aplicação de mídia. Como referência de ordem de grandeza, a [Ofcom usa um arquivo de 2 MB como exemplo de foto ou vídeo curto de baixa resolução](https://www.ofcom.org.uk/phones-and-broadband/mobile-phones/mobile-matters-download-speeds-connection-rates-and-latency-levels-revealed). MB e MiB diferem: aqui 2 MiB são 2.097.152 bytes e 10 MiB são 10.485.760 bytes. Um vídeo de 10 MiB corresponde, por exemplo, a aproximadamente 21 segundos de conteúdo a 4 Mbit/s, sem contar overhead do contêiner. São representantes de carga, não tamanhos fixos dessas aplicações. Para reforçar a justificativa, registre tamanho/codec/resolução de um pequeno conjunto real das duas aplicações, sem incluir conteúdo privado na entrega.

Um único nó C1 pode iniciar vários processos clientes; isso representa concorrência de requisições compartilhando o mesmo acesso. Informe essa escolha. Se optar por nós clientes separados, eles precisam compartilhar o mesmo gargalo e suas diferenças passam a fazer parte do planejamento.

GET/PUT geram `2 × 2 × 3 × 2 = 24` células e **264 rodadas**. Com uma requisição por cliente em cada rodada, há `2 × 2 × 2 × 11 × (1+8+32) = 3.608` requisições. HEAD acrescenta 12 células, 132 rodadas e 1.804 requisições: total conservador de **36 células, 396 rodadas e 5.412 requisições**. Onze linhas de clientes da mesma rodada não equivalem a onze repetições independentes.

Dimensione o tempo antes de congelar a matriz. Com os tamanhos acima, somente GET/PUT transferem aproximadamente 10.824 MiB por perfil. O piso teórico combinado a 100 e 20 Mbit/s é cerca de **91 minutos**, sem conexão, cabeçalhos, disco, aquecimento, calibração ou pausas. Reserve mais tempo e faça um piloto. A dupla 1/100 MiB do guia original levaria cerca de 12,7 horas só de transmissão nas mesmas condições. Se alterar tamanhos ou concorrência por restrição de recursos, justifique antes da campanha e preserve os fatores pedidos; não elimine cenários após observar resultados desfavoráveis.

### 7.2 Preparar dados e estado

No ambiente de execução, antes das medições:

```bash
cd /work
mkdir -p client-data server-data client-output
dd if=/dev/urandom of=client-data/foto_2MiB.bin bs=1M count=2 status=none
dd if=/dev/urandom of=client-data/video_10MiB.bin bs=1M count=10 status=none
cp client-data/foto_2MiB.bin client-data/video_10MiB.bin server-data/
sha256sum client-data/*.bin > experiments/input-sha256.txt
```

Para PUT, use `put_<tamanho>_<client_id>.bin` como nome remoto. Para GET, todos podem ler o mesmo arquivo imutável, mas cada cliente grava destino próprio. Inicialize arquivos remotos de PUT antes da medição para avaliar **sobrescrita em todas as rodadas**; teste criação separadamente. Limpe resultados locais fora do intervalo medido e valide hashes depois de cada rodada, sem acrescentar esse tempo ao tempo de resposta.

Adote uma política de cache: por exemplo, sistema aquecido com uma rodada de aquecimento não contabilizada antes de cada célula. Não afirme que apagar diretórios limpa o cache do kernel. Não execute `drop_caches` entre algumas condições e outras não. Mantenha iguais versão, buffer, política de sincronização, opções TCP e carga de fundo.

Randomize a ordem das células dentro de cada perfil com semente registrada e alterne/revisite os perfis em blocos quando viável; calibre após cada mudança. Aguarde o fim de todos os clientes de uma rodada antes de iniciar a próxima. Registre hora, ordem e aquecimento. Se 32 clientes ainda não alcançarem um platô, relate que o ponto de saturação não foi observado ou amplie a faixa com justificativa.

### 7.3 Métricas e limites do cronômetro

Use `clock_gettime(CLOCK_MONOTONIC, ...)` no cliente C. Inicie imediatamente **antes de conectar**, depois de preparar argumentos; finalize GET após receber e fechar/publicar o arquivo local, PUT após receber a confirmação final do servidor, HEAD após receber os cabeçalhos. Inclua estabelecimento TCP e I/O da operação; exclua geração dos arquivos, processo de análise e verificação posterior de hash. Informe se resolução DNS está incluída; usando IP numérico, evite essa fonte de variação.

Para uma operação GET/PUT bem-sucedida:

```text
tempo_resposta_ms = (fim - início) × 1000
goodput_Mbit_s = bytes_de_conteúdo × 8 / ((fim - início) × 1.000.000)
```

Chame essa taxa de vazão útil da aplicação (goodput), não taxa bruta do enlace. Mbit/s usa 10^6 bits; MiB/s usa 2^20 bytes. Para uma rodada concorrente, meça uma janela comum desde a liberação dos clientes até todos concluírem e calcule:

```text
goodput_agregado_Mbit_s = 8 × soma(bytes concluídos com sucesso) / janela_segundos / 1.000.000
```

**Não some taxas individuais calculadas sobre janelas diferentes.** Guarde também taxa de sucesso, número de falhas e duração da rodada. Falhas não recebem vazão zero como se fossem transferências completas; a taxa de sucesso permanece explícita. HEAD não transfere conteúdo, logo sua vazão de conteúdo é não aplicável.

## 8. Coletar os dados de forma reproduzível

### 8.1 Sequência de execução

1. Termine os testes funcionais e valide a calibração de A/B.
2. No nó S1, inicie `server` com a raiz absoluta correta e salve stdout/stderr. Confirme a porta com `ss -lntp`.
3. Prepare os arquivos e destinos de PUT de cada célula; execute o aquecimento e descarte apenas essa rodada identificada como aquecimento.
4. No nó C1, execute 11 rodadas por célula, com os clientes liberados juntos; salve uma linha por requisição e outra por rodada.
5. Verifique hashes fora da medição, registre corrupção como falha e preserve os logs. Não avance após corrupção sem investigar a implementação.
6. Registre recursos do host/nós, configuração e ordem. Ao mudar perfil, valide novamente e mantenha os dados anteriores.

### 8.2 Coletor de uma célula

Salve o bloco abaixo em `scripts/run_cell.py`. Ele usa apenas a biblioteca padrão e a interface JSON da seção 4. **Ele não funciona diretamente com a saída chave/valor do cliente do PDF**: implemente o contrato especificado ou adapte e valide o parser de maneira explícita. O coletor inicia processos C de verdade; Python só organiza o experimento. Não inclui aquecimento nem inicialização dos arquivos remotos.

```python
import argparse
import csv
import hashlib
import json
import math
import subprocess
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('host')
p.add_argument('profile', choices=['A', 'B'])
p.add_argument('operation', choices=['GET', 'PUT', 'HEAD'])
p.add_argument('size_mib', type=int, choices=[2, 10])
p.add_argument('concurrency', type=int, choices=[1, 8, 32])
p.add_argument('--rounds', type=int, default=11)
p.add_argument('--timeout', type=float, default=600)
p.add_argument('--out', default='experiments/raw')
p.add_argument('--server-root', default='server-data')
a = p.parse_args()
if a.rounds < 11:
    p.error('use pelo menos 11 rodadas medidas')
root = Path(a.out) / uuid.uuid4().hex
root.mkdir(parents=True)
size = a.size_mib * 1048576
name = 'foto_2MiB.bin' if a.size_mib == 2 else 'video_10MiB.bin'
bandwidth, delay = (100, 5) if a.profile == 'A' else (20, 20)
base = dict(profile=a.profile, bandwidth_mbps=bandwidth,
            delay_oneway_ms=delay, operation=a.operation,
            file_size_bytes=size, concurrency=a.concurrency)

def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            result.update(block)
    return result.hexdigest()

expected_hash = digest(Path('client-data') / name) if a.operation != 'HEAD' else None

def append_csv(path, row):
    exists = path.exists()
    with path.open('a', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(row))
        if not exists:
            w.writeheader()
        w.writerow(row)

for repeat in range(1, a.rounds + 1):
    run_id = f'{root.name}-{repeat:02d}'
    gate = threading.Barrier(a.concurrency + 1)
    local_dir = root / run_id
    local_dir.mkdir()

    def request(client_id):
        remote = (f'put_{a.size_mib}_{client_id}.bin'
                  if a.operation == 'PUT' else name)
        cmd = ['./client', a.host, '9000', a.operation, remote]
        if a.operation == 'PUT':
            cmd.append(str(Path('client-data') / name))
        elif a.operation == 'GET':
            cmd.append(str(local_dir / f'download-{client_id}.bin'))
        gate.wait()
        start = time.perf_counter()
        status, count, duration, rate, success, error = 0, 0, None, None, False, ''
        stdout, stderr = '', ''
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               timeout=a.timeout, check=False)
            stdout, stderr = r.stdout, r.stderr
            d = json.loads(stdout)
            status, count = int(d['status']), int(d['bytes'])
            duration = float(d['response_ms'])
            if not math.isfinite(duration) or duration <= 0 or count < 0:
                raise ValueError('telemetria numérica inválida')
            expected = 0 if a.operation == 'HEAD' else size
            success = r.returncode == 0 and 200 <= status < 300 and count == expected
            if success and a.operation != 'HEAD':
                rate = count * 8 / (duration / 1000) / 1e6
            error = str(d.get('error', ''))
            if not success and not error:
                error = 'retorno, status ou comprimento inesperado'
        except Exception as exc:
            success, rate = False, None
            error = f'{type(exc).__name__}: {exc}'
        end = time.perf_counter()
        # A verificação fica fora dos dois intervalos de desempenho.
        if success and a.operation != 'HEAD':
            target = (Path(a.server_root) / remote if a.operation == 'PUT'
                      else local_dir / f'download-{client_id}.bin')
            try:
                if digest(target) != expected_hash:
                    raise ValueError('SHA-256 divergente')
            except Exception as exc:
                success, rate = False, None
                error = f'integridade: {exc}'
        (local_dir / f'{client_id}.stdout').write_text(stdout, encoding='utf-8')
        (local_dir / f'{client_id}.stderr').write_text(stderr, encoding='utf-8')
        row = dict(base, run_id=run_id, repeat=repeat, client_id=client_id,
                   start_s=start, end_s=end, status=status, bytes=count,
                   response_ms=duration, throughput_mbps=rate,
                   success=int(success), error=error)
        return row

    with ThreadPoolExecutor(max_workers=a.concurrency) as pool:
        jobs = [pool.submit(request, i) for i in range(1, a.concurrency + 1)]
        # Início conservador da janela comum, antes da liberação.
        released = time.perf_counter()
        gate.wait()
        rows = [j.result() for j in jobs]
    elapsed = max(r['end_s'] for r in rows) - released
    successful = [r for r in rows if r['success']]
    for row in rows:
        append_csv(root / 'requests.csv', row)
    aggregate = (sum(r['bytes'] for r in successful) * 8 / elapsed / 1e6
                 if a.operation != 'HEAD' else None)
    append_csv(root / 'rounds.csv', dict(
        base, run_id=run_id, repeat=repeat, successes=len(successful),
        failures=a.concurrency-len(successful), round_ms=elapsed*1000,
        aggregate_mbps=aggregate))
print(root)
```

Exemplo no terminal C1, depois de implementar os executáveis e preparar a célula:

```bash
cd /work
python3 scripts/run_cell.py 10.0.4.2 A GET 2 8 --rounds 11
```

Cada chamada gera uma pasta exclusiva e não sobrescreve uma coleta anterior. Repita para todas as combinações da matriz, na ordem planejada. Mude o perfil **no CORE**, não apenas no argumento do script; esse argumento só identifica o CSV. Antes de PUT, crie no servidor os nomes `put_2_1.bin` até `put_2_32.bin` e equivalentes de 10 MiB com os arquivos de referência, conforme a célula. Por usarem nomes por cliente, chamadas do coletor não devem rodar simultaneamente.

O lançamento dos processos tem pequeno desvio de início, visível em `start_s`; não é simultaneidade perfeita. Para objetos muito pequenos, pode dominar a janela agregada. Registre essa limitação e, se necessário, implemente uma barreira nos clientes C antes de conectar. O tempo individual usa o cronômetro interno do cliente; a janela agregada inclui o lançamento dos processos. Ambos devem ser identificados no relatório.

O coletor verifica status, comprimento e SHA-256 automaticamente. Na verificação de PUT, precisa ter acesso ao diretório do servidor pelo sistema de arquivos: `--server-root` vale `server-data` por padrão, relativo ao diretório atual. Na montagem compartilhada deste roteiro, execute em `/work`, onde esse caminho identifica a mesma raiz usada pelo servidor em S1. Se a sessão isolar arquivos por nó, disponibilize a raiz para a verificação fora da rede medida ou adapte a verificação no nó S1 antes de iniciar a próxima rodada. Não declare sucesso sem verificar o conteúdo remoto. A falha de integridade fica identificada em `error` e exclui a transferência do total de bytes bem-sucedidos.

## 9. Analisar sem misturar cenários

### 9.1 Unidade de repetição

Uma célula é `(perfil, capacidade, atraso, método, tamanho, concorrência)`. Uma repetição é uma rodada completa de C clientes. As requisições de uma mesma rodada compartilham recursos e não são amostras independentes de rede. Para IC da média, use 11 valores por célula: por exemplo, a **média dos tempos dos clientes em cada rodada**, ou o goodput agregado de cada rodada.

Para cada métrica, apresente n válido, média, mediana, desvio padrão amostral e IC de 95%. Para a média de uma métrica por rodada:

```text
desvio amostral = sqrt(soma((x_i - média)^2) / (n - 1))
IC95% = média ± t(0,975; n-1) × desvio / sqrt(n)
```

O IC de Student é aproximado e pressupõe rodadas suficientemente independentes; não garante normalidade nem que 11 repetições bastem em toda situação. Verifique estabilidade, assimetria e outliers. Informe mediana/boxplot/CDF; se a incerteza for grande, aumente as repetições com critério documentado, sem apagar os primeiros dados. Um intervalo entre percentis descreve distribuição e não deve ser rotulado automaticamente como IC da média.

Apresente falhas por célula, inclusive timeouts. A análise de desempenho de rodadas totalmente bem-sucedidas deve vir acompanhada da quantidade de rodadas excluídas e taxa de sucesso. Não oculte falhas para melhorar médias.

### 9.2 Script de resumo

Após revisar integridade e dados, salve como `analysis/analyze.py`. Dependências: pandas, numpy e scipy. Ele gera resumos estatísticos para tempo e vazão, usa a rodada como unidade de IC e mantém uma tabela explícita de falhas.

```python
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import t

p = argparse.ArgumentParser()
p.add_argument('raw', nargs='?', default='experiments/raw')
p.add_argument('--out', default='experiments/summary')
a = p.parse_args()
files = sorted(Path(a.raw).glob('*/requests.csv'))
round_files = sorted(Path(a.raw).glob('*/rounds.csv'))
if not files or not round_files:
    raise SystemExit('dados de requisições e rodadas ausentes')
req = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
rounds = pd.concat([pd.read_csv(f) for f in round_files], ignore_index=True)
keys = ['profile', 'bandwidth_mbps', 'delay_oneway_ms', 'operation',
        'file_size_bytes', 'concurrency']
if req.duplicated(['run_id', 'client_id']).any() or rounds.run_id.duplicated().any():
    raise SystemExit('identificadores duplicados')
if not set(req.run_id) == set(rounds.run_id):
    raise SystemExit('requisições e rodadas não correspondem')
for run_id, part in req.groupby('run_id'):
    r = rounds.loc[rounds.run_id == run_id].iloc[0]
    if (len(part) != int(r.concurrency) or
        int(part.success.sum()) != int(r.successes) or
        int(r.successes) + int(r.failures) != int(r.concurrency)):
        raise SystemExit(f'contagem inconsistente em {run_id}')
    if any(part[k].nunique(dropna=False) != 1 or part[k].iloc[0] != r[k] for k in keys):
        raise SystemExit(f'fatores inconsistentes em {run_id}')
out = Path(a.out)
out.mkdir(parents=True, exist_ok=True)
failures = rounds.groupby(keys, dropna=False).agg(
    rounds_total=('run_id', 'size'), successes=('successes', 'sum'),
    failures=('failures', 'sum')).reset_index()
failures['success_rate'] = failures.successes / (failures.successes + failures.failures)
failures.to_csv(out / 'failures.csv', index=False)
complete = rounds.loc[rounds.failures.eq(0)].copy()
good = req.loc[req.run_id.isin(complete.run_id) & req.success.eq(1)]
means = good.groupby('run_id').agg(
    response_mean_ms=('response_ms', 'mean'),
    individual_mean_mbps=('throughput_mbps', 'mean'))
metrics = complete.merge(means, on='run_id', how='left')
metrics.to_csv(out / 'round_metrics.csv', index=False)
records = []
for values, part in metrics.groupby(keys, dropna=False):
    for metric in ['response_mean_ms', 'individual_mean_mbps', 'aggregate_mbps']:
        x = pd.to_numeric(part[metric], errors='coerce').dropna().to_numpy()
        if not np.isfinite(x).all():
            raise SystemExit(f'métrica não finita: {metric}')
        n = len(x)
        mean = float(x.mean()) if n else np.nan
        sd = float(x.std(ddof=1)) if n > 1 else np.nan
        half = float(t.ppf(.975, n-1)*sd/np.sqrt(n)) if n > 1 else np.nan
        records.append(dict(zip(keys, values), metric=metric, n=n,
            mean=mean, median=float(np.median(x)) if n else np.nan,
            std=sd, ci95_low=mean-half, ci95_high=mean+half))
pd.DataFrame(records, columns=keys + ['metric', 'n', 'mean', 'median', 'std',
    'ci95_low', 'ci95_high']).to_csv(out / 'summary.csv', index=False)
print(f'Resumos em {out}; confira n e failures.csv antes de interpretar os ICs.')
```

```bash
python3 -m venv .venv-analysis
source .venv-analysis/bin/activate
pip install pandas numpy scipy matplotlib
pip freeze > analysis/requirements-lock.txt
python analysis/analyze.py experiments/raw --out experiments/summary
```

Confira se todas as células planejadas estão presentes e têm pelo menos 11 rodadas válidas antes de interpretar os ICs. O script não sabe qual matriz foi planejada; essa conferência continua necessária. Se houver falhas, mostre-as e registre novas rodadas com novos IDs; não substitua silenciosamente as anteriores.

### 9.3 Gráficos e interpretação

Produza com `round_metrics.csv` e `summary.csv`, mantendo separados método, tamanho e perfil:

| Gráfico | Comparação e finalidade |
| --- | --- |
| Linhas: goodput agregado × concorrência, com IC | Detectar crescimento e platô; uma figura por perfil/método, linhas por tamanho |
| Pontos/barras: tempo médio × concorrência, com IC | Comparar custo de fila e compartilhamento, sem misturar tamanhos |
| Boxplot de médias por rodada | Mostrar variabilidade das repetições em condições equivalentes |
| CDF de tempo individual por célula | Mostrar distribuição descritiva; não tratar as linhas como repetições independentes para IC |
| Taxa de sucesso × concorrência | Mostrar quando a carga provoca recusas, timeouts ou corrupção |

Identifique unidades, n, nível do IC e fatores fixos nas legendas. Se usar barras de desvio padrão, nomeie-as como desvio, não IC. Não reúna A/B numa única distribuição sem explicar a mistura. Analise HEAD separadamente, pelo tempo e taxa de operações, sem fabricar vazão de arquivo.

Compare o platô da vazão agregada da aplicação à calibração iperf3 no mesmo sentido. Se a vazão agregada estabilizar perto da capacidade enquanto o tempo cresce, isso sustenta saturação do enlace. Se ficar muito abaixo, investigue CPU, disco, threads, cópias, janelas TCP e filas. O produto capacidade × RTT ajuda a avaliar a ordem de grandeza da janela necessária; é um diagnóstico, não uma prova isolada.

Reporte CPU/RAM/I/O do ambiente durante carga, por exemplo com `top`, `ps`, `vmstat` e contadores do enlace. No CORE, os nós compartilham recursos do hospedeiro: evite atribuir uma medição global exclusivamente ao servidor. O ponto de saturação é observado, não presumido por haver 32 clientes. Se não o encontrar, declare o limite da faixa avaliada.

## 10. Vídeo e submissão

Uma divisão possível de até 10 minutos:

| Tempo | Conteúdo |
| --- | --- |
| 0:00-0:50 | Integrantes, motivação e problema |
| 0:50-2:20 | O que foi implementado, arquitetura em C, métodos, erros e concorrência |
| 2:20-3:30 | Demonstração curta de GET/PUT, sobrescrita e integridade |
| 3:30-5:00 | Onde executou: CORE, topologia, gargalo e validação ping/traceroute/iperf |
| 5:00-7:40 | Matriz, repetições, métricas, gráficos, resultados e explicação do desempenho |
| 7:40-8:40 | Gargalos, saturação observada e limitações |
| 8:40-9:20 | Contribuição de cada integrante |
| 9:20-9:50 | Autoavaliação do grupo e conclusões |

Deixe margem para não ultrapassar 10 minutos. Use resultados medidos; não narre números ilustrativos deste roteiro. Explique decisões e limitações de protocolo/ambiente. Se a ambiguidade sobre métodos tiver sido esclarecida, registre a interpretação aplicada.

**Entrega no Classroom até 05/11/2026: código(s) do servidor e link do vídeo.** Hospede o vídeo na nuvem e conceda acesso ao professor; teste a permissão com outra sessão/conta. Não envie o arquivo de vídeo pelo Classroom. Inclua fontes e instruções de compilação conforme o mecanismo da atividade. Cliente C, sessão CORE, dados brutos, scripts e README são complementos recomendados para reprodução; não substituem os dois entregáveis explícitos.

## 11. Checklist de conclusão

- [ ] Até três integrantes identificados; prazo de 05/11/2026 conferido.
- [ ] Servidor e cliente usam sockets em C e foram compilados no ambiente dos nós.
- [ ] GET/PUT e sobrescritas verificadas por tamanho e SHA-256.
- [ ] Atendimento realmente simultâneo; sem temporários compartilhados por acidente.
- [ ] Códigos de erro e transferências interrompidas testados.
- [ ] Interpretação de HTTP e quantidade de operações documentada; HEAD incluído se usada a alternativa conservadora.
- [ ] Sessão CORE salva, duas redes de acesso distintas, núcleo e rotas completas.
- [ ] Um gargalo com capacidade/atraso registrados por sentido; sem erro/perda configurados.
- [ ] Ping fim a fim/até roteadores, traceroute e iperf3 nos dois sentidos preservados por perfil.
- [ ] Dois tamanhos associados e justificados para duas aplicações de Internet.
- [ ] Duas tecnologias de acesso e níveis de baixa/média/alta concorrência representados.
- [ ] Pelo menos 11 rodadas por célula; dados faltantes/falhas e novas tentativas identificados.
- [ ] Tempos e vazões GET/PUT coletados com limites/unidades claros; integridade dos resultados revisada.
- [ ] Vazão individual e agregada distinguidas; nenhuma soma inadequada de taxas.
- [ ] Média, mediana, desvio e IC calculados por cenário, com rodada como unidade independente.
- [ ] Gráficos separados pelos fatores; gargalos e saturação sustentados pelos dados ou limite da avaliação declarado.
- [ ] README com versões, comandos, matriz, política de cache/sincronização e contribuições.
- [ ] Vídeo até 10 minutos com todos os tópicos, contribuições e autoavaliação.
- [ ] Código(s) do servidor e link acessível do vídeo submetidos no Classroom.

## 12. Fontes e limites desta revisão

As exigências acadêmicas foram extraídas exclusivamente do [enunciado local](referencias/trabalho1_redes_enunciado.pdf), pp. 1-4. Os defeitos do roteiro anterior referem-se ao [guia local](referencias/guia_execucao_trabalho1_redes.pdf), pp. 1-21. A documentação técnica oficial e os levantamentos primários estão vinculados junto às recomendações correspondentes; foram consultados em 03/11/2026.

Nenhum resultado experimental foi produzido nesta revisão. A instalação do CORE, a compilação da aplicação C, as transferências, a calibração e a campanha precisam ser executadas pelo grupo. As bibliotecas e programas de coleta/análise não substituem a implementação da aplicação exigida pelo trabalho.

Verificações deste Markdown: sintaxe dos dois blocos Python; contagens da matriz e estimativas de transmissão; referências locais; e 143 requisições simuladas no coletor, cobrindo GET/PUT/HEAD, concorrência, JSON inválido, timeout e conteúdo corrompido. As contagens de sucesso/falha, a ausência de vazão de conteúdo para HEAD e a detecção de hash divergente passaram nesses testes. O script estatístico teve a sintaxe verificada, mas não foi executado com suas dependências nem com dados reais.
