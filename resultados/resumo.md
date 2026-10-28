# Resumo dos resultados

> **Dados 100% sintéticos**, gerados por regras definidas em `analise.py`. Os padrões abaixo refletem essas regras e não descrevem nenhum banco, cliente ou mercado real.

Parâmetros desta execução: seed = 42; 1.000 clientes, 1.195 contas, 30.000 transações (601 negadas).

## Leitura dos resultados

- Maior valor mensal: 2025-12 (R$ 1.782.577,07); menor: 2025-02 (R$ 1.309.251,66).
- Tipo com maior participação no valor: TED (50,1%).
- Maior taxa de negação mensal: Credito em 2025-09 (15,42%, contra uma média de 3,06% nos demais meses do mesmo tipo).
- Ticket médio mais alto: Premium (R$ 988,51); mais baixo: Varejo (R$ 392,31).
- Os 10% de clientes que mais movimentam concentram 43,7% do valor concluído.

## 1. Volume mensal (transações concluídas)

| mes | qtd_transacoes | valor_total | variacao_pct_valor |
| --- | --- | --- | --- |
| 2025-01 | 2.105 | 1.336.846,54 | - |
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

## 2. Mix por tipo de transação

| tipo | qtd_transacoes | valor_total | pct_valor |
| --- | --- | --- | --- |
| TED | 2.378 | 9.203.606,45 | 50,10 |
| Credito | 5.794 | 2.952.684,28 | 16,10 |
| Boleto | 3.623 | 2.782.517,10 | 15,20 |
| PIX | 13.253 | 2.768.666,06 | 15,10 |
| Debito | 4.351 | 646.343,65 | 3,50 |

## 3. Maiores taxas de negação mensais (10 primeiras linhas)

| mes | tipo | total | negadas | taxa_negacao_pct |
| --- | --- | --- | --- | --- |
| 2025-09 | Credito | 506 | 78 | 15,42 |
| 2025-01 | Credito | 407 | 22 | 5,41 |
| 2025-02 | Credito | 455 | 22 | 4,84 |
| 2025-11 | Credito | 579 | 23 | 3,97 |
| 2025-03 | Credito | 453 | 15 | 3,31 |
| 2025-08 | Credito | 502 | 15 | 2,99 |
| 2025-05 | Credito | 473 | 14 | 2,96 |
| 2025-10 | Debito | 418 | 12 | 2,87 |
| 2025-11 | Debito | 387 | 11 | 2,84 |
| 2025-04 | Debito | 362 | 10 | 2,76 |

A tabela completa está em `negacao_mensal_por_tipo.csv`.

## 4. Ticket médio por segmento

| segmento | qtd_transacoes | clientes_com_transacao | ticket_medio | valor_total |
| --- | --- | --- | --- | --- |
| Premium | 5.664 | 161 | 988,51 | 5.598.929,00 |
| Pequena Empresa | 7.703 | 160 | 839,34 | 6.465.425,25 |
| Varejo | 16.032 | 676 | 392,31 | 6.289.463,29 |

## 5. Concentração do valor por decil de clientes (decil 1 = maiores)

| decil | clientes | valor_total | pct_valor |
| --- | --- | --- | --- |
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
