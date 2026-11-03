# Testes

A tarefa T03 criará o executor de testes da aplicação. Já existem testes automatizados do diagnóstico de ambiente:

```bash
python3 -m unittest discover -s tests -p 'test_environment.py' -v
```

No Windows, use `python` no lugar de `python3`. Os testes simulam comandos e falhas de ferramentas; não comprovam disponibilidade real de Linux/CORE. Eles não são a suíte funcional da aplicação.

Cobertura prioritária:

- Parsing de mensagens, comprimentos inválidos, transferência parcial e conteúdo binário.
- GET/PUT com criação e sobrescrita, comparados por SHA-256.
- Ausência de arquivo, permissão, desconexão e corpo truncado.
- Atendimento simultâneo e PUTs do mesmo nome sem corrupção.
- Contrato JSON e limites do cronômetro.
- Coletor e análise com dados sintéticos identificados em `tests/fixtures/`.

Separe testes funcionais em localhost dos testes emulados no CORE. Não considere descoberta de zero casos um teste aprovado. Exemplos de entrada e saída devem deixar claro quando forem sintéticos, sem serem copiados para a campanha.
