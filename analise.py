"""Banking Analytics (dados SINTÉTICOS).

Gera dados fictícios de transações bancárias, carrega em SQLite, executa as
consultas de sql/consultas.sql e salva CSVs, gráficos e um resumo em resultados/.

Uso:
    python analise.py
    python analise.py --seed 7 --saida resultados --banco dados/banco.db
"""
from __future__ import annotations

import argparse
import bisect
import math
import random
import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent
SQL_DIR = RAIZ / "sql"

SEED_PADRAO = 42
ANO = 2025
N_CLIENTES_PADRAO = 1000
N_TRANSACOES_PADRAO = 30000

# ---------------------------------------------------------------------------
# Regras do gerador de dados.
# Tudo que o projeto "descobre" nos dados vem destas regras: os dados são
# fictícios e os padrões foram definidos aqui de propósito (ver README).
# ---------------------------------------------------------------------------
SEGMENTOS = [("Varejo", 70), ("Premium", 15), ("Pequena Empresa", 15)]
MULTIPLICADOR_VALOR = {"Varejo": 1.0, "Premium": 2.5, "Pequena Empresa": 2.0}
PESO_ATIVIDADE = {"Varejo": 1.0, "Premium": 1.5, "Pequena Empresa": 2.0}
UFS = [("SP", 32), ("RJ", 12), ("MG", 11), ("RS", 6), ("PR", 6), ("BA", 6),
       ("PE", 5), ("SC", 5), ("CE", 4), ("GO", 4), ("DF", 3), ("Outras", 6)]
TIPOS = [("PIX", 45), ("Credito", 20), ("Debito", 15), ("Boleto", 12), ("TED", 8)]
CANAIS_POR_TIPO = {
    "PIX": [("App", 85), ("Internet Banking", 15)],
    "TED": [("Internet Banking", 60), ("App", 30), ("Agencia", 10)],
    "Boleto": [("App", 55), ("Internet Banking", 35), ("Agencia", 10)],
    "Debito": [("Maquininha", 100)],
    "Credito": [("Maquininha", 60), ("E-commerce", 40)],
}
# (valor mediano em R$, dispersão) por tipo de transação
VALOR_POR_TIPO = {"PIX": (80, 1.0), "TED": (1500, 1.0), "Boleto": (350, 0.8),
                  "Debito": (70, 0.8), "Credito": (220, 0.9)}
TAXA_NEGACAO = {"PIX": 0.015, "TED": 0.010, "Boleto": 0.010,
                "Debito": 0.020, "Credito": 0.030}
# Padrão plantado: em setembro a negação no cartão de crédito sobe para 15%.
MES_ANOMALIA = 9
TAXA_NEGACAO_ANOMALIA = 0.15
CRESCIMENTO_MENSAL = 0.03  # o volume de transações cresce ~3% ao mês
DIAS_NO_MES = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]  # 2025 não é bissexto
PESO_HORA = [1] * 6 + [3] * 3 + [8] * 9 + [6] * 4 + [2] * 2  # 24 valores: 0h a 23h


# ---------------------------------------------------------------------------
# Geração de dados (usa só random.random() para ser reprodutível entre versões)
# ---------------------------------------------------------------------------
def _escolher(rng: random.Random, opcoes: list[tuple]):
    """Sorteia um valor de uma lista de (valor, peso)."""
    total = sum(peso for _, peso in opcoes)
    alvo = rng.random() * total
    acumulado = 0.0
    for valor, peso in opcoes:
        acumulado += peso
        if alvo < acumulado:
            return valor
    return opcoes[-1][0]


def _lognormal(rng: random.Random, mediana: float, sigma: float) -> float:
    """Valor lognormal (muitos valores pequenos, poucos muito grandes)."""
    u1 = 1.0 - rng.random()  # evita log(0)
    u2 = rng.random()
    z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
    return mediana * math.exp(sigma * z)


