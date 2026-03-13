import sqlite3
import os

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
