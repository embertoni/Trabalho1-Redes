# Contrato do protocolo e das interfaces

## 1. Escopo

A aplicação implementa um subconjunto controlado de HTTP sobre TCP, usando sockets POSIX em C.

Este contrato não declara conformidade completa com HTTP. O protocolo foi definido para atender às operações do trabalho, permitir transferências binárias e fornecer respostas estruturadas.

Operações obrigatórias:

- `GET`: baixar um arquivo do servidor;

- `PUT`: enviar um arquivo ao servidor.

Operação adicional proposta:

- `HEAD`: consultar metadados sem transferir o corpo do arquivo.

A operação `HEAD` é uma extensão conservadora adotada pelo grupo devido à ambiguidade do enunciado. Ela será documentada separadamente das métricas obrigatórias de GET e PUT.

## 2. Transporte

- Transporte: TCP.

- Servidor: aceita conexões TCP.

- Porta padrão: `9000`.

- Cada conexão atende uma operação.

- Após enviar a resposta, o servidor encerra a conexão.

- O servidor atende clientes simultâneos usando uma thread POSIX por conexão.

- Não existe uma mensagem por `send()` ou `recv()`; o código deve tratar mensagens parciais.

- O servidor deve aceitar clientes conectados simultaneamente sem serializar transferências completas com um lock global.

## 3. Requisições

A requisição possui um cabeçalho textual terminado por `\r\n\r\n`. Os cabeçalhos utilizam codificação ASCII compatível com HTTP. O corpo do `PUT` pode conter qualquer sequência de bytes e não deve ser tratado como texto.

### GET

```
GET /arquivo.bin HTTP/1.1

Host: servidor

Connection: close
```

O `GET` solicita o conteúdo completo do arquivo remoto.

### HEAD

```
HEAD /arquivo.bin HTTP/1.1

Host: servidor

Connection: close
```

O `HEAD` solicita os metadados que seriam retornados por um `GET`, mas sem o corpo do arquivo.

### PUT

```
PUT /arquivo.bin HTTP/1.1

Host: servidor

Content-Length: 1048576

Connection: close



<bytes binários do arquivo>
```

O corpo do `PUT` possui exatamente o número de bytes informado em `Content-Length`.

O servidor deve rejeitar o `PUT` quando:

- `Content-Length` estiver ausente;

- `Content-Length` não for um número decimal válido;

- `Content-Length` for negativo;

- o valor ultrapassar o limite máximo configurado;

- o corpo recebido for menor que o tamanho declarado;

- houver bytes adicionais incompatíveis com a operação definida.

## 4. Caminhos de arquivos

O caminho remoto deve:

- iniciar com `/`;

- conter apenas um nome de arquivo simples;

- não conter diretórios;

- não conter `..`;

- não conter `.` como componente;

- não conter barras adicionais depois da barra inicial;

- não conter bytes NUL;

- não ultrapassar o limite de tamanho definido pelo programa;

- não escapar da raiz de dados do servidor.

Exemplos válidos:

```
/arquivo.bin
/teste.dat
/imagem.jpg
```

Exemplos inválidos:

```
../arquivo.bin
/a/arquivo.bin
/./arquivo.bin
/../segredo
/a//b.bin
```

Os arquivos ficam confinados à raiz de dados do servidor. A implementação deve evitar traversal de diretórios e não deve confiar apenas na remoção textual de `..` para garantir segurança contra links simbólicos.

A versão inicial do contrato aceita somente nomes remotos planos, sem subdiretórios. Essa restrição reduz ambiguidades na implementação, nos testes e na campanha experimental.

## 5. Limites

Os limites iniciais são:

- porta: `1` a `65535`;

- tamanho máximo do caminho remoto: `255` bytes;

- tamanho máximo do cabeçalho: `8192` bytes;

- tamanho máximo do arquivo: `1 GiB` (`1073741824` bytes), salvo configuração menor na linha de comando;