def gerar_dados(seed: int = SEED_PADRAO,
                n_clientes: int = N_CLIENTES_PADRAO,
                n_transacoes: int = N_TRANSACOES_PADRAO) -> dict[str, list[tuple]]:
    """Gera clientes, contas e transações fictícias. Mesma seed = mesmos dados."""
    rng = random.Random(seed)

    inicio, fim = date(2020, 1, 1), date(2024, 12, 31)
    intervalo = (fim - inicio).days
    clientes = []
    for cliente_id in range(1, n_clientes + 1):
        segmento = _escolher(rng, SEGMENTOS)
        uf = _escolher(rng, UFS)
        cadastro = inicio + timedelta(days=int(rng.random() * intervalo))
        clientes.append((cliente_id, segmento, uf, cadastro.isoformat()))

    contas = []
    segmento_da_conta = {}
    pesos_da_conta = []
    for cliente_id, segmento, _uf, _cadastro in clientes:
        tipos_de_conta = ["corrente"] + (["poupanca"] if rng.random() < 0.2 else [])
        atividade_cliente = PESO_ATIVIDADE[segmento] * _lognormal(rng, 1.0, 0.9)
        for tipo_conta in tipos_de_conta:
            conta_id = len(contas) + 1
            contas.append((conta_id, cliente_id, tipo_conta))
            segmento_da_conta[conta_id] = segmento
            pesos_da_conta.append(atividade_cliente * (0.3 if tipo_conta == "poupanca" else 1.0))

    acumulados, soma = [], 0.0
    for peso in pesos_da_conta:
        soma += peso
        acumulados.append(soma)

    pesos_mes = [(mes, 1 + CRESCIMENTO_MENSAL * (mes - 1)) for mes in range(1, 13)]
    pesos_hora = list(enumerate(PESO_HORA))

    brutas = []
    for _ in range(n_transacoes):
        indice = min(bisect.bisect(acumulados, rng.random() * soma), len(contas) - 1)
        conta_id = contas[indice][0]
        mes = _escolher(rng, pesos_mes)
        dia = 1 + int(rng.random() * DIAS_NO_MES[mes - 1])
        hora = _escolher(rng, pesos_hora)
        minuto, segundo = int(rng.random() * 60), int(rng.random() * 60)
        data_hora = f"{ANO}-{mes:02d}-{dia:02d} {hora:02d}:{minuto:02d}:{segundo:02d}"

        tipo = _escolher(rng, TIPOS)
        canal = _escolher(rng, CANAIS_POR_TIPO[tipo])
        mediana, sigma = VALOR_POR_TIPO[tipo]
        valor = _lognormal(rng, mediana, sigma) * MULTIPLICADOR_VALOR[segmento_da_conta[conta_id]]
        valor = round(max(1.0, valor), 2)

        taxa = TAXA_NEGACAO[tipo]
        if tipo == "Credito" and mes == MES_ANOMALIA:
            taxa = TAXA_NEGACAO_ANOMALIA
        status = "negada" if rng.random() < taxa else "concluida"
        brutas.append((data_hora, conta_id, tipo, canal, valor, status))

    brutas.sort()  # ordena por data/hora; o id segue a ordem cronológica
    transacoes = [(i, conta_id, data_hora, tipo, canal, valor, status)
                  for i, (data_hora, conta_id, tipo, canal, valor, status) in enumerate(brutas, start=1)]
    return {"clientes": clientes, "contas": contas, "transacoes": transacoes}


# ---------------------------------------------------------------------------
# Banco de dados e consultas
# ---------------------------------------------------------------------------
def criar_banco(caminho: str | Path, dados: dict[str, list[tuple]]) -> sqlite3.Connection:
    """Cria o banco SQLite (apagando o anterior) e carrega os dados."""
    if str(caminho) != ":memory:":
        caminho = Path(caminho)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        try:
            caminho.unlink(missing_ok=True)
        except PermissionError:
            sys.exit(f"Não foi possível recriar {caminho}. Feche o arquivo em outros programas e tente de novo.")
    conn = sqlite3.connect(str(caminho))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript((SQL_DIR / "schema.sql").read_text(encoding="utf-8"))
    conn.executemany("INSERT INTO clientes VALUES (?, ?, ?, ?)", dados["clientes"])
    conn.executemany("INSERT INTO contas VALUES (?, ?, ?)", dados["contas"])
    conn.executemany("INSERT INTO transacoes VALUES (?, ?, ?, ?, ?, ?, ?)", dados["transacoes"])
    conn.commit()
    return conn


def carregar_consultas(caminho: Path = SQL_DIR / "consultas.sql") -> dict[str, str]:
    """Lê sql/consultas.sql e devolve {nome: texto SQL}."""
    consultas: dict[str, str] = {}
    nome, linhas = None, []
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        if linha.startswith("-- consulta:"):
            if nome:
                consultas[nome] = "\n".join(linhas).strip()
            nome, linhas = linha.split(":", 1)[1].strip(), []
        elif nome:
            linhas.append(linha)
    if nome:
        consultas[nome] = "\n".join(linhas).strip()
    return consultas


