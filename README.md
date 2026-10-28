# 📊 Banking Analytics

**Análise de transações bancárias fictícias com Python, SQL e SQLite.**

> ⚠️ **Dados 100% sintéticos.** Clientes, contas, transações e resultados foram gerados por regras definidas no código. Nenhum dado representa clientes ou bancos reais.

## 🎯 O problema

Como uma área de produto de um banco fictício pode entender o comportamento das transações?

Este projeto responde a cinco perguntas de negócio usando SQL e Python, gerando tabelas, gráficos e um resumo analítico com **um único comando**.

## 🛠️ Tecnologias

- **Python:** geração de dados, execução e exportação das análises.
- **SQLite:** armazenamento local e consultas SQL.
- **Pandas:** organização dos resultados.
- **Matplotlib:** visualização dos indicadores.
- **Pytest:** testes automatizados.

## 🔎 Análises realizadas

| Pergunta de negócio | Consulta | Técnicas SQL |
|---|---|---|
| Como evoluem o volume e o valor mensal? | `volume_mensal` | CTE, `GROUP BY`, `LAG` |
| Qual é a participação de cada tipo de transação? | `mix_por_tipo` | Agregação e função de janela |
| Como varia a taxa de negação ao longo do tempo? | `negacao_mensal_por_tipo` | `CASE`, `SUM` |
| O ticket médio muda entre segmentos? | `ticket_por_segmento` | `JOIN`, `AVG`, `COUNT(DISTINCT)` |
| Quanto os 10% de clientes com maior movimentação concentram? | `concentracao_por_decil` | CTEs, `NTILE` |

## 📈 Resultados de exemplo

Execução com `seed = 42`:

- **1.000** clientes
- **1.195** contas
- **30.000** transações
- **601** transações negadas

### Gráficos gerados

![Evolução mensal do valor transacionado](resultados/grafico_valor_mensal.png)

![Participação por tipo de transação](resultados/grafico_mix_por_tipo.png)

![Taxa mensal de negação](resultados/grafico_negacao_mensal.png)

### Principais observações

- O valor mensal das transações concluídas variou de R$ 1,31 milhão a R$ 1,78 milhão.
- TED representou 50,1% do valor movimentado, embora correspondesse a cerca de 8% das transações concluídas.
- A taxa de negação no cartão de crédito chegou a 15,42% em setembro.
- O ticket médio variou entre os segmentos: Premium (R$ 988,51), Pequena Empresa (R$ 839,34) e Varejo (R$ 392,31).
- Os 10% de clientes com maior movimentação concentraram 43,7% do valor concluído.

📄 Consulte [o relatório completo](resultados/resumo.md) para ver as tabelas e os indicadores.

### ⚠️ Como interpretar os resultados

Os padrões observados decorrem, em parte, das regras usadas para gerar os dados:

- A elevação da taxa de negação no cartão em setembro foi inserida intencionalmente no gerador.
- O número de transações cresce em média 3% ao mês por construção; os valores movimentados também variam conforme a distribuição dos valores individuais.
- TED e a concentração de movimentação refletem a distribuição sintética dos valores.
- Os segmentos possuem multiplicadores de valor predefinidos.

Portanto, os resultados servem para demonstrar a execução das consultas e o processo de análise, não para tirar conclusões sobre o mercado financeiro real.

## 🚀 Como executar no Windows

**Requisito:** Python 3.10 ou superior, instalado pelo [site oficial](https://www.python.org/downloads/).

No terminal do VS Code, dentro da pasta do projeto, execute:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python analise.py
python -m pytest
```

O script gera o banco SQLite em `dados/banco.db` e atualiza os arquivos de `resultados/`.

Para gerar outro conjunto de dados:

```powershell
python analise.py --seed 7
```

A mesma seed reproduz os mesmos dados.

> Se o PowerShell bloquear a ativação do ambiente virtual, você pode usar o CMD e executar `.venv\Scripts\activate.bat`.

## 🧪 Testes automatizados

O comando `python -m pytest` executa quatro testes para verificar:

- Reprodutibilidade dos dados gerados.
- Integridade dos dados e relacionamentos.
- Correção da consulta de volume mensal em uma base pequena calculada manualmente.
- Geração dos arquivos esperados.

Os testes verificam a mecânica do projeto, não a validade dos resultados para o mundo real.

## 📁 Estrutura do projeto

```text
banking-analytics/
├── analise.py
├── sql/
│   ├── schema.sql
│   └── consultas.sql
├── tests/
│   └── test_analise.py
├── resultados/
├── requirements.txt
└── pytest.ini
```

## 💡 Decisões técnicas

- **SQLite:** permite executar SQL localmente, sem configurar um servidor, e suporta CTEs e funções de janela.
- **Gerador próprio:** dispensa dados pessoais e dependências desnecessárias.
- **Seed fixa:** permite reproduzir os resultados.
- **Resultados versionados:** facilitam a visualização do projeto diretamente no GitHub.
- **CSV em `utf-8-sig`:** facilita a abertura dos arquivos no Excel com os acentos preservados.

## 📌 Limitações

- Os dados são sintéticos e não representam operações financeiras reais.
- O projeto não realiza detecção de fraude nem modelagem preditiva.
- Os valores monetários usam `REAL` por simplicidade; sistemas financeiros reais exigem tratamento monetário mais rigoroso.
- As taxas mensais podem oscilar por causa do tamanho da amostra.
- Não há dashboard, API ou aplicação web: o foco é a análise reproduzível com SQL e Python.

## 👨‍💻 Sobre

Projeto de estudo e portfólio desenvolvido por [Max Godoy](https://github.com/maxgodoydev), estudante de Desenvolvimento de Software Multiplataforma na FATEC Zona Sul.

Desenvolvido com auxílio de IA (Claude, da Anthropic), com execução e testes do código. O projeto tem finalidade educacional e não se destina à produção.