- `Content-Length` obrigatório para `PUT`;

- `Content-Length` não pode ser negativo;

- valores numéricos devem ser decimais completos, sem caracteres extras;

- cabeçalho malformado deve ser rejeitado;

- método desconhecido deve ser rejeitado;

- campos obrigatórios repetidos ou contraditórios devem ser rejeitados;

- o limite de leitura deve impedir que um cabeçalho ilimitado consuma memória.

Os limites que forem compartilhados entre o parser, o servidor e o cliente devem ser centralizados em `src/protocol.h`.

## 6. Respostas

A resposta possui cabeçalho textual terminado por `\r\n\r\n`.

### Formato geral de sucesso

```
HTTP/1.1 200 OK

Content-Length: 1234

Connection: close



<corpo opcional>
```

### GET bem-sucedido

- status: `200 OK`;

- `Content-Length`: tamanho do arquivo;

- corpo: bytes completos do arquivo.

Exemplo:

```
HTTP/1.1 200 OK

Content-Length: 1234

Connection: close



<1234 bytes do arquivo>
```

### HEAD bem-sucedido

- status: `200 OK`;

- `Content-Length`: tamanho do arquivo;

- corpo: vazio.

Exemplo:

```
HTTP/1.1 200 OK

Content-Length: 1234

Connection: close
```

### PUT bem-sucedido

Quando o arquivo é criado:

```
HTTP/1.1 201 Created

Content-Length: 0

Connection: close
```

Quando o arquivo existente é substituído:

```
HTTP/1.1 200 OK

Content-Length: 0

Connection: close
```

A política adotada é que `PUT` sempre substitui o arquivo existente. O servidor pode usar `201 Created` para arquivo novo e `200 OK` para sobrescrita.

### Erros

| Código | Motivo | Uso esperado |
| --- | --- | --- |
| `400` | Bad Request | Requisição malformada, cabeçalho inválido ou caminho inválido |
| `404` | Not Found | Arquivo inexistente em `GET` ou `HEAD` |
| `405` | Method Not Allowed | Método reconhecido, mas não permitido para a operação |
| `413` | Content Too Large | Corpo ou arquivo maior que o limite |
| `500` | Internal Server Error | Erro interno inesperado |
| `501` | Not Implemented | Método não implementado |
| `507` | Insufficient Storage | Falha para criar, gravar ou publicar o arquivo |

As respostas de erro devem conter, no mínimo:

```
HTTP/1.1 404 Not Found

Content-Length: 0

Connection: close
```

O servidor deve enviar uma resposta estruturada sempre que a fase do protocolo permitir. Se ocorrer uma falha depois que o cabeçalho de sucesso e parte do corpo já foram enviados, não é possível inserir uma nova resposta HTTP na mesma conexão; nesse caso, o cliente deve detectar a transferência incompleta e registrar a falha.

## 7. Integridade do PUT

O servidor deve:

1. validar a requisição e o caminho remoto;

1. validar o `Content-Length` antes de alocar ou gravar recursos;

1. criar um arquivo temporário exclusivo por operação;

1. receber exatamente `Content-Length` bytes;

1. tratar `recv()` parcial;

1. detectar desconexão ou truncamento;

1. fechar o arquivo corretamente;

1. sincronizar os dados quando essa política estiver habilitada;

1. publicar o resultado com `rename()` atômico;

1. remover o temporário em caso de falha.

Não deve existir um arquivo temporário compartilhado entre threads.

O PID não pode ser usado como único identificador do temporário, pois várias threads do mesmo processo compartilham o mesmo PID. A implementação deve preferir `mkstemp()` ou mecanismo equivalente que produza um temporário exclusivo.

O arquivo final não deve ser truncado ou substituído antes que a transferência completa seja validada. Em caso de falha, o arquivo anterior deve permanecer intacto sempre que possível.

## 8. Integridade do GET

O servidor deve:

1. validar o método e o caminho;