def executar_consultas(conn: sqlite3.Connection) -> dict[str, pd.DataFrame]:
    return {nome: pd.read_sql_query(sql, conn) for nome, sql in carregar_consultas().items()}


# ---------------------------------------------------------------------------
# Formatação (padrão brasileiro nos gráficos e no resumo; CSVs mantêm ponto decimal)
# ---------------------------------------------------------------------------
def _br(valor: float, casas: int = 2) -> str:
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def _celula(valor) -> str:
    if pd.isna(valor):
        return "-"
    if isinstance(valor, float):
        return _br(valor, 2)
    if isinstance(valor, int):
        return _br(valor, 0)
    return str(valor)


def _tabela_md(df: pd.DataFrame) -> str:
    linhas = ["| " + " | ".join(df.columns) + " |",
              "| " + " | ".join("---" for _ in df.columns) + " |"]
    for registro in df.itertuples(index=False):
        linhas.append("| " + " | ".join(_celula(v) for v in registro) + " |")
    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Gráficos (só matplotlib). Padrão comum aos três: título-conclusão, subtítulo,
# legenda, títulos de eixo, rodapé com aviso de dados sintéticos e a consulta de origem.
# Os títulos e as legendas são calculados a partir dos resultados das consultas.
# ---------------------------------------------------------------------------
AZUL, AZUL_CLARO, DESTAQUE = "#1F3A5F", "#A9BCD3", "#E4572E"
CINZA, CINZA_CLARO, TEXTO = "#6B7280", "#D9DEE5", "#1F2937"
VERDE, VERMELHO = "#2E7D5B", "#B03A2E"
MESES_PT = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
_FUNDO = {"facecolor": "white", "edgecolor": "none", "pad": 1.5}  # rótulos legíveis sobre a linha de média
NOME_TIPO = {"Credito": "Crédito", "Debito": "Débito"}  # os dados não têm acento; o gráfico sim


def _nome_tipo(tipo: str) -> str:
    return NOME_TIPO.get(tipo, tipo)


def _mes_pt(mes: str) -> str:
    """'2025-09' -> 'Set'."""
    return MESES_PT[int(mes[5:7]) - 1]


