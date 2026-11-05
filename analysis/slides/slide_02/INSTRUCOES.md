# Slide 2 — O que foi desenvolvido e como

## Uso dos materiais

Inserir arquitetura.png ou arquitetura.svg. arquitetura.mmd permite editar o esquema em Mermaid; as imagens já estão renderizadas.

## Conteúdo e fala do roteiro

**Adicionar ao slide:** diagrama `Cliente C → TCP / subconjunto de HTTP → Servidor C`; três linhas: GET baixa, PUT envia, HEAD consulta metadados; pequenos rótulos “thread por conexão”, “temporário exclusivo” e “publicação com rename”. No rodapé: `src/client.c`, `src/server.c`, `src/protocol.c`.

**Fala sugerida — Integrante 1:**

> Implementamos cliente e servidor com a API de sockets POSIX em C. O protocolo é um subconjunto controlado de HTTP sobre TCP, com uma operação por conexão. GET recebe um arquivo, PUT envia um arquivo ao servidor e HEAD consulta os metadados sem transferir seu conteúdo. O servidor cria uma thread por conexão para permitir atendimento concorrente. A implementação trata mensagens parciais e usa arquivos temporários exclusivos antes da publicação do destino. Isso reduz o risco de deixar um arquivo parcialmente transferido como resultado final. HEAD foi incluído como extensão conservadora do grupo, considerando a ambiguidade apontada no guia.

**Orientação visual:** apresentar o fluxo e as decisões; evitar uma captura de código com dezenas de linhas. Não afirmar conformidade completa com HTTP.
