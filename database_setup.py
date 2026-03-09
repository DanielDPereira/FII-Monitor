import sqlite3

def setup_database():
    # Conecta ao arquivo do banco (será criado se não existir)
    conn = sqlite3.connect('fii_monitor.db')
    cursor = conn.cursor()

    # Habilita o suporte a Chaves Estrangeiras (Foreign Keys) no SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. TABELA DE ATIVOS
    # CHECK(length(ticker) <= 6) garante a integridade pedida
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ativos (
            ticker TEXT PRIMARY KEY CHECK(length(ticker) <= 6),
            nome TEXT NOT NULL,
            setor TEXT,
            preco_teto REAL DEFAULT 0.0
        )
    ''')

    # 2. TABELA DE TRANSAÇÕES
    # Registra o histórico de compras e vendas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            data TEXT NOT NULL,          -- Formato: YYYY-MM-DD
            tipo TEXT CHECK(tipo IN ('COMPRA', 'VENDA')),
            quantidade INTEGER NOT NULL CHECK(quantidade > 0),
            preco_unitario REAL NOT NULL,
            FOREIGN KEY (ticker) REFERENCES ativos (ticker)
        )
    ''')

    # 3. TABELA DE PROVENTOS (Dividendos)
    # Para acompanhar quanto o fundo está rendendo no seu bolso
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            data_pagamento TEXT NOT NULL,
            valor_total REAL NOT NULL,
            FOREIGN KEY (ticker) REFERENCES ativos (ticker)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Banco de dados 'fii_monitor.db' configurado com sucesso!")

if __name__ == "__main__":
    setup_database()