def _figura(titulo: str, subtitulo: str, seed: int, consulta: str, legenda: list,
            esquerda: float = 0.09):
    """Figura com faixa de destaque, título, subtítulo, legenda e rodapé padronizados."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fig, ax = plt.subplots(figsize=(10, 6.0))
    fig.subplots_adjust(top=0.72, bottom=0.15, left=esquerda, right=0.96)
    fig.add_artist(Rectangle((0.02, 0.928), 0.006, 0.037, transform=fig.transFigure, color=DESTAQUE))
    fig.text(0.04, 0.965, titulo, fontsize=16, fontweight="bold", color=TEXTO, ha="left", va="top")
    fig.text(0.04, 0.905, subtitulo, fontsize=10, color=CINZA, ha="left", va="top", linespacing=1.5)
    fig.legend(handles=legenda, loc="upper left", bbox_to_anchor=(0.04, 0.80), ncol=len(legenda),
               frameon=False, fontsize=9.5, labelcolor=TEXTO, borderpad=0, borderaxespad=0,
               handlelength=1.3, columnspacing=1.8)
    fig.text(0.04, 0.03, f"Dados 100% sintéticos (seed = {seed}). Não representam clientes nem mercado reais.",
             fontsize=8, color=CINZA, ha="left", va="bottom")
    fig.text(0.96, 0.03, f"Fonte: consulta {consulta}", fontsize=8,
             color=CINZA, ha="right", va="bottom")
    ax.spines[["top", "right"]].set_visible(False)
    return fig, ax


def _salvar(fig, pasta: Path, nome: str) -> Path:
    import matplotlib.pyplot as plt
    arquivo = pasta / nome
    fig.savefig(arquivo, dpi=200, facecolor="white")
    plt.close(fig)
    return arquivo


def _grafico_valor_mensal(res: dict[str, pd.DataFrame], pasta: Path, seed: int) -> Path:
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    vm = res["volume_mensal"]
    milhoes = vm["valor_total"] / 1_000_000
    media = milhoes.mean()
    variacao_total = (milhoes.iloc[-1] / milhoes.iloc[0] - 1) * 100
    comparativo = "mais" if variacao_total >= 0 else "menos"
    titulo = (f"{_mes_pt(vm['mes'].iloc[-1])} movimentou {_br(abs(variacao_total), 1)}% "
              f"{comparativo} que {_mes_pt(vm['mes'].iloc[0])}")
    subtitulo = ("Valor das transações concluídas por mês, em R$ milhões.\n"
                 "Os indicadores acima das barras mostram a variação percentual sobre o mês anterior.")
    legenda = [
        Patch(facecolor=AZUL_CLARO, label="Demais meses"),
        Patch(facecolor=DESTAQUE, label="Maior mês"),
        Line2D([], [], color=CINZA, linestyle="--", linewidth=1.2, label=f"Média mensal ({_br(media, 2)})"),
        Line2D([], [], marker="^", color=VERDE, linestyle="", markersize=7, label="Alta sobre o mês anterior"),
        Line2D([], [], marker="v", color=VERMELHO, linestyle="", markersize=7, label="Queda sobre o mês anterior"),
    ]
    fig, ax = _figura(titulo, subtitulo, seed, "volume_mensal", legenda)

    posicao_max = int(milhoes.to_numpy().argmax())
    cores = [DESTAQUE if i == posicao_max else AZUL_CLARO for i in range(len(vm))]
    ax.bar(range(len(vm)), milhoes, color=cores, width=0.68, zorder=3)
    ax.axhline(media, color=CINZA, linestyle="--", linewidth=1, zorder=4)  # equivale à linha média do Power BI
    teto = milhoes.max()
    for i, (valor, var) in enumerate(zip(milhoes, vm["variacao_pct_valor"])):
        ax.text(i, valor + teto * 0.02, _br(valor, 2), ha="center", va="bottom",
                fontsize=9, fontweight="bold", color=TEXTO, zorder=5, bbox=_FUNDO)
        if not pd.isna(var):
            seta, cor = ("▲", VERDE) if var >= 0 else ("▼", VERMELHO)
            ax.text(i, valor + teto * 0.095, f"{seta} {_br(abs(var), 1)}%", ha="center",
                    va="bottom", fontsize=8, color=cor, zorder=5, bbox=_FUNDO)
    ax.set_ylim(0, teto * 1.22)
    ax.set_xticks(range(len(vm)), [_mes_pt(m) for m in vm["mes"]])
    ax.set_yticks([])
    ax.set_xlabel(f"Mês ({vm['mes'].iloc[0][:4]})", fontsize=9.5, color=CINZA, labelpad=8)
    ax.set_ylabel("Valor concluído (R$ milhões)", fontsize=9.5, color=CINZA, labelpad=8)
    ax.spines[["left"]].set_visible(False)
    ax.spines["bottom"].set_color(CINZA_CLARO)
    ax.tick_params(axis="x", length=0, labelsize=10, colors=TEXTO)
    return _salvar(fig, pasta, "grafico_valor_mensal.png")


def _grafico_mix_por_tipo(res: dict[str, pd.DataFrame], pasta: Path, seed: int) -> Path:
    import numpy as np
    from matplotlib.patches import Patch
    mix = res["mix_por_tipo"].copy()
    mix["pct_qtd"] = 100.0 * mix["qtd_transacoes"] / mix["qtd_transacoes"].sum()
    mix["pct_valor_exato"] = 100.0 * mix["valor_total"] / mix["valor_total"].sum()
    # a diferença usa os valores já arredondados, para bater com o que aparece no gráfico
    mix["dif"] = mix["pct_valor_exato"].round(1) - mix["pct_qtd"].round(1)
    mix = mix.sort_values("pct_valor_exato").reset_index(drop=True)  # maior valor no topo

    destaque = mix.loc[mix["dif"].abs().idxmax()]
    titulo = (f"{_nome_tipo(destaque['tipo'])}: {_br(destaque['pct_qtd'], 1)}% das transações "
              f"e {_br(destaque['pct_valor_exato'], 1)}% do valor")
    subtitulo = ("Participação de cada tipo na quantidade e no valor das transações concluídas.\n"
                 "Barras ordenadas pela participação no valor; a coluna da direita mostra a diferença entre as duas.")
    legenda = [Patch(facecolor=AZUL, label="% do valor"), Patch(facecolor=AZUL_CLARO, label="% da quantidade")]
    fig, ax = _figura(titulo, subtitulo, seed, "mix_por_tipo", legenda, esquerda=0.11)

    y, altura = np.arange(len(mix)), 0.36
    series = ((y + altura / 2, mix["pct_valor_exato"], AZUL), (y - altura / 2, mix["pct_qtd"], AZUL_CLARO))
    for posicoes, valores, cor in series:
        barras = ax.barh(posicoes, valores, height=altura, color=cor, zorder=3)
        ax.bar_label(barras, labels=[f"{_br(v, 1)}%" for v in valores], padding=4,
                     fontsize=9.5, color=TEXTO)
    # coluna de diferença (valor menos quantidade, em pontos percentuais)
    ax.text(1.0, 1.015, "Valor − quantidade\n(p.p.)", transform=ax.transAxes, ha="right", va="bottom",
            fontsize=8.5, color=CINZA, linespacing=1.3)
    for yi, d in zip(y, mix["dif"]):
        sinal = "+" if d >= 0 else "−"
        ax.text(1.0, yi, f"{sinal}{_br(abs(d), 1)}", transform=ax.get_yaxis_transform(), ha="right",
                va="center", fontsize=10, fontweight="bold", color=TEXTO)
    ax.set_yticks(y, [_nome_tipo(t) for t in mix["tipo"]])
    ax.set_xlim(0, max(mix["pct_qtd"].max(), mix["pct_valor_exato"].max()) * 1.45)  # barras partem de zero
    ax.set_xticks([])
    ax.set_xlabel("Participação no total das transações concluídas (%)", fontsize=9.5, color=CINZA, labelpad=8)
    ax.set_ylabel("Tipo de transação", fontsize=9.5, color=CINZA, labelpad=8)
    ax.spines[["left", "bottom"]].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=11, colors=TEXTO)
    return _salvar(fig, pasta, "grafico_mix_por_tipo.png")


def _grafico_negacao_mensal(res: dict[str, pd.DataFrame], pasta: Path, seed: int) -> Path:
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.patches import Patch, Rectangle

    neg = res["negacao_mensal_por_tipo"]
    tabela = neg.pivot(index="tipo", columns="mes", values="taxa_negacao_pct")
    # coluna "Total": taxa do período inteiro (soma das negadas / soma do total), não média das taxas
    soma = neg.groupby("tipo")[["negadas", "total"]].sum()
    total_tipo = 100.0 * soma["negadas"] / soma["total"]
    tabela = tabela.loc[total_tipo.sort_values(ascending=False).index]
    meses = list(tabela.columns)

    pico = neg.loc[neg["taxa_negacao_pct"].idxmax()]
    outros = neg[(neg["tipo"] == pico["tipo"]) & (neg["mes"] != pico["mes"])]["taxa_negacao_pct"].mean()
    titulo = (f"{_nome_tipo(pico['tipo'])} negou {_br(pico['taxa_negacao_pct'], 1)}% das transações "
              f"em {_mes_pt(pico['mes'])}")
    subtitulo = "Taxa de negação por tipo e mês (% de transações negadas). A coluna Total cobre o período inteiro."
    if not pd.isna(outros):
        subtitulo += f"\nNos demais meses, {_nome_tipo(pico['tipo'])} ficou em média em {_br(outros, 1)}% ao mês."
    legenda = [Patch(facecolor="white", edgecolor=TEXTO, linewidth=2, label="Maior valor do período")]
    fig, ax = _figura(titulo, subtitulo, seed, "negacao_mensal_por_tipo", legenda, esquerda=0.10)

    mensal = tabela.to_numpy(dtype=float)
    valores = np.column_stack([mensal, total_tipo.loc[tabela.index].to_numpy(dtype=float)])
    n_linhas, n_colunas = valores.shape
    vmax = np.nanmax(mensal)  # escala de cor definida pelos meses; o Total usa a mesma escala
    cmap = LinearSegmentedColormap.from_list("negacao", ["#F3F5F8", "#F4C3B1", DESTAQUE, "#9E2B12"])
    ax.imshow(np.ma.masked_invalid(valores), cmap=cmap, vmin=0, vmax=vmax, aspect="auto")
    for i in range(n_linhas):
        for j in range(n_colunas):
            v = valores[i, j]
            texto, cor = ("–", CINZA) if np.isnan(v) else (_br(v, 1), "white" if v > 0.55 * vmax else TEXTO)
            ax.text(j, i, texto, ha="center", va="center", fontsize=9, color=cor,
                    fontweight="bold" if j == n_colunas - 1 else "normal")
    ax.set_xticks(range(n_colunas), [_mes_pt(m) for m in meses] + ["Total"])
    ax.set_yticks(range(n_linhas), [_nome_tipo(t) for t in tabela.index])
    ax.set_xticks(np.arange(-0.5, n_colunas, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n_linhas, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=2.5)
    ax.tick_params(which="both", length=0)
    ax.tick_params(axis="both", labelsize=10, colors=TEXTO)
    ax.get_xticklabels()[-1].set_fontweight("bold")
    ax.set_xlabel(f"Mês ({meses[0][:4]})", fontsize=9.5, color=CINZA, labelpad=8)
    for lado in ax.spines.values():
        lado.set_visible(False)
    ax.axvline(n_colunas - 1.5, color=TEXTO, linewidth=1.2, zorder=4)  # separa os meses do total
    j, i = meses.index(pico["mes"]), list(tabela.index).index(pico["tipo"])
    ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor=TEXTO, linewidth=2.2, zorder=5))

    # legenda da escala de cor (equivale à legenda da formatação condicional no Power BI)
    barra = fig.add_axes([0.66, 0.78, 0.17, 0.016])
    barra.imshow(np.linspace(0, 1, 256)[None, :], cmap=cmap, aspect="auto", extent=[0, vmax, 0, 1])
    barra.set_xticks([])
    barra.set_yticks([])
    for lado in barra.spines.values():
        lado.set_visible(False)
    fig.text(0.60, 0.788, "Taxa de negação", fontsize=9.5, color=TEXTO, ha="right", va="center")
    fig.text(0.65, 0.788, "0%", fontsize=9, color=CINZA, ha="right", va="center")
    fig.text(0.84, 0.788, f"{_br(vmax, 1)}%", fontsize=9, color=CINZA, ha="left", va="center")
    return _salvar(fig, pasta, "grafico_negacao_mensal.png")


def gerar_graficos(res: dict[str, pd.DataFrame], pasta: Path, seed: int = SEED_PADRAO) -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")  # gera arquivos sem abrir janela
    import matplotlib.pyplot as plt
    plt.rcParams["font.family"] = "DejaVu Sans"  # já vem com o matplotlib: mesmo visual no Windows e no Linux
    return [_grafico_valor_mensal(res, pasta, seed),
            _grafico_mix_por_tipo(res, pasta, seed),
            _grafico_negacao_mensal(res, pasta, seed)]


# ---------------------------------------------------------------------------
# Resumo em Markdown (os textos de "leitura" são calculados a partir dos resultados)
# ---------------------------------------------------------------------------
def escrever_resumo(res: dict[str, pd.DataFrame], contagens: dict[str, int],
                    seed: int, pasta: Path) -> Path:
    vm, mix, neg = res["volume_mensal"], res["mix_por_tipo"], res["negacao_mensal_por_tipo"]
    seg, conc = res["ticket_por_segmento"], res["concentracao_por_decil"]

    mes_max = vm.loc[vm["valor_total"].idxmax()]
    mes_min = vm.loc[vm["valor_total"].idxmin()]
    tipo_top = mix.iloc[0]
    pico = neg.loc[neg["taxa_negacao_pct"].idxmax()]
    outros = neg[(neg["tipo"] == pico["tipo"]) & (neg["mes"] != pico["mes"])]["taxa_negacao_pct"].mean()
    seg_top, seg_base = seg.iloc[0], seg.iloc[-1]
    decil1 = conc.loc[conc["decil"] == 1, "pct_valor"].iloc[0]

    if pd.isna(outros):
        comparacao = ""
    else:
        comparacao = f", contra uma média de {_br(outros, 2)}% nos demais meses do mesmo tipo"

    leitura = [
        f"- Maior valor mensal: {mes_max['mes']} (R$ {_br(mes_max['valor_total'])}); "
        f"menor: {mes_min['mes']} (R$ {_br(mes_min['valor_total'])}).",
        f"- Tipo com maior participação no valor: {tipo_top['tipo']} ({_br(tipo_top['pct_valor'], 1)}%).",
        f"- Maior taxa de negação mensal: {pico['tipo']} em {pico['mes']} "
        f"({_br(pico['taxa_negacao_pct'], 2)}%{comparacao}).",
        f"- Ticket médio mais alto: {seg_top['segmento']} (R$ {_br(seg_top['ticket_medio'])}); "
        f"mais baixo: {seg_base['segmento']} (R$ {_br(seg_base['ticket_medio'])}).",
        f"- Os 10% de clientes que mais movimentam concentram {_br(decil1, 1)}% do valor concluído.",
    ]

    partes = [
        "# Resumo dos resultados",
        "",
        "> **Dados 100% sintéticos**, gerados por regras definidas em `analise.py`. "
        "Os padrões abaixo refletem essas regras e não descrevem nenhum banco, cliente ou mercado real.",
        "",
        f"Parâmetros desta execução: seed = {seed}; {_br(contagens['clientes'], 0)} clientes, "
        f"{_br(contagens['contas'], 0)} contas, {_br(contagens['transacoes'], 0)} transações "
        f"({_br(contagens['negadas'], 0)} negadas).",
        "",
        "## Leitura dos resultados",
        "",
        *leitura,
        "",
        "## 1. Volume mensal (transações concluídas)",
        "",
        _tabela_md(vm),
        "",
        "## 2. Mix por tipo de transação",
        "",
        _tabela_md(mix),
        "",
        "## 3. Maiores taxas de negação mensais (10 primeiras linhas)",
        "",
        _tabela_md(neg.sort_values("taxa_negacao_pct", ascending=False).head(10)),
        "",
        "A tabela completa está em `negacao_mensal_por_tipo.csv`.",
        "",
        "## 4. Ticket médio por segmento",
        "",
        _tabela_md(seg),
        "",
        "## 5. Concentração do valor por decil de clientes (decil 1 = maiores)",
        "",
        _tabela_md(conc),
        "",
    ]
    arquivo = pasta / "resumo.md"
    arquivo.write_text("\n".join(partes), encoding="utf-8")
    return arquivo


# ---------------------------------------------------------------------------
# Orquestração
# ---------------------------------------------------------------------------
def executar(seed: int = SEED_PADRAO,
             saida: str | Path = "resultados",
             banco: str | Path = "dados/banco.db",
             n_clientes: int = N_CLIENTES_PADRAO,
             n_transacoes: int = N_TRANSACOES_PADRAO) -> Path:
    if sqlite3.sqlite_version_info < (3, 25, 0):
        sys.exit(f"SQLite {sqlite3.sqlite_version} é antigo demais: as consultas usam funções de janela (3.25+).")

    pasta = Path(saida)
    pasta.mkdir(parents=True, exist_ok=True)

    print(f"1/4 Gerando dados sintéticos (seed={seed})...")
    dados = gerar_dados(seed, n_clientes, n_transacoes)
    conn = criar_banco(banco, dados)

    try:
        print("2/4 Executando consultas SQL...")
        res = executar_consultas(conn)
        for nome, df in res.items():
            df.to_csv(pasta / f"{nome}.csv", index=False, encoding="utf-8-sig")
        pd.read_sql_query("SELECT * FROM transacoes ORDER BY transacao_id LIMIT 20", conn).to_csv(
            pasta / "amostra_transacoes.csv", index=False, encoding="utf-8-sig")
        contagens = {
            "clientes": conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0],
            "contas": conn.execute("SELECT COUNT(*) FROM contas").fetchone()[0],
            "transacoes": conn.execute("SELECT COUNT(*) FROM transacoes").fetchone()[0],
            "negadas": conn.execute("SELECT COUNT(*) FROM transacoes WHERE status = 'negada'").fetchone()[0],
        }
    finally:
        conn.close()

    print("3/4 Gerando gráficos...")
    gerar_graficos(res, pasta, seed)

    print("4/4 Escrevendo resumo...")
    escrever_resumo(res, contagens, seed, pasta)

    print(f"Pronto. Resultados em: {pasta.resolve()}")
    return pasta


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Análise de transações bancárias SINTÉTICAS com SQLite.")
    parser.add_argument("--seed", type=int, default=SEED_PADRAO, help="semente do gerador (padrão: 42)")
    parser.add_argument("--saida", default="resultados", help="pasta de resultados (padrão: resultados)")
    parser.add_argument("--banco", default="dados/banco.db", help="arquivo SQLite (padrão: dados/banco.db)")
    args = parser.parse_args(argv)
    executar(seed=args.seed, saida=args.saida, banco=args.banco)


if __name__ == "__main__":
    main()
