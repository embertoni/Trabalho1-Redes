# Fase 2 — Protocolo e implementação

## Contrato do protocolo

O usuário informou que havia criado `docs/CONTRATO_PROTOCOLO.md` apenas com o início da especificação GET e perguntou o que faltava. Foi explicado que o documento deveria definir o protocolo antes da implementação.

O arquivo completo foi então gerado e disponibilizado. Ele especifica:

- escopo;
- TCP e porta 9000;
- GET, PUT e HEAD;
- formato de cabeçalhos;
- `Content-Length`;
- caminhos válidos e prevenção de traversal;
- limites;
- códigos de resposta;
- integridade do PUT;
- integridade do GET;
- concorrência;
- interface do servidor;
- interface do cliente;
- formato JSON;
- medição de tempo e vazão;
- compatibilidade com o repositório.

O usuário colou o arquivo no repositório e confirmou a conclusão dessa etapa.

## `src/protocol.h`

Foi criada a interface compartilhada do protocolo com:

- constantes de porta e limites;
- enums de resultado, método e status;
- estruturas de requisição, resposta e limites;
- funções para validação de caminhos;
- construção e análise de requisições e respostas;
- envio e recebimento parciais;
- cópia binária.

O usuário apresentou o resultado de `git status --short`, contendo os arquivos de documentação, topologia, calibração e `src/protocol.h`. A saída foi considerada compatível.

## `src/protocol.c`

Foi fornecida uma implementação completa para:

- conversão de métodos;
- frases de status;
- validação de caminho;
- localização de `\r\n\r\n`;
- parser de requisições;
- parser de respostas;
- construção de mensagens;
- `protocol_send_all`;
- recebimento de cabeçalhos;
- cópia exata de arquivos.

A compilação foi realizada com:

```bash
gcc \
  -D_POSIX_C_SOURCE=200809L \
  -Isrc \
  -std=c11 \
  -Wall \
  -Wextra \
  -Wpedantic \
  -O2 \
  -g \
  -pthread \
  -c src/protocol.c \
  -o /tmp/protocol.o
```

## Correção do AddressSanitizer

Os testes encontraram overflow de pilha em `sscanf`, causado por:

```c
"%31s %257s %31s %n"
```

O vetor possuía 257 bytes, mas `%257s` poderia escrever 258 bytes incluindo o terminador. A correção mínima foi:

```c
"%31s %256s %31s %n"
```

Depois da correção, os testes com AddressSanitizer passaram.

## Testes unitários

Foi criado `tests/test_protocol.c`, com testes de:

- valores padrão;
- métodos;
- frases de status;
- caminhos válidos e inválidos;
- fim de cabeçalho;
- GET;
- PUT;
- HEAD;
- respostas;
- `socketpair`;
- buffers pequenos;
- casos negativos.

Comando de execução:

```bash
/tmp/test_protocol
```

Resultado esperado:

```text
test_protocol: todos os testes passaram
```

Também foi utilizada compilação com:

```bash
-fsanitize=address,undefined
```

## Servidor

O usuário pediu o `server.c` completo em vez de subetapas. Foi gerado um servidor completo com:

- socket TCP;
- `bind`;
- `listen`;
- `accept`;
- uma thread POSIX por conexão;
- GET;
- HEAD;
- PUT;
- arquivos binários;
- temporário exclusivo com `mkstemp`;
- `fsync`;
- publicação atômica com `rename`;
- respostas de erro;
- limites de arquivo;
- validação da raiz;
- fechamento de descritores.

O arquivo foi disponibilizado como `server.c` para cópia em:

```text
src/server.c
```

## Cliente

Foi gerado um `client.c` completo com:

- GET;
- PUT;
- HEAD;
- argumentos de linha de comando;
- conexão TCP;
- transferência binária;
- temporário exclusivo para GET;
- publicação atômica;
- relógio monotônico;
- cálculo de vazão;
- uma linha JSON por tentativa;
- tratamento de falhas.

O arquivo foi disponibilizado para cópia em:

```text
src/client.c
```

## Integração local

A validação local foi organizada com:

```bash
make clean
make build
```

Foram testados:

- PUT de arquivo pequeno;
- GET do mesmo arquivo;
- HEAD;
- arquivo inexistente;
- arquivos binários de 1 MiB e 2 MiB;
- sobrescrita;
- dez GETs concorrentes;
- comparação de hashes.

A etapa foi considerada concluída quando os binários oficiais `build/server` e `build/client` passaram a compilar e os arquivos permaneceram íntegros.
