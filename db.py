import sqlite3
import os
import csv
from datetime import datetime

# Caminho absoluto do banco de dados, sempre relativo a este arquivo
DB_PATH = os.path.join(os.path.dirname(__file__), "fii_monitor.db")


def _normalize_user_ticker(ticker: str) -> str:
    """Normaliza ticker informado pelo usuario (trim + upper)."""
    return (ticker or "").strip().upper()


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# ── ATIVOS ──────────────────────────────────────────────────────────────────

def listar_ativos():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT ticker, nome, setor FROM ativos ORDER BY ticker"
        ).fetchall()
    return [dict(r) for r in rows]


def buscar_ativo(ticker: str):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT ticker, nome, setor FROM ativos WHERE ticker = ?",
            (_normalize_user_ticker(ticker),),
        ).fetchone()
    return dict(row) if row else None


def inserir_ativo(ticker: str, nome: str, setor: str) -> bool:
    """Retorna True se inserido, False se ticker já existe."""
    try:
        ticker_db = _normalize_user_ticker(ticker)
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO ativos (ticker, nome, setor) VALUES (?, ?, ?)",
                (ticker_db, nome, setor),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def atualizar_ativo(ticker: str, nome: str, setor: str):
    ticker_db = _normalize_user_ticker(ticker)
    with get_connection() as conn:
        conn.execute(
            "UPDATE ativos SET nome = ?, setor = ? WHERE ticker = ?",
            (nome, setor, ticker_db),
        )
        conn.commit()


def deletar_ativo(ticker: str):
    ticker_db = _normalize_user_ticker(ticker)
    with get_connection() as conn:
        conn.execute("DELETE FROM ativos WHERE ticker = ?", (ticker_db,))
        conn.commit()


# ── DADOS DE MERCADO (YFINANCE) ────────────────────────────────────────────

def _upsert_ativo_minimo(conn, ticker: str):
    ticker_norm = _normalize_user_ticker(ticker)
    conn.execute(
        """
        INSERT INTO ativos (ticker, nome, setor)
        VALUES (?, ?, 'Outro')
        ON CONFLICT(ticker) DO NOTHING
        """,
        (ticker_norm, ticker_norm),
    )


def _parse_int(value):
    if value in (None, ""):
        return None
    return int(float(value))


def _parse_float(value):
    if value in (None, ""):
        return None
    return float(value)


def _normalize_date(value):
    if value in (None, ""):
        return None
    return str(value)


