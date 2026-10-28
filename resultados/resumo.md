# 📊 Resumo dos Resultados

> ⚠️ **Dados 100% sintéticos.** Gerados por regras definidas em `analise.py`. Os resultados demonstram o funcionamento das consultas e não representam bancos, clientes ou mercados reais.

**Parâmetros da execução:** `seed = 42` · 1.000 clientes · 1.195 contas · 30.000 transações · 601 negadas

## 🔎 Principais indicadores

- **Maior valor mensal:** dezembro/2025 — R$ 1.782.577,07.
- **Menor valor mensal:** fevereiro/2025 — R$ 1.309.251,66.
- **Maior participação no valor movimentado:** TED — 50,1%.
- **Maior taxa mensal de negação:** crédito em setembro/2025 — 15,42%, contra média de 3,06% nos demais meses desse tipo.
- **Maior ticket médio:** Premium — R$ 988,51.
- **Menor ticket médio:** Varejo — R$ 392,31.
- **Concentração:** os 10% de clientes com maior movimentação representam 43,7% do valor concluído.

## 📈 1. Evolução mensal

*Transações concluídas entre janeiro e dezembro de 2025.*

| Mês | Transações | Valor total (R$) | Variação mensal (%) |
|---|---:|---:|---:|
| 2025-01 | 2.105 | 1.336.846,54 | — |
| 2025-02 | 2.211 | 1.309.251,66 | -2,10 |
| 2025-03 | 2.191 | 1.313.321,60 | 0,30 |
| 2025-04 | 2.325 | 1.644.314,62 | 25,20 |
| 2025-05 | 2.345 | 1.379.628,93 | -16,10 |
| 2025-06 | 2.403 | 1.574.632,25 | 14,10 |
| 2025-07 | 2.487 | 1.575.828,99 | 0,10 |
| 2025-08 | 2.565 | 1.535.801,41 | -2,50 |
| 2025-09 | 2.402 | 1.447.299,25 | -5,80 |
| 2025-10 | 2.737 | 1.699.711,06 | 17,40 |
| 2025-11 | 2.776 | 1.754.604,16 | 3,20 |
| 2025-12 | 2.852 | 1.782.577,07 | 1,60 |

## 💳 2. Participação por tipo de transação

| Tipo | Transações | Valor total (R$) | Participação (%) |
|---|---:|---:|---:|
| TED | 2.378 | 9.203.606,45 | 50,10 |
| Crédito | 5.794 | 2.952.684,28 | 16,10 |
| Boleto | 3.623 | 2.782.517,10 | 15,20 |
| PIX | 13.253 | 2.768.666,06 | 15,10 |
| Débito | 4.351 | 646.343,65 | 3,50 |

## 🚫 3. Taxas de negação

*As dez maiores taxas mensais retornadas pela consulta.*

| Mês | Tipo | Total | Negadas | Taxa (%) |
|---|---|---:|---:|---:|
| 2025-09 | Crédito | 506 | 78 | 15,42 |
| 2025-01 | Crédito | 407 | 22 | 5,41 |
| 2025-02 | Crédito | 455 | 22 | 4,84 |
| 2025-11 | Crédito | 579 | 23 | 3,97 |
| 2025-03 | Crédito | 453 | 15 | 3,31 |
| 2025-08 | Crédito | 502 | 15 | 2,99 |
| 2025-05 | Crédito | 473 | 14 | 2,96 |
| 2025-10 | Débito | 418 | 12 | 2,87 |
| 2025-11 | Débito | 387 | 11 | 2,84 |
| 2025-04 | Débito | 362 | 10 | 2,76 |

A tabela completa está disponível em `negacao_mensal_por_tipo.csv`.

## 👥 4. Ticket médio por segmento

| Segmento | Transações | Clientes com transação | Ticket médio (R$) | Valor total (R$) |
|---|---:|---:|---:|---:|
| Premium | 5.664 | 161 | 988,51 | 5.598.929,00 |
| Pequena Empresa | 7.703 | 160 | 839,34 | 6.465.425,25 |
| Varejo | 16.032 | 676 | 392,31 | 6.289.463,29 |

## 📊 5. Concentração por decil

*O decil 1 reúne os clientes com maior valor movimentado.*

| Decil | Clientes | Valor total (R$) | Participação (%) |
|---:|---:|---:|---:|
| 1 | 100 | 8.022.426,65 | 43,70 |
| 2 | 100 | 3.437.564,38 | 18,70 |
| 3 | 100 | 2.272.254,53 | 12,40 |
| 4 | 100 | 1.580.773,11 | 8,60 |
| 5 | 100 | 1.107.395,85 | 6,00 |
| 6 | 100 | 779.300,97 | 4,20 |
| 7 | 100 | 533.164,68 | 2,90 |
| 8 | 99 | 349.787,52 | 1,90 |
| 9 | 99 | 194.379,70 | 1,10 |
| 10 | 99 | 76.770,15 | 0,40 |

## ⚠️ Como interpretar

Os padrões observados são influenciados pelas regras do gerador:

- **Negação em setembro:** a taxa de crédito foi elevada intencionalmente para 15%.
- **Variação mensal:** a quantidade de transações cresce em média 3% ao mês por construção; os valores totais também dependem de transações individuais de maior valor.
- **Participação da TED e concentração:** refletem a distribuição sintética dos valores.
- **Diferenças entre segmentos:** os multiplicadores de valor foram predefinidos no gerador.

**Conclusão:** o projeto demonstra como transformar perguntas de negócio em consultas SQL, gerar indicadores e analisar resultados de forma reproduzível. Os números não devem ser interpretados como evidências sobre o mercado financeiro real.
