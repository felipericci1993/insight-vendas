# Evidências de verificação

Preparado em 05/11/2026. Todos os dados são fictícios.

## Executado e aprovado

- Python 3.12.14: **27 testes automatizados aprovados**. Saída: [test-results.txt](test-results.txt).
- Geração normal: `python -m insight_vendas data/vendas_demo.csv --output dist` produziu os quatro arquivos, 120 registros válidos e três rejeições esperadas.
- Modo estrito: `data/modelo.csv` produziu um relatório com um registro válido e nenhuma rejeição.
- Compilação estática de Python: `python -m compileall -q insight_vendas tests`, sem erro.
- Sintaxe JavaScript: script extraído de `dist/index.html` e verificado com Node 24.22.1 (`node --check`), sem erro.
- Revisão independente do código: nenhuma falha reproduzível de cálculo, validação ou injeção encontrada. A observação sobre risco de escrita parcial levou à preparação temporária, substituição por arquivo e documentação da limitação restante.

## Cobertura Python

1. Datas ISO/brasileiras, ano bissexto, datas impossíveis e limites de anos.
2. Decimais com ponto/vírgula, arredondamento de meio centavo e desconto de 100%.
3. Rejeição de negativos, NaN, infinito, notação científica, milhar e casas excessivas.
4. Quantidade inteira, limites de quantidade, preço e desconto.
5. Campos obrigatórios, limites de texto e caracteres de controle.
6. Status permitido e normalização de acentos.
7. UTF-8 com BOM, codificação inválida e CSV malformado.
8. Colunas faltantes, extras, repetidas e ordem diferente.
9. Duplicatas, primeira ocorrência válida e número de linha da rejeição.
10. Base vazia, base inteiramente inválida, tamanho e quantidade máxima de registros.
11. Exclusão de pendentes/cancelados do faturamento e ticket sem divisão por zero.
12. Proteção contra fórmulas em CSV e contra encerramento do script pelo JSON.
13. Hash CSP correspondente ao script gerado.
14. Arquivos de saída, modo estrito sem escrita e mensagem de entrada inexistente.
15. Proteção do arquivo original e validação dos destinos antes de escrever.

## QA desktop pela prévia oficial

O QA desktop anterior à versão 1.0.1 aprovou filtros combinados, busca, limpeza dos filtros, paginação, modais e exportação. A captura está em [screenshots/desktop-before-filter-fix.png](screenshots/desktop-before-filter-fix.png). Essa imagem registra a versão anterior ao ajuste e não comprova o resultado visual da versão nova.

Foi encontrado um problema de layout: o seletor de categoria cortava parte de “Todas as categorias”. Na versão 1.0.1, a faixa de filtros passa a usar flex-wrap, campos com largura mínima de 200 px, busca com base de 240 px e campos de largura total em telas de até 480 px. Os filtros quebram de linha em vez de comprimir o texto.

Após a alteração, os 27 testes Python passaram novamente. O hash do JavaScript e dos três arquivos de dados permaneceu igual, demonstrando que a mudança se restringiu à apresentação. A sintaxe JavaScript também foi revalidada. **A revisão visual desktop da versão 1.0.1 confirmou o texto completo e os filtros em duas linhas, sem sobreposição.** A captura está em [screenshots/desktop-v1.0.1.png](screenshots/desktop-v1.0.1.png).

Na mesma revisão desktop foram observados:

- Filtro combinado de categoria e região: quatro pedidos, R$ 1.091,43 de faturamento.
- Busca `PV-1064`: um pedido, R$ 659,70.
- Limpeza e troca para setembro de 2026: 48 pedidos, R$ 8.213,99.
- Outubro de 2026: 72 pedidos, R$ 13.788,40.

Esses resultados são verificações funcionais e visuais manuais na prévia oficial; não são uma execução do roteiro Playwright. Exportação, modais e paginação foram aprovados no QA desktop anterior ao ajuste de CSS, não repetidos nesta revisão final.

## Limitações e verificações pendentes

A inicialização do Chromium headless falhou antes de abrir o painel, com `socket() failed: Operation not permitted`. A tentativa de execução com escalonamento também não iniciou o navegador. Não foi uma falha observada na interface do projeto.

O roteiro automatizado de navegador não foi executado até o fim. A captura e o QA funcional desktop descritos acima vieram da prévia oficial. **O ajuste visual desktop da versão 1.0.1 foi revalidado; o QA mobile não foi concluído.** Não afirmar homologação de responsividade mobile, acessibilidade completa ou impressão. Nenhuma nova tentativa de DevTools foi feita após a negativa explícita de acesso.

O teste `tests/browser_smoke.py` está preparado para verificar:

- Página offline e filtros reconciliados com o resultado Python.
- Estado vazio, busca sem acentos, limpeza dos filtros e paginação repetida.
- Fechar/reabrir diálogo, Escape, retorno de foco e histórico preservado.
- CSV com todos os registros do recorte, não apenas a página visível.
- Conteúdo malicioso exibido como texto e fórmula neutralizada no download.
- Ausência de transbordamento em 320, 390, 768 e 1440 px.
- Zero erros JavaScript/CSP e zero requisições HTTP(S).
- Capturas desktop e mobile quando a execução terminar.

## Ainda não executado

- QA mobile.
- Firefox, Safari e Edge.
- Leitor de tela, auditoria WCAG completa, testes de carga e pentest.
- Integração com dados reais e hospedagem do painel.

## CI no GitHub

O workflow `Testes Python` cobre Python 3.11, 3.12 e 3.13. Consulte a [aba Actions](https://github.com/felipericci1993/insight-vendas/actions) para o resultado remoto do commit que está avaliando. Este documento registra os testes locais em Python 3.12.14, sem substituir o status remoto de CI.

## Valores de referência

Na base inteira: 120 válidos, 95 concluídos, nove cancelados, R$ 22.002,39 de faturamento, R$ 231,60 de ticket e R$ 4.287,51 pendentes. Outubro: 72 válidos, 56 concluídos, R$ 13.788,40 de faturamento e R$ 246,22 de ticket.

O relatório `dist/erros.csv` registra os três problemas deliberados da entrada. O relatório `dist/resumo.json` permite conferir os valores calculados independentemente da interface.

