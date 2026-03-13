"""
Página: Carteira e Transações
"""

from datetime import date
import streamlit as st
import sys
import os

# Garante que o diretório raiz do projeto está no path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import db


TIPOS_TRANSACAO = ["COMPRA", "VENDA"]


def _fmt_brl(valor):
    if valor is None:
        return "-"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _fmt_pct(valor):
    if valor is None:
        return "-"
    return f"{valor:.2f}%"


def render():
    st.title("📈 Carteira")
    st.markdown("Acompanhe posição consolidada e registre suas operações.")
    st.divider()

    tab_resumo, tab_transacao, tab_historico = st.tabs(
        ["📊 Posição Atual", "➕ Registrar Transação", "🧾 Histórico"]
    )

    with tab_resumo:
        _tab_resumo()

    with tab_transacao:
        _tab_transacao()

    with tab_historico:
        _tab_historico()


def _tab_resumo():
    resumo = db.resumo_carteira()
    posicoes = db.calcular_posicoes_carteira()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ativos em Carteira", resumo["ativos_em_carteira"])
    col2.metric("Custo Total", _fmt_brl(resumo["custo_total"]))
    col3.metric("Valor Atual", _fmt_brl(resumo["valor_atual_total"]))

    pl_total = resumo["pl_total"]
    delta_total = None
    if resumo["custo_total"] > 0:
        delta_total = _fmt_pct((pl_total / resumo["custo_total"]) * 100)
    col4.metric("P/L Total", _fmt_brl(pl_total), delta=delta_total)

    st.markdown("---")

    if not posicoes:
        st.info("Nenhuma posição em carteira. Registre compras na aba de transações.", icon="📭")
        return

    tabela = []
    for p in posicoes:
        pl_pct = None
        if p["custo_posicao"] > 0 and p["pl_nao_realizado"] is not None:
            pl_pct = (p["pl_nao_realizado"] / p["custo_posicao"]) * 100

        tabela.append(
            {
                "Ticker": p["ticker"],
                "Nome": p["nome"],
                "Setor": p["setor"],
                "Qtd": p["quantidade"],
                "Preço Médio": _fmt_brl(p["preco_medio"]),
                "Custo": _fmt_brl(p["custo_posicao"]),
                "Preço Atual": _fmt_brl(p["preco_atual"]),
                "Valor Atual": _fmt_brl(p["valor_atual"]),
                "P/L": _fmt_brl(p["pl_nao_realizado"]),
                "P/L %": _fmt_pct(pl_pct),
            }
        )

    st.dataframe(tabela, use_container_width=True, hide_index=True)


def _tab_transacao():
    st.subheader("Registrar Compra ou Venda")

    ativos = db.listar_ativos()
    if not ativos:
        st.warning("Cadastre ao menos um ativo antes de lançar transações.")
        return

    opcoes_ativos = [a["ticker"] for a in ativos]

    with st.form("form_transacao", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            ticker = st.selectbox("Ticker", options=opcoes_ativos)
            tipo = st.radio("Tipo", options=TIPOS_TRANSACAO, horizontal=True)
        with col2:
            data_tx = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")
            quantidade = st.number_input("Quantidade", min_value=1, step=1)

        preco_unitario = st.number_input(
            "Preço Unitário (R$)",
            min_value=0.01,
            step=0.01,
            format="%.2f",
        )

        enviar = st.form_submit_button("💾 Salvar Transação", use_container_width=True, type="primary")

    if enviar:
        ok = db.inserir_transacao(
            ticker=ticker,
            data=data_tx.isoformat(),
            tipo=tipo,
            quantidade=int(quantidade),
            preco_unitario=float(preco_unitario),
        )
        if ok:
            st.success(f"Transação de {tipo} para {ticker} registrada com sucesso.")
            st.rerun()
        else:
            st.error("Não foi possível salvar: o ativo informado não existe.")


def _tab_historico():
    st.subheader("Histórico de Transações")

    transacoes = db.listar_transacoes(limite=1000)
    if not transacoes:
        st.info("Nenhuma transação registrada ainda.", icon="🧾")
        return

    tabela = []
    for tx in transacoes:
        tabela.append(
            {
                "ID": tx["id"],
                "Data": tx["data"],
                "Ticker": tx["ticker"],
                "Tipo": tx["tipo"],
                "Quantidade": tx["quantidade"],
                "Preço Unitário": _fmt_brl(tx["preco_unitario"]),
                "Valor Total": _fmt_brl(tx["valor_total"]),
            }
        )

    st.dataframe(tabela, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.caption("Exclusão de transação é permanente e altera os cálculos da carteira.")

    ids = [tx["id"] for tx in transacoes]
    tx_id = st.selectbox("Selecionar ID para excluir", options=ids)
    confirmar = st.checkbox("Confirmo exclusão da transação selecionada")

    if st.button("🗑️ Excluir Transação", disabled=not confirmar):
        db.deletar_transacao(tx_id)
        st.success("Transação excluída com sucesso.")
        st.rerun()
