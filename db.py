import sqlite3
import os
import csv
from datetime import datetime

# Caminho absoluto do banco de dados, sempre relativo a este arquivo
DB_PATH = os.path.join(os.path.dirname(__file__), "fii_monitor.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# ── ATIVOS ──────────────────────────────────────────────────────────────────

def listar_ativos():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT ticker, nome, setor, preco_teto FROM ativos ORDER BY ticker"
        ).fetchall()
    return [dict(r) for r in rows]


def buscar_ativo(ticker: str):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT ticker, nome, setor, preco_teto FROM ativos WHERE ticker = ?",
            (ticker.upper(),),
        ).fetchone()
    return dict(row) if row else None


def inserir_ativo(ticker: str, nome: str, setor: str, preco_teto: float) -> bool:
    """Retorna True se inserido, False se ticker já existe."""
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO ativos (ticker, nome, setor, preco_teto) VALUES (?, ?, ?, ?)",
                (ticker.upper(), nome, setor, preco_teto),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def atualizar_ativo(ticker: str, nome: str, setor: str, preco_teto: float):
    with get_connection() as conn:
        conn.execute(
            "UPDATE ativos SET nome = ?, setor = ?, preco_teto = ? WHERE ticker = ?",
            (nome, setor, preco_teto, ticker.upper()),
        )
        conn.commit()


def deletar_ativo(ticker: str):
    with get_connection() as conn:
        conn.execute("DELETE FROM ativos WHERE ticker = ?", (ticker.upper(),))
        conn.commit()


# ── DADOS DE MERCADO (YFINANCE) ────────────────────────────────────────────

def _upsert_ativo_minimo(conn, ticker: str):
    ticker_norm = ticker.upper().strip()
    conn.execute(
        """
        INSERT INTO ativos (ticker, nome, setor, preco_teto)
        VALUES (?, ?, 'Outro', 0)
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
                ticker = row["ticker"].upper().strip()
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
                ticker = row["ticker"].upper().strip()
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
                ticker = row["ticker"].upper().strip()
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
                ticker = row["ticker"].upper().strip()
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
                ticker = row["ticker"].upper().strip()
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
                a.preco_teto,
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
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT ticker, date, open, high, low, close, volume, dividends
            FROM fii_price_history
            WHERE ticker = ?
            ORDER BY date DESC
            LIMIT ?
            """,
            (ticker.upper(), int(limite)),
        ).fetchall()
    return [dict(r) for r in rows]