1. abrir o arquivo somente dentro da raiz autorizada;

1. obter o tamanho do arquivo;

1. enviar o cabeçalho completo;

1. enviar todos os bytes do arquivo;

1. tratar `send()` parcial;

1. detectar erro de leitura ou desconexão;

1. encerrar a conexão após a operação.

O cliente deve:

1. iniciar a medição antes de estabelecer a conexão;

1. receber e validar o cabeçalho;

1. confirmar o código de resposta;

1. ler exatamente o `Content-Length` informado;

1. detectar corpo menor que o tamanho declarado;

1. gravar o conteúdo em arquivo temporário exclusivo;

1. substituir o destino local somente após a transferência completa;

1. remover o temporário em caso de falha.

O destino local não deve ser truncado antes de uma transferência válida ser concluída.

## 9. Interface do servidor

Formato geral:

```
build/server [opções]
```

Opções mínimas:

```
--host ENDEREÇO
--port PORTA
--root DIRETÓRIO
--max-file-size BYTES
--help
```

Exemplo:

```bash
build/server \
  --host 0.0.0.0 \
  --port 9000 \
  --root server-data
```

Valores padrão:

```
host: 0.0.0.0
port: 9000
root: server-data
max-file-size: 1073741824
```

O servidor deve:

- criar o socket TCP;

- configurar as opções necessárias;

- associar o endereço e a porta;

- entrar em modo de escuta;

- aceitar conexões;

- criar um atendimento independente por conexão;

- fechar corretamente os descritores;

- enviar diagnósticos para `stderr`;

- não misturar logs de diagnóstico com dados estruturados do cliente.

## 10. Interface do cliente

Formato geral:

```
build/client --host ENDEREÇO --port PORTA --method MÉTODO --remote CAMINHO [opções]
```

### GET

```bash
build/client \
  --host 10.10.5.10 \
  --port 9000 \
  --method GET \
  --remote /arquivo.bin \
  --output client-output/arquivo.bin
```

### PUT

```bash
build/client \
  --host 10.10.5.10 \
  --port 9000 \
  --method PUT \
  --remote /arquivo.bin \
  --input client-data/arquivo.bin
```

### HEAD

```bash
build/client \
  --host 10.10.5.10 \
  --port 9000 \
  --method HEAD \
  --remote /arquivo.bin
```

Opções adicionais:

```
--connect-timeout SEGUNDOS
--io-timeout SEGUNDOS
--request-id IDENTIFICADOR
--help
```

Regras da interface:

- `--host`, `--port`, `--method` e `--remote` são obrigatórios;

- `GET` exige `--output`;

- `PUT` exige `--input`;

- `HEAD` não exige arquivo de saída;

- argumentos desconhecidos devem causar erro;

- diagnósticos detalhados devem ser enviados para `stderr`;

- o cliente deve produzir exatamente uma linha JSON em `stdout` para cada tentativa, inclusive quando houver falha.

## 11. JSON do cliente

O cliente deve produzir uma linha JSON válida por tentativa.

### Sucesso em GET

```json
{"status":"ok","method":"GET","remote":"/arquivo.bin","status_code":200,"bytes":1048576,"elapsed_ms":23.41,"throughput_mbps":361.22,"error":null}
```

### Sucesso em PUT

```json
{"status":"ok","method":"PUT","remote":"/arquivo.bin","status_code":201,"bytes":1048576,"elapsed_ms":25.17,"throughput_mbps":334.84,"error":null}
```

### Falha remota

```json
{"status":"error","method":"GET","remote":"/inexistente.bin","status_code":404,"bytes":0,"elapsed_ms":2.13,"throughput_mbps":null,"error":"remote_file_not_found"}
```

### Falha de conexão

```json
{"status":"error","method":"GET","remote":"/arquivo.bin","status_code":0,"bytes":0,"elapsed_ms":1000.42,"throughput_mbps":null,"error":"connection_failed"}
```