def importar_dados_mercado_csv(data_dir: str) -> dict:
    """Importa CSVs do coletor para o SQLite com upsert por ticker+date."""
    files = {
        "price_history": os.path.join(data_dir, "price_history.csv"),
        "monthly_prices": os.path.join(data_dir, "monthly_prices.csv"),
        "dividends": os.path.join(data_dir, "dividends.csv"),
        "dividends_monthly": os.path.join(data_dir, "dividends_monthly.csv"),
        "metrics": os.path.join(data_dir, "metrics.csv"),
    }

    missing = [name for name, path in files.items() if not os.path.exists(path)]
    if missing:
        raise FileNotFoundError(
            f"Arquivos ausentes em {data_dir}: {', '.join(missing)}"
        )

    counters = {
        "fii_price_history": 0,
        "fii_monthly_prices": 0,
        "fii_dividends": 0,
        "fii_dividends_monthly": 0,
        "fii_metrics": 0,
    }

    with get_connection() as conn:
        with open(files["price_history"], "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ticker = _normalize_user_ticker(row["ticker"])
                _upsert_ativo_minimo(conn, ticker)
                conn.execute(
                    """
                    INSERT INTO fii_price_history
                    (ticker, date, open, high, low, close, volume, dividends)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(ticker, date) DO UPDATE SET
                        open = excluded.open,
                        high = excluded.high,
                        low = excluded.low,
                        close = excluded.close,
                        volume = excluded.volume,
                        dividends = excluded.dividends
                    """,
                    (
                        ticker,
                        _normalize_date(row.get("date")),
                        _parse_float(row.get("open")),
                        _parse_float(row.get("high")),
                        _parse_float(row.get("low")),
                        _parse_float(row.get("close")),
                        _parse_int(row.get("volume")),
                        _parse_float(row.get("dividends")) or 0,
                    ),
                )
                counters["fii_price_history"] += 1

        with open(files["monthly_prices"], "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ticker = _normalize_user_ticker(row["ticker"])
                _upsert_ativo_minimo(conn, ticker)
                conn.execute(
                    """
                    INSERT INTO fii_monthly_prices
                    (ticker, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(ticker, date) DO UPDATE SET
                        open = excluded.open,
                        high = excluded.high,
                        low = excluded.low,
                        close = excluded.close,
                        volume = excluded.volume
                    """,
                    (
                        ticker,
                        _normalize_date(row.get("date")),
                        _parse_float(row.get("open")),
                        _parse_float(row.get("high")),
                        _parse_float(row.get("low")),
                        _parse_float(row.get("close")),
                        _parse_int(row.get("volume")),
                    ),
                )
                counters["fii_monthly_prices"] += 1

        with open(files["dividends"], "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ticker = _normalize_user_ticker(row["ticker"])
                _upsert_ativo_minimo(conn, ticker)
                conn.execute(
                    """
                    INSERT INTO fii_dividends (ticker, date, dividend)
                    VALUES (?, ?, ?)
                    ON CONFLICT(ticker, date) DO UPDATE SET
                        dividend = excluded.dividend
                    """,
                    (
                        ticker,
                        _normalize_date(row.get("date")),
                        _parse_float(row.get("dividend")) or 0,
                    ),
                )
                counters["fii_dividends"] += 1

        with open(files["dividends_monthly"], "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ticker = _normalize_user_ticker(row["ticker"])
                _upsert_ativo_minimo(conn, ticker)
                conn.execute(
                    """
                    INSERT INTO fii_dividends_monthly (ticker, date, dividend)
                    VALUES (?, ?, ?)
                    ON CONFLICT(ticker, date) DO UPDATE SET
                        dividend = excluded.dividend
                    """,
                    (
                        ticker,
                        _normalize_date(row.get("date")),
                        _parse_float(row.get("dividend")) or 0,
                    ),
                )
                counters["fii_dividends_monthly"] += 1

        with open(files["metrics"], "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ticker = _normalize_user_ticker(row["ticker"])
                _upsert_ativo_minimo(conn, ticker)
                conn.execute(
                    """
                    INSERT INTO fii_metrics
                    (ticker, collected_at, price, book_value, p_vp, dividend_yield_api,
                     dividend_12m, dy_12m, market_cap, avg_volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        ticker,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        _parse_float(row.get("price")),
                        _parse_float(row.get("book_value")),
                        _parse_float(row.get("p_vp")),
                        _parse_float(row.get("dividend_yield_api")),
                        _parse_float(row.get("dividend_12m")),
                        _parse_float(row.get("dy_12m")),
                        _parse_int(row.get("market_cap")),
                        _parse_int(row.get("avg_volume")),
                    ),
                )
                counters["fii_metrics"] += 1

        conn.commit()

    return counters


def listar_ativos_com_metricas_recentes():
    """Lista ativos junto com último snapshot de métricas, quando existir."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                a.ticker,
                a.nome,
                a.setor,
                m.price,
                m.p_vp,
                m.dy_12m,
                m.dividend_yield_api,
                m.collected_at
            FROM ativos a
            LEFT JOIN fii_metrics m
                ON m.ticker = a.ticker
               AND m.collected_at = (
                   SELECT MAX(m2.collected_at)
                   FROM fii_metrics m2
                   WHERE m2.ticker = a.ticker
               )
            ORDER BY a.ticker
            """
        ).fetchall()
    return [dict(r) for r in rows]


def obter_historico_preco(ticker: str, limite: int = 30):
    ticker_db = _normalize_user_ticker(ticker)
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT ticker, date, open, high, low, close, volume, dividends
            FROM fii_price_history
            WHERE ticker = ?
            ORDER BY date DESC
            LIMIT ?
            """,
            (ticker_db, int(limite)),
        ).fetchall()
    return [dict(r) for r in rows]


# ── TRANSAÇÕES E CARTEIRA ──────────────────────────────────────────────────

def inserir_transacao(
    ticker: str,
    data: str,
    tipo: str,
    quantidade: int,
    preco_unitario: float,
) -> bool:
    """Insere transacao para um ativo existente. Retorna False se ativo nao existir."""
    ticker_db = _normalize_user_ticker(ticker)
    tipo_db = (tipo or "").strip().upper()

    if tipo_db not in ("COMPRA", "VENDA"):
        raise ValueError("tipo deve ser COMPRA ou VENDA")

    if quantidade <= 0:
        raise ValueError("quantidade deve ser maior que zero")

    if preco_unitario <= 0:
        raise ValueError("preco_unitario deve ser maior que zero")

    with get_connection() as conn:
        ativo = conn.execute(
            "SELECT 1 FROM ativos WHERE ticker = ?",
            (ticker_db,),
        ).fetchone()
        if not ativo:
            return False

        conn.execute(
            """
            INSERT INTO transacoes (ticker, data, tipo, quantidade, preco_unitario)
            VALUES (?, ?, ?, ?, ?)
            """,
            (ticker_db, data, tipo_db, int(quantidade), float(preco_unitario)),
        )
        conn.commit()
    return True


def listar_transacoes(ticker: str = None, limite: int = 500):
    """Lista transacoes mais recentes, opcionalmente filtrando por ticker."""
    query = (
        """
        SELECT id, ticker, data, tipo, quantidade, preco_unitario,
               ROUND(quantidade * preco_unitario, 2) AS valor_total
        FROM transacoes
        """
    )
    params = []

    if ticker:
        query += " WHERE ticker = ?"
        params.append(_normalize_user_ticker(ticker))

    query += " ORDER BY data DESC, id DESC LIMIT ?"
    params.append(int(limite))

    with get_connection() as conn:
        rows = conn.execute(query, tuple(params)).fetchall()
    return [dict(r) for r in rows]


def deletar_transacao(transacao_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM transacoes WHERE id = ?", (int(transacao_id),))
        conn.commit()


def calcular_posicoes_carteira():
    """
    Consolida carteira por ticker a partir das transacoes e do ultimo preco coletado.
    Retorna apenas ativos com quantidade em carteira maior que zero.
    """
    with get_connection() as conn:
        transacoes = conn.execute(
            """
            SELECT ticker, data, tipo, quantidade, preco_unitario
            FROM transacoes
            ORDER BY ticker, data, id
            """
        ).fetchall()

        ativos = conn.execute(
            "SELECT ticker, nome, setor FROM ativos"
        ).fetchall()

        precos_rows = conn.execute(
            """
            SELECT m.ticker, m.price
            FROM fii_metrics m
            INNER JOIN (
                SELECT ticker, MAX(collected_at) AS max_collected_at
                FROM fii_metrics
                GROUP BY ticker
            ) latest
                ON latest.ticker = m.ticker
               AND latest.max_collected_at = m.collected_at
            """
        ).fetchall()

    ativos_map = {row["ticker"]: dict(row) for row in ativos}
    precos_map = {row["ticker"]: row["price"] for row in precos_rows}

    consolidado = {}
    for tx in transacoes:
        ticker = tx["ticker"]
        qtd = int(tx["quantidade"])
        preco = float(tx["preco_unitario"])
        tipo = tx["tipo"]

        if ticker not in consolidado:
            consolidado[ticker] = {
                "ticker": ticker,
                "nome": ativos_map.get(ticker, {}).get("nome", ticker),
                "setor": ativos_map.get(ticker, {}).get("setor", "Outro"),
                "quantidade": 0,
                "custo_posicao": 0.0,
                "lucro_realizado": 0.0,
            }

        pos = consolidado[ticker]

        if tipo == "COMPRA":
            pos["quantidade"] += qtd
            pos["custo_posicao"] += qtd * preco
        elif tipo == "VENDA":
            if pos["quantidade"] <= 0:
                continue

            qtd_venda = min(qtd, pos["quantidade"])
            preco_medio_atual = pos["custo_posicao"] / pos["quantidade"]
            pos["lucro_realizado"] += (preco - preco_medio_atual) * qtd_venda
            pos["custo_posicao"] -= preco_medio_atual * qtd_venda
            pos["quantidade"] -= qtd_venda

            if pos["quantidade"] == 0:
                pos["custo_posicao"] = 0.0

    posicoes = []
    for ticker, pos in consolidado.items():
        if pos["quantidade"] <= 0:
            continue

        preco_medio = pos["custo_posicao"] / pos["quantidade"]
        preco_atual = precos_map.get(ticker)
        valor_atual = (
            float(preco_atual) * pos["quantidade"]
            if preco_atual is not None
            else None
        )
        pl_nao_realizado = (
            valor_atual - pos["custo_posicao"]
            if valor_atual is not None
            else None
        )

        posicoes.append(
            {
                "ticker": ticker,
                "nome": pos["nome"],
                "setor": pos["setor"],
                "quantidade": pos["quantidade"],
                "preco_medio": round(preco_medio, 4),
                "custo_posicao": round(pos["custo_posicao"], 2),
                "preco_atual": round(float(preco_atual), 4) if preco_atual is not None else None,
                "valor_atual": round(valor_atual, 2) if valor_atual is not None else None,
                "pl_nao_realizado": round(pl_nao_realizado, 2) if pl_nao_realizado is not None else None,
                "lucro_realizado": round(pos["lucro_realizado"], 2),
            }
        )

    posicoes.sort(key=lambda x: x["custo_posicao"], reverse=True)
    return posicoes


def resumo_carteira():
    posicoes = calcular_posicoes_carteira()
    custo_total = round(sum(p["custo_posicao"] for p in posicoes), 2)

    valor_atual_total = round(
        sum(p["valor_atual"] for p in posicoes if p["valor_atual"] is not None),
        2,
    )
    pl_total = round(valor_atual_total - custo_total, 2)

    return {
        "ativos_em_carteira": len(posicoes),
        "custo_total": custo_total,
        "valor_atual_total": valor_atual_total,
        "pl_total": pl_total,
    }
