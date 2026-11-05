# Slide 3 — Onde: topologia e perfis

## Uso dos materiais

Usar topologia.png como desenho da sessão salva. Para uma captura real, abrir no CORE o XML do perfil desejado, enquadrar nós/gargalo e gravar a tela separadamente. O notebook não inicia sessão. O campo zero de capacidade em outros enlaces é apenas o parâmetro salvo, não uma vazão medida zero. Rotas e calibração exigem validação própria.

## Conteúdo e fala do roteiro

**Adicionar ao slide:** captura legível da sessão CORE salva ou desenho fiel `Cliente → acesso → núcleo → gargalo → núcleo → acesso → Servidor`; cliente `10.10.1.10`, servidor `10.10.5.10`; destacar `R_Nucleo_1 ↔ R_Nucleo_2`. Tabela:

| Perfil | Capacidade nominal | Atraso configurado por sentido | Perda configurada |
| --- | --- | --- | --- |
| A | 100 Mbit/s | 5 ms | 0% |
| B | 20 Mbit/s | 20 ms | 0% |

**Fala sugerida — Integrante 2:**

> A topologia salva no CORE coloca cliente e servidor em redes de acesso distintas, conectadas por um núcleo. O enlace entre os dois roteadores de núcleo representa o gargalo. Comparamos o perfil A, de 100 megabits por segundo e 5 milissegundos de atraso por sentido, ao perfil B, de 20 megabits e 20 milissegundos. Não configuramos perda. Os perfis representam condições simplificadas de acesso fixo e móvel, e não características universais dessas tecnologias. Esses valores são parâmetros configurados; a comprovação da calibração é uma limitação que retomaremos.

**Conferência:** os XMLs de A/B preservam `delay=5000/20000` e `bandwidth=100000000/20000000`. A descrição antiga `topologia-etapa4.txt` usa “latência 10 ms” sem a mesma precisão por sentido; use os valores dos XMLs e da matriz, sem chamá-los de RTT medido.
