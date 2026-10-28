import pandas as pd

import analise


def test_mesma_seed_gera_os_mesmos_dados():
    a = analise.gerar_dados(seed=1, n_clientes=30, n_transacoes=200)
    b = analise.gerar_dados(seed=1, n_clientes=30, n_transacoes=200)
    c = analise.gerar_dados(seed=2, n_clientes=30, n_transacoes=200)
    assert a == b
    assert a != c


def test_dados_gerados_respeitam_a_integridade():
    conn = analise.criar_banco(":memory:", analise.gerar_dados(seed=1, n_clientes=50, n_transacoes=500))
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
    assert conn.execute("SELECT COUNT(*) FROM transacoes").fetchone()[0] == 500
    assert conn.execute("SELECT COUNT(*) FROM transacoes WHERE valor <= 0").fetchone()[0] == 0


def test_volume_mensal_bate_com_calculo_feito_a_mao():
    # Base mínima: o resultado esperado foi calculado manualmente.
    #   jan: 100,00 + 50,00 concluídas (a negada de 999,00 não conta) -> 2 transações, 150,00
    #   fev: 300,00                                                   -> 1 transação,  300,00 (+100,0%)
    #   mar: 150,00                                                   -> 1 transação,  150,00 (-50,0%)
    dados = {
        "clientes": [(1, "Varejo", "SP", "2024-01-01")],
        "contas": [(1, 1, "corrente")],
        "transacoes": [
            (1, 1, "2025-01-10 10:00:00", "PIX", "App", 100.0, "concluida"),
            (2, 1, "2025-01-20 11:00:00", "PIX", "App", 50.0, "concluida"),
            (3, 1, "2025-01-25 12:00:00", "TED", "App", 999.0, "negada"),
            (4, 1, "2025-02-05 09:00:00", "TED", "App", 300.0, "concluida"),
            (5, 1, "2025-03-15 14:00:00", "Boleto", "App", 150.0, "concluida"),
        ],
    }
    conn = analise.criar_banco(":memory:", dados)
    df = pd.read_sql_query(analise.carregar_consultas()["volume_mensal"], conn)

    assert list(df["mes"]) == ["2025-01", "2025-02", "2025-03"]
    assert list(df["qtd_transacoes"]) == [2, 1, 1]
    assert list(df["valor_total"]) == [150.0, 300.0, 150.0]
    assert pd.isna(df["variacao_pct_valor"].iloc[0])  # não há mês anterior para comparar
    assert list(df["variacao_pct_valor"].iloc[1:]) == [100.0, -50.0]


def test_execucao_completa_gera_todos_os_arquivos(tmp_path):
    saida = tmp_path / "resultados"
    analise.executar(seed=3, saida=saida, banco=tmp_path / "banco.db", n_clientes=100, n_transacoes=3000)

    esperados = [
        "resumo.md", "amostra_transacoes.csv",
        "volume_mensal.csv", "mix_por_tipo.csv", "negacao_mensal_por_tipo.csv",
        "ticket_por_segmento.csv", "concentracao_por_decil.csv",
        "grafico_valor_mensal.png", "grafico_mix_por_tipo.png", "grafico_negacao_mensal.png",
    ]
    for nome in esperados:
        arquivo = saida / nome
        assert arquivo.exists() and arquivo.stat().st_size > 0, nome
