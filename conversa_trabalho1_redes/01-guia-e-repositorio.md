# Fase 1 — Guia, repositório e ambiente

## Solicitação inicial

O usuário solicitou a análise do PDF anexado, a elaboração de um guia detalhado para execução do trabalho em Windows, a identificação das ferramentas necessárias, os procedimentos de download e instalação e a descrição clara de todos os requisitos e da melhor abordagem de solução.

Foi produzido um guia em DOCX/PDF com base no enunciado, incluindo WSL2, Docker, CORE, Vagrant/VirtualBox, compilação, topologia e implementação.

## Atualização solicitada

O usuário pediu que o guia fosse atualizado com os códigos completos necessários. Foi incorporado um apêndice com a implementação de referência, incluindo protocolo, servidor e cliente, e a implementação foi compilada e testada.

## Repositório correto

Inicialmente foi analisado um repositório incorreto. O usuário informou o repositório correto:

```text
https://github.com/embertoni/Trabalho1-Redes
```

O repositório correto foi confirmado e foram consultados os arquivos:

```text
AGENTS.md
docs/AMBIENTE.md
Makefile
scripts/check-environment.ps1
scripts/check-environment.sh
docs/STATUS.md
docs/DECISOES.md
docs/GUIA_COMPLETO_TRABALHO1_REDES.md
```

A partir desse momento, todas as orientações passaram a considerar esse repositório.

## Instalação e validação do ambiente

O desenvolvimento foi organizado para Windows com WSL2, Docker Desktop e CORE em contêiner. Foram considerados:

- Windows/PowerShell para instalação e diagnóstico;
- WSL2/Ubuntu para compilação e comandos Linux;
- Docker Desktop com integração WSL2;
- CORE em contêiner privilegiado;
- GCC, Make, Python, iproute2, ping, traceroute e iperf3.

A validação foi realizada com os scripts de ambiente do repositório. O usuário confirmou que a etapa de instalação e diagnóstico estava concluída.

## Construção do CORE

Durante a construção do CORE, ocorreu erro porque o `Dockerfile.ubuntu` referenciava a imagem intermediária `emane-python:latest` sem que ela tivesse sido criada. A correção foi construir primeiro a imagem intermediária e depois a imagem principal:

```bash
docker build \
  -t emane-python \
  -f dockerfiles/Dockerfile.emane-python .

docker build \
  -t core-trabalho1 \
  -f dockerfiles/Dockerfile.ubuntu .
```

Também foi identificado que `traceroute` e `iperf3` não estavam disponíveis dentro do contêiner. A orientação foi instalá-los no ambiente do CORE e repetir a validação:

```bash
apt-get update
apt-get install -y traceroute iperf3
```

Depois da correção, a Etapa 2 foi considerada concluída.

## Topologia inicial

Foi criada e validada uma topologia mínima no CORE, seguida da topologia definitiva com:

- Cliente;
- Servidor;
- roteadores de acesso;
- roteadores de núcleo;
- enlace de gargalo;
- redes de acesso distintas para Cliente e Servidor;
- rotas estáticas;
- testes de `ping`, `traceroute` e `iperf3`.

A topologia consolidada utiliza, entre outras, as redes:

```text
10.10.1.0/24
10.10.2.0/30
10.10.3.0/30
10.10.4.0/30
10.10.5.0/24
```

Com os endereços principais:

```text
Cliente: 10.10.1.10
Servidor: 10.10.5.10
```

O enlace de gargalo foi definido entre:

```text
R_Nucleo_1 e R_Nucleo_2
```

## Arquivos criados na preparação

```text
docs/CONTRATO_PROTOCOLO.md
experiments/calibration/topologia-etapa4.txt
topology/trabalho1-etapa4.xml
topology/trabalho1-etapa4-perfil-A.xml
```

O usuário confirmou a conclusão da preparação da topologia e solicitou o início da implementação guiada.
