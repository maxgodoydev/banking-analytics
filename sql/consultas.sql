-- Consultas analíticas (SQLite) sobre dados SINTÉTICOS.
-- Cada bloco começa com "-- consulta: <nome>"; o nome vira o nome do arquivo CSV de resultado.
-- Cada bloco contém exatamente um comando SELECT.


-- consulta: volume_mensal
-- Pergunta: como evoluem a quantidade e o valor das transações concluídas mês a mês?
-- Técnicas: CTE, GROUP BY, função de janela LAG.
WITH mensal AS (
    SELECT
        strftime('%Y-%m', data_hora) AS mes,
        COUNT(*)                     AS qtd_transacoes,
        ROUND(SUM(valor), 2)         AS valor_total
    FROM transacoes
    WHERE status = 'concluida'
    GROUP BY mes
)
SELECT
    mes,
    qtd_transacoes,
    valor_total,
    ROUND(
        100.0 * (valor_total - LAG(valor_total) OVER (ORDER BY mes))
              / LAG(valor_total) OVER (ORDER BY mes),
        1
    ) AS variacao_pct_valor
FROM mensal
ORDER BY mes;


-- consulta: mix_por_tipo
-- Pergunta: quanto cada tipo de transação (PIX, TED, boleto, cartão) representa do valor total?
-- Técnicas: GROUP BY, função de janela sobre agregação (SUM(SUM(...)) OVER ()).
SELECT
    tipo,
    COUNT(*)             AS qtd_transacoes,
    ROUND(SUM(valor), 2) AS valor_total,
    ROUND(100.0 * SUM(valor) / SUM(SUM(valor)) OVER (), 1) AS pct_valor
FROM transacoes
WHERE status = 'concluida'
GROUP BY tipo
ORDER BY valor_total DESC;


-- consulta: negacao_mensal_por_tipo
-- Pergunta: em que meses e em quais tipos a taxa de negação foge do normal?
-- Técnicas: agregação condicional (CASE dentro de SUM).
SELECT
    strftime('%Y-%m', data_hora) AS mes,
    tipo,
    COUNT(*)                                          AS total,
    SUM(CASE WHEN status = 'negada' THEN 1 ELSE 0 END) AS negadas,
    ROUND(100.0 * SUM(CASE WHEN status = 'negada' THEN 1 ELSE 0 END) / COUNT(*), 2)
                                                      AS taxa_negacao_pct
FROM transacoes
GROUP BY mes, tipo
ORDER BY mes, tipo;


-- consulta: ticket_por_segmento
-- Pergunta: o valor médio por transação difere entre os segmentos de clientes?
-- Técnicas: JOIN de três tabelas, AVG, COUNT(DISTINCT ...).
SELECT
    cl.segmento,
    COUNT(*)                        AS qtd_transacoes,
    COUNT(DISTINCT cl.cliente_id)   AS clientes_com_transacao,
    ROUND(AVG(t.valor), 2)          AS ticket_medio,
    ROUND(SUM(t.valor), 2)          AS valor_total
FROM transacoes AS t
JOIN contas     AS c  ON c.conta_id    = t.conta_id
JOIN clientes   AS cl ON cl.cliente_id = c.cliente_id
WHERE t.status = 'concluida'
GROUP BY cl.segmento
ORDER BY ticket_medio DESC;


-- consulta: concentracao_por_decil
-- Pergunta: que parcela do valor movimentado vem dos 10% de clientes que mais movimentam?
-- Técnicas: duas CTEs encadeadas, NTILE, função de janela sobre agregação.
-- Leitura: decil 1 = os 10% de clientes com maior valor movimentado.
WITH valor_por_cliente AS (
    SELECT
        c.cliente_id,
        SUM(t.valor) AS valor_total
    FROM transacoes AS t
    JOIN contas     AS c ON c.conta_id = t.conta_id
    WHERE t.status = 'concluida'
    GROUP BY c.cliente_id
),
decis AS (
    SELECT
        cliente_id,
        valor_total,
        NTILE(10) OVER (ORDER BY valor_total DESC) AS decil
    FROM valor_por_cliente
)
SELECT
    decil,
    COUNT(*)                 AS clientes,
    ROUND(SUM(valor_total), 2) AS valor_total,
    ROUND(100.0 * SUM(valor_total) / SUM(SUM(valor_total)) OVER (), 1) AS pct_valor
FROM decis
GROUP BY decil
ORDER BY decil;