Campos mínimos:

| Campo | Tipo | Regra |
| --- | --- | --- |
| `status` | string | `ok` ou `error` |
| `method` | string | `GET`, `PUT` ou `HEAD` |
| `remote` | string | caminho remoto solicitado |
| `status_code` | inteiro | código recebido ou `0` se não houve resposta |
| `bytes` | inteiro | bytes úteis transferidos |
| `elapsed_ms` | número | tempo total da tentativa em milissegundos |
| `throughput_mbps` | número ou `null` | vazão útil; `null` quando não aplicável ou quando a operação falhar |
| `error` | string ou `null` | motivo da falha; `null` em caso de sucesso |

Para `HEAD`:

```
bytes: 0
throughput_mbps: null
```

Os valores numéricos devem ser emitidos como números JSON, não como strings.

## 12. Medição

O cronômetro deve usar relógio monotônico, como `clock_gettime(CLOCK_MONOTONIC, ...)`.

Para GET e PUT, o tempo inclui:

1. criação da conexão;

1. envio da requisição;

1. envio do corpo, quando existente;

1. recebimento da resposta;

1. recebimento do corpo, no GET;

1. conclusão definida da operação;

1. encerramento ou fechamento da conexão.

O tempo termina quando a operação é concluída ou quando ocorre uma falha definitiva.

Falhas não devem ser convertidas em amostras de sucesso com vazão zero. Elas devem permanecer identificadas como falhas no JSON e nos dados de análise.

A vazão útil será calculada por:

```
throughput_mbps = bytes * 8 / elapsed_seconds / 1e6
```

Para GET, `bytes` representa os bytes do arquivo recebidos.

Para PUT, `bytes` representa os bytes do arquivo enviados.

Para HEAD, a vazão de conteúdo não é aplicável e deve ser `null`.

A medição deve registrar claramente se inclui conexão, processamento remoto e encerramento da conexão. Essa política deve permanecer idêntica em todas as rodadas da campanha.

## 13. Concorrência

O servidor deve permitir múltiplos clientes conectados simultaneamente.

A unidade de atendimento é uma conexão. Cada conexão deve possuir:

- buffers próprios;

- estado próprio;

- temporário próprio;

- métricas próprias;

- tratamento de erro próprio.

O servidor não deve usar um lock global para serializar transferências completas. Locks, quando necessários, devem proteger somente estruturas compartilhadas e trechos curtos.

A aplicação deve tratar corretamente:

- várias conexões simultâneas;

- conexões encerradas prematuramente;

- requisições para arquivos diferentes;

- requisições simultâneas para o mesmo nome remoto;

- respostas parciais;

- arquivos binários;

- cabeçalhos maiores que o limite;

- tamanhos inválidos;

- falhas de leitura e escrita.

A unidade estatística independente da campanha será a rodada, não cada cliente concorrente individual da mesma rodada.

## 14. Compatibilidade com o repositório

Os arquivos-fonte ficarão em:

```
src/
```

Os executáveis ficarão em:

```
build/server
build/client
```

A compilação será feita pelo `Makefile` da raiz.

A implementação inicial será organizada em:

```
src/protocol.h
src/protocol.c
src/server.c
src/client.c
```

O protocolo compartilhado será implementado inicialmente em:

```
src/protocol.h
src/protocol.c
```

O código deve seguir as opções de compilação já definidas no `Makefile`:

```
-std=c11 -Wall -Wextra -Wpedantic -O2 -g
```

A aplicação será executada em Linux/CORE. O Windows/WSL é utilizado para preparação, compilação auxiliar e organização, mas os resultados experimentais obrigatórios serão produzidos no CORE.

Este documento define uma proposta técnica do grupo. Os requisitos explícitos do enunciado e eventuais esclarecimentos do professor prevalecem sobre as escolhas propostas aqui, especialmente quanto à inclusão do método `HEAD` e aos detalhes do protocolo.
