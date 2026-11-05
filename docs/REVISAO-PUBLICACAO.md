# Revisão do pacote de portfólio

Revisado em **05/11/2026**, versão **1.0.1**. Este registro descreve a revisão local do pacote enviado ao repositório público. Não confirma hospedagem, licença de código aberto ou resultado remoto de CI.

## Conteúdo revisado

- Código Python, template HTML/CSS/JavaScript, testes, configuração de CI e documentação.
- Modelo CSV e base fictícia: os 120 registros válidos usam nomes no formato “Cliente demo”. O modelo usa “Cliente fictício”.
- Quatro saídas em `dist/`, reproduzidas a partir de `data/vendas_demo.csv` com comparação byte a byte.
- Duas capturas de tela: desktop antes do ajuste e desktop da versão 1.0.1. Inspeção visual não identificou conta pessoal, credenciais, dados de clientes reais ou elementos externos ao painel.
- O pacote não inclui diretório `.git`, histórico, caches Python, ambiente virtual ou pastas de relatórios particulares.

## Busca de informações indevidas

Foi feita uma busca heurística nos arquivos de texto por formatos comuns de chaves privadas, tokens GitHub, chaves AWS, chaves Google/OpenAI, tokens Slack, JWTs, atribuições de credenciais, endereços de e-mail e caminhos pessoais. **Nenhum indício foi encontrado pelos padrões usados.**

Também foram revisados o inventário de arquivos, os nomes de clientes da demonstração e as duas imagens. A `.gitignore` inclui arquivos de configuração sensíveis e pastas sugeridas para saídas privadas. Ela não impede o envio de arquivos já rastreados ou adicionados à força.

Esta é uma revisão limitada e heurística, não uma garantia de ausência de segredos, varredura de todo o computador, auditoria independente ou pentest. O escopo é somente o pacote selecionado. Antes de publicar versões futuras, repetir a revisão dos arquivos e do histórico que será enviado.

## Verificações técnicas repetidas

- **27 testes Python aprovados**, em Python 3.12.14.
- Compilação estática de Python e sintaxe JavaScript aprovadas.
- As quatro saídas em `dist/` correspondem byte a byte a uma geração limpa da base fictícia.
- Modo estrito gera a saída do modelo válido e rejeita a base demonstrativa com erros deliberados sem escrever uma saída.
- Totais da base e dos meses conferidos contra os cálculos Python.
- Links relativos da documentação e caminhos das imagens verificados.
- Manifesto SHA-256 e integridade do ZIP verificados na preparação da entrega.

## Estado do QA de interface

**Desktop 1.0.1 revalidado:** texto da categoria completo, filtros em duas linhas sem sobreposição, filtros combinados, busca, limpeza e troca de mês. Exportação, modais e paginação foram aprovados no QA desktop anterior ao ajuste de CSS. As evidências e resultados estão em [TESTES.md](TESTES.md).

**Não verificado:** mobile, roteiro Playwright completo, outros navegadores, leitores de tela, auditoria WCAG, impressão e testes de carga. O status remoto de CI deve ser consultado na aba Actions do repositório. Não usar o pacote para anunciar aprovação dessas etapas.

## Situação para publicação

O material está preparado para revisão e envio como **projeto demonstrativo desktop**, com os limites acima visíveis. Destino: `felipericci1993/insight-vendas`, visibilidade pública e sem arquivo de licença. Não foram criadas uma release ou hospedagem do painel. O envio inclui somente o código, os dados fictícios e as evidências selecionadas, não a pasta de trabalho inteira.
