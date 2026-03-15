import tempfile
import unittest
from pathlib import Path

import database_setup
import db


class DBCarteiraTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        temp_db_path = str(Path(self.temp_dir.name) / "test_fii_monitor.db")

        self.original_db_path = db.DB_PATH
        self.original_setup_db_path = database_setup.DB_PATH

        db.DB_PATH = temp_db_path
        database_setup.DB_PATH = temp_db_path
        database_setup.setup_database(verbose=False)

        db.inserir_ativo("MXRF11", "Maxi Renda", "Recebíveis (CRI)")

    def tearDown(self):
        db.DB_PATH = self.original_db_path
        database_setup.DB_PATH = self.original_setup_db_path
        try:
            self.temp_dir.cleanup()
        except PermissionError:
            pass

    def _inserir_preco_atual(self, ticker: str, price: float, collected_at: str = "2026-03-14 10:00:00"):
        with db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO fii_metrics
                (ticker, collected_at, price, book_value, p_vp, dividend_yield_api,
                 dividend_12m, dy_12m, market_cap, avg_volume)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (ticker, collected_at, price, None, None, None, None, None, None, None),
            )
            conn.commit()

    def _inserir_dividendo(self, ticker: str, date: str, dividend: float):
        with db.get_connection() as conn:
            conn.execute(
                "INSERT INTO fii_dividends (ticker, date, dividend) VALUES (?, ?, ?)",
                (ticker, date, dividend),
            )
            conn.commit()

    def test_calcula_preco_medio_e_valor_atual(self):
        db.inserir_transacao("MXRF11", "2026-01-10", "COMPRA", 10, 10.0)
        db.inserir_transacao("MXRF11", "2026-01-20", "COMPRA", 5, 12.0)
        self._inserir_preco_atual("MXRF11", 11.0)

        posicoes = db.calcular_posicoes_carteira()

        self.assertEqual(len(posicoes), 1)
        pos = posicoes[0]
        self.assertEqual(pos["quantidade"], 15)
        self.assertAlmostEqual(pos["preco_medio"], 10.6667, places=4)
        self.assertEqual(pos["custo_posicao"], 160.0)
        self.assertEqual(pos["valor_atual"], 165.0)
        self.assertEqual(pos["pl_nao_realizado"], 5.0)

    def test_venda_parcial_mantem_preco_medio_e_calcula_lucro_realizado(self):
        db.inserir_transacao("MXRF11", "2026-01-10", "COMPRA", 10, 10.0)
        db.inserir_transacao("MXRF11", "2026-01-20", "COMPRA", 10, 12.0)
        db.inserir_transacao("MXRF11", "2026-02-01", "VENDA", 5, 15.0)

        pos = db.calcular_posicoes_carteira()[0]

        self.assertEqual(pos["quantidade"], 15)
        self.assertEqual(pos["custo_posicao"], 165.0)
        self.assertAlmostEqual(pos["preco_medio"], 11.0, places=4)
        self.assertEqual(pos["lucro_realizado"], 20.0)

    def test_bloqueia_venda_sem_saldo(self):
        db.inserir_transacao("MXRF11", "2026-01-10", "COMPRA", 2, 10.0)

        with self.assertRaisesRegex(ValueError, "saldo atual é 2"):
            db.inserir_transacao("MXRF11", "2026-01-11", "VENDA", 3, 11.0)

    def test_atualizar_transacao_recalcula_posicao(self):
        db.inserir_transacao("MXRF11", "2026-01-10", "COMPRA", 10, 10.0)
        db.inserir_transacao("MXRF11", "2026-01-15", "COMPRA", 5, 8.0)

        transacao = db.listar_transacoes(limite=10)[0]
        db.atualizar_transacao(
            transacao_id=transacao["id"],
            ticker="MXRF11",
            data="2026-01-15",
            tipo="COMPRA",
            quantidade=5,
            preco_unitario=14.0,
        )

        pos = db.calcular_posicoes_carteira()[0]
        self.assertEqual(pos["custo_posicao"], 170.0)
        self.assertAlmostEqual(pos["preco_medio"], 11.3333, places=4)

    def test_sincroniza_proventos_conforme_posicao_na_data(self):
        db.inserir_transacao("MXRF11", "2026-01-10", "COMPRA", 10, 10.0)
        db.inserir_transacao("MXRF11", "2026-02-10", "VENDA", 4, 11.0)
        self._inserir_dividendo("MXRF11", "2026-02-01", 0.10)
        self._inserir_dividendo("MXRF11", "2026-03-01", 0.10)

        inserted = db.sincronizar_proventos_automaticos()
        resumo = db.resumo_carteira()
        pos = db.calcular_posicoes_carteira()[0]

        self.assertEqual(inserted, 2)
        self.assertEqual(pos["proventos_acumulados"], 1.6)
        self.assertEqual(resumo["proventos_acumulados_total"], 1.6)


if __name__ == "__main__":
    unittest.main()