# Slide 5 — Demonstração e cobertura dos dados

## Uso dos materiais

Usar cobertura_registros.png e um clipe real de cerca de 15 segundos. registros_reais.json pode ser exibido como alternativa rotulada “registro da campanha”. Para gravar: 1) preparar cliente/servidor C; 2) mostrar GET e PUT completos e sua saída; 3) identificar CORE ou localhost; 4) guardar o clipe nesta pasta com nome próprio, como demonstracao_real.mp4; 5) inserir o clipe na apresentação. O notebook não executa essas operações nem sobrescreve o vídeo. Sobrescrita só deve ser anunciada com evidência antes/depois. Localhost demonstra função, não valida a topologia CORE.

## Conteúdo e fala do roteiro

**Adicionar ao slide:** clipe de aproximadamente 15 segundos mostrando uma execução real de GET e PUT com os executáveis C e sua saída JSON; ao lado, resumo do notebook: 36/36 células com 11 rodadas completas; zero requisições ausentes; zero falhas detectadas nos critérios avaliados. Rodapé: “Integridade de PUT no destino: não comprovada pelos hashes preservados”.

**Fala sugerida — Integrante 1:**

> Aqui mostramos a interface do cliente e a saída estruturada que registra código de resposta, bytes, duração e vazão. Na campanha analisada, todas as 36 configurações têm as 11 rodadas completas previstas. Não encontramos requisições ausentes nem falhas nos critérios de telemetria avaliados, e os hashes preservados de GET não apresentaram divergências. Isso demonstra cobertura e consistência dos registros analisados, mas não comprova todas as propriedades do sistema: no PUT, falta o hash do arquivo publicado no servidor.

**Preparação:** gravar o clipe antes do vídeo, em ambiente disponível e identificado. Caso a demonstração seja em localhost, rotular “demonstração funcional em localhost”; ela não representa evidência da topologia CORE. Se não houver nova execução, mostrar registros existentes com a legenda “registro da campanha”, sem simular uma execução ao vivo. Não mostrar comandos digitados sem tempo para sua execução real. Teste de sobrescrita só deve ser anunciado como demonstrado se houver evidência antes/depois.
