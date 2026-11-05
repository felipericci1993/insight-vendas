# Publicação e manutenção no GitHub

Destino confirmado: [felipericci1993/insight-vendas](https://github.com/felipericci1993/insight-vendas). O repositório é público e não inclui arquivo de licença. Este roteiro ajuda a repetir a revisão antes de futuras atualizações.

## Apresentação do projeto

- **Nome:** `insight-vendas`
- **Descrição:** Automação em Python que transforma CSVs de vendas em um dashboard HTML offline, com validação, filtros e exportação. Projeto demonstrativo com dados fictícios.
- **Tópicos:** `python`, `csv`, `data-validation`, `dashboard`, `html`, `javascript`, `portfolio`, `offline-first`
- **Versão da aplicação:** `1.0.1`
- **Site:** deixar em branco até existir uma hospedagem verificada.

O README já inclui uma captura real da versão desktop, comandos para executar, regras dos indicadores e limites conhecidos. Não adicionar selo de CI aprovado antes de uma execução remota bem-sucedida, nem divulgar cliente, retorno financeiro ou compatibilidade não verificados.

## Cuidados antes de cada atualização

1. Confirmar o repositório de destino e revisar o commit atual antes de enviar mudanças.
2. Definir a visibilidade: um repositório público expõe código, histórico e todos os arquivos enviados; um privado não funciona como vitrine pública sem compartilhar acesso.
3. Decidir a licença. O pacote não concede uma licença de código aberto. Não adicionar uma licença em nome do titular sem essa escolha.
4. Manter exclusivamente os dados fictícios e as evidências publicáveis deste pacote. Não enviar a pasta de trabalho inteira, arquivos pessoais, credenciais ou bases reais.
5. Manter a ressalva de QA mobile pendente. A publicação como demonstração desktop não equivale a homologação mobile.

## Arquivos do projeto

- `.github/workflows/tests.yml` e `.gitignore`
- `README.md` e `CHANGELOG.md`
- `insight_vendas/`: código-fonte, sem `__pycache__`
- `data/`: modelo e base fictícia
- `dist/`: quatro saídas geradas exclusivamente da base fictícia
- `tests/`: testes Python e roteiro opcional de navegador
- `docs/`: caso de portfólio, resultados, capturas e manifesto
- `requirements-dev.txt`: dependência opcional de QA

O arquivo `docs/manifest-sha256.json` permite conferir os bytes revisados. Ele não é uma assinatura, prova de autoria nem auditoria de segurança. Não inclui seu próprio hash. O ZIP de entrega não deve ser adicionado dentro do repositório.

## Verificação depois do envio

1. Confirmar a URL, a visibilidade e o commit efetivamente recebido pelo GitHub.
2. Verificar a renderização do README e das imagens usando os links relativos.
3. Acompanhar o workflow **Testes Python** para esse commit, incluindo Python 3.11, 3.12 e 3.13. Até isso acontecer, a matriz remota continua não verificada.
4. Baixar uma cópia limpa, extrair e abrir `dist/index.html`. A visualização de um HTML no GitHub mostra código-fonte; não é um site publicado.
5. Manter a documentação alinhada ao que foi efetivamente verificado. Uma tag ou release GitHub é uma ação separada e não foi criada nesta entrega.
6. Configurar hospedagem somente se desejado e autorizado. Nenhum fluxo de deploy está incluído neste pacote.

## Cuidados ao usar dados próprios

Gere relatórios privados em `relatorios-privados/`, que está ignorada pelo Git. Essa convenção reduz erros, mas não garante privacidade: arquivos já rastreados ou adicionados à força continuam podendo ser enviados. O HTML e o JSON incorporam todos os pedidos, inclusive aqueles ocultos pelos filtros. Revise os arquivos e obtenha a autorização necessária antes de compartilhar uma adaptação.
