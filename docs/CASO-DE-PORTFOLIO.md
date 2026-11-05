# Insight Vendas: automação de relatório a partir de CSV

## Natureza do projeto

Exemplo fictício, preparado para estudo e portfólio. Casa Prisma não é um cliente atendido. Nenhuma receita ou melhoria apresentada é um resultado de trabalho comercial real.

## Cenário

Uma loja recebe exportações de vendas e precisa repetir o mesmo processo: identificar linhas inválidas, remover pedidos duplicados da análise e preparar um resumo para consulta. O desafio demonstrado é tornar essa rotina reproduzível e rastreável.

## Solução implementada

Um comando Python lê um CSV, valida os campos e produz quatro arquivos: painel HTML offline, resumo JSON, base tratada e relatório de rejeições. O painel permite filtrar por mês, categoria e região, buscar pedidos e baixar o recorte em CSV.

A interface mostra faturamento após descontos, quantidade de pedidos concluídos, ticket médio, valores pendentes, evolução temporal e participação por categoria. O QA desktop inicial pela prévia oficial aprovou os filtros, a busca, a limpeza, a paginação, os modais e a exportação. Um texto cortado no seletor de categoria motivou o ajuste de layout da versão 1.0.1. A revisão desktop da versão 1.0.1 confirmou a correção do texto e filtros em duas linhas sem sobreposição. Filtros combinados, busca, limpeza e troca de mês foram rechecados. A homologação mobile continua pendente.

## O que o código demonstra

- Python para processamento de arquivos e automação repetível.
- Validação de dados, tratamento de erros e rastreabilidade das rejeições.
- Cálculos monetários com Decimal e valores inteiros em centavos.
- HTML, CSS e JavaScript sem dependências externas em tempo de execução.
- Controles rotulados, foco visível, alternativas textuais para o gráfico e estados vazios.
- Testes automatizados, documentação e configuração de CI pronta para revisão.
- Cuidados básicos contra injeção de HTML e fórmulas nas exportações.

## Evidência objetiva

A base de exemplo contém 123 linhas: 120 válidas e três rejeitadas de forma deliberada. Há 95 pedidos concluídos, totalizando R$ 22.002,39 após descontos. Os 27 testes Python passaram e a sintaxe do JavaScript foi verificada. O QA desktop inicial foi aprovado e o ajuste visual da versão 1.0.1 foi revalidado. O QA mobile continua pendente. Os resultados remotos de CI ficam na aba Actions do repositório. Este relato técnico registra as verificações locais e a revisão desktop.

## Limites de uma contratação semelhante

Antes de estimar um projeto real, alinhar: formato e volume da entrada, regras de status, possibilidade de mais de um item por pedido, impostos, descontos, necessidade de banco de dados, periodicidade, privacidade, formato de entrega e revisão visual. Este exemplo não é um ERP, aplicação multiusuário ou sistema contábil.

## Descrição curta do projeto

Automação demonstrativa em Python para transformar CSVs de vendas em um painel interativo offline. Inclui validação de dados, identificação de duplicatas, indicadores, filtros e exportação do recorte. Código com testes e documentação. Cenário e dados fictícios; não representa trabalho para cliente real.

