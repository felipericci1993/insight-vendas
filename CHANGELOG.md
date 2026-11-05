# Histórico de mudanças

## 1.0.1 · 05/11/2026

- Corrige a distribuição dos filtros com quebra de linha e largura mínima para os campos.
- Revisão desktop confirma que “Todas as categorias” aparece inteiro, sem sobreposição dos controles.
- Revalida filtros combinados, busca de pedido, limpeza e troca de mês na prévia oficial.
- Inclui a captura desktop atual, documentação de publicação e limites explícitos da validação.
- Mantém os cálculos e o JavaScript da versão anterior. Os 27 testes Python continuam aprovados.

**Pendente:** QA mobile, roteiro automatizado de navegador completo, outros navegadores e validações adicionais descritas em `docs/TESTES.md`. O código está disponível no repositório público; não há hospedagem do painel. Consulte Actions para o resultado remoto de cada commit.

## 1.0.0 · 05/11/2026

- Primeira demonstração: validação CSV, cálculos em centavos, painel HTML offline e exportações.
- Base fictícia com 120 pedidos válidos e três rejeições deliberadas.
- Testes Python, configuração de CI e documentação técnica.
- QA desktop inicial de filtros, busca, limpeza, paginação, modais e exportação.
