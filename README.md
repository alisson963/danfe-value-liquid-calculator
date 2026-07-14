# Robô de Valor Líquido para DANFE

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-funcional-brightgreen.svg)](#status)

Automação em Python para leitura de documentos fiscais, extração de dados dos itens e geração de uma planilha Excel com cálculo de valor líquido.

## Sumário

- [Visão geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Tecnologias](#tecnologias)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Requisitos](#requisitos)
- [Como executar](#como-executar)
- [Saída gerada](#saída-gerada)
- [Fórmula aplicada](#fórmula-aplicada)
- [Testes](#testes)
- [Segurança dos dados](#segurança-dos-dados)
- [Changelog](#changelog)
- [Licença](#licença)
- [Status](#status)

## Visão geral

O projeto foi criado para reduzir atividades manuais em rotinas que envolvem conferência de DANFEs, leitura de itens e cálculo de valores líquidos. A solução processa documentos em lote, organiza os dados por nota fiscal e exporta um arquivo final em Excel para conferência.

![Fluxo do projeto](docs/fluxo_processamento.png)

O processamento segue cinco etapas: entrada dos documentos, extração dos dados, cálculo dos impostos, exportação para Excel e conferência final.

## Funcionalidades

- Leitura de múltiplos documentos em uma pasta de entrada.
- Extração de dados de DANFE em PDF, HTML, TXT e XML.
- Identificação de chave de acesso, número da NF, emitente, destinatário e itens.
- Cálculo de ICMS, PIS, COFINS, IPI, valor líquido total e valor líquido unitário.
- Geração de planilha Excel com abas de resultado, documentos, resumo e erros.
- Registro de logs e tratamento de falhas sem interromper todos os documentos.

## Arquitetura

![Arquitetura](docs/arquitetura.png)

O `executar.py` é o ponto de entrada e orquestra os demais módulos em `src/`:

| Módulo | Responsabilidade |
| --- | --- |
| `config.py` | Pastas e parâmetros de execução |
| `extrator_texto.py` | Extração de dados de PDF, HTML e TXT |
| `extrator_xml.py` | Extração de dados do XML da NF-e |
| `calculadora.py` | Cálculo do valor líquido |
| `exportador.py` | Geração da planilha Excel final |

## Tecnologias

- Python
- Pandas
- OpenPyXL
- PDFPlumber
- BeautifulSoup

## Estrutura do projeto

```text
robo-valor-liquido-danfe/
├── 01_documentos_para_analisar/   # Documentos de entrada
├── 02_resultados/                 # Excel gerado
├── 03_logs/                       # Logs de execução
├── 04_documentos_processados/     # Documentos já processados
├── docs/                          # Diagramas e documentação
├── examples/                      # Exemplos sintéticos
├── src/                           # Código-fonte
├── tests/                         # Testes automatizados
├── executar.py                    # Ponto de entrada
├── requirements.txt               # Dependências
├── README.md
└── .gitignore
```

## Requisitos

- Python 3.10 ou superior

## Como executar

Clone o repositório e acesse a pasta do projeto:

```bash
git clone <url-do-repositorio>
cd robo-valor-liquido-danfe
```

(Opcional) crie e ative um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/Mac
.venv\Scripts\activate         # Windows
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Coloque os documentos na pasta:

```text
01_documentos_para_analisar
```

Execute:

```bash
python executar.py
```

O Excel final será gerado em:

```text
02_resultados/resultado_valor_liquido.xlsx
```

## Saída gerada

A planilha final possui abas para facilitar a conferência:

- **Resultado Final**: itens extraídos e cálculos linha por linha.
- **Documentos**: resumo por arquivo analisado.
- **Resumo**: indicadores gerais do processamento.
- **Erros**: documentos que exigem revisão manual.

## Fórmula aplicada

O cálculo principal considera os percentuais definidos no arquivo de configuração:

```text
Valor ICMS = (Valor Total + IPI calculado) × Alíquota ICMS
Base PIS/COFINS = Valor Total - Valor ICMS
Valor PIS = Base PIS/COFINS × PIS
Valor COFINS = Base PIS/COFINS × COFINS
Valor Líquido Total = Valor Total - ICMS - PIS - COFINS
Valor Líquido Unitário = Valor Líquido Total / Quantidade
```

## Testes

O projeto utiliza `pytest` para os testes automatizados:

```bash
pytest
```

## Segurança dos dados

Este repositório não contém DANFEs reais, XMLs reais, chaves de acesso, planilhas internas ou informações de empresas. As pastas de entrada, saída, logs e processados são ignoradas pelo Git para evitar o envio acidental de arquivos sensíveis.

## Changelog

O histórico de versões está disponível em [CHANGELOG.md](CHANGELOG.md).

## Licença

Este projeto está sob a licença [MIT](LICENSE).

## Status

Projeto funcional para fins de automação, estudo e portfólio. Pode ser adaptado para diferentes layouts de documentos fiscais e rotinas de conferência.
