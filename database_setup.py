import os
import sqlite3


DB_PATH = os.path.join(os.path.dirname(__file__), "fii_monitor.db")


def _column_exists(cursor, table_name: str, column_name: str) -> bool:
    rows = cursor.execute(f"PRAGMA table_info({table_name})").fetchall()
    return any(row[1] == column_name for row in rows)


def _migrate_ativos_remove_preco_teto(conn, cursor):
    """Remove coluna legado preco_teto de ativos, preservando dados."""
    if not _column_exists(cursor, "ativos", "preco_teto"):
        return

    conn.execute("PRAGMA foreign_keys = OFF;")
    cursor.execute("ALTER TABLE ativos RENAME TO ativos_old")
    cursor.execute(
        '''
        CREATE TABLE ativos (
            ticker TEXT PRIMARY KEY CHECK(length(ticker) <= 15),
            nome TEXT NOT NULL,
            setor TEXT
        )
        '''
    )
    cursor.execute(
        '''
        INSERT INTO ativos (ticker, nome, setor)
        SELECT ticker, nome, setor
        FROM ativos_old
        '''
    )
    cursor.execute("DROP TABLE ativos_old")
    conn.execute("PRAGMA foreign_keys = ON;")


def setup_database(verbose: bool = True):
    # Conecta ao arquivo do banco (será criado se não existir)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Habilita o suporte a chaves estrangeiras no SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. TABELA DE ATIVOS
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS ativos (
            ticker TEXT PRIMARY KEY CHECK(length(ticker) <= 15),
            nome TEXT NOT NULL,
            setor TEXT
        )
        '''
    )

    # Migração para bancos legados que ainda possuem preco_teto em ativos.
    _migrate_ativos_remove_preco_teto(conn, cursor)

    # 2. TABELA DE TRANSAÇÕES (carteira do usuário)
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            data TEXT NOT NULL,
            tipo TEXT CHECK(tipo IN ('COMPRA', 'VENDA')),
            quantidade INTEGER NOT NULL CHECK(quantidade > 0),
            preco_unitario REAL NOT NULL,
            FOREIGN KEY (ticker) REFERENCES ativos (ticker)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
        )
        '''
    )

    # 3. TABELA DE PROVENTOS (carteira do usuário)
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS proventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            data_pagamento TEXT NOT NULL,
            valor_total REAL NOT NULL,
            FOREIGN KEY (ticker) REFERENCES ativos (ticker)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
        )
        '''
    )

    # 4. HISTÓRICO DIÁRIO (modelo price_history.csv)
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS fii_price_history (
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            dividends REAL DEFAULT 0,
            PRIMARY KEY (ticker, date),
            FOREIGN KEY (ticker) REFERENCES ativos (ticker)
                ON UPDATE CASCADE
                ON DELETE CASCADE
        )
        '''
    )

    # 5. HISTÓRICO MENSAL DE PREÇOS (modelo monthly_prices.csv)
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS fii_monthly_prices (
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (ticker, date),
            FOREIGN KEY (ticker) REFERENCES ativos (ticker)
                ON UPDATE CASCADE
                ON DELETE CASCADE
        )
        '''
    )

    # 6. DIVIDENDOS POR EVENTO (modelo dividends.csv)
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS fii_dividends (
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            dividend REAL NOT NULL,
            PRIMARY KEY (ticker, date),
            FOREIGN KEY (ticker) REFERENCES ativos (ticker)
                ON UPDATE CASCADE
                ON DELETE CASCADE
        )
        '''
    )

    # 7. DIVIDENDOS MENSAIS AGREGADOS (modelo dividends_monthly.csv)
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS fii_dividends_monthly (
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            dividend REAL NOT NULL,
            PRIMARY KEY (ticker, date),
            FOREIGN KEY (ticker) REFERENCES ativos (ticker)
                ON UPDATE CASCADE
                ON DELETE CASCADE
        )
        '''
    )

    # 8. SNAPSHOT DE MÉTRICAS (modelo metrics.csv)
    # Mantém histórico de coleta com timestamp para comparar evoluções.
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS fii_metrics (
            ticker TEXT NOT NULL,
            collected_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            price REAL,
            book_value REAL,
            p_vp REAL,
            dividend_yield_api REAL,
            dividend_12m REAL,
            dy_12m REAL,
            market_cap INTEGER,
            avg_volume INTEGER,
            PRIMARY KEY (ticker, collected_at),
            FOREIGN KEY (ticker) REFERENCES ativos (ticker)
                ON UPDATE CASCADE
                ON DELETE CASCADE
        )
        '''
    )

    # Índices auxiliares para consultas frequentes por ticker e data.
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_fii_price_history_ticker_date "
        "ON fii_price_history (ticker, date DESC)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_fii_monthly_prices_ticker_date "
        "ON fii_monthly_prices (ticker, date DESC)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_fii_dividends_ticker_date "
        "ON fii_dividends (ticker, date DESC)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_fii_dividends_monthly_ticker_date "
        "ON fii_dividends_monthly (ticker, date DESC)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_fii_metrics_ticker_collected_at "
        "ON fii_metrics (ticker, collected_at DESC)"
    )

    conn.commit()
    conn.close()
    if verbose:
        print(f"Banco de dados configurado com sucesso em: {DB_PATH}")


if __name__ == "__main__":
    setup_database